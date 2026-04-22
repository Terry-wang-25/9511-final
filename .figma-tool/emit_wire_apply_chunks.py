#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate make_apply_wires_js outputs in multiple files for use_figma size limits."""

import json
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PER_CHUNK = 38


def main() -> None:
    per = int(os.environ.get("WIRES_PER_CHUNK", str(DEFAULT_PER_CHUNK)))
    spec = json.loads((ROOT / "wire_spec.json").read_text(encoding="utf-8"))
    man = json.loads((ROOT / "figma_manifest.json").read_text(encoding="utf-8"))
    m = man["framesByHtmlFile"]
    n = sum(1 for w in spec["wires"] if w["from"] in m and w["to"] in m)
    nchunks = max(1, math.ceil(n / per)) if per > 0 else 1
    print(f"Applicable wires: {n}, chunks: {nchunks} (~{per} wires/chunk)")
    env_base = os.environ.copy()
    for i in range(nchunks):
        env = env_base.copy()
        env["WIRE_CHUNK"] = str(i)
        env["WIRE_CHUNKS"] = str(nchunks)
        env["WIRE_OUT"] = f"figma_wires_part{i}.js"
        subprocess.run(
            [sys.executable, str(ROOT / "make_apply_wires_js.py")],
            env=env,
            cwd=str(ROOT),
            check=True,
        )
    print(f"Wrote {ROOT / 'figma_wires_part0.js'} … part{nchunks - 1}.js")
    print("应用顺序: 对 use_figma 先执行 part0（整段替换 reactions），再依次 part1…（追加）。")


if __name__ == "__main__":
    main()
