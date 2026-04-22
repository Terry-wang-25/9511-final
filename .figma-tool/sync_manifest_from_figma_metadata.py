#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge figma_manifest.json using get_metadata XML for page 9511-watermelon_update.

用法:
  1. 在 Cursor / Figma MCP 中对 fileKey 调用 get_metadata，nodeId 填画布页 id（如 0:1）。
  2. 将返回的 XML 全文保存为 metadata.xml（UTF-8）。
  3. 运行: python sync_manifest_from_figma_metadata.py metadata.xml

规则: 顶层 <frame id="N:M" name="..."> 与 原型设计/<basename> 内 <title> 归一化后匹配则写入 manifest。
已有 framesByHtmlFile 中的条目会保留（以 manifest 为准时可先备份）。

无法自动匹配的帧会打印到 stderr，可手工补进 figma_manifest.json 或增加 figma_title_overrides.json。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
PROTOTYPE = REPO / "原型设计"
MAN = ROOT / "figma_manifest.json"
OVERRIDES = ROOT / "figma_title_overrides.json"

TOP_FRAME_RE = re.compile(r'^  <frame id="([^"]+)" name="([^"]*)"', re.MULTILINE)
TITLE_RE = re.compile(r"<title[^>]*>([^<]+)</title>", re.IGNORECASE | re.DOTALL)


def norm(s: str) -> str:
    s = s.strip()
    for ch in ("\u2014", "\u2013", "\u2212"):
        s = s.replace(ch, "-")
    s = s.replace("—", "-")
    return " ".join(s.split()).lower()


def strip_screen_prefix(name: str) -> str:
    n = name.strip()
    if n.lower().startswith("screen / "):
        return n[9:].strip()
    return n


def html_title(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    m = TITLE_RE.search(raw)
    return m.group(1).strip() if m else ""


def load_nav_basenames() -> set[str]:
    data = json.loads((ROOT / "nav_graph.json").read_text(encoding="utf-8"))
    by = data["by_file"]
    need = set(by.keys())
    for edges in by.values():
        for e in edges:
            need.add(e["to"])
    return {f for f in need if (PROTOTYPE / f).is_file()}


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    xml_path = Path(sys.argv[1])
    xml = xml_path.read_text(encoding="utf-8", errors="replace")
    top_frames: dict[str, str] = {}
    for nid, name in TOP_FRAME_RE.findall(xml):
        top_frames[nid] = name

    overrides: dict[str, str] = {}
    if OVERRIDES.is_file():
        overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))

    titles = {}
    for base in sorted(load_nav_basenames()):
        titles[base] = norm(html_title(PROTOTYPE / base))

    inv_override = {norm(v): k for k, v in overrides.items()}

    by_title: dict[str, list[str]] = {}
    for base, t in titles.items():
        if not t:
            continue
        by_title.setdefault(t, []).append(base)

    manifest = json.loads(MAN.read_text(encoding="utf-8"))
    frames: dict[str, str] = dict(manifest.get("framesByHtmlFile", {}))
    used_bases = set(frames.keys())

    unmatched_frames: list[tuple[str, str]] = []

    for nid, fname in sorted(top_frames.items(), key=lambda x: x[0]):
        stem = strip_screen_prefix(fname)
        nt = norm(stem)
        base = overrides.get(fname) or overrides.get(stem)
        if not base and nt in inv_override:
            base = inv_override[nt]
        if not base:
            candidates = by_title.get(nt, [])
            if len(candidates) == 1:
                base = candidates[0]
            elif len(candidates) > 1:
                unmatched_frames.append((nid, fname + f" [ambiguous: {candidates}]"))
                continue
        if not base:
            fuzzy = [b for b, t in titles.items() if t and (t in nt or nt in t)]
            if len(fuzzy) == 1:
                base = fuzzy[0]
            else:
                unmatched_frames.append((nid, fname))
                continue
        if base not in used_bases:
            frames[base] = nid
            used_bases.add(base)

    manifest["framesByHtmlFile"] = dict(sorted(frames.items(), key=lambda x: x[0].lower()))
    MAN.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MAN} with {len(frames)} entries")
    if unmatched_frames:
        print("未自动匹配的顶层帧（请手工核对）:", file=sys.stderr)
        for nid, fn in unmatched_frames:
            print(f"  {nid}\t{fn}", file=sys.stderr)


if __name__ == "__main__":
    main()
