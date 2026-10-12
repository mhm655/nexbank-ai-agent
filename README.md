# NexBank Agentic AI Customer Service Agent with Feedback Loops

A specification-first design for a production-grade, self-improving AI customer service system for **NexBank**, a fictional Indian neo-bank (2.7M customers, ~18,000 interactions/day).

> Status: **Day 13 of 15** (Levels 1-6 complete: architecture, NLU, knowledge base and retrieval, guardrails and safety, continuous learning pipeline, and escalation, metrics, system prompt, governed parameters and template library; simulations, audit logging and risk matrices (Day 14) next). Most remaining folders are placeholders that later days fill in. See [CHANGELOG.md](CHANGELOG.md).

## Targets

| Metric | Target |
|---|---|
| Containment rate | >= 70% |
| CSAT | >= 4.5 / 5 |
| Incorrect financial advice | 0% |
| First reply | < 30 s (engineering budget < 3 s p95 per turn; see decision D-07) |
| KB retrieval p95 latency | < 200 ms |
| First contact resolution (FCR) | >= 70% |
| Escalation rate | < 30% |
| Average handle time (AHT) | < 8 min |

## Navigation

| Path | Contents | Filled on |
|---|---|---|
| `docs/requirements-traceability.md` | Requirement > brief section > deliverable file > status | Day 1 (updated daily) |
| `docs/assumptions-and-decisions.md` | Assumptions, open questions, decisions | Day 1 (updated daily) |
| `docs/stakeholder-analysis.md` | Customer Experience Board vs Risk Committee tensions | Day 1 |
| `docs/architecture/` | System architecture, dialogue management, response generation; conversation design: A9 patterns, anti-patterns, tone (`conversation-design.md`, Day 13) | Days 1-3, 13 |
| `docs/intent-taxonomy/` | Intents, entities, disambiguation, sentiment, `utterances.csv`, `language-detection.md` | Days 4-6 |
| `docs/knowledge-base/` | KB schema and ER model, 77 entries in `entries/` ([index](docs/knowledge-base/README.md), Day 7); retrieval pipeline, maintenance workflow and access matrix (Day 8) | Days 7-8 |
| `docs/guardrails/` | Advice boundary (`financial-advice.md`), 8 security rules (`account-security.md`), regulatory mapping (`regulatory-mapping.md`) on Day 9; adversarial defences (`adversarial-defences.md`), response safety layer (`output-safety-layer.md`), monitoring dashboard (`monitoring-dashboard.md`) and incident playbook (`incident-response-playbook.md`) on Day 10. Registry: `config/guardrails.yaml` (58 guardrails). Tests: `tests/adversarial/` and `tests/guardrails/` (190 cases, specified not run). Layers: `diagrams/guardrail-layers.mmd` | Days 9-10 |
| `docs/learning-pipeline/` | Loop, update classes and cadence (overview.md); supervisor corrections, CSAT signals and outcome tracking; data pipeline with consent and deletion (data-pipeline.md); A/B testing with power analysis and sequential design (ab-testing.md); immutable layer, gates G0-G9, canary and rollback (safety-invariants.md); Level 5 boss as a simulated worked example (boss-level5.md). Loop diagram: diagrams/learning-loop.mmd | Day 11 |
| `docs/escalation/`, `docs/metrics/` | `triggers.md` (ESC-001..015, precedence, 7 additions), `routing-and-handoff.md`, `queue-management.md` (overflow, capacity model, EQ-01..12); `kpi-framework.md`, `improvement-cycle.md`, `dashboards.md`. Rules: `config/escalation_rules.yaml`. Tests: `tests/escalation/` (63 cases, specified not run). Diagram: `diagrams/escalation-routing.mmd` | Day 12 |
| `docs/compliance/`, `docs/risk/` | Audit logging, risk matrix | Day 14 |
| `diagrams/` | Mermaid sources | Days 2-13 |
| `simulations/` | 20+ annotated conversations | Day 14 |
| `tests/` | Guardrail, adversarial, escalation (63 cases, validator, Level 6 boss), NLU, KB (validator, Level 3 boss), templates (`tests/templates/validate_templates.py`: templates, parameters and prompt layers) and safety-suite cases; fixed safety suite `tests/safety-suite/` (355 cases indexed in `manifest.yaml`: 253 by reference, 102 new, specified not run; `manifest.lock.yaml` holds the accepted hashes; validator `validate_manifest.py`) | Days 5-14 |
| `config/` | YAML/JSON configs; `parameters.yaml` (8 A12.3 parameters, 98 project thresholds by reference); `system-prompt/` (6 layers, 84 assertions, manifest); `templates/` (63 templates, 131 variants, en/hi/hinglish, not native-reviewed) | Days 3-13 |

## Conventions

- Thresholds, IDs and parameters live in `config/*.yaml` and are the single source of truth; `config/parameters.yaml` is the index of all thresholds. Docs reference them rather than restating values.
- All rates, fees and figures come from the simulated NexBank catalogue. No real-world product data is used.
- Statistical planning values in `docs/learning-pipeline/` are proposals and are marked as such; simulated figures are labelled simulated.
- No real customer data. Examples use pseudonymised or synthetic values only.
