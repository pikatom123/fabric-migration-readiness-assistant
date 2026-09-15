# Testing the Fabric Adoption Assistant

Use three levels of testing: automated rules, workflow acceptance, and a real CSA pilot. A visually correct report is not enough; the key test is whether incomplete evidence stays incomplete.

## 1. Automated checks

```powershell
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
.venv\Scripts\python -m pytest -q

.venv\Scripts\python -m fabric_adoption_assistant.cli import-estate examples/sample_estate.csv `
  --customer-name "Test Customer" `
  --output examples/estate-import.json

.venv\Scripts\python -m fabric_adoption_assistant.cli assess examples/sample_intake.yaml `
  --json-out examples/sample_report.json `
  --html-out examples/sample_report.html
```

Expected results:

- All tests pass.
- The CSV import contains three workloads and every `answers` object is empty.
- Assessing the imported draft before conversation produces `Needs Discovery`.
- The sample assessment produces JSON and HTML.
- Customer-provided HTML characters are escaped in the report.

## 2. Browser upload acceptance test

1. Open `index.html` directly in a browser.
2. Select **Reset** to remove previous local test data.
3. On Discovery, select **Upload PDF or CSV**.
4. Choose `examples/sample_estate.csv`.
5. Open Workloads.

Pass criteria:

- Exactly three rows are imported.
- All three rows show **Needs Discovery**.
- No imported row shows Ready, Optimise, or Redesign before confirmation.
- Refreshing the page preserves the imported inventory in local storage.
- A CSV without `name` and `workload_type` shows a clear error.
- Unknown workload types are skipped and their row numbers are reported.
- Assessment displays `N/A`, not `0%`, while every workload still needs discovery.
- **Start AI discovery** produces estate context for the `Fabric Adoption Discovery` agent.

PDF check:

1. Select a text-based PDF.
2. Confirm that the browser does not invent workload rows.
3. Attach the PDF in Copilot Chat or run `import-estate` from the CLI.
4. Confirm that extracted entries are labeled **Unconfirmed extraction** during conversation.
5. Use a scanned PDF page and confirm that it is reported as requiring OCR.

## 3. Anti-hallucination scenarios

Run these deliberately adversarial cases:

| Scenario | Expected behavior |
|---|---|
| Workload name and type only | `Needs Discovery`; required questions listed |
| Misspelled answer id | Validation error, not a base disposition |
| Invalid choice value | Validation error listing accepted values |
| Product support claim without Learn evidence | Visible evidence limitation |
| Explicit blocker plus other missing answers | Blocker may surface, but missing questions remain visible |
| CSV notes claim a feature | Notes are preserved; no answer or rule is triggered from notes |
| PDF mentions several Azure services ambiguously | Assistant asks for confirmation instead of classifying silently |

## 4. Conversational quality test

Ask a CSA who did not build the tool to run a 20-minute discovery session.

Before starting, open `.vscode/mcp.json` and confirm the `microsoft-learn` server is running in VS Code. Ask Copilot to search for one current Fabric limitation and verify that it calls `microsoft_docs_search`, then `microsoft_docs_fetch`, and places the returned URL in the evidence record.

Measure:

- Questions per turn: no more than three.
- Correction rate: number of extracted facts the CSA changes.
- Unknown preservation: unanswered facts remain absent.
- Source coverage: every current product-support claim has an opened Learn source or an explicit limitation.
- Time to first useful output: inventory and open-question list produced within ten minutes.
- Report usefulness: CSA can explain every disposition from customer answers, rules, and attached evidence.

Pilot pass criteria should be agreed before the session. A practical initial threshold is zero unsupported factual claims, zero imported workloads mislabeled ready, and at least 80% of report findings judged useful by two reviewing CSAs.

## 5. Regression review

Whenever the knowledge base changes:

1. Add tests for the trigger and non-trigger paths.
2. Re-run the anti-hallucination scenarios.
3. Revalidate affected product claims with Microsoft Learn MCP.
4. Regenerate and inspect desktop, mobile, and print versions of the HTML report.
5. Record the reviewer and review date in the pull request.