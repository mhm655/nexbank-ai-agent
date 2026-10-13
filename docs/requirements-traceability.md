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
| R-27 | 15 escalation triggers (ESC-001..015), precedence, routing, 8-element handoff, queue management, de-escalation, escalation quality metrics; Level 6 boss (10 edge cases) | A6, B, D | 6 | `docs/escalation/triggers.md`, `docs/escalation/routing-and-handoff.md`, `docs/escalation/queue-management.md`, `config/escalation_rules.yaml`, `diagrams/escalation-routing.mmd`, `tests/escalation/` (64 cases, validator), `config/templates/escalation.yaml` | 12, 13 | done |
| R-28 | KPIs (leading, lagging, operational), improvement cycle, 3 dashboards | A8, A1.4 | 6 | `docs/metrics/kpi-framework.md`, `docs/metrics/improvement-cycle.md`, `docs/metrics/dashboards.md` | 12 | done |
| R-29 | Conversation design: 5 mandatory patterns, 8 anti-patterns with penalties, brand tone | A9 | 6 | `docs/architecture/conversation-design.md`, `config/system-prompt/layer3-dialogue.md`, `config/templates/` (A9 codes per template) | 13 | done (Hindi and Hinglish wording not native-reviewed) |
| R-30 | 6-layer system prompt with immutability rules, 8 governed parameters, 15+ prompt templates with trigger conditions and safety annotations | A12, D (Day 12-13) | 6 | `config/system-prompt/` (6 layers, README, manifest), `config/parameters.yaml`, `config/templates/` (73 templates, 147 variants), `tests/templates/prompt-assertions.yaml`, `tests/templates/wording_lint.yaml` | 13 | done (no committee review; specified not run) |
| R-31 | 20+ annotated conversations | D (Day 14-15), B (Level 7) | 7 | `simulations/` (32 conversations, 318 messages, `INDEX.md`, `pattern-audit.md`) | 14 | done (designed examples, not run; Hindi, Hinglish and Gujarati wording not native-reviewed) |
| R-32 | Audit and compliance logging: interaction-level (A10.1, 11 fields) and turn-level (A10.2, 14 fields) schemas, retention, field masking, event taxonomy, 16 audit queries, answer-to-version traceability | A10.1, A10.2, A11.3 | 7 | `docs/compliance/audit-logging.md` sections 1-6, 13, 14, `config/audit_log.schema.json`, `tests/compliance/examples/`, `diagrams/audit-log-flow.mmd` | 14 | done (specified, not run) |
| R-33 | Risk assessment matrices: technical, business, ethical; heat map, top 10 residual, appetite | A11.1, A11.2, A11.3 | 7 | `docs/risk/risk-matrix.md` (55 risks: RISK-T-18, RISK-T-19, RISK-E-23 added on the Day 14 audit) | 14 | done (scores are design-time judgements) |
| R-34 | Cross-reference audit, transfer to `@ZethetaIntern` | F | 7 | n/a | 15 | todo |
| R-35 | Graceful fallback when no relevant knowledge is found; gap handling | A2.3 | 3 | `docs/knowledge-base/retrieval-pipeline.md` sections 9-10, `docs/knowledge-base/entries/escalation.yaml`, `config/templates/support.yaml` (TPL-KB-GAP, TPL-KB-DEGRADE) | 7, 8, 13 | done |
| R-36 | KB maintenance workflow, regulatory fast-track, staleness alerts; access matrix by auth level; Level 3 boss (5 queries, 3+ entries) | A2.3, B | 3 | `docs/knowledge-base/maintenance-workflow.md`, `docs/knowledge-base/access-control-matrix.md`, `tests/kb/boss-level3.yaml`, `tests/kb/README.md` | 8 | done |
| R-37 | Guardrail registry: implementation type (rule, model, hybrid), enforcement point, action, immutability and false-positive target per guardrail; defence-in-depth diagram | A4, PLAN Phase 4 items 1-5 | 4 | `config/guardrails.yaml`, `diagrams/guardrail-layers.mmd` | 9 | done |
| R-38 | Fixed safety suite, minimum 200 cases, 100% pass before any update; every ESC-001..015 and every guardrail covered | A5.4 | 5 | `tests/safety-suite/manifest.yaml` (356 cases: 254 by reference [190 Day 10, 64 Day 12], 102 new; 291 on Day 11, 349 after the Day 11 audit fixes), `tests/safety-suite/manifest.lock.yaml`, `tests/safety-suite/*.yaml`, `tests/safety-suite/README.md`, `tests/safety-suite/validate_manifest.py` | 11 | done (specified, not run) |
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
| R-50 | Level 7 boss: 25-turn journey across 3 intents with authentication, guardrail activation, sentiment recovery and escalation decision | B (Level 7) | 7 | `simulations/conv-30-level-7-integration-journey.md` | 14 | done (designed, not run) |
| R-51 | All six test personas exercised | A13.2 | 7 | `simulations/INDEX.md` section 4.2 | 14 | done |
| R-52 | Each adversarial vector demonstrated end to end | A4.4 | 7 | `simulations/conv-04`, `conv-13` (denial of service), `conv-14` (identity spoofing) | 14 | done |
| R-53 | Information-versus-advice boundary in each A4.1 category | A4.1 | 7 | `simulations/conv-03`, `conv-08`, `conv-10`, `conv-16`, `conv-30` | 14 | done |
| R-54 | Escalation triggers demonstrated in conversation | A6 | 7 | `simulations/INDEX.md` sections 4.4, 4.5 | 14 | done for 15 of 15 (ESC-010 fires in conv-32 on message 16, not on message 15) |
| R-55 | Five patterns applied and eight anti-patterns absent, per conversation, with evidence; AUTO-FAIL figure sweep | A9.1, A9.2, Part D Day 14-15 | 7 | `simulations/pattern-audit.md`, the self-audit block of each conversation | 14 | done |
| R-56 | Secondary-language fallback ladder demonstrated | A2.4 (multi-language support), D-22 | 7 | `simulations/conv-29-rajesh-gujarati-fallback-ladder.md` | 14 | draft (no reviewed Gujarati template; replies in Hindi) |
| R-57 | Simulation validator | Part D Day 14-15 | 7 | `tests/simulations/validate_simulations.py`, `tests/simulations/README.md` | 14 | done |
| R-58 | Log integrity, encryption and key management, access control matrix with break-glass, retention schedule | A10.3, A1.3 | 7 | `docs/compliance/audit-logging.md` sections 7-10 | 14 | done (HSM, mode and role holders are dependencies AL-D3, AL-D8) |
| R-59 | Deletion workflow within 30 days incl. backups and training data; deletion certificate; legal hold | A10.3, A11.3 | 7 | `docs/compliance/audit-logging.md` section 11 | 14 | draft (legal reading AL-D1 open) |
| R-60 | Regulatory reporting: monthly RBI summary, quarterly complaint analysis, annual AI audit report, 48-hour ad-hoc queries | A10.3 | 7 | `docs/compliance/audit-logging.md` section 12 | 14 | draft (formats and recipients AL-D2 open) |
| R-61 | Fail-closed behaviour when the audit bus is down; enhanced logging for payment-related conversations | A4.3, A10.3 | 7 | `docs/compliance/audit-logging.md` sections 15-17 | 14 | done (class H2 needs Risk Committee) |
| R-62 | Statistical fairness testing, counterfactual pairs, transparency, accountability chain, privacy purposes | A11.3 | 7 | `docs/risk/fairness-testing.md`, `tests/compliance/fairness-pairs.yaml` (15 pairs, 30 cases, incl. FAIR-15) | 14 | done (pairs specified, not run) |
| R-63 | Submission checklist: mandatory minimums, proxy lists for the 10 failure conditions and 7 deliverable requirements | Part D, A9.2, D-01, D-02 | 7 | `docs/compliance/submission-checklist.md` | 14 | draft (simulations and CHANGELOG pending) |
| R-64 | Compliance and risk validator with seeded-defect evidence | A10, A11 | 7 | `tests/compliance/validate_compliance.py`, `tests/compliance/README.md` | 14 | done |

Note: R-38: suite cases are specified, not executed (D-79).
