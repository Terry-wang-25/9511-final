/**
 * Batch local HTML → Figma html-to-design captures.
 * Usage: node run-batch.mjs batch.json
 * batch.json: [{ "captureId": "uuid", "file": "Some Page.html" }, ...]
 */
import { chromium } from "playwright";
import fs from "fs";

const path = process.argv[2];
if (!path || !fs.existsSync(path)) {
  console.error("Usage: node run-batch.mjs batch.json");
  process.exit(1);
}

const batch = JSON.parse(fs.readFileSync(path, "utf8"));
const base = "http://127.0.0.1:8765/";
const browser = await chromium.launch({ headless: true });

for (const row of batch) {
  const { captureId, file } = row;
  const endpoint = `https://mcp.figma.com/mcp/capture/${captureId}/submit`;
  const hash =
    `figmacapture=${captureId}` +
    `&figmaendpoint=${encodeURIComponent(endpoint)}` +
    `&figmadelay=2000`;
  const url = `${base}${encodeURI(file)}#${hash}`;
  const page = await browser.newPage();
  try {
    await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
    const ms = Number(process.env.CAPTURE_WAIT_MS || 12000);
    await page.waitForTimeout(ms);
    console.log(JSON.stringify({ ok: true, file, captureId }));
  } catch (e) {
    console.log(JSON.stringify({ ok: false, file, captureId, error: String(e) }));
  } finally {
    await page.close();
  }
}

await browser.close();
