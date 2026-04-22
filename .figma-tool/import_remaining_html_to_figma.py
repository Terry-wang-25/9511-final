#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出尚未写入 figma_manifest 的本地 HTML（按文件名排序），便于分批导入 Figma。

用法:
  python import_remaining_html_to_figma.py           # 打印缺失数量与全部列表
  python import_remaining_html_to_figma.py --batch 10 --offset 0   # 仅打印本批 10 个文件名

导入一批的推荐步骤（需在 Cursor 里用 Figma MCP 拿 captureId）:
  1) 对每个「本批」文件调用一次 generate_figma_design(existingFile + fileKey + page 0:1)，得到互不相同的 captureId。
  2) 将 [{\"captureId\":\"...\",\"file\":\"a.html\"}, ...] 写入 batch.json。
  3) 在 原型设计 目录已用 http-server 暴露 8765 的前提下:
       set CAPTURE_WAIT_MS=20000 && node run-batch.mjs batch.json
  4) 用同一 captureId 轮询 generate_figma_design 直至 completed，从返回 URL 取 node-id，合并进 figma_manifest.json。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
PROTO = REPO / "原型设计"
MAN = ROOT / "figma_manifest.json"


def missing_files() -> list[str]:
    htmls = sorted({p.name for p in PROTO.glob("*.html")})
    man = json.loads(MAN.read_text(encoding="utf-8"))
    have = set(man["framesByHtmlFile"].keys())
    return [f for f in htmls if f not in have]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=0, help="每批条数，0 表示不分批")
    ap.add_argument("--offset", type=int, default=0, help="分批起始下标")
    args = ap.parse_args()
    miss = missing_files()
    print(f"本地 HTML 总数: {len(sorted({p.name for p in PROTO.glob('*.html')}))}")
    print(f"manifest 已有: {len(json.loads(MAN.read_text(encoding='utf-8'))['framesByHtmlFile'])}")
    print(f"仍缺: {len(miss)}")
    if args.batch > 0:
        chunk = miss[args.offset : args.offset + args.batch]
        print(f"\n本批 offset={args.offset} count={len(chunk)}:")
        for f in chunk:
            print(f)
    else:
        for f in miss:
            print(f)


if __name__ == "__main__":
    main()
