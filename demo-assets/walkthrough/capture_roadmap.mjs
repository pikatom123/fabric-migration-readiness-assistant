import { chromium } from "playwright";
import path from "node:path";
import { pathToFileURL } from "node:url";

const pagePath = path.resolve(import.meta.dirname, "roadmap.html");
const outputPath = path.resolve(import.meta.dirname, "roadmap.png");
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(pagePath).href, { waitUntil: "load" });
await page.screenshot({ path: outputPath });
await browser.close();
console.log(outputPath);