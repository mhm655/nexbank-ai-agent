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
| R-25 | 6 adversarial vectors and 50+ tests | A4 | 4 | `docs/guardrails/adversarial-defences.md`, `tests/adversarial/` (62 cases, 60 attacks, 27 boss), `tests/guardrails/` (128 cases), `GR-ATK-01..11` | 10 | done |
| R-26 | Continuous learning pipeline: three feedback sources, update strategy, safety preservation | A5, D (Day 11) | 5 | `docs/learning-pipeline/overview.md`, `supervisor-corrections.md`, `csat-signals.md`, `outcome-tracking.md`, `safety-invariants.md`, `diagrams/learning-loop.mmd` | 11 | done |
| R-27 | 15 escalation triggers (ESC-001..015), precedence, routing, 8-element handoff, queue management, de-escalation, escalation quality metrics; Level 6 boss (10 edge cases) | A6, B, D | 6 | `docs/escalation/triggers.md`, `docs/escalation/routing-and-handoff.md`, `docs/escalation/queue-management.md`, `config/escalation_rules.yaml`, `diagrams/escalation-routing.mmd`, `tests/escalation/` (63 cases, validator), `config/templates/escalation.yaml` | 12, 13 | done |
| R-28 | KPIs (leading, lagging, operational), improvement cycle, 3 dashboards | A8, A1.4 | 6 | `docs/metrics/kpi-framework.md`, `docs/metrics/improvement-cycle.md`, `docs/metrics/dashboards.md` | 12 | done |
| R-29 | Conversation design: 5 mandatory patterns, 8 anti-patterns with penalties, brand tone | A9 | 6 | `docs/architecture/conversation-design.md`, `config/system-prompt/layer3-dialogue.md`, `config/templates/` (A9 codes per template) | 13 | done (Hindi and Hinglish wording not native-reviewed) |
| R-30 | 6-layer system prompt with immutability rules, 8 governed parameters, 15+ prompt templates with trigger conditions and safety annotations | A12, D (Day 12-13) | 6 | `config/system-prompt/` (6 layers, README, manifest), `config/parameters.yaml`, `config/templates/` (63 templates) | 13 | done (no committee review; specified not run) |
| R-31 | 20+ annotated conversations | D | 7 | `simulations/` | 14 | todo |
| R-32 | Audit and compliance logging | A10 | 7 | `docs/compliance/audit-logging.md` | 14 | todo |
| R-33 | Risk assessment matrices | A11 | 7 | `docs/risk/risk-matrix.md` | 14 | todo |
| R-34 | Cross-reference audit, transfer to `@ZethetaIntern` | F | 7 | n/a | 15 | todo |
| R-35 | Graceful fallback when no relevant knowledge is found; gap handling | A2.3 | 3 | `docs/knowledge-base/retrieval-pipeline.md` sections 9-10, `docs/knowledge-base/entries/escalation.yaml`, `config/templates/support.yaml` (TPL-KB-GAP, TPL-KB-DEGRADE) | 7, 8, 13 | done |
| R-36 | KB maintenance workflow, regulatory fast-track, staleness alerts; access matrix by auth level; Level 3 boss (5 queries, 3+ entries) | A2.3, B | 3 | `docs/knowledge-base/maintenance-workflow.md`, `docs/knowledge-base/access-control-matrix.md`, `tests/kb/boss-level3.yaml`, `tests/kb/README.md` | 8 | done |
| R-37 | Guardrail registry: implementation type (rule, model, hybrid), enforcement point, action, immutability and false-positive target per guardrail; defence-in-depth diagram | A4, PLAN Phase 4 items 1-5 | 4 | `config/guardrails.yaml`, `diagrams/guardrail-layers.mmd` | 9 | done |
| R-38 | Fixed safety suite, minimum 200 cases, 100% pass before any update; every ESC-001..015 and every guardrail covered | A5.4 | 5 | `tests/safety-suite/manifest.yaml` (355 cases: 253 by reference [190 Day 10, 63 Day 12], 102 new; 291 on Day 11, 349 after the Day 11 audit fixes), `tests/safety-suite/manifest.lock.yaml`, `tests/safety-suite/*.yaml`, `tests/safety-suite/README.md`, `tests/safety-suite/validate_manifest.py` | 11 | done (specified, not run) |
| R-39 | Data pipeline: collection, redaction, consent, features, versioning, quality gates, right to deletion in training data | D (Day 11), A10.3, A11.3 | 5 | `docs/learning-pipeline/data-pipeline.md` | 11 | done |
| R-40 | A/B testing framework: traffic split, metric hierarchy, power, sequential testing, stopping rules (Scientist badge) | A8.4, D (Day 11), B3.2 | 5 | `docs/learning-pipeline/ab-testing.md` | 11 | done |
| R-41 | Experiment governance and approval workflow per configuration owner | A12.3, A12.2 | 5 | `docs/learning-pipeline/ab-testing.md` section 11 | 11, 13 | done (governed values in `config/parameters.yaml`) |
| R-42 | Immutable safety layer; safety-preserving update protocol: canary 1/5/25/100, regression, red team, HITL, circuit breaker, rollback | A5.4, A12.2 | 5 | `docs/learning-pipeline/safety-invariants.md`, `docs/guardrails/monitoring-dashboard.md` section 8, `config/guardrails.yaml` (GR-SYS-02, GR-SYS-03, GR-SYS-04) | 10, 11 | done |
| R-43 | Level 5 boss: simulated update, CSAT +0.3, no safety regression | B (Level 5) | 5 | `docs/learning-pipeline/boss-level5.md` | 11 | done (simulated worked example, not a measurement) |
| R-44 | Closed-loop improvement cycle (Detect, Diagnose, Design, Deploy, Validate, Document) | A8.4 | 6 | `docs/metrics/improvement-cycle.md`, `docs/learning-pipeline/overview.md` section 2 | 11, 12 | done |
| R-45 | Testable assertions for every prompt instruction; prompt version control with metadata | A12.2 | 6 | `config/system-prompt/layer*.md` (84 assertions), `config/system-prompt/manifest.yaml`, `config/system-prompt/README.md` section 7 | 13 | done |
| R-46 | Generation strategy per reply: template for safety-critical, LLM for conversational, hybrid with locked slots; persona and length | A2.4 | 6 | `config/templates/README.md` section 3, `docs/architecture/response-generation.md` | 3, 13 | done |
| R-47 | Primary-language coverage of customer-facing wording (English, Hindi, Hinglish) | A2.4 | 6 | `config/templates/*.yaml`, `config/templates/labels.yaml` | 13 | draft (not native-reviewed; no secondary-language text) |
| R-48 | Template, parameter and prompt validator | A12.2, A9.2 | 6 | `tests/templates/validate_templates.py`, `tests/templates/README.md` | 13 | done |
| R-49 | Layer 5 dynamic context as typed notice slots (promotions, status, known issues, temporary policy) | A12.1, A12.2 | 6 | `config/system-prompt/layer5-operational.md`, `TPL-SYS-NOTICE` | 13 | done |

Note: R-38: suite cases are specified, not executed (D-79).
