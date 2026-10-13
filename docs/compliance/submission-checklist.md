# Submission Checklist

Brief refs: Part D (pp.56-62) for the mandatory minimums and the daily deliverables, A9.2 (pp.24-25) for the AUTO-FAIL item and the anti-patterns, Part B Campaign Mode (pp.38-40) for the seven levels, Repository Structure (p.62). Decisions: D-01 (proxy for the "10 automatic failure conditions"), D-02 (proxy for the "7 deliverable requirements"). Check: `tests/compliance/validate_compliance.py` check 9 recomputes every count below from the repository.

**Status.** The system is specified, not built. A "met" status here means a count in the repository reaches the brief's number; it does not mean a test was executed. Counts were taken by script on the day this file was written (Day 14). The brief never lists its "10 automatic failure conditions" or its "7 deliverable requirements" (questions 1 and 2 of the draft in `docs/coordinator-questions.md`, not yet sent); sections 3 and 4 are the project's proxy lists and are not claimed to be the brief's lists. Items under `simulations/` were being written by another agent when the counts were taken and are marked "pending Day 14 simulations" with the count at that time.

## 1. How to read this file

| Column | Meaning |
|---|---|
| ID | MM = mandatory minimum or structure item; FC = proxy failure condition (D-01); DR = proxy deliverable requirement (D-02); DD = Part D Day 14-15 deliverable |
| Brief | Where the brief states the requirement (page numbers are those printed on the PDF) |
| Required | The brief's number |
| Repo evidence | File or files that hold the evidence |
| How to count | The rule the validator uses |
| Count now | The number recomputed by `python tests/compliance/validate_compliance.py` |
| Status | `met`; `not met`; `pending` (work still in progress, with the reason); `manual` (cannot be checked by script) |

## 2. Mandatory minimums and structure

| ID | Requirement | Brief | Required | Repo evidence | How to count | Count now | Status |
|---|---|---|---|---|---|---|---|
| MM-01 | Intent taxonomy with at least 25 intent categories | A3 title p.9; Part D Day 4-6 p.57; Level 2 p.38 | at least 25 | `config/intents.yaml`, `docs/intent-taxonomy/taxonomy.md` | entries under `intents:` in `config/intents.yaml` | 41 | met |
| MM-02 | Hierarchical structure: primary > secondary > tertiary for every intent | Part D Day 4-6 p.57 | 25 (all intents) | `config/intents.yaml` | intents with `primary`, `secondary` and `tertiary` all set | 41 | met |
| MM-03 | At least 10 sample utterances for every intent | Part D Day 4-6 p.57 | at least 10 for the smallest intent | `docs/intent-taxonomy/utterances.csv` | rows per `intent_id`; the figure is the smallest group (all intents present) | 13 | met |
| MM-04 | 250 or more sample utterances in total | Part D Day 4-6 p.57 | at least 250 | `docs/intent-taxonomy/utterances.csv` | data rows of the CSV | 551 | met |
| MM-05 | Disambiguation rules for the 6 overlapping intent pairs | Part D Day 4-6 p.57 | 6 | `diagrams/disambiguation-01-txn-status-vs-dispute.mmd` and five more, `docs/intent-taxonomy/disambiguation.md` | files `diagrams/disambiguation-*.mmd` | 6 | met |
| MM-06 | At least 50 sample knowledge base entries | Part D Day 7-8 p.58; Level 3 p.38 | at least 50 | `docs/knowledge-base/entries/*.yaml` | items under `entries:` in the files of `docs/knowledge-base/entries/` | 77 | met |
| MM-07 | At least 50 adversarial test cases across all guardrail categories | Part D Day 9-10 p.59 | at least 50 | `tests/adversarial/*.yaml` | items under `cases:` in the six files of `tests/adversarial/` | 62 | met |
| MM-08 | Defences and cases for all 6 adversarial attack vectors | Part D Day 9-10 p.59; A4.4 | 6 | `tests/adversarial/*.yaml`, `docs/guardrails/adversarial-defences.md` | distinct `vector` values of the six adversarial files | 6 | met |
| MM-09 | Level 4 boss: 20 adversarial attack scenarios across all 6 vectors | Level 4 p.39 | at least 20 | `tests/adversarial/*.yaml` | cases with `boss: true` | 27 | met |
| MM-10 | All 8 mandatory account security guardrails | A4.2 p.12; Part D Day 9-10 p.58 | 8 | `config/guardrails.yaml`, `docs/guardrails/account-security.md` | guardrail IDs GR-SEC-R1 to GR-SEC-R8 in the registry | 8 | met |
| MM-11 | At least 10 escalation trigger conditions | A6 p.16; overview p.1 | at least 10 | `config/escalation_rules.yaml`, `docs/escalation/triggers.md` | items under `triggers:` | 15 | met |
| MM-12 | The 15 trigger conditions of A6, with priority and SLA | A6 title p.16; Part D Day 12-13 p.60 | 15 | `config/escalation_rules.yaml`, `tests/escalation/validate_escalation.py` | items under `triggers:` | 15 | met |
| MM-13 | Handoff protocol with the 8-element context package | Part D Day 12-13 p.60 | 8 | `config/escalation_rules.yaml`, `docs/escalation/routing-and-handoff.md` | items under `handoff_package.elements` | 8 | met |
| MM-14 | At least 15 prompt templates with trigger conditions and safety annotations | Part D Day 12-13 p.60 | at least 15 | `config/templates/*.yaml`, `tests/templates/validate_templates.py` | items under `templates:` in the template files | 73 | met |
| MM-15 | Fixed safety test suite of at least 200 cases | A5.4 p.15 | at least 200 | `tests/safety-suite/manifest.yaml`, `tests/safety-suite/validate_manifest.py` | items under `cases:` in the manifest | 356 | met |
| MM-16 | System prompt in 6 layers with immutability rules | A12.1 p.33; Part D Day 12-13 p.60 | 6 | `config/system-prompt/layer0-identity.md` to `config/system-prompt/layer5-operational.md`, `config/system-prompt/manifest.yaml` | files `layer[0-5]-*.md` | 6 | met |
| MM-17 | High-level architecture with at least 8 components | Part D Day 1-3 p.57; Level 1 p.38 | at least 8 | `docs/architecture/system-architecture.md`, `docs/architecture/component-interfaces.md` | numbered rows of the component table in `component-interfaces.md` | 12 | met |
| MM-18 | Failure mode analysis for each component with fallback strategies | Part D Day 1-3 p.57 | at least 12 rows (one per component) | `docs/architecture/failure-modes.md` | numbered rows of the FMEA table (the 12 components are all covered by the table) | 24 | met |
| MM-19 | Scalability specification at 1x, 10x and 100x load | Part D Day 1-3 p.57 | 3 | `docs/architecture/latency-scalability-cost.md` | rows 1x, 10x, 100x of the scale table | 3 | met |
| MM-20 | Latency budget with end-to-end response time under 3 s | Part D Day 1-3 p.57 | 1 (stated) | `docs/architecture/latency-scalability-cost.md` | search for the 3 s budget; 1 if present | 1 | met |
| MM-21 | Knowledge retrieval within 200 ms | Overview p.1; Level 3 p.38 | 1 (stated) | `docs/knowledge-base/retrieval-pipeline.md` | search for `200 ms`; 1 if present | 1 | met |
| MM-22 | The 5 mandatory conversation design patterns | A9.1 p.23; Part D Day 14-15 p.60 | 5 | `docs/architecture/conversation-design.md` | rows P1 to P5 | 5 | met |
| MM-23 | The 8 anti-patterns, none in any conversation | A9.2 p.24; Part D Day 14-15 p.60 | 8 | `docs/architecture/conversation-design.md` | rows AP1 to AP8 (the check on the 32 conversations is `simulations/pattern-audit.md`) | 8 | met |
| MM-24 | 3 dashboards: real-time operations, daily performance, weekly strategic | Part D Day 12-13 p.60 | 3 | `docs/metrics/dashboards.md` | the three dashboard sections | 3 | met |
| MM-25 | Closed-loop improvement cycle with 6 stages (Detect, Diagnose, Design, Deploy, Validate, Document) | A8.4 p.21; Part D Day 12-13 p.60 | 6 | `docs/metrics/improvement-cycle.md` | stage rows of the cycle table | 6 | met |
| MM-26 | Learning pipeline integrating 3 feedback sources | Level 5 p.39 | 3 | `docs/learning-pipeline/supervisor-corrections.md`, `docs/learning-pipeline/csat-signals.md`, `docs/learning-pipeline/outcome-tracking.md` | the three source documents | 3 | met |
| MM-27 | The six A13.2 test personas used in the test cases | A13.2 p.36 | 6 | `tests/adversarial/*.yaml`, `tests/guardrails/*.yaml` | distinct persona names among Priya, Rajesh, Meera, Arjun, Sunita, Vikram | 6 | met |
| MM-28 | Dialogue state machine specification (states, transitions, guards) | Part D Day 1-3 p.57 | 2 (document and diagram) | `docs/architecture/dialogue-management.md`, `diagrams/dialogue-state-machine.mmd` | the two files exist | 2 | met |
| MM-29 | Repository follows the mandatory structure (README, 7 docs folders, diagrams, simulations, tests, config, CHANGELOG) | Repository Structure p.62 | 13 | repository root | paths present among the 13 listed on p.62 | 13 | met |
| MM-30 | CHANGELOG with daily entries over the 15-day period, each with date, tasks, decisions, challenges, open questions, plan; the brief also writes "Complete CHANGELOG.md with all 7 daily entries" (p.61) and "daily progress over the 15-day period" (p.62), and D-03 reads the 7 as a floor | Part D Day 14-15 p.61; Daily CHANGELOG Requirements p.61 | 15 (one per day) | `CHANGELOG.md` | headings `## Day N` in `CHANGELOG.md` | 14 | pending Day 15 CHANGELOG entry (Day 14 is written; Day 15 is not written yet) |
| MM-31 | At least 20 annotated sample conversations | Part D Day 14-15 p.60; case studies p.56 | at least 20 | `simulations/conv-*.md` | files `simulations/conv-*.md` | 32 | met |
| MM-32 | Level 2 boss: 10 ambiguous messages disambiguated | Level 2 p.38 | 10 | `tests/nlu/boss-level2.yaml` | items under `cases:` | 10 | met |
| MM-33 | Level 3 boss: 5 queries needing synthesis from 3 or more entries | Level 3 p.38 | 5 | `tests/kb/boss-level3.yaml` | items under `cases:` | 5 | met |
| MM-34 | Level 6 boss: 10 edge-case escalation conversations | Level 6 p.39 | 10 | `tests/escalation/boss-level6.yaml` | items under `cases:` | 10 | met |
| MM-35 | Level 1 boss: conversation with 12 topic switches in 20 turns | Level 1 p.38 | 1 (document) | `docs/architecture/boss-trace.md` | the document exists; turn and switch counts are checked by reading it | 1 | met |
| MM-36 | Level 5 boss: simulated model update with CSAT +0.3 and no safety regression | Level 5 p.39 | 1 (document) | `docs/learning-pipeline/boss-level5.md` | the document exists (a worked example, not a measurement) | 1 | met |

Summary: 35 of 36 rows met, 1 pending, 0 not met.

Extra items found under the structure rule (MM-29). The brief's folder list (p.62) has no `docs/compliance/` or `docs/risk/`; the audit logging specification and the risk matrix, which Part D asks for on Days 14-15, are filed there, together with `tests/compliance/` and `config/audit_log.schema.json`. `graphify-out/` at the root is tooling output. Whether extra folders are acceptable under "this exact structure" is an open question (section 6, item 6).

## 3. Proxy list for the "10 automatic failure conditions" (D-01)

D-01 defines the proxy as the AUTO-FAIL item and the anti-pattern table of A9.2, plus all mandatory minimums. The rows below make it ten items so that it can be ticked off: the one AUTO-FAIL item, the eight anti-patterns (each carries a penalty in the brief, so each is treated as a condition to avoid), and one row that is true only when no mandatory minimum of section 2 fails. This is the project's reading. If the coordinator supplies the real list (question 1), replace this section.

| ID | Condition | Brief | Required | Repo evidence | How to count | Count now | Status |
|---|---|---|---|---|---|---|---|
| FC-01 | AUTO-FAIL: stating a non-existent product benefit or an incorrect interest rate | A9.2 table p.25 (marked AUTO-FAIL, Safety-Critical) | at least 1 trap case | GR-OUT-01, GR-OUT-03, GR-REG-18 in `config/guardrails.yaml`; `tests/safety-suite/hallucination-traps.yaml`; `docs/guardrails/output-safety-layer.md` | cases with suite category `hallucination_trap` in the manifest | 21 | met |
| FC-02 | Anti-pattern AP1: Robotic Loop (-20) | A9.2 table pp.24-25; Part D Day 14-15 p.60 | 1 documented control | row AP1 of `docs/architecture/conversation-design.md` (controls at prompt layer, template, platform rule and output check) | row AP1 present with all columns filled; occurrences in conversations: pending Day 14 simulations | 1 | met (documented); occurrence check pending Day 14 simulations |
| FC-03 | Anti-pattern AP2: Information Dump (-10) | A9.2 table pp.24-25; Part D Day 14-15 p.60 | 1 documented control | row AP2 of `docs/architecture/conversation-design.md` (controls at prompt layer, template, platform rule and output check) | row AP2 present with all columns filled; occurrences in conversations: pending Day 14 simulations | 1 | met (documented); occurrence check pending Day 14 simulations |
| FC-04 | Anti-pattern AP3: False Confidence (-30) | A9.2 table pp.24-25; Part D Day 14-15 p.60 | 1 documented control | row AP3 of `docs/architecture/conversation-design.md` (controls at prompt layer, template, platform rule and output check) | row AP3 present with all columns filled; occurrences in conversations: pending Day 14 simulations | 1 | met (documented); occurrence check pending Day 14 simulations |
| FC-05 | Anti-pattern AP4: Premature Escalation (-10) | A9.2 table pp.24-25; Part D Day 14-15 p.60 | 1 documented control | row AP4 of `docs/architecture/conversation-design.md` (controls at prompt layer, template, platform rule and output check) | row AP4 present with all columns filled; occurrences in conversations: pending Day 14 simulations | 1 | met (documented); occurrence check pending Day 14 simulations |
| FC-06 | Anti-pattern AP5: Empathy Bypass (-20) | A9.2 table pp.24-25; Part D Day 14-15 p.60 | 1 documented control | row AP5 of `docs/architecture/conversation-design.md` (controls at prompt layer, template, platform rule and output check) | row AP5 present with all columns filled; occurrences in conversations: pending Day 14 simulations | 1 | met (documented); occurrence check pending Day 14 simulations |
| FC-07 | Anti-pattern AP6: Authentication Theatre (-10) | A9.2 table pp.24-25; Part D Day 14-15 p.60 | 1 documented control | row AP6 of `docs/architecture/conversation-design.md` (controls at prompt layer, template, platform rule and output check) | row AP6 present with all columns filled; occurrences in conversations: pending Day 14 simulations | 1 | met (documented); occurrence check pending Day 14 simulations |
| FC-08 | Anti-pattern AP7: Sycophantic Recovery (-10) | A9.2 table pp.24-25; Part D Day 14-15 p.60 | 1 documented control | row AP7 of `docs/architecture/conversation-design.md` (controls at prompt layer, template, platform rule and output check) | row AP7 present with all columns filled; occurrences in conversations: pending Day 14 simulations | 1 | met (documented); occurrence check pending Day 14 simulations |
| FC-09 | Anti-pattern AP8: Knowledge Hallucination (AUTO-FAIL) | A9.2 table pp.24-25; Part D Day 14-15 p.60 | 1 documented control | row AP8 of `docs/architecture/conversation-design.md` (controls at prompt layer, template, platform rule and output check) | row AP8 present with all columns filled; occurrences in conversations: pending Day 14 simulations | 1 | met (documented); occurrence check pending Day 14 simulations |
| FC-10 | Any mandatory minimum of section 2 not met (counting rows MM-01 to MM-36 without a pending status) | D-01; Part D Day 14-15 p.61 | 0 not met | section 2 of this file | rows of section 2 whose status is `not met` | 0 | met for the rows checked; MM-30 pending |

## 4. Proxy list for the "7 deliverable requirements" (D-02)

D-02 reads the seven requirements as the seven campaign levels of Part B: Architecture, NLU, Knowledge Base, Guardrails, Learning, Escalation and CSAT, Integration. Each row lists the files that carry the deliverable. The count is how many of those files exist; content is covered by the validators in section 7.

| ID | Deliverable requirement | Brief | Required | Repo evidence | How to count | Count now | Status |
|---|---|---|---|---|---|---|---|
| DR-1 | Architecture and dialogue management (Level 1) | Level 1 p.38; Part D Day 1-3 p.57 | 9 files | `docs/architecture/system-architecture.md`, `docs/architecture/component-interfaces.md`, `docs/architecture/dialogue-management.md`, `docs/architecture/failure-modes.md` and 5 more (listed in `tests/compliance/validate_compliance.py`, `DR_FILES`) | existing files among the 9 listed | 9 of 9 files | met |
| DR-2 | Intent taxonomy and NLU (Level 2) | Level 2 p.38; Part D Day 4-6 pp.57-58 | 10 files | `config/intents.yaml`, `config/entities.yaml`, `docs/intent-taxonomy/taxonomy.md`, `docs/intent-taxonomy/entities.md` and 6 more (listed in `tests/compliance/validate_compliance.py`, `DR_FILES`) | existing files among the 10 listed | 10 of 10 files | met |
| DR-3 | Knowledge base and retrieval (Level 3) | Level 3 p.38; Part D Day 7-8 p.58 | 9 files | `docs/knowledge-base/kb-schema.md`, `docs/knowledge-base/retrieval-pipeline.md`, `docs/knowledge-base/maintenance-workflow.md`, `docs/knowledge-base/access-control-matrix.md` and 5 more (listed in `tests/compliance/validate_compliance.py`, `DR_FILES`) | existing files among the 9 listed | 9 of 9 files | met |
| DR-4 | Guardrails and safety (Level 4) | Level 4 p.39; Part D Day 9-10 pp.58-59 | 20 files | `docs/guardrails/account-security.md`, `docs/guardrails/adversarial-defences.md`, `docs/guardrails/financial-advice.md`, `docs/guardrails/incident-response-playbook.md` and 16 more (listed in `tests/compliance/validate_compliance.py`, `DR_FILES`) | existing files among the 20 listed | 20 of 20 files | met |
| DR-5 | Continuous learning pipeline (Level 5) | Level 5 p.39; Part D Day 11 p.59 | 11 files | `docs/learning-pipeline/overview.md`, `docs/learning-pipeline/supervisor-corrections.md`, `docs/learning-pipeline/csat-signals.md`, `docs/learning-pipeline/outcome-tracking.md` and 7 more (listed in `tests/compliance/validate_compliance.py`, `DR_FILES`) | existing files among the 11 listed | 11 of 11 files | met |
| DR-6 | Escalation, satisfaction and system prompt (Level 6) | Level 6 p.39; Part D Day 12-13 p.60 | 14 files | `docs/escalation/triggers.md`, `docs/escalation/routing-and-handoff.md`, `docs/escalation/queue-management.md`, `config/escalation_rules.yaml` and 10 more (listed in `tests/compliance/validate_compliance.py`, `DR_FILES`) | existing files among the 14 listed | 14 of 14 files | met |
| DR-7 | Integration: conversations, audit logging, risk matrix, final documentation (Level 7) | Level 7 p.40; Part D Day 14-15 pp.60-61 | 11 files | `docs/compliance/audit-logging.md`, `config/audit_log.schema.json`, `diagrams/audit-log-flow.mmd`, `docs/risk/risk-matrix.md` and 7 more (listed in `tests/compliance/validate_compliance.py`, `DR_FILES`) | existing files among the 11 listed | 11 of 11 files | met (files present: 11 of 11; `simulations/` holds 30 conversations, 20 required) |

## 5. Part D Day 14-15 deliverables

| ID | Deliverable | Brief | Required | Repo evidence | How to count | Count now | Status |
|---|---|---|---|---|---|---|---|
| DD-01 | 20+ sample conversations with turns, intents, entities, guardrail activations and decision points | Part D Day 14-15 p.60 | at least 20 | `simulations/` | see MM-31 | 32 | met |
| DD-02 | Level 7 boss: a 25-turn journey over 3 intents with authentication, guardrail activation, sentiment recovery and escalation decision | Level 7 p.40 | 1 conversation | `simulations/conv-30-level-7-integration-journey.md` | read the conversation | 1 | met |
| DD-03 | Audit and compliance logging specification (interaction-level and turn-level schemas) | Part D Day 14-15 p.61; A10 pp.27-29 | 11 conversation fields, 14 turn fields | `docs/compliance/audit-logging.md`, `config/audit_log.schema.json`, `tests/compliance/examples/` | check 3 and 4 of the validator | 25 | met |
| DD-04 | Risk assessment matrix (technical, business, ethical) | Part D Day 14-15 p.61; A11 pp.30-32 | 3 matrices | `docs/risk/risk-matrix.md`, `docs/risk/fairness-testing.md` | check 6 of the validator | 3 | met |
| DD-05 | Complete CHANGELOG | Part D Day 14-15 p.61 | entries for every day | `CHANGELOG.md` | see MM-30 | 14 | pending Day 15 CHANGELOG entry |
| DD-06 | Final documentation polish and cross-reference validation | Part D Day 14-15 p.60 | none stated | all validators in section 7 | run section 7 | 0 | pending Day 15 |
| DD-07 | Verify against all 10 automatic failure conditions | Part D Day 14-15 p.61 | list not given | sections 3 and 4 of this file | run the validator | 0 | pending Day 15 (proxy lists written) |
| DD-08 | Transfer the repository to @ZethetaIntern | Part D Day 14-15 p.61 | done | n/a | not checkable by script | 0 | manual (Day 15) |

## 6. Open sign-offs and launch blockers

These are items that the repository cannot close by itself. They are collected from the Day 13 and Day 14 open questions and from the dependency lists of `docs/compliance/audit-logging.md` section 17 and `docs/guardrails/incident-response-playbook.md`. `docs/risk/risk-matrix.md` RISK-B-10 points here.

| # | Item | Owner | Source |
|---|---|---|---|
| 1 | Coordinator answers to question 1 (the real list of 10 failure conditions) and question 2 (the real list of 7 deliverable requirements) of the draft; sections 3 and 4 are proxies until then | Project author, coordinator | D-01, D-02, `docs/coordinator-questions.md` |
| 2 | Native review of Hindi and Hinglish wording; no secondary-language template text exists; KB facts are English only | Head of Customer Experience; Risk Committee for safety text | D-145, RISK-E-16 |
| 3 | Review of the crisis template by the Crisis Response team and a clinical adviser; no helpline number is held | Risk Committee | D-146 |
| 4 | Risk Committee review of prompt layers 0 to 4 and of the guardrail registry; legal review of layer 2; no committee has reviewed any layer | Risk Committee, Regulatory Compliance Manager | RISK-B-10, INV-12 |
| 5 | Legal reading of retention against deletion and of "derived data"; residual-record rule | Data Protection lead, Legal, Regulatory Compliance Manager | AL-D1, D-87, D-157, D-183 |
| 6 | Whether the extra folders `docs/compliance/` and `docs/risk/` satisfy the "exact structure" of p.62, or the two areas should move into an existing folder | Project author, coordinator | MM-29 |
| 7 | Report formats, recipients and due dates for the four A10.3 reports; the content of the Banking Ombudsman requirements | Chief Risk Officer | AL-D2, G-04 |
| 8 | Encryption mode, meaning of quarterly rotation, HSM and key ceremony | Information Security Officer | AL-D3, G-07 |
| 9 | Named holders of the roles in the access matrix, the break-glass approvers and the incident roles | Chief Risk Officer | AL-D8, IR-D1 |
| 10 | Legal review and insurance for AI-caused customer loss (the brief names both as mitigations) | Chief Risk Officer | RISK-B-04, IR-D5 |
| 11 | Risk Committee sign-off of the after-hours deviation and a decision on the 60 percent staffing aim | Chief Risk Officer; CTO | RISK-B-05, RISK-B-06, D-163, D-130 |
| 12 | Agreement of the restricted fairness view (data source, cell floor, access list) and of the fairness margins | Risk Committee, Data Protection lead | D-188, `docs/risk/fairness-testing.md` section 2.1 |
| 13 | Protective actions proceeding without a bus acknowledgement (class H2) | Risk Committee | D-185 |

## 7. Re-running the checks

| Command (from the repository root) | What it covers |
|---|---|
| `python tests/compliance/validate_compliance.py` | This file's counts, the audit log schema and examples, the risk register, the fairness pairs and the numbers quoted in the compliance and risk documents |
| `python tests/kb/validate_kb_entries.py` | KB entries (MM-06) |
| `python tests/escalation/validate_escalation.py` | Triggers, queues, Level 6 boss (MM-11 to MM-13, MM-34) |
| `python tests/safety-suite/validate_manifest.py` | The fixed suite (MM-15) |
| `python tests/templates/validate_templates.py` | Templates and prompt layers (MM-14, MM-16) |
| the checks under `tests/simulations/` | Written with `simulations/` by the Day 14 simulations work; not covered by this file |

Counts change when files change. Run the validator after any edit and update the "Count now" column; the validator fails when a number differs from the repository.

## 8. Decisions

D-190 covers the production of this file (counts by script, proxy lists, status vocabulary). It adds no rule to the product; it records how the submission is checked.
