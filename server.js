import "dotenv/config";
import express from "express";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { AIProjectClient } from "@azure/ai-projects";
import { DefaultAzureCredential } from "@azure/identity";

const endpoint = process.env.FOUNDRY_PROJECT_ENDPOINT;
const deployment = process.env.FOUNDRY_MODEL_DEPLOYMENT;

if (!endpoint || !deployment) {
  throw new Error("FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL_DEPLOYMENT must be configured.");
}

const project = new AIProjectClient(endpoint, new DefaultAzureCredential());
const openAI = project.getOpenAIClient();
const app = express();
const root = path.dirname(fileURLToPath(import.meta.url));
const indexHtml = await readFile(path.join(root, "index.html"), "utf8");

app.use(express.json({ limit: "100kb" }));
app.get("/", (_req, res) => res.type("html").send(indexHtml));

const workloadTypes = [
  "Power BI", "SSAS / Azure Analysis Services", "Azure SQL", "Synapse",
  "Databricks", "Azure Data Factory", "Logic Apps", "Spark jobs", "Automation runbooks"
];
const featureIds = [
  "calculated-columns", "composite-model", "unsupported-model", "self-hosted-ir",
  "custom-connector", "ssis", "private-network", "custom-libraries", "streaming",
  "stateful", "cdc", "high-overlap", "manual-ops"
];

const interviewSchema = {
  type: "object",
  additionalProperties: false,
  required: [
    "assistantMessage", "complete", "coverage", "facts", "architectureHints",
    "quickReplies", "context", "workloadCandidates"
  ],
  properties: {
    assistantMessage: { type: "string" },
    complete: { type: "boolean" },
    coverage: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["id", "label", "status"],
        properties: {
          id: { type: "string" },
          label: { type: "string" },
          status: { type: "string", enum: ["missing", "partial", "complete"] }
        }
      }
    },
    facts: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["label", "value"],
        properties: { label: { type: "string" }, value: { type: "string" } }
      }
    },
    architectureHints: { type: "array", items: { type: "string" } },
    quickReplies: { type: "array", items: { type: "string" } },
    context: {
      type: "object",
      additionalProperties: false,
      required: [
        "customerName", "industry", "region", "targetDate", "users", "concurrentUsers",
        "governance", "strategy", "outcomes", "constraints"
      ],
      properties: {
        customerName: { type: ["string", "null"] },
        industry: { type: ["string", "null"] },
        region: { type: ["string", "null"] },
        targetDate: { type: ["string", "null"] },
        users: { type: ["number", "null"] },
        concurrentUsers: { type: ["number", "null"] },
        governance: { type: ["string", "null"], enum: ["1", "2", "3", "4", null] },
        strategy: { type: ["string", "null"] },
        outcomes: { type: ["string", "null"] },
        constraints: { type: ["string", "null"] }
      }
    },
    workloadCandidates: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["name", "type", "size", "refresh", "concurrency", "complexity", "features", "notes"],
        properties: {
          name: { type: "string" },
          type: { type: "string", enum: workloadTypes },
          size: { type: "number" },
          refresh: { type: "number" },
          concurrency: { type: "number" },
          complexity: { type: "string", enum: ["Low", "Medium", "High"] },
          features: { type: "array", items: { type: "string", enum: featureIds } },
          notes: { type: "string" }
        }
      }
    }
  }
};

const instructions = `You are a senior Microsoft Fabric Cloud Solution Architect conducting an adaptive migration discovery interview.

Your job is to ask exactly one focused question at a time and choose the next best question from everything already known. Do not give a generic questionnaire. Briefly acknowledge useful information, explain why the next question matters when helpful, then ask the question.

Cover these areas before marking complete:
1. Business outcomes, scope, deadline, migration strategy, and success measures.
2. Current estate: Power BI, SSAS/AAS, Azure SQL, Synapse, Databricks, ADF, Logic Apps, Spark, runbooks, and non-Microsoft sources.
3. Data volumes, growth, ingestion rates, retention, refresh frequency, latency, concurrency, and peak overlap.
4. Semantic models: model mode, DAX, calculated columns/tables, composite models, RLS/OLS, XMLA, MDX, writeback, and unsupported features.
5. Integration: connectors, gateways, self-hosted IR, SSIS, triggers, CDC, private endpoints, and network boundaries.
6. Engineering: notebooks, runtimes, libraries, CI/CD, source control, monitoring, ownership, and support model.
7. Security, governance, residency, identities, tenant boundaries, Purview, and regulatory constraints.
8. Real-time, orchestration, ML, and application-integration requirements.
9. Capacity signals needed by the Fabric SKU Estimator and representative pilot candidates.

Always return all nine coverage entries in this exact order and with these IDs: business, estate, scale, semantic-models, integration, engineering, governance, specialized-workloads, capacity-pilot. Mark each missing, partial, or complete from the evidence collected so far.

Ask follow-ups when an answer is vague, contradictory, or lacks scale. Prefer bounded, answerable questions and offer 2-4 short quick replies where useful. Do not recommend a final architecture until critical unknowns are resolved. Treat Logic Apps and runbooks as external runtimes unless they are purely data orchestration. Surface Direct Lake limitations, connector parity, integration runtime dependencies, refresh overlap, capacity pressure, and maintainability risks.

Maintain a cumulative structured extraction. Never invent values. Use 0 for unknown numeric workload fields and explain unknowns in notes. Keep the assistantMessage concise and end it with exactly one question unless complete.`;

function validMessages(messages) {
  if (!Array.isArray(messages) || messages.length > 50) return false;
  return messages.every(message =>
    ["user", "assistant"].includes(message?.role) &&
    typeof message?.text === "string" &&
    message.text.length <= 5000
  );
}

app.post("/api/discovery", async (req, res, next) => {
  try {
    const { messages = [], context = {}, workloads = [] } = req.body || {};
    if (!validMessages(messages)) {
      return res.status(400).json({ error: "Invalid or oversized interview transcript." });
    }

    const input = [
      {
        role: "user",
        content: `Current extracted assessment state:\n${JSON.stringify({ context, workloads })}`
      },
      ...messages.map(message => ({ role: message.role, content: message.text })),
      ...(messages.length ? [] : [{ role: "user", content: "Begin the interview with the single highest-value opening question." }])
    ];

    const response = await openAI.responses.create({
      model: deployment,
      instructions,
      input,
      text: {
        format: {
          type: "json_schema",
          name: "fabric_discovery_interview",
          strict: true,
          schema: interviewSchema
        }
      }
    });

    if (!response.output_text) {
      throw new Error("The Foundry model returned no structured interview output.");
    }
    res.json(JSON.parse(response.output_text));
  } catch (error) {
    next(error);
  }
});

app.use((error, _req, res, _next) => {
  console.error(error);
  res.status(502).json({
    error: error instanceof Error ? error.message : "Microsoft Foundry request failed."
  });
});

const port = Number(process.env.PORT || 3000);
app.listen(port, () => {
  console.log(`Fabric readiness assistant running at http://localhost:${port}`);
});
