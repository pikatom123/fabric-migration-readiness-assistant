import { chromium } from "playwright";
import path from "node:path";
import os from "node:os";
import { pathToFileURL } from "node:url";

const bundle = path.join(os.tmpdir(), "fabric-team-test-bundle-validation");
const appUrl = pathToFileURL(path.join(bundle, "Fabric_Migration_Readiness_Assistant.html")).href;
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

async function reset() {
  await page.evaluate(() => localStorage.clear());
  await page.reload();
}

async function upload(fileName) {
  await page.locator("#estateUpload").setInputFiles(path.join(bundle, fileName));
  await page.waitForTimeout(300);
  return page.locator("#uploadStatus").innerText();
}

await page.goto(appUrl);
await reset();
await page.locator("#sampleBtn").click();
const assessedRows = await page.locator("#workloadRows tr").count();
const assessedReady = await page.locator("#workloadRows .badge.ready").count();
const assessedOptimise = await page.locator("#workloadRows .badge.optimize").count();
const assessedRedesign = await page.locator("#workloadRows .badge.blocked").count();
const assessedScore = await page.locator("#scoreRing").innerText();

await reset();
const largeStatus = await upload("Fabrikam_Manufacturing_Large_Estate.csv");
const largeRows = await page.locator("#workloadRows tr").count();
const largeDiscovery = await page.locator("#workloadRows").getByText("Needs Discovery", { exact: true }).count();

await reset();
const mixedStatus = await upload("Mixed_Quality_Import.csv");
const mixedRows = await page.locator("#workloadRows tr").count();
await page.locator('[data-view="workloads"]').click();
await page.locator("#workloadRows .edit").nth(3).click();
const markupNotes = await page.locator("#workloadNotes").inputValue();
await page.locator("#closeDialogBtn").click();

await reset();
const invalidStatus = await upload("Invalid_Missing_Headers.csv");
const invalidRows = await page.locator("#workloadRows .edit").count();

const result = { assessedRows, assessedReady, assessedOptimise, assessedRedesign, assessedScore, largeStatus, largeRows, largeDiscovery, mixedStatus, mixedRows, markupRenderedAsText: markupNotes.includes("<script>"), invalidStatus, invalidRows };
console.log(JSON.stringify(result, null, 2));

const failures = [];
if (assessedRows !== 20 || assessedReady !== 4 || assessedOptimise !== 11 || assessedRedesign !== 5 || assessedScore !== "62%") failures.push("mixed assessed sample");
if (!largeStatus.includes("Imported 20 workloads")) failures.push("large import status");
if (largeRows !== 20 || largeDiscovery < 20) failures.push("large imported rows");
if (!mixedStatus.includes("Imported 5 workloads") || !mixedStatus.includes("Skipped rows: 4, 5")) failures.push("mixed import status");
if (mixedRows !== 5 || !result.markupRenderedAsText) failures.push("mixed imported rows or markup safety");
if (invalidStatus !== "CSV must contain name and workload_type columns." || invalidRows !== 0) failures.push("invalid-header rejection");

await browser.close();
if (failures.length) throw new Error(`Bundle validation failed: ${failures.join(", ")}`);
