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
const healthcareStatus = await upload("Northwind_Healthcare_Assessed_Estate.csv");
const healthcare = {
  rows: await page.locator("#workloadRows tr").count(),
  ready: await page.locator("#workloadRows .badge.ready").count(),
  optimise: await page.locator("#workloadRows .badge.optimize").count(),
  redesign: await page.locator("#workloadRows .badge.blocked").count(),
  discovery: await page.locator("#workloadRows .badge.discovery").count(),
  score: await page.locator("#scoreRing").innerText()
};

await reset();
const financeStatus = await upload("Woodgrove_Financial_Services_Assessed_Estate.csv");
const finance = {
  rows: await page.locator("#workloadRows tr").count(),
  ready: await page.locator("#workloadRows .badge.ready").count(),
  optimise: await page.locator("#workloadRows .badge.optimize").count(),
  redesign: await page.locator("#workloadRows .badge.blocked").count(),
  discovery: await page.locator("#workloadRows .badge.discovery").count(),
  score: await page.locator("#scoreRing").innerText()
};

await reset();
const energyStatus = await upload("Contoso_Energy_Utilities_Assessed_Estate.csv");
const energy = {
  rows: await page.locator("#workloadRows tr").count(),
  ready: await page.locator("#workloadRows .badge.ready").count(),
  optimise: await page.locator("#workloadRows .badge.optimize").count(),
  redesign: await page.locator("#workloadRows .badge.blocked").count(),
  discovery: await page.locator("#workloadRows .badge.discovery").count(),
  score: await page.locator("#scoreRing").innerText()
};

const result = { healthcareStatus, healthcare, financeStatus, finance, energyStatus, energy };
console.log(JSON.stringify(result, null, 2));

const failures = [];
if (!healthcareStatus.includes("Imported 14 workloads") || !healthcareStatus.includes("confirmed assessment")) failures.push("healthcare import status");
if (healthcare.rows !== 14 || healthcare.ready !== 4 || healthcare.optimise !== 7 || healthcare.redesign !== 3 || healthcare.discovery !== 0 || healthcare.score !== "66%") failures.push("healthcare assessment mix");
if (!financeStatus.includes("Imported 16 workloads") || !financeStatus.includes("confirmed assessment")) failures.push("finance import status");
if (finance.rows !== 16 || finance.ready !== 4 || finance.optimise !== 8 || finance.redesign !== 4 || finance.discovery !== 0 || finance.score !== "64%") failures.push("finance assessment mix");
if (!energyStatus.includes("Imported 15 workloads") || !energyStatus.includes("confirmed assessment")) failures.push("energy import status");
if (energy.rows !== 15 || energy.ready !== 4 || energy.optimise !== 7 || energy.redesign !== 4 || energy.discovery !== 0 || energy.score !== "64%") failures.push("energy assessment mix");

await browser.close();
if (failures.length) throw new Error(`Bundle validation failed: ${failures.join(", ")}`);
