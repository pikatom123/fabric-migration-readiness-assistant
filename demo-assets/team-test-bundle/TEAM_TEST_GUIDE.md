# Fabric Migration Readiness Assistant - Team Test Pack

This pack tests a larger manufacturing estate and the browser's safety boundaries. No installation or web server is required.

## Start

1. Extract the ZIP to a normal folder.
2. Open `Fabric_Migration_Readiness_Assistant.html` in Edge or Chrome.
3. Select **Reset** before each scenario.
4. Keep browser zoom at 100%.

The page stores test data in browser local storage. Reset prevents one scenario from affecting another.

## Scenario 1 - Large manufacturing estate

File: `Fabrikam_Manufacturing_Large_Estate.csv`

Customer context to enter:

| Field | Value |
|---|---|
| Customer | Fabrikam Manufacturing |
| Industry | Manufacturing |
| Region | West Europe |
| Target date | 2027-09-30 |
| Users | 4200 |
| Peak concurrent users | 480 |
| Strategy | Coexistence / phased |
| Outcomes | Unify plant, supply-chain, finance, and telemetry analytics while reducing duplicated platforms and data movement. |
| Constraints | Private connectivity and EU residency are mandatory. Plant operations cannot tolerate ingestion downtime. Month-end closes in three hours. |

Steps:

1. Upload the large-estate CSV.
2. Confirm the status says **Imported 20 workloads**.
3. Select **Continue**.
4. Confirm every workload is **Needs Discovery**.
5. Open **Assessment** and confirm readiness is `N/A`, not `0%`.
6. Open **Summary** and inspect total estate volume and open discovery count.
7. Refresh the browser and confirm all 20 workloads remain available.
8. Select **Start AI discovery** and inspect the generated prompt.

Expected results:

- 20 workloads import and none are silently classified Ready, Optimise, or Redesign.
- All nine supported workload families appear.
- Total listed estate size is 96.151 TB, displayed as approximately 96.2 TB.
- The prompt includes Fabrikam context and all imported workloads.
- Notes remain evidence only; words such as CDC, writeback, or custom connector do not automatically trigger rules.

## Scenario 2 - Mixed-quality import

File: `Mixed_Quality_Import.csv`

Steps:

1. Reset the page.
2. Upload the mixed-quality CSV.
3. Inspect the upload message and Workloads table.
4. Open the Markup safety check workload.

Expected results:

- Five workloads import.
- Rows 4 and 5 are reported as skipped: unsupported Snowflake and missing workload name.
- `power-bi` normalizes to Power BI.
- The negative size is safely represented as 0 GB.
- The quoted comma stays inside one notes field.
- The `<script>` text is visible as text and never executes.

## Scenario 3 - Missing required headers

File: `Invalid_Missing_Headers.csv`

Expected result:

- No workload imports.
- The page displays: `CSV must contain name and workload_type columns.`

## Scenario 4 - Manual discovery

1. Reset the page.
2. Select **Continue**, then **Add workload**.
3. Add a Power BI workload with calculated columns, composite model, and high overlap.
4. Add an Azure Data Factory workload with SHIR and a custom connector.
5. Add a streaming Spark workload.
6. Review Assessment and Summary.

Expected results:

- Power BI recommends a semantic model with Direct Lake and upstream transformation optimisation.
- Data Factory exposes connectivity and connector-parity blockers.
- Spark maps to Real-Time Intelligence, Eventstream, and Fabric Spark.
- Summary shows capacity pressure because overlap or streaming is present.

## Scenario 5 - Persistence and reset

1. Import any valid CSV.
2. Refresh the page.
3. Confirm the state persists.
4. Select **Reset** and confirm the imported estate is removed.

## Record feedback

For each scenario, capture browser/version, pass/fail, unexpected behavior, missing question, misleading recommendation, and screenshot. Product-support conclusions still require validation against current Microsoft Learn guidance.
