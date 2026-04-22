#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit Plugin API JS for use_figma: apply wires from wire_spec + figma_manifest."""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

TEMPLATE = r"""
const MANIFEST = __MANIFEST__;
const SPECS = __SPECS__;
const page = figma.root.children.find((p) => p.name === '9511-watermelon_update');
await figma.setCurrentPageAsync(page);
await page.loadAsync();

const PROTECTED = new Set(['49:2', '43:2']);
const LOGIN = '38:2';
function gate(srcRoot, dest) {
  if (!PROTECTED.has(dest)) return dest;
  if (srcRoot === LOGIN) return dest;
  if (srcRoot === '49:2' || srcRoot === '43:2') return dest;
  return LOGIN;
}

function collectText(n) {
  return n.findAll((c) => c.type === 'TEXT')
    .map((c) => c.characters.replace(/\s+/g, ' ').trim())
    .filter(Boolean)
    .join(' ');
}

function interactiveNodes(root) {
  return root.findAll(
    (n) =>
      n.type === 'FRAME' &&
      (n.name === 'Link' ||
        n.name.startsWith('Link -') ||
        n.name.startsWith('Link') ||
        n.name === 'Button' ||
        n.name.startsWith('Button'))
  ).filter((n) => 'setReactionsAsync' in n);
}

function shouldSkipFrontendOnly(node) {
  const chain = [node.name, node.parent ? node.parent.name : '', node.parent && node.parent.parent ? node.parent.parent.name : '']
    .join(' ')
    .toLowerCase();
  return /listen|utility-la-language|site search|hero-search|search input|floating-ai|contact our\s*ai|voice|microphone/i.test(chain);
}

const transition = { type: 'DISSOLVE', duration: 0.2, easing: { type: 'LINEAR' } };
let applied = 0;
let skipped = 0;
const errors = [];

function findMatch(root, labels, labelIndex) {
  const candidates = interactiveNodes(root);
  for (const primary of labels) {
    if (!primary || primary === '(script navigation)') continue;
    const exact = candidates.filter((n) => {
      const t = collectText(n);
      return t === primary || t.startsWith(primary + ' ') || t.startsWith(primary + '›');
    });
    if (exact.length > labelIndex) return exact[labelIndex];
    const contains = candidates.filter((n) => collectText(n).includes(primary));
    if (contains.length > labelIndex) return contains[labelIndex];
  }
  return null;
}

for (const row of SPECS) {
  const srcId = MANIFEST[row.f];
  const destId = gate(srcId, MANIFEST[row.t]);
  if (srcId === destId) { skipped++; continue; }
  const root = await figma.getNodeByIdAsync(srcId);
  if (!root || root.type !== 'FRAME') { errors.push('bad root ' + row.f); continue; }
  const node = findMatch(root, row.lb, row.i);
  if (!node) { skipped++; continue; }
  if (shouldSkipFrontendOnly(node)) { skipped++; continue; }
  try {
__REACTION_BLOCK__
    applied++;
  } catch (e) {
    errors.push(row.f + ' -> ' + row.t + ': ' + String(e));
  }
}

return { applied, skipped, errors: errors.slice(0, 40), errorCount: errors.length };
"""


def main():
    spec = json.loads((ROOT / "wire_spec.json").read_text(encoding="utf-8"))
    man = json.loads((ROOT / "figma_manifest.json").read_text(encoding="utf-8"))
    m = man["framesByHtmlFile"]
    wires = [w for w in spec["wires"] if w["from"] in m and w["to"] in m]
    compact = [{"f": w["from"], "t": w["to"], "lb": w["labels"], "i": w["labelIndex"]} for w in wires]
    chunk = int(os.environ.get("WIRE_CHUNK", "0"))
    nchunks = int(os.environ.get("WIRE_CHUNKS", "1"))
    if nchunks > 1:
        n = len(compact)
        lo = chunk * n // nchunks
        hi = (chunk + 1) * n // nchunks
        compact = compact[lo:hi]
    payload = json.dumps(compact, ensure_ascii=False)
    manifest_json = json.dumps(m, ensure_ascii=False)
    # Chunk 0 replaces reactions; later chunks append (MCP payload size limit).
    merge = nchunks > 1 and chunk > 0
    if merge:
        reaction_block = """    const prev = node.reactions && node.reactions.length ? [...node.reactions] : [];
    await node.setReactionsAsync([
      ...prev,
      { trigger: { type: 'ON_CLICK' }, actions: [{ type: 'NODE', destinationId: destId, navigation: 'NAVIGATE', transition }] },
    ]);"""
    else:
        reaction_block = """    await node.setReactionsAsync([
      { trigger: { type: 'ON_CLICK' }, actions: [{ type: 'NODE', destinationId: destId, navigation: 'NAVIGATE', transition }] },
    ]);"""
    js = (
        TEMPLATE.replace("__MANIFEST__", manifest_json)
        .replace("__SPECS__", payload)
        .replace("__REACTION_BLOCK__", reaction_block)
        .strip()
        + "\n"
    )
    out_name = os.environ.get("WIRE_OUT", "figma_apply_wires_generated.js")
    out = ROOT / out_name
    out.write_text(js.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
    print(f"Wrote {out} for {len(compact)} wires")


if __name__ == "__main__":
    main()
