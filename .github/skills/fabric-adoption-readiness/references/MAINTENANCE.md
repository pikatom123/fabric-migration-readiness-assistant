# Skill Maintenance and Current-Guidance Protocol

## Freshness model

The skill does not treat cached model knowledge as current product truth. For every customer assessment, current support and limitation claims are retrieved from Microsoft Learn MCP and recorded with URL and retrieval date.

Use three maintenance cadences:

- Per engagement: revalidate every claim that affects target pattern, blocker, or required design change.
- Monthly: review all `docs_query` entries in the knowledge base and triage changed Learn guidance.
- Event driven: review immediately after major Fabric announcements, field escalation, failed migration, or specialist-skill update.

## Update workflow

1. Inventory the affected workload keys and rules in `src/fabric_adoption_assistant/data/knowledge_base.yaml`.
2. Run each `docs_query` through `microsoft_docs_search`.
3. Open selected sources with `microsoft_docs_fetch`; do not update from search snippets alone.
4. Record the narrow supported claim, URL, retrieval date, and affected rules in the pull request or release record.
5. Update questions or deterministic rules only when explicit evidence or reviewed field learning requires it.
6. Add trigger, non-trigger, validation, and report regression tests.
7. Run:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

8. Regenerate sample reports and test the standalone browser scenarios.
9. Obtain review from a second CSA for changed blocker or target-pattern logic.
10. Release with a rules version and concise migration note.

## Release record template

```yaml
version: <semver or date-based version>
released_on: <YYYY-MM-DD>
reviewers: [<name>]
workloads_changed: [<keys>]
evidence:
  - title: <opened Learn page>
    url: <opened URL>
    retrieved_on: <YYYY-MM-DD>
    supported_claim: <narrow claim>
rules_changed: [<rule ids or descriptions>]
tests_added: [<test names>]
breaking_changes: <none or migration action>
```

## Guardrails

- Do not automatically rewrite rules from documentation text.
- Do not remove a blocker without reviewed evidence and a non-trigger test.
- Do not overwrite historical assessment evidence when guidance changes.
- Do not put customer names, estate data, or credentials in skill files.
- If Learn MCP is unavailable, publish an evidence limitation rather than a current claim.
