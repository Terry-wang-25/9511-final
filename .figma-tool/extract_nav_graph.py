#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract all in-site navigation edges from 原型设计 HTML (+ known JS-only flows)."""

from __future__ import annotations

import json
import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent / "原型设计"
OUT = Path(__file__).resolve().parent / "nav_graph.json"


def norm_href(base_file: str, href: str) -> str | None:
    if not href or href.startswith(("javascript:", "mailto:", "tel:")):
        return None
    s = href.strip()
    if s in ("#", ""):
        return None
    if s.startswith("#"):
        return None  # in-page anchor — prototype optional
    parts = urlsplit(s)
    if parts.scheme in ("http", "https"):
        return None  # external
    path = unquote(parts.path)
    if not path or path == "/":
        return None
    leaf = path.split("/")[-1]
    if "?" in leaf:
        leaf = leaf.split("?")[0]
    if not leaf.lower().endswith(".html"):
        return None
    return leaf


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.edges: list[dict] = []
        self._tag_stack: list[str] = []
        self._a_href: str | None = None
        self._a_labels: list[str] = []
        self._script_buf: list[str] = []
        self._in_script = False
        self._in_a = False

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        self._tag_stack.append(tag)
        if tag == "script":
            src = ad.get("src", "")
            if not src:
                self._in_script = True
                self._script_buf = []
            return
        if tag == "a":
            self._in_a = True
            self._a_href = ad.get("href")
            self._a_labels = []
            lab = ad.get("aria-label") or ad.get("title")
            if lab:
                self._a_labels.append(lab.strip())
            return
        if tag == "img" and self._a_href is not None:
            alt = (ad.get("alt") or "").strip()
            if alt:
                self._a_labels.append(alt)
            return
        if tag == "area":
            href = ad.get("href")
            to = norm_href("", href or "")
            if to:
                self.edges.append(
                    {
                        "kind": "area",
                        "to": to,
                        "labels": [ad.get("alt", "").strip() or "area"],
                    }
                )

    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        if tag == "script" and self._in_script:
            self._in_script = False
            text = "".join(self._script_buf)
            for m in re.finditer(
                r'window\.location\.href\s*=\s*["\']([^"\']+)["\']', text
            ):
                to = norm_href("", m.group(1))
                if to:
                    self.edges.append(
                        {
                            "kind": "script_assign",
                            "to": to,
                            "labels": ["(script navigation)"],
                        }
                    )
            self._script_buf = []
            return
        if tag == "a" and self._a_href is not None:
            self._in_a = False
            to = norm_href("", self._a_href)
            if to:
                inner = " ".join(self._a_labels).strip() or "(image link)"
                self.edges.append(
                    {"kind": "anchor", "to": to, "labels": [inner]}
                )
            self._a_href = None
            self._a_labels = []

    def handle_data(self, data):
        if self._in_script:
            self._script_buf.append(data)
            return
        if self._a_href is not None and self._tag_stack and self._tag_stack[-1] != "script":
            t = data.strip()
            if t:
                self._a_labels.append(t)


def synthetic_edges(filename: str, raw: str) -> list[dict]:
    """Edges not visible as static <a href>."""
    out: list[dict] = []
    if 'src="site-preferences.js"' in raw or "src='site-preferences.js'" in raw:
        # wireGlobalChatFab() appends la-chat-fab -> Overlay - Chatbot.html
        if filename.endswith(".html") and not filename.startswith("Overlay"):
            out.append(
                {
                    "kind": "synthetic_chat_fab",
                    "to": "Overlay - Chatbot.html",
                    "labels": ["Chat with us", "Chat with us 💬"],
                }
            )

    # Check My Rights — form submit (preventDefault + location)
    cm = {
        "Check My Rights - Page 1.html": "Check My Rights - Page 2.html",
        "Check My Rights - Page 2.html": "Check My Rights - Page 3.html",
        "Check My Rights - Page 3.html": "Check My Rights - Page 4.html",
        "Check My Rights - Page 4.html": "Check My Rights - Page 5.html",
        "Check My Rights - Page 5.html": "Check My Rights - Result.html",
    }
    if filename in cm:
        out.append(
            {
                "kind": "form_submit_quiz",
                "to": cm[filename],
                "labels": ["Next", "Continue", "(submit quiz)"],
            }
        )

    # 任务1 step2 Continue button -> 你的信息页面 (topic query ignored in Figma)
    if filename == "任务 1 的第二个页面.html":
        out.append(
            {
                "kind": "button_continue_claim",
                "to": "任务 1 的你的信息页面.html",
                "labels": ["Continue", "Continue to next step"],
            }
        )
    if filename == "任务 1 的你的信息页面.html":
        out.append(
            {
                "kind": "button_continue_claim",
                "to": "任务 1 的第三个页面.html",
                "labels": ["Continue", "Continue to next step"],
            }
        )

    return out


def main():
    all_html = sorted(ROOT.glob("*.html"))
    by_file: dict[str, list[dict]] = {}

    for fp in all_html:
        rel = fp.name
        raw = fp.read_text(encoding="utf-8", errors="replace")
        p = LinkCollector()
        try:
            p.feed(raw)
        except Exception as e:
            print("parse warn", rel, e)
        edges = p.edges + synthetic_edges(rel, raw)
        # Dedupe (to, kind, first label)
        seen = set()
        uniq = []
        for e in edges:
            key = (e["to"], e["kind"], tuple(e.get("labels") or []))
            if key in seen:
                continue
            seen.add(key)
            uniq.append(e)
        by_file[rel] = uniq

    targets: set[str] = set()
    for edges in by_file.values():
        for e in edges:
            targets.add(e["to"])

    manifest_hint = sorted(set(by_file.keys()) | targets)

    OUT.write_text(
        json.dumps(
            {
                "root": str(ROOT),
                "file_count": len(by_file),
                "edge_count": sum(len(v) for v in by_file.values()),
                "unique_targets": len(targets),
                "by_file": by_file,
                "all_local_html": manifest_hint,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"Wrote {OUT} — {len(by_file)} files, {sum(len(v) for v in by_file.values())} edges"
    )


if __name__ == "__main__":
    main()
