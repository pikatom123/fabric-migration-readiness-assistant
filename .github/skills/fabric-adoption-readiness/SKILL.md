---
name: fabric-adoption-readiness
description: "Run or maintain a conversational, evidence-grounded Microsoft Fabric adoption or migration readiness assessment. Use when a CSA asks to assess an analytics estate, discover migration blockers, map workloads to Fabric, prepare adoption recommendations, generate a customer-ready readiness report, refresh current Fabric guidance, update readiness rules, validate product support, or release the reusable CSA assessment pack. Covers Power BI, SSAS/AAS, Azure SQL, Synapse, Databricks, ADF, Logic Apps, Spark, and Automation runbooks."
---

# Fabric Adoption Readiness

Use the `Fabric Adoption Discovery` custom agent for the interview. The agent chooses questions adaptively; the packaged Python engine validates the resulting evidence and applies repeatable readiness rules.

## Non-negotiable grounding rules

1. Label information as one of: `Customer answer`, `Microsoft Learn evidence`, or `Assessment rule`.
2. Never infer an unanswered field. Leave it absent so the engine returns `Needs Discovery`.
3. Never invent product support, limits, migration parity, URLs, quotes, or SKU recommendations.
4. Search Microsoft Learn through `microsoft_docs_search`, open the selected article with `microsoft_docs_fetch`, and use `microsoft_code_sample_search` only when implementation examples are needed. Attach only sources actually returned and opened during this session.
5. If Learn MCP is unavailable or inconclusive, record the statement as a validation action and add an evidence limitation. Do not convert it into a fact.
6. Treat capacity guidance as directional. Use measured telemetry and the Fabric SKU Estimator or cost-estimation skill for sizing.

## Conversation

### 1. Establish scope

Start with the supplied estate and ask only the highest-value missing question. Ask at most three questions in one turn. Change the next question based on each answer; do not follow a fixed sequence. Reflect back only confirmed answers.

If the user provides a PDF or CSV estate inventory, import it before asking them to repeat information:

```powershell
python -m fabric_adoption_assistant.cli import-estate <estate.pdf-or-csv> \
  --customer-name <customer> \
  --output <customer>-estate-import.json
```

- CSV: Treat `name`, `workload_type`, `size_gb`, and `notes` as imported source fields. The importer intentionally leaves all assessment `answers` empty.
- PDF: Treat extracted page text as an unconfirmed source document. Propose candidate workloads with the page number and exact supporting text, then ask the user to confirm or correct them.
- Never assess directly from a PDF extraction or an uploaded row. Confirm the inventory first, then run the workload-specific questions.
- If a PDF page has no extractable text, state that OCR is required. Do not guess from an empty or unreadable page.

List supported workload types when needed:

```powershell
python -m fabric_adoption_assistant.cli workloads
```

### 2. Discover each workload

For every workload instance, capture its name, type, approximate size when known, and notes. Use the engine's question metadata as a coverage checklist, not as a mandatory order. The agent may ask a more specific question when it resolves the same field without loss of meaning.

```powershell
python -m fabric_adoption_assistant.cli questions <workload_type> --answers-json '<confirmed-json>'
```

Map confirmed answers to the returned question ids when writing the intake. Do not add guessed defaults. Resolve ambiguous answers with a follow-up rather than normalizing silently.

For imported inventories, present a compact confirmation table containing source location, proposed workload name, proposed type, size, and notes. Label the table `Unconfirmed extraction`. Only move confirmed entries into the assessment intake.

### 3. Ground current product claims

Use the returned `docs_query` with `microsoft_docs_search`. Open the relevant Learn result with `microsoft_docs_fetch` before using it. For each claim retained in the assessment, record:

```yaml
evidence:
  - title: <title returned by Learn MCP>
    url: <URL returned by Learn MCP>
    claim: <narrow claim supported by the opened page>
    retrieved_on: <current YYYY-MM-DD>
```

Evidence supports a claim; it does not replace customer discovery. Prefer current workload-specific guidance over general overview pages.

### 4. Use specialist Fabric skills

After the deterministic assessment identifies a target or validation action, use installed Fabric skills for deeper work:

- Power BI or AAS model compatibility and implementation: `semantic-model-authoring`
- Databricks migration: `databricks-migration`
- Synapse migration: `synapse-migration`
- HDInsight or Spark migration: `hdinsight-migration` or `spark-cli`
- Data Factory pipeline migration: `pipeline-migration`
- Fabric Activator suitability: `activator-cli`
- Capacity and cost validation: `e2e-fabric-cost-estimation`

Do not invoke implementation skills merely to make the readiness report look complete. Invoke them when the customer requests a deeper assessment or the current disposition depends on details covered by that skill.

### 5. Confirm and assess

Before writing the intake, summarize critical confirmed facts and unresolved questions. Ask the user to correct inaccuracies. Write the confirmed structure to YAML and run:

```powershell
python -m fabric_adoption_assistant.cli assess <intake.yaml> \
  --json-out <customer>-readiness.json \
  --html-out <customer>-readiness.html
```

### 6. Present results

Lead with blockers and `Needs Discovery` items. Explain that confidence is discovery completeness, not probability of migration success. Provide the HTML report as the customer artifact and JSON as the reusable machine-readable record.

## Intake contract

Use `examples/sample_intake.yaml` as the shape. Keep raw customer answers in `answers`; keep documentation claims in `evidence`. Do not place agent-generated prose into either field without the user's confirmation or a source.

## Refresh and release current guidance

When asked to update the skill, validate current support, or release the CSA pack, follow `references/MAINTENANCE.md`. In summary:

1. Identify the affected workload keys, product claims, questions, and deterministic rules.
2. Run each affected `docs_query` through Microsoft Learn MCP and open the selected pages. Search snippets alone are not evidence.
3. Record the narrow supported claim, URL, retrieval date, and affected rule. Preserve inconclusive findings as evidence limitations.
4. Update `src/fabric_adoption_assistant/data/knowledge_base.yaml` only when opened evidence or reviewed field learning supports the change.
5. Add both trigger and non-trigger regression tests. Include validation and report tests when contracts or output change.
6. Run the full pytest suite and the three packaged browser scenarios.
7. Require a second CSA review for changed blocker, target-pattern, or keep-outside-Fabric logic.
8. Release with rules version, reviewer, evidence date, changed workloads, test result, and migration note.

Do not automatically convert documentation text into rules, rewrite historical evidence, or publish unreviewed support claims. Existing customer assessments retain the rules and evidence versions used when they were produced.

## Reuse across CSAs

Use `docs/CSA_REUSE_PLAYBOOK.md` for engagement setup, roles, quality gates, and handoff. Store real customer artifacts outside the shared repository. Share only de-identified rule feedback and generic scenarios.
