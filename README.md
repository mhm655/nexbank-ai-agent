# NexBank Agentic AI Customer Service Agent with Feedback Loops

A specification-first design for a production-grade, self-improving AI customer service system for **NexBank**, a fictional Indian neo-bank (2.7M customers, ~18,000 interactions/day).

> Status: **Day 6 of 15** (Level 1 architecture complete; Level 2 NLU specs and utterance library complete). Most folders are placeholders that later days fill in. See [CHANGELOG.md](CHANGELOG.md).

## Targets

| Metric | Target |
|---|---|
| Containment rate | >= 70% |
| CSAT | >= 4.5 / 5 |
| Incorrect financial advice | 0% |
| First reply | < 30 s (engineering budget < 3 s p95 per turn; see decision D-07) |
| KB retrieval p95 latency | < 200 ms |

## Navigation

| Path | Contents | Filled on |
|---|---|---|
| `docs/requirements-traceability.md` | Requirement > brief section > deliverable file > status | Day 1 (updated daily) |
| `docs/assumptions-and-decisions.md` | Assumptions, open questions, decisions | Day 1 (updated daily) |
| `docs/stakeholder-analysis.md` | Customer Experience Board vs Risk Committee tensions | Day 1 |
| `docs/architecture/` | System architecture, dialogue management, response generation | Days 1-3 |
| `docs/intent-taxonomy/` | Intents, entities, disambiguation, sentiment, `utterances.csv`, `language-detection.md` | Days 4-6 |
| `docs/knowledge-base/` | KB schema and ER model, 77 entries in `entries/` ([index](docs/knowledge-base/README.md), Day 7); retrieval pipeline and access matrix (Day 8) | Days 7-8 |
| `docs/guardrails/` | Advice boundary, security rules, adversarial defences | Days 9-10 |
| `docs/learning-pipeline/` | Supervisor, CSAT and outcome feedback loops, A/B testing | Day 11 |
| `docs/escalation/`, `docs/metrics/` | ESC-001..015, routing, KPIs, dashboards | Days 12-13 |
| `docs/compliance/`, `docs/risk/` | Audit logging, risk matrix | Day 14 |
| `diagrams/` | Mermaid sources | Days 2-13 |
| `simulations/` | 20+ annotated conversations | Day 14 |
| `tests/` | Guardrail, adversarial, escalation, NLU and safety-suite cases | Days 5-14 |
| `config/` | YAML/JSON configs, 6-layer system prompt, 15+ templates | Days 3-13 |

## Conventions

- Thresholds, IDs and parameters live in `config/*.yaml` and are the single source of truth. Docs reference them rather than restating values.
- All rates, fees and figures come from the simulated NexBank catalogue. No real-world product data is used.
- No real customer data. Examples use pseudonymised or synthetic values only.
