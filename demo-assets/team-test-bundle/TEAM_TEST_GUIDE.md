# Fabric Migration Readiness Assistant - Team Test Pack

This pack contains two valid, CSA-confirmed assessments from different industries. Each CSV produces a realistic mixture of workloads that are Ready, need Optimisation, or require Redesign. No installation or web server is required.

## Start

1. Extract the ZIP to a normal folder.
2. Open `Fabric_Migration_Readiness_Assistant.html` in Edge or Chrome.
3. Select **Reset** before each scenario.
4. Upload the scenario CSV from the Discovery page.
5. Review Workloads, Assessment, and Summary.

The extended CSV fields represent facts already confirmed by a CSA. A basic inventory CSV without `assessment_confirmed=true` still remains Needs Discovery.

## Scenario 1 - Northwind Healthcare

File: `Northwind_Healthcare_Assessed_Estate.csv`

Suggested customer context:

| Field | Value |
|---|---|
| Customer | Northwind Health Network |
| Industry | Healthcare |
| Region | UK South |
| Users | 2600 |
| Peak concurrent users | 320 |
| Strategy | Coexistence / phased |
| Outcomes | Improve clinical and operational insight while consolidating duplicated analytics platforms. |
| Constraints | Patient-data residency, private connectivity, and uninterrupted clinical ingestion are mandatory. |

Expected results:

- 14 valid workloads import as a confirmed assessment.
- 4 are Ready, 7 need Optimisation, and 3 require Redesign.
- Overall readiness is 66%.
- Direct Lake, Warehouse, Lakehouse, Data Factory, Real-Time Intelligence, retained Logic Apps, and Automation patterns appear.
- The hospital integration factory, legacy cube, and clinical approval workflow expose redesign blockers.

## Scenario 2 - Woodgrove Financial Services

File: `Woodgrove_Financial_Services_Assessed_Estate.csv`

Suggested customer context:

| Field | Value |
|---|---|
| Customer | Woodgrove Bank |
| Industry | Financial Services |
| Region | West Europe |
| Users | 5100 |
| Peak concurrent users | 620 |
| Strategy | Coexistence / phased |
| Outcomes | Modernise risk, finance, fraud, and regulatory analytics with stronger governance and lower data movement. |
| Constraints | Regulatory evidence, private connectivity, and month-end reporting deadlines are mandatory. |

Expected results:

- 16 valid workloads import as a confirmed assessment.
- 4 are Ready, 8 need Optimisation, and 4 require Redesign.
- Overall readiness is 64%.
- The legacy risk model, capital cube, regulatory SQL pool, and SSIS payment integration require redesign.
- The summary highlights refresh overlap, streaming demand, estate scale, and high concurrency as capacity-watch signals.

## Scenario 3 - Contoso Energy & Utilities

File: `Contoso_Energy_Utilities_Assessed_Estate.csv`

Suggested customer context:

| Field | Value |
|---|---|
| Customer | Contoso Energy |
| Industry | Energy & Utilities |
| Region | North Europe |
| Users | 3400 |
| Peak concurrent users | 410 |
| Strategy | Coexistence / phased |
| Outcomes | Modernise grid, meter, trading, forecasting, and regulatory analytics while improving near-real-time visibility. |
| Constraints | Critical grid operations, private connectivity, regulatory settlement deadlines, and uninterrupted telemetry ingestion are mandatory. |

Expected results:

- 15 valid workloads import as a confirmed assessment.
- 4 are Ready, 7 need Optimisation, and 4 require Redesign.
- Overall readiness is 64%.
- The generation reporting model, settlement SQL pool, field telemetry integration, and outage approvals require redesign.
- Streaming demand, large estate size, high concurrency, and refresh overlap produce a capacity-watch signal.

## Persistence and reset

1. Import either CSV and refresh the page.
2. Confirm the assessment persists.
3. Select **Reset** and confirm all workloads are removed.

## CSV confirmation fields

The assessed scenarios use these optional fields: `assessment_confirmed`, `refresh_per_day`, `concurrency`, `complexity`, and pipe-delimited `features`. Set `assessment_confirmed=true` only after a CSA has confirmed those facts with the customer.

## Record feedback

Use `TEST_RESULTS_TEMPLATE.csv` to capture browser/version, pass/fail, unexpected behavior, missing questions, misleading recommendations, and screenshots. Product-support conclusions still require validation against current Microsoft Learn guidance.
