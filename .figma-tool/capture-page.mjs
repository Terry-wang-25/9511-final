/**
 * Opens a localhost HTML page with Figma html-to-design hash params and triggers capture.
 * Usage: node capture-page.mjs <captureId> <filename.html>
 */
import { chromium } from "playwright";

const captureId = process.argv[2];
const htmlFile = process.argv[3];
if (!captureId || !htmlFile) {
  console.error("Usage: node capture-page.mjs <captureId> <filename.html>");
  process.exit(1);
}

const base = "http://127.0.0.1:8765/";
const endpoint = `https://mcp.figma.com/mcp/capture/${captureId}/submit`;
const pathPart = encodeURI(htmlFile);
const hash =
  `figmacapture=${captureId}` +
  `&figmaendpoint=${encodeURIComponent(endpoint)}` +
  `&figmadelay=2000`;
const url = `${base}${pathPart}#${hash}`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
try {
  await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
  // html-to-design capture.js triggers from hash; allow upload to complete
  const ms = Number(process.env.CAPTURE_WAIT_MS || 12000);
  await page.waitForTimeout(ms);
  console.log(JSON.stringify({ url, status: "waited" }));
} finally {
  await browser.close();
}
