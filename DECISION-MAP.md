# Fabric Solution Decision Map

A living architecture canvas for greenfield data and analytics conversations. It
helps a customer and architect move from a blank room to an explicit, reasoned,
and adaptable Microsoft Fabric solution direction.

This is not a product selector or a one-time assessment. It is a decision system.
Architecture choices form a dependency graph, every direction carries trade-offs,
and the current set of choices generates the next delivery roadmap.

A team might begin with data in OneLake, a Fabric Lakehouse, and Direct Lake. New
evidence may later favour ADLS as the system of record and Azure Databricks for
engineering. The map should make that pivot safe: preserve why the original choice
was made, identify what the change affects, and regenerate the work ahead.

## Product thesis

Architecture workshops often produce diagrams without preserving the decisions,
evidence, assumptions, and rejected alternatives behind them. Those diagrams age
poorly because nobody can tell which choices remain valid when a requirement
changes.

The Decision Map treats the architecture as an evolving set of hypotheses:

> Given these customer requirements and this evidence, this is our current best
> direction, these are the consequences, and this is what we need to prove next.

The goal is not to recommend Fabric everywhere. The goal is to make the best-fit
boundary between Fabric, Azure Databricks, ADLS, Microsoft Purview, source systems,
and other services clear and defensible. A customer can make Unity Catalog and
ADLS authoritative while still using Fabric for semantic models and reporting.
Another can make OneLake and Fabric authoritative. Both are valid when ownership,
identity, policy enforcement, and operational consequences are explicit.

## Current prototype

The self-contained prototype includes:

- A 25-node dependency map from delivery strategy and governance authority through operations and adoption
- Product-first, platform-first, and dual-track initial delivery strategies
- Fabric-first, Fabric plus Azure Databricks, and open Azure estate directions
- Centralised, domain-aligned, and multiple governed boundary topologies
- Fabric and Purview, Unity Catalog-authoritative, and federated catalog models
- Workforce, managed identity, service principal, guest, and privileged identity guidance
- OneLake-authoritative, ADLS plus Unity Catalog, and split storage authority patterns
- OneLake copy, shortcut, ADLS landing, and regional recovery patterns
- Fabric Lakehouse, Warehouse, and Databricks compute choices
- Direct Lake, Import, and DirectQuery semantic model choices
- Managed reporting, governed self-service, embedded, and external sharing choices
- Shared, tiered, and domain-owned Fabric capacity topologies
- Governance, security, automation, observability, FinOps, reliability, and adoption decisions
- Three facilitator questions and an evidence gate for every decision
- Authored rationale, advantages, trade-offs, and Microsoft documentation links
- Customer-specific context and rationale notes
- Downstream review flags when an upstream choice changes
- A four-phase roadmap generated from the current choices
- A chronological decision log that records pivots
- A Fabric-first greenfield starter that can be challenged and changed

The prototype stores its state in browser local storage. Its decision graph,
trade-offs, dependencies, and roadmap phases are currently authored defaults; they
are not yet generated from a full customer discovery model.

## Workshop flow

1. Frame the customer outcomes, users, constraints, and service levels.
2. Load the greenfield starter or begin with an empty map.
3. Select a decision node and compare viable directions.
4. Review the rationale, advantages, trade-offs, and linked evidence.
5. Record customer-specific assumptions and choose a current direction.
6. Capture evidence through a proof of concept, telemetry, policy review, or cost model.
7. Pivot when the evidence points elsewhere.
8. Revisit the dependent decisions highlighted by the map.
9. Treat the generated roadmap as the next delivery hypothesis.

The **Load greenfield starter** action creates a complete Fabric-first hypothesis:
domain-aligned workspaces, Fabric and Purview catalog authority, a hybrid identity
model, OneLake as the storage authority, Fabric Lakehouse, Direct Lake, governed
self-service, central guardrails with domain ownership, shared capacity, native
monitoring, and showback. It is a conversation starter, not a prescribed reference
architecture.

### Initial delivery strategy

**Product-first** and **platform-first** are not mutually exclusive end states.
This decision asks what the first funded release should optimise for:

- **Product-first** delivers one named outcome end to end, then extracts reusable
	platform patterns from evidence.
- **Platform-first** establishes minimum shared foundations for several committed
	product teams and proves them through a lighthouse use case.
- **Dual-track** funds a thin platform and a lighthouse product together, with a
	shared backlog and explicit team boundaries.

Choose based on funded demand, accountable owners, and capabilities that are
demonstrably shared now. Do not build an enterprise platform solely for predicted
future consumers, and do not let a product-first release ignore security,
governance, or reuse.

## Enterprise decision coverage

The map separates concerns when they have different owners, evidence, or blast
radius. Selecting a technology does not silently decide its governance model.

| Area | Decisions the workshop must resolve |
| --- | --- |
| Strategy | Initial delivery strategy, source estate, and Fabric/Databricks/Azure platform boundary |
| Organisation | Tenant, geography, domain, workspace, environment, and capacity boundaries |
| Governance authority | Whether Fabric and Purview, Unity Catalog, or federated catalogs own metadata, lineage, policy, and entitlements |
| Identity | Workforce groups, managed identities, service principals, workload federation, guests, privileged access, and lifecycle |
| Storage | OneLake or ADLS authority, Delta ownership, zones, shortcuts, writes, retention, deletion, and optimisation |
| Data movement | Batch, CDC, mirroring, streaming, gateways, replay, idempotency, and schema change |
| Resilience | Residency, regional placement, RPO/RTO tiers, restore, replay, redeployment, and recovery ownership |
| Engineering | Fabric Lakehouse, Warehouse, Databricks, product contracts, medallion or dimensional design, and data quality |
| Consumption | Direct Lake, Import, DirectQuery, semantic reuse, managed BI, self-service, paginated, embedded, and operational reporting |
| Sharing | Cross-workspace, cross-domain, cross-tenant, partner data products, APIs, and external analytics |
| Security | Tenant and workspace controls, item permissions, RLS/OLS, private access, gateways, DNS, audit, and break-glass paths |
| Delivery | Environments, Git, deployment, IaC, APIs, configuration, secrets, tests, approvals, rollback, and drift |
| Capacity | Region, SKU, workload concurrency, smoothing, workspace placement, isolation tiers, scale triggers, and administration |
| Operations | Service ownership, observability, quality telemetry, incidents, runbooks, recovery tests, and support boundaries |
| Economics | Fabric capacity, Databricks compute, storage, network, licensing, showback, chargeback, budgets, and unit economics |
| Evolution | AI timing and platform, adoption, enablement, outcome telemetry, architecture reviews, and technical debt |

### Unity Catalog and Fabric

Choosing **Unity Catalog authoritative** means Unity Catalog governs Databricks
data objects, external locations, credentials, and privileges. It does not make
Fabric permissions disappear. The workshop must still resolve:

- How Fabric reaches governed Delta data, such as an approved OneLake shortcut or
	another supported access pattern
- How Microsoft Entra principals map to Unity Catalog identities and Fabric users
- Which system owns catalog metadata, classification, lineage, quality, and access
	approval for each asset type
- Where Fabric workspace, item, semantic model, RLS, OLS, and report permissions
	remain authoritative
- Who owns table writes, optimisation, retention, deletion, and schema evolution
- How cross-platform lineage, audit, revocation, and incident investigation work

Avoid claiming one universal governance plane when controls are actually enforced
by several products. Use an authority matrix to identify the system of record and
enforcement point for every governance concern.

### Multiple governance boundaries

A workspace is a collaboration and security boundary, but it may not be sufficient
for every legal, geographic, subsidiary, customer, or operational isolation need.
The topology decision therefore asks separately about tenant, region, domain,
workspace, environment, and capacity boundaries. For each boundary, record:

- The reason for separation and the accountable owner
- Data residency, identity, policy, administration, and cost implications
- How approved data and semantic products cross the boundary
- How deployments, metadata, support, and recovery operate across it
- Whether the isolation requirement has been tested rather than assumed

### Capacity guidance

Do not select a Fabric SKU from data volume alone. Capacity planning should include
interactive report concurrency, semantic model mode, refresh and ingestion windows,
Spark and warehouse workload shape, Real-Time Intelligence, AI activity, background
operations, geography, isolation, and growth. Begin with representative workload
tests and capacity telemetry, then agree:

- Initial SKU and region
- Which workspaces share or receive isolated capacity
- Peak concurrency and background scheduling assumptions
- Scale-up, scale-down, reassignment, and intervention triggers
- Capacity administrators and product owners
- Reservation, budget, showback, or chargeback model
- How Fabric cost is considered alongside Databricks, ADLS, network, and licensing

The app provides shared, tiered, and domain-owned topology choices. It does not
calculate or prescribe a SKU because reliable sizing requires measured workload
telemetry and current commercial inputs.

## Decision model

Each architecture decision should eventually carry:

| Element | Purpose |
| --- | --- |
| Question | The customer choice that must be made |
| Context | Requirements and constraints that shape the answer |
| Options | Credible directions, including non-Fabric alternatives |
| Trade-offs | Benefits, limitations, operational cost, and lock-in |
| Evidence | Documentation, telemetry, experiments, policy, and cost data |
| Confidence | How strongly the evidence supports the current direction |
| Dependencies | Decisions that constrain or are affected by this choice |
| Validation | The proof required before the choice is considered accepted |
| Owner | The person accountable for resolving and revisiting the decision |
| History | Previous choices and why the architecture changed |

## Improvement roadmap

### 1. Make discovery drive the graph

Capture volume, velocity, latency, source estate, networking, residency, skills,
operating model, budget, and recovery needs. Use those facts to rank relevant
decisions, hide irrelevant paths, surface contradictions, and explain why an option
fits. This is the most important next step: the map should respond to the customer,
not only to clicks.

### 2. Add scenario branches

Allow architects to fork the current state into named scenarios such as
**Fabric-first**, **Fabric plus Databricks**, and **ADLS-led**. Compare them side by
side across capability fit, complexity, cost drivers, risk, skills, and time to
value without overwriting the baseline.

### 3. Strengthen the evidence model

Attach evidence to individual claims rather than one link per option. Record the
source, publication date, date checked, applicable region, customer evidence, and
confidence. Mark claims that still need validation and make stale evidence visible.

### 4. Explain dependency impact

Replace broad transitive review flags with specific reasoning: what assumption was
invalidated, why the downstream choice may change, and which proof should be rerun.
Distinguish a direct conflict from a low-risk review.

### 5. Make the roadmap executable

Generate roadmap items with dependencies, owners, effort ranges, exit criteria,
proof-of-concept tasks, and decision gates. Derive timing from customer constraints
instead of fixed week ranges, then export the result as a backlog or delivery plan.

### 6. Produce durable architecture outputs

Export and import the complete decision model as JSON. Generate customer-ready
Markdown or PDF, Architecture Decision Records, a solution diagram, risk register,
assumption log, and an implementation backlog from the same source of truth.

### 7. Add measurable economics

Connect capacity and platform choices to measured workload telemetry and current
pricing inputs. Show cost drivers and sensitivity ranges rather than false-precision
estimates, and make the cost impact of a pivot visible.

### 8. Support collaboration and governance

Move beyond local storage to versioned assessments with participants, comments,
approvals, decision owners, and review dates. Keep an audit trail and allow a
customer to reopen the architecture after implementation evidence arrives.

## Product principles

- **Start with outcomes, not services.** Technology choices follow customer value
	and constraints.
- **Keep alternatives credible.** Fabric is not automatically the answer to every
	node.
- **Show the reasoning.** A recommendation without evidence and trade-offs is only
	an opinion.
- **Prefer reversible choices.** Make lock-in, migration cost, and exit paths
	explicit.
- **Treat uncertainty honestly.** Record confidence and what must be proved next.
- **Preserve history.** A pivot is learning, not a failed architecture.
- **Generate action.** Every unresolved decision should produce a next step, owner,
	or validation task.

## Run locally

Open `decision-map.html` in a modern browser. No build or server is required. The app is
self-contained and stores the current architecture and decision history in browser
local storage.

## Validation boundary

All recommendations are directional. Validate them against current Microsoft
documentation, regional and feature availability, customer policy, security and
compliance requirements, measured workload telemetry, and an agreed cost model
before implementation.
