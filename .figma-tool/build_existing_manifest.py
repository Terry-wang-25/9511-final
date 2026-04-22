#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python build_existing_manifest.py <metadata_xml_path>")
    metadata = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    existing_ids = set(re.findall(r'^  <frame id="([^"]+)"', metadata, flags=re.MULTILINE))
    manifest = json.loads((ROOT / "figma_manifest.json").read_text(encoding="utf-8"))
    frames = manifest["framesByHtmlFile"]
    keep = {k: v for k, v in frames.items() if v in existing_ids}
    manifest["framesByHtmlFile"] = dict(sorted(keep.items(), key=lambda x: x[0].lower()))
    out = ROOT / "figma_manifest_existing.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"kept={len(keep)} dropped={len(frames)-len(keep)} out={out}")

if __name__ == "__main__":
    main()
