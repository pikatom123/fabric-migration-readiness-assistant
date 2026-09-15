# Fabric Migration Readiness Assistant

An interactive prototype that helps Cloud Solution Architects assess analytics
workloads for migration to Microsoft Fabric.

## Version 1

- Captures customer goals, constraints, scale, and governance context
- Answers discovery questions using local, context-aware guided intelligence
- Inventories workloads across Microsoft analytics and integration services
- Maps workloads to Fabric patterns using explainable rules
- Flags blockers, redesign needs, and optimisation opportunities
- Produces directional inputs for the Fabric SKU Estimator
- Generates a printable customer-ready readiness summary

## Run locally

Open `index.html` in a modern browser. The prototype is self-contained and saves
assessment data in browser local storage.

The discovery assistant runs entirely in the browser. It uses the captured
customer context and explainable workload assessment rules; it does not send
customer information to an external AI service.

## Disclaimer

Recommendations are directional. Validate them against current Microsoft Fabric
documentation, regional availability, and measured workload telemetry.
