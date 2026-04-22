#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flatten nav_graph.json into ordered prototype wire spec with duplicate label indices."""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NG = ROOT / "nav_graph.json"
OUT = ROOT / "wire_spec.json"


def main():
    data = json.loads(NG.read_text(encoding="utf-8"))
    by_file = data["by_file"]
    label_seq: dict[tuple[str, str], int] = defaultdict(int)
    wires = []
    for from_file in sorted(by_file.keys()):
        for edge in by_file[from_file]:
            to = edge["to"]
            labels = edge.get("labels") or ["(link)"]
            primary = labels[0]
            key = (from_file, primary)
            idx = label_seq[key]
            label_seq[key] += 1
            wires.append(
                {
                    "from": from_file,
                    "to": to,
                    "labels": labels,
                    "kind": edge["kind"],
                    "labelIndex": idx,
                }
            )
    OUT.write_text(
        json.dumps(
            {
                "wire_count": len(wires),
                "wires": wires,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {OUT} with {len(wires)} wires")


if __name__ == "__main__":
    main()
