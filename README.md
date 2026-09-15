# Fabric Migration Readiness Assistant

An interactive prototype that helps Cloud Solution Architects assess analytics
workloads for migration to Microsoft Fabric.

## Capabilities

- Runs an adaptive Microsoft Foundry-powered architecture discovery interview
- Chooses the next best question from previous answers and current unknowns
- Extracts customer context, architecture facts, coverage, and workload candidates
- Inventories workloads across Microsoft analytics and integration services
- Maps workloads to Fabric patterns using explainable rules
- Flags blockers, redesign needs, and optimisation opportunities
- Produces directional inputs for the Fabric SKU Estimator
- Generates a printable customer-ready readiness summary

## Run locally

1. Install Node.js 22 or later and run `npm install`.
2. Copy `.env.example` to `.env`.
3. Sign in with Azure CLI using an identity that can access the Foundry project.
4. Run `npm start`.
5. Open `http://localhost:3000`.

The browser never receives Azure credentials. The Node.js backend authenticates
to Microsoft Foundry with `DefaultAzureCredential`.

## Disclaimer

Recommendations are directional. Validate them against current Microsoft Fabric
documentation, regional availability, and measured workload telemetry.
