# Requirements Traceability

Status: `todo` / `draft` / `done`. Brief sections refer to the ZeTheta PDF. Updated daily. Level numbers follow the campaign levels (D-02).

| ID | Requirement | Brief § | Level | Deliverable file(s) | Day | Status |
|---|---|---|---|---|---|---|
| R-01 | Repo in the required structure, README, CHANGELOG (daily) | D / F | 7 | `README.md`, `CHANGELOG.md` | 1, 15 | draft |
| R-02 | Requirements traceability, assumptions, stakeholder analysis | D | 7 | `docs/requirements-traceability.md`, `docs/assumptions-and-decisions.md`, `docs/stakeholder-analysis.md` | 1 | done |
| R-03 | System architecture, minimum 8 components | A2 | 1 | `docs/architecture/system-architecture.md`, `diagrams/architecture.mmd` | 2 | done |
| R-04 | Component interface contracts | A2 | 1 | `docs/architecture/component-interfaces.md` | 2 | done |
| R-05 | Agent/tool matrix, least privilege | A2 | 1 | `diagrams/agents-and-tools.mmd`, system-architecture §3 | 2 | done |
| R-06 | Dialogue state schema: intent+confidence+alternatives, slots, >= 20 turns, sentiment trajectory, auth level, guardrail state, escalation proximity, carry-over | A2.1 | 1 | `config/dialogue_state.schema.json` | 3 | done |
| R-07 | Dialogue policy: action space, hybrid decision logic, confirmation, clarification, recovery, proactive | A2.1 | 1 | `docs/architecture/dialogue-management.md` | 3 | done |
| R-08 | Multi-turn reasoning: anaphora, topic switching, implicit intent, contradictions, context window | A2.1 | 1 | `docs/architecture/dialogue-management.md` | 3 | done |
| R-09 | Dialogue state machine and auth flow | A2.1 | 1 | `diagrams/dialogue-state-machine.mmd`, `diagrams/auth-flow.mmd` | 3 | done |
| R-10 | Response generation: template/LLM/hybrid, persona, length calibration, safety layer | A2.4 | 1 | `docs/architecture/response-generation.md` | 3 | done |
| R-11 | Multilingual: Hindi, English, Hinglish primary; 5 secondary | A2.4 | 1 | `docs/architecture/multilingual.md`, `docs/intent-taxonomy/language-detection.md` | 3, 6 | done |
| R-12 | Failure-mode analysis | A2 | 1 | `docs/architecture/failure-modes.md` | 3 | done |
| R-13 | Latency, scalability, cost | A2 / D1 | 1 | `docs/architecture/latency-scalability-cost.md` | 3 | done |
| R-14 | Level 1 boss trace (20 turns, 12 topic switches) | B | 1 | `docs/architecture/boss-trace.md` | 3 | done |
| R-15 | 25+ intent taxonomy (aim 30+), 3 tiers, per-layer thresholds, multi-intent, OOS | A2.2, A3 | 2 | `docs/intent-taxonomy/taxonomy.md`, `config/intents.yaml`, `docs/architecture/nlu-pipeline-overview.md` | 4-5 | done |
| R-16 | Entity catalogue with validation and sensitivity | A2.2 | 2 | `docs/intent-taxonomy/entities.md`, `config/entities.yaml` | 4 | done |
| R-17 | 6 disambiguation pairs and the Level 2 boss (10 ambiguous messages) | A3, B | 2 | `docs/intent-taxonomy/disambiguation.md`, `diagrams/disambiguation-*.mmd`, `tests/nlu/boss-level2.yaml` | 5, 6 | done |
| R-18 | Sentiment and emotion spec | A2.2 | 2 | `docs/intent-taxonomy/sentiment.md` | 5 | done |
| R-19 | Utterance library (300+) | D | 2 | `docs/intent-taxonomy/utterances.csv`, `tests/nlu/README.md` | 6 | done |
| R-20 | 50+ KB entries, schema, versioning, TTL, access control | A2.3 | 3 | `docs/knowledge-base/kb-schema.md`, `docs/knowledge-base/entries/*.yaml`, `docs/knowledge-base/README.md`, `diagrams/kb-er-model.mmd`, `tests/kb/validate_kb_entries.py` | 7 | done |
| R-21 | Retrieval pipeline (hybrid, rerank, p95 < 200 ms) | A2.3 | 3 | `docs/knowledge-base/retrieval-pipeline.md`, `diagrams/retrieval-pipeline.mmd` | 8 | done |
| R-22 | Financial advice boundary | A4.1 | 4 | `docs/guardrails/financial-advice.md`, `config/guardrails.yaml` (GR-ADV-01..09) | 9 | done |
| R-23 | 8 account-security rules | A4.2 | 4 | `docs/guardrails/account-security.md`, `config/guardrails.yaml` (GR-SEC-R1..R8) | 9 | done |
| R-24 | RBI / PCI DSS / KYC-AML / SEBI / IRDAI / DPDP / Ombudsman mapping | A4.3, appendix | 4 | `docs/guardrails/regulatory-mapping.md`, `config/guardrails.yaml` (GR-REG-01..20) | 9 | done |
| R-25 | 6 adversarial vectors and 50+ tests | A4 | 4 | `docs/guardrails/adversarial-defences.md`, `tests/adversarial/` | 10 | todo |
| R-26 | Continuous learning pipeline and safety preservation (200-case suite) | A5 | 5 | `docs/learning-pipeline/`, `tests/safety-suite/` | 11 | todo |
| R-27 | 15 escalation triggers (ESC-001..015), routing, handoff | A6 | 6 | `docs/escalation/`, `config/escalation_rules.yaml` | 12 | todo |
| R-28 | KPIs, 3 dashboards | A8 | 6 | `docs/metrics/` | 12 | todo |
| R-29 | Conversation design: 5 patterns, 8 anti-patterns | A9 | 6 | `docs/architecture/response-generation.md` and `config/templates/` | 13 | todo |
| R-30 | 6-layer system prompt, 8 parameters, 15+ templates | A12 | 6 | `config/system-prompt/`, `config/parameters.yaml`, `config/templates/` | 13 | todo |
| R-31 | 20+ annotated conversations | D | 7 | `simulations/` | 14 | todo |
| R-32 | Audit and compliance logging | A10 | 7 | `docs/compliance/audit-logging.md` | 14 | todo |
| R-33 | Risk assessment matrices | A11 | 7 | `docs/risk/risk-matrix.md` | 14 | todo |
| R-34 | Cross-reference audit, transfer to `@ZethetaIntern` | F | 7 | n/a | 15 | todo |
| R-35 | Graceful fallback when no relevant knowledge is found; gap handling | A2.3 | 3 | `docs/knowledge-base/retrieval-pipeline.md` sections 9-10, `docs/knowledge-base/entries/escalation.yaml` | 7, 8 | done (template text Day 13) |
| R-36 | KB maintenance workflow, regulatory fast-track, staleness alerts; access matrix by auth level; Level 3 boss (5 queries, 3+ entries) | A2.3, B | 3 | `docs/knowledge-base/maintenance-workflow.md`, `docs/knowledge-base/access-control-matrix.md`, `tests/kb/boss-level3.yaml`, `tests/kb/README.md` | 8 | done |
| R-37 | Guardrail registry: implementation type (rule, model, hybrid), enforcement point, action, immutability and false-positive target per guardrail; defence-in-depth diagram | A4, PLAN Phase 4 items 1-5 | 4 | `config/guardrails.yaml`, `diagrams/guardrail-layers.mmd` | 9 | done |

Note: R-29 is partly covered on Day 3 by the persona and conversation-pattern content in `response-generation.md`; it is finalised on Day 13.
