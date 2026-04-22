#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
PROTOTYPE = REPO / "原型设计"

TITLE_RE = re.compile(r"<title[^>]*>([^<]+)</title>", re.IGNORECASE | re.DOTALL)
TOP_FRAME_RE = re.compile(r'^  <frame id="([^"]+)" name="([^"]*)"', re.MULTILINE)


def norm(s: str) -> str:
    for ch in ("\u2014", "\u2013", "\u2212"):
        s = s.replace(ch, "-")
    return " ".join(s.strip().split()).lower()


def html_title(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    m = TITLE_RE.search(raw)
    return m.group(1).strip() if m else ""


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python refresh_manifest_from_metadata.py <metadata_xml_path>")

    metadata_path = Path(sys.argv[1])
    xml = metadata_path.read_text(encoding="utf-8", errors="replace")

    nav_graph = json.loads((ROOT / "nav_graph.json").read_text(encoding="utf-8"))
    basenames = set(nav_graph["by_file"].keys())
    for edges in nav_graph["by_file"].values():
        for e in edges:
            basenames.add(e["to"])
    basenames = {b for b in basenames if (PROTOTYPE / b).is_file()}

    by_title: dict[str, list[str]] = {}
    for base in sorted(basenames):
        t = norm(html_title(PROTOTYPE / base))
        if not t:
            continue
        by_title.setdefault(t, []).append(base)

    manifest = json.loads((ROOT / "figma_manifest.json").read_text(encoding="utf-8"))
    frames = dict(manifest.get("framesByHtmlFile", {}))

    replaced = 0
    ambiguous = []
    unmatched = []

    for nid, frame_name in TOP_FRAME_RE.findall(xml):
        stem = frame_name.strip()
        if stem.lower().startswith("screen / "):
            stem = stem[9:].strip()
        key = norm(stem)
        cands = by_title.get(key, [])
        if len(cands) == 1:
            base = cands[0]
            if frames.get(base) != nid:
                frames[base] = nid
                replaced += 1
        elif len(cands) > 1:
            ambiguous.append((nid, frame_name, cands))
        else:
            unmatched.append((nid, frame_name))

    manifest["framesByHtmlFile"] = dict(sorted(frames.items(), key=lambda x: x[0].lower()))
    (ROOT / "figma_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"updated manifest entries: {replaced}")
    print(f"total entries: {len(frames)}")
    print(f"ambiguous frames: {len(ambiguous)}")
    print(f"unmatched frames: {len(unmatched)}")
    if ambiguous:
        print("ambiguous sample:", ambiguous[:5])


if __name__ == "__main__":
    main()
