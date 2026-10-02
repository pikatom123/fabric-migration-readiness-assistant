# CSA Reuse Playbook

## Engagement outcome

Use the assistant to turn an initial migration conversation into a confirmed workload inventory, open-question list, directional readiness position, target patterns, risks, design changes, optimisation actions, and capacity-estimator inputs.

## Before the workshop

1. Create an engagement folder outside the product repository.
2. Collect available inventory, architecture diagrams, reports, pipeline lists, and telemetry.
3. Record customer outcome, decision deadline, region, governance constraints, and workshop attendees.
4. Open the workspace and approve the Microsoft Learn MCP server.
5. Run the latest skill update check described in the maintenance playbook.
6. Never place customer files or credentials in the shared Git repository.

Suggested engagement structure:

```text
<Customer>-<YYYYMM>/
  01-source/
  02-confirmed-intake/
  03-evidence/
  04-assessment/
  05-customer-output/
  06-review/
```

## During the workshop

1. Import the estate or enter workloads manually.
2. Label extracted facts unconfirmed until the customer validates them.
3. Ask no more than three questions at a time.
4. Prioritise blockers, target-pattern decisions, connectivity/security, scale/concurrency, then optimisation.
5. Record current product claims only after opening Microsoft Learn evidence.
6. Separate application workflows from data orchestration.
7. Confirm unresolved facts and owners before ending.

## After the workshop

1. Review the confirmed-facts summary with the customer.
2. Run the deterministic engine and preserve its rules version.
3. Review blockers and Needs Discovery items before presenting readiness.
4. Validate capacity inputs with telemetry and the SKU Estimator.
5. Generate customer HTML/PDF and internal JSON/evidence artifacts.
6. Record agreed next actions, owners, due dates, and specialist assessments.

## Reusable roles

| Role | Responsibility |
|---|---|
| Lead CSA | Facilitates discovery and owns customer recommendation |
| Workload specialist | Validates detailed Power BI, Spark, SQL, pipeline, or RTI concerns |
| Customer platform owner | Confirms constraints, operations, identity, network, and governance |
| Customer workload owner | Confirms workload behaviour and business criticality |
| Reviewer | Challenges unsupported claims and approves customer output |
| Rules maintainer | Owns evidence refresh, tests, versioning, and release notes |

## Quality gate

A customer report is ready only when:

- every assessed workload has confirmed decision-changing facts;
- unknowns remain visible rather than defaulted;
- every current product-support claim has opened evidence or a stated limitation;
- blockers, optimisation actions, and target patterns are explainable;
- capacity is described as directional unless measured validation is complete;
- a second CSA has reviewed high-impact recommendations;
- the report records rules and evidence versions.

## Handoff template

```text
Customer outcome:
Decision deadline:
Estate scope:
Readiness position:
Ready workloads:
Optimisation candidates:
Redesign / retain workloads:
Material unknowns:
Capacity evidence required:
Specialist reviews required:
Next three actions and owners:
Rules version:
Evidence reviewed on:
```

## Feedback to the shared product

Submit only reusable, de-identified learning: missing question, false trigger, missed blocker, ambiguous recommendation, evidence change, or report usability issue. Add trigger and non-trigger regression tests before changing shared rules.
