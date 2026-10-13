# Continuous Learning Pipeline: Overview

Brief refs: A5 (p.15: three feedback sources; A5.1 to A5.4), A8.4 (p.21: DETECT, DIAGNOSE, DESIGN, DEPLOY, VALIDATE, DOCUMENT), A8.5 (p.22: learning pipeline metrics on the weekly dashboard), A10.3 (p.28: deletion includes model training data), A11.1 (p.30: model drift P1), A11.3 (p.32: training data anonymised with consent), A12.1 to A12.3 (pp.33-34: six prompt layers, layered immutability, governed parameters), Part B Level 5 (p.39), Part D Day 11 (p.59). Component 12 in `docs/architecture/system-architecture.md`; contract in `docs/architecture/component-interfaces.md` row 12; failure modes 22 and 23 in `docs/architecture/failure-modes.md`. Registry: `config/guardrails.yaml` (GR-SYS-02, GR-SYS-03, GR-SYS-04).

**Status.** The brief fixes: three feedback sources, the four correction severities, the propagation timeline (immediate, daily, weekly), 50 reviews per supervisor per day, the five outcome classes, the 7/14/30-day windows, the 200-case safety suite, the 1% > 5% > 25% > 100% rollout, the circuit breaker, the immutable layer, the layer immutability rule and the A12.3 owners. Every other number in the learning-pipeline documents is a proposal and is marked as one. The system is specified, not built: no figure here is a measurement. Decisions: D-95 to D-114.

## 1. Purpose and documents

The pipeline turns what happens in conversations into reviewed, tested and reversible improvements, and it must do so "without degrading safety invariants" (brief task statement, p.1). It is an offline component: it never acts inside a customer turn.

| Document | Content |
|---|---|
| `overview.md` (this file) | the loop, what may be updated, cadence, update strategy, roles |
| `supervisor-corrections.md` | feedback source 1: sampling, review tool, taxonomy, agreement, workload (A5.1) |
| `csat-signals.md` | feedback source 2: check-ins, CSAT, implicit signals, bias correction, attribution (A5.2) |
| `outcome-tracking.md` | feedback source 3: follow-ups, repeat contact, outcome classes, retention (A5.3) |
| `data-pipeline.md` | collection, redaction, consent, features, dataset versions, quality gates, deletion |
| `ab-testing.md` | experiment design, power, sequential testing, governance (A8.4 DEPLOY, A12.3) |
| `safety-invariants.md` | immutable layer, fixed suite, gates G0 to G9, canary, circuit breaker (A5.4) |
| `boss-level5.md` | Level 5 boss: one simulated update traced through every gate |
| `diagrams/learning-loop.mmd` | flowchart of the loop and the gates |
| `tests/safety-suite/` | the fixed safety regression suite (356 cases) and its validator |

## 2. The loop end to end

The loop is the A8.4 improvement cycle with the A5.4 safety protocol placed inside DEPLOY.

| Step (A8.4) | What happens | Inputs | Output | Owner |
|---|---|---|---|---|
| 1. COLLECT | turn and conversation logs (A10), supervisor corrections, CSAT and implicit signals, outcome records are written to the learning store after redaction and consent filtering | Audit and Telemetry Bus, review tool, survey, ticket systems | versioned datasets | Data Engineering |
| 2. DETECT | dashboards surface anomalies within 15 minutes (A8.4); daily and weekly reports surface slow trends | metrics of `docs/metrics/` (Day 12) and `docs/guardrails/monitoring-dashboard.md` | finding with evidence | ML Team, CX Team |
| 3. DIAGNOSE | each finding is tied to one component: NLU accuracy, knowledge gap, generation quality, escalation logic (A8.4), plus retrieval, policy, tool, guardrail | correction `component` field, attribution (`csat-signals.md` section 7), outcome classes | root cause and candidate update class | finding owner |
| 4. DESIGN | a hypothesis is written and scored on impact, effort and risk (A8.4); the lowest update class that can fix it is chosen (section 4) | diagnosis | candidate with a pre-registration draft | class owner |
| 5. DEPLOY | gates G0 to G9: scope check, data gate, regression evaluation, fixed safety suite, red-team run, human approval, shadow run, canary 1% and 5%, A/B at 25%, 100% | candidate | released version or rejection | per gate, `safety-invariants.md` section 5 |
| 6. VALIDATE | post-deployment regression monitoring for 28 days (proposal); the circuit breaker stays armed | cohort metrics | confirmed or rolled back | ML Team, Risk owner |
| 7. DOCUMENT | experiment record, decision, what was learned, new suite cases | all of the above | entry in the experiment registry and the change log | experiment owner |

Two rules hold at every step. First, the pipeline proposes and humans dispose: nothing that changes customer-facing behaviour ships without the approval its owner requires (section 3). Second, the only automatic action the pipeline may take in production is a rollback to the previous version (`docs/guardrails/monitoring-dashboard.md` section 8).

### 2.1 When the three feedback sources disagree

Part D asks for feedback source integration. The sources often disagree about one conversation (a rating of 5 on a conversation a supervisor marked S1; a "resolved" close followed by a repeat contact). Precedence, highest first (D-159):

| Rank | Source | Why it outranks those below | What the lower-ranked signal is still used for |
|---|---|---|---|
| 1 | Supervisor verdict S1 (critical safety error), confirmed by second review | a safety breach is a fact about the reply, whatever the customer felt | the rating is kept; a satisfied customer after an unsafe reply is itself a finding (the unsafe behaviour pleases) |
| 2 | System-of-record outcome and matured outcome class (`outcome-tracking.md`): ticket closed, reversal credited, repeat contact, false-resolution | it records what happened to the issue | a high rating with a false-resolution is flagged, not averaged away |
| 3 | Supervisor verdicts S2, S3, S4 | a trained reader with the full trace | disagreement with the rating feeds attribution |
| 4 | Explicit customer feedback: CSAT rating, comment, check-in answer | the customer's own judgement of the experience | |
| 5 | Implicit signals | indirect | |
| 6 | Predicted signals (pCSAT, silent-dissatisfaction score) | a model output, never a measurement | triage only |

Rules: precedence decides the label used for diagnosis and for training or evaluation rows, not which data is kept; every signal stays on the record. A conflict between ranks 1 to 4 on one conversation is itself sampled for review (it enters the always-reviewed list within capacity). Precedence never applies across metrics: CSAT is still reported as CSAT, FCR as FCR. No rank can override a guardrail or the fixed suite.

## 3. What may and may not be updated

A12.2 states "Layers 0-2 immutable by learning pipeline. Only Layers 3-5 modifiable through continuous improvement; only Layer 5 without RC review." A5.4 requires "an immutable rule-based safety layer that cannot be modified by the learning pipeline". D-58 extends this to every registered guardrail.

### 3.1 Update classes, in order of preference (D-95)

| Class | Artefact | The pipeline may | Approval before release | A/B needed |
|---|---|---|---|---|
| U1 | Knowledge base entries (`docs/knowledge-base/`) | raise a change request with evidence; it never edits or publishes an entry | the entry's approval chain in `docs/knowledge-base/maintenance-workflow.md` | canary comparison of that workflow; a powered A/B only when the claim is a CSAT or FCR gain |
| U2 | Prompt layers 3 (dialogue), 4 (knowledge), 5 (operational) | draft a new version | layers 3 and 4: prompt owner plus Risk Committee review (A12.2); layer 5: operations owner, no Risk Committee review, typed notice slots only | layers 3 and 4: yes; layer 5: no (status notices), suite and lint only |
| U3 | A12.3 parameters and the registered thresholds marked proposable in `config/parameters.yaml` (D-171 as amended by D-197; a threshold of a guardrail or the rule layer, and the structure of an ESC trigger condition, stay excluded; the three A12.3 parameters inside ESC conditions stay proposable with bounds), inside their governed range | propose a value with evidence | the owner and change process of A12.3 (`ab-testing.md` section 11) | where A12.3 says so |
| U4 | NLU and retrieval models: intent, entity, sentiment, language ID, embedder, re-ranker, fusion weights | build a retrained candidate from a released dataset version | NLU Team lead; Risk Committee review if a CRITICAL intent slice moves | yes |
| U5 | Policy model: the learned ranking among actions the rules already allow; a change of the generation model version | build or evaluate a candidate | ML Team lead plus Risk Committee review (A12.3 treats `model_temperature` this way) | yes |

Order of preference means: a finding is fixed with the lowest class that can fix it. A wrong or unclear answer is first a KB question (U1), then a wording question (U2), then a threshold question (U3). Retraining (U4, U5) is used when the diagnosis names the model and no lower class resolves it. Reasons: lower classes are easier to review line by line, faster to roll back (epoch pointer or flag), cheaper to test, and carry less risk of side effects on unrelated intents. Each candidate records why the lower classes were not enough.

### 3.2 Excluded from the pipeline (read-only)

| # | Artefact | Why | Changed only by |
|---|---|---|---|
| X1 | Prompt layers 0 (identity), 1 (safety), 2 (regulatory) | A12.2 | Risk Committee (A12.1: quarterly or rebrand, annual, as regulations change) |
| X2 | The rule layer: redaction rules RED-01 to RED-07, validators, lexicons, allow and deny lists, the auth matrix in `config/intents.yaml`, tool scopes | A5.4, system-architecture.md section 5 | safety change control (`safety-invariants.md` section 9) |
| X3 | All 58 registered guardrails: rule, action, threshold, enforcement point, and the classifier weights of hybrid and model guardrails | D-58; every entry has `immutable: true` | safety change control |
| X4 | Registry parameters: `guardrail_strictness_level`, `session_timeout_minutes`, advice thresholds, false-positive bounds, adversarial limits | GR-SYS-03, A12.3 | Risk Committee |
| X5 | The escalation triggers ESC-001 to ESC-015 as conditions (brief A6; `config/escalation_rules.yaml`, Day 12) | escalation is "a critical safety component" (A6) | escalation owner with Risk Committee; `escalation_sentiment_threshold`, `max_conversation_turns` and `retrieval_confidence_threshold` follow A12.3 and stay proposable within the bounds and maximum steps of `config/parameters.yaml` (D-197, which amends D-171) |
| X6 | The fixed safety suite and its manifest, the circuit-breaker conditions, the containment levers, audit logs, consent and deletion records | they are the controls on the pipeline | their own owners; cases are add-only |

For an excluded artefact the pipeline may file an observation (for example "RED-04 redacted 14 postal codes this week") to the owner. It cannot submit a change, and a change proposal that names an excluded target is rejected at gate G0 and logged (GR-SYS-02, cases SS-LRN-01 to SS-LRN-06). Enforcement is structural: the pipeline's service identity has no write permission on these artefacts (`safety-invariants.md` section 2).

## 4. Cadence

A5.1 fixes the propagation timeline: "immediate for safety issues, batched daily for quality, weekly for style".

| Lane | Trigger | What "propagation" means | Target (proposal unless stated) |
|---|---|---|---|
| Safety, immediate (brief) | a correction of severity S1, a hard-zero counter above 0, a suite failure on production | an incident is opened under `docs/guardrails/incident-response-playbook.md`; a tighten-only lever contains it; the permanent fix goes through safety change control; a new suite case is written before the fix ships | acknowledge and contain per the playbook severity (SEV0 5 and 30 minutes, SEV1 15 minutes and 2 hours) |
| Quality, daily batch (brief) | S2 corrections, low-CSAT findings, false resolutions, KB gaps | the day's findings are triaged into change requests and labelled training rows; U1 and layer 5 changes can enter their gates the same day | batch cut at 06:00 local with the daily dashboard |
| Style, weekly (brief) | S3 corrections, tone and wording findings | grouped into one layer 3 candidate per week at most; released on the monthly layer 3 cycle of A12.1 after its A/B | weekly triage, monthly release |

The immediate lane never uses the pipeline to change a guardrail. Speed comes from the levers, which only tighten (D-86); learning from the incident is then slow and reviewed.

## 5. Update strategy

What is updated, how often, and whether training is incremental or full (Part D Day 11). Frequencies for layers come from A12.1; the rest are proposals (D-106).

| Class | Typical content | Frequency | Incremental or full | Rollback |
|---|---|---|---|---|
| U1 KB | clarity rewrites, new FAQ and troubleshooting entries, gap entries, translations | continuous; published per the KB workflow | incremental: one entry version; the index epoch is rebuilt | epoch pointer (`maintenance-workflow.md` section 3.6) |
| U2 layer 5 | system status, known issues, current promotions, temporary policy notices (A12.1) | daily or as needed (A12.1) | replace the notice slots | flag flip to the previous version |
| U2 layers 3 and 4 | tone, empathy patterns, confirmation wording, how retrieved knowledge and uncertainty are phrased | monthly (A12.1); weekly style findings are batched into it | full replacement of the layer text as a new version; the diff is reviewed | flag flip |
| U3 parameters | `intent_confidence_threshold`, `knowledge_retrieval_top_k`, `retrieval_confidence_threshold`, `model_temperature`, `max_conversation_turns`, `escalation_sentiment_threshold` | on evidence; at most one change per parameter per quarter (proposal) | one value | previous value |
| U4 NLU models | intent, entity, sentiment, language ID | every 21 days (proposal), and at once when the Model Drift Score reaches 0.05 (A8.3) or the taxonomy changes | full retrain from the base encoder on the current clean dataset; warm-start from the last checkpoint is allowed only when no deleted customer's rows are in that checkpoint's lineage | previous model version |
| Deletion-only rebuild (any trained model: NLU, retrieval, policy ranker, pCSAT) | the same code, hyper-parameters and base model as the model it replaces; training data minus tombstoned rows | every 14 days whenever a tombstone touches the model's lineage (proposal, D-157) | full rebuild from the base model; not a behaviour change, so it takes the short path G1, G2 equivalence, G3 and the 1% and 5% canary, with no A/B stage | the replaced model, but only until day 30 of its oldest tombstone; after that the fallback is the previous compliant model or the rules-only path |
| U4 retrieval models | embedder, re-ranker, fusion weights | quarterly at most (proposal); weights on evidence | full: a model change rebuilds the index as a new epoch | epoch pointer |
| U5 policy ranker | ordering among allowed actions | quarterly (proposal) | full retrain on logged data; shadow run before any exposure | rules-only fallback (FMEA 9) |
| U5 generation model version | provider model upgrade | when the provider changes it or on evidence | not trained by NexBank; treated as a new candidate through every gate | pinned previous version |

Why full retraining is the default for U4. A10.3 says deletion covers "derived data including model training data", and requests must be processed within 30 days. A checkpoint that was trained on a deleted customer's rows still carries their influence, so warm-starting from it would carry that influence forward. The models are small encoders, so the cost of a full rebuild is acceptable. Whether a trained model counts as "derived data" is a legal reading; the strict reading is taken as the default and flagged for the Data Protection lead (D-104).

The 21-day retrain cycle does not by itself meet the 30-day duty, because a retrained candidate that changes behaviour must pass gates G6 to G8: a request made just after a cut-off waits up to 21 days, then build, shadow, 1%, 5% and 14 days of A/B exposure put the CSAT final look near day 41 and the FCR final look near day 48. Deletion is therefore decoupled from improvement by the **deletion-only rebuild** in the table above (D-157). It changes the data and nothing else, so it needs no A/B test: it passes the data gate G1 (QG-07 confirms the tombstones are gone), an equivalence check at G2 (every headline metric on the frozen evaluation sets within 0.5 points of the model it replaces, no CRITICAL slice lower beyond noise, and prediction agreement of at least 98%; proposals), the fixed suite G3, owner sign-off, and the 1% and 5% canary stages with the breaker, then goes to 100%. Worst case: 14 days to the next cycle, 2 days to purge and build, 1 day for G1 to G3, 1 day at 1% and 2 days at 5%, so the old model is retired by day 20, with 10 days of margin (`data-pipeline.md` section 9). A rebuild that fails equivalence is treated as a behaviour change and cannot use the short path; the margin exists to absorb one failed attempt.

Limits on parallel change (proposal): one candidate in rollout per surface (KB epoch, prompt, parameters, NLU, retrieval, policy) and at most two surfaces in rollout at once, so that a metric movement can be attributed. Mutual exclusion rules are in `ab-testing.md` section 3. A deletion-only rebuild is exempt from the one-per-surface limit because it is not a candidate for a behaviour change: when an experiment is running on the same surface, the rebuild is applied to the model of each arm at the same time (as a safety fix would be), is recorded in the experiment log, and its canary runs inside each arm.

## 6. Roles

The brief names the bodies (A1.3) and the parameter owners (A12.3); named individuals are a dependency, as in `monitoring-dashboard.md` section 9.

| Role | Responsibility in the loop |
|---|---|
| Supervisors (A5.1) | review sampled conversations, label corrections, 50 reviews per day |
| Review leads | calibration sessions, adjudication of disagreements, reviewer outlier checks |
| Data Engineering | collection, redaction, consent filter, dataset versions, quality gates, deletion propagation |
| NLU Team (A12.3 owner) | U4 candidates; owner of `intent_confidence_threshold`, `knowledge_retrieval_top_k`, `retrieval_confidence_threshold` |
| ML Team (A12.3 owner) | U5 candidates, `model_temperature`, drift monitoring, circuit breaker operation |
| CX Team (A12.3 owner) | layer 3 drafts, CSAT programme, `escalation_sentiment_threshold` proposals |
| Product (A12.3 owner) | `max_conversation_turns`, layer 5 notices with operations |
| Security (A12.3 owner) | `session_timeout_minutes` (ceiling of 5, D-56), review of anything touching authentication |
| KB owners and KB Operations | U1 change requests through the KB workflow |
| Experiment statistician (independent of the candidate's author) | reviews the pre-registration, runs or checks the analysis |
| Customer Experience Board | approves `escalation_sentiment_threshold`; consulted on layer 3 tone |
| Risk Committee (CRO, Regulatory Compliance Manager, Information Security Officer) | reviews layers 3 and 4 and model changes; sole owner of X1 to X6; approves suite changes |
| Data Protection lead | consent model, deletion certificates, legal hold (D-87) |

Separation of duties: the author of a candidate is never its approver, its statistician or the reviewer of its red-team run. Supervisors who label data do not tune guardrails (D-89).

## 7. Pipeline health metrics

A8.5 asks the weekly dashboard for "training data volume, model version history, safety test pass rates". The pipeline also reports on itself.

| Metric | Definition | Target |
|---|---|---|
| Safety suite pass rate (DM-13) | cases passed divided by cases, per candidate and weekly on production | 100% (A5.4) |
| Model Drift Score | performance drift from baseline on the frozen evaluation set | below 0.05 (A8.3) |
| Training data volume | rows per dataset version, by source and language | reported; minimum rows per intent in `data-pipeline.md` QG-05 |
| Model and prompt version history | version, author, approval chain, deployment date, model version (A12.2) | complete for every release |
| Reviewer agreement | Cohen's kappa on double-reviewed items | 0.70 or more (proposal, `supervisor-corrections.md` section 6) |
| Finding-to-release time | by lane and class | reported |
| Candidates rejected per gate | count by gate G0 to G9 | reported; a gate that never rejects is reviewed |
| Rollbacks | count and cause | reported; each adds a suite or regression case |
| Deletion propagation time | request to last purge | 30 days or less (A10.3) |
| Share of improvements by class | U1 to U5 | reported; a falling U1 share is a warning that retraining is replacing content fixes |

## 8. Decisions and open items

Decisions made in this document: D-95 (update classes and exclusions), D-106 (cadence and full retraining by default), D-157 (deletion-only rebuild path), D-159 (precedence when the feedback sources disagree).

1. Named owners and deputies for every role are a dependency on NexBank (as D-84).
2. The 14-day deletion-only rebuild cycle depends on the legal reading of "derived data" (D-104, D-157); its equivalence tolerances are proposals to calibrate on the first rebuilds.
3. `config/parameters.yaml` holds the governed copy of the proposals in these documents.
