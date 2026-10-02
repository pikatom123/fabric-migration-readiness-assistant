import { chromium } from "playwright";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = path.resolve(import.meta.dirname, "../..");
const appUrl = `${pathToFileURL(path.join(root, "index.html")).href}?scoutTheme=light`;
const csvPath = path.join(root, "demo-assets/output/Contoso_Estate_Inventory.csv");
const videoDir = path.join(root, "demo-assets/walkthrough/raw");

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  colorScheme: "light",
  recordVideo: { dir: videoDir, size: { width: 1440, height: 900 } },
});
const page = await context.newPage();

const pause = milliseconds => page.waitForTimeout(milliseconds);

async function humanClick(locator) {
  const box = await locator.boundingBox();
  if (!box) throw new Error(`Element is not visible: ${await locator.evaluate(el => el.id || el.textContent)}`);
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 24 });
  await pause(500);
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
}

async function smoothScrollTo(locator) {
  await locator.evaluate(el => el.scrollIntoView({ behavior: "smooth", block: "center" }));
  await pause(1100);
}

await page.goto(appUrl, { waitUntil: "load" });
await page.evaluate(() => localStorage.removeItem("fabric-readiness-prototype-v1"));
await page.reload({ waitUntil: "load" });
await pause(4000);

const uploadButton = page.locator("#uploadEstateBtn");
const chooserPromise = page.waitForEvent("filechooser");
await humanClick(uploadButton);
const chooser = await chooserPromise;
await chooser.setFiles(csvPath);
await page.waitForFunction(() => document.querySelector("#uploadStatus")?.textContent.includes("Imported 5"));
await pause(5500);

await humanClick(page.locator("#nextBtn"));
await pause(6500);

await humanClick(page.locator("#addWorkloadBtn"));
await pause(5000);
await humanClick(page.locator("#closeDialogBtn"));
await pause(1500);

await humanClick(page.locator('[data-view="discovery"]'));
await pause(1200);
await humanClick(page.locator("#sampleBtn"));
await pause(3000);
await humanClick(page.locator('[data-view="workloads"]'));
await pause(5500);

await humanClick(page.locator("#nextBtn"));
await pause(5500);

const assessmentCards = page.locator(".assessment");
for (let index = 0; index < await assessmentCards.count(); index++) {
  const card = assessmentCards.nth(index);
  await smoothScrollTo(card);
  await humanClick(card.locator(".expand"));
  await pause(3600);
  await humanClick(card.locator(".expand"));
  await pause(500);
}

await humanClick(page.locator("#nextBtn"));
await pause(7000);
await smoothScrollTo(page.locator("#targetPatterns"));
await pause(5000);
await smoothScrollTo(page.locator("#estimatorInputs"));
await pause(7500);

const rawVideo = await page.video().path();
await context.close();
await browser.close();
console.log(rawVideo);
