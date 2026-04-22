#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Report nav_graph targets that are missing on disk under 原型设计."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
PROTOTYPE = REPO / "原型设计"
NG = ROOT / "nav_graph.json"


def main():
    data = json.loads(NG.read_text(encoding="utf-8"))
    by = data["by_file"]
    need = set(by.keys())
    for edges in by.values():
        for e in edges:
            need.add(e["to"])
    missing = sorted(f for f in need if not (PROTOTYPE / f).is_file())
    print(f"原型设计目录: {PROTOTYPE}")
    print(f"nav 中引用到的文件数: {len(need)}")
    print(f"磁盘缺失: {len(missing)}")
    for f in missing:
        print(f"  {f}")


if __name__ == "__main__":
    main()
