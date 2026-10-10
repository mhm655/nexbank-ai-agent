# Learning Data Pipeline

Brief refs: Part D Day 11 (p.59: "data pipeline: collection, preprocessing, feature engineering, versioning, quality gates, privacy"), A10.1 and A10.2 (p.27-28: conversation and turn log schemas, retention), A10.3 (p.28: encryption, least privilege, "Customer right-to-deletion requests processed within 30 days", "Deletion includes all copies, backups, and derived data including model training data", "Deletion certificates generated and stored for regulatory proof"), A11.3 (p.32: "Collect only minimum information necessary", "Training data must be anonymised with customer consent", "Never infer or store sensitive attributes (religion, politics, health)", "Cross-customer data leakage must be architecturally impossible"), A12.2 (p.34: version control with metadata), Regulatory Reference Summary (p.70: DPDP Act 2023, "consent management, data localisation"; IT Rules 2011). Related: `config/entities.yaml` (RED-01 to RED-07, sensitivity tiers), GR-REG-13, regulatory-mapping rows M-21 and M-25 and dependency G-05, D-87 (legal hold), `overview.md`.

**Status.** The brief fixes: the log schemas and retention periods, encryption and access rules, the 30-day deletion duty with its scope and certificates, consent and anonymisation for training data, and the ban on sensitive-attribute inference. Consent mechanics, the gate thresholds, the dataset layout and the deletion timeline inside the 30 days are proposals (D-104, D-105). The brief does not describe the DPDP Act's mechanics beyond the summary line; nothing here quotes the Act.

## 1. Principles

1. **Minimum data.** The pipeline receives only what a stated purpose needs (A11.3). Raw identifiers never enter it.
2. **Consent before use.** A conversation is used for model training only with a positive, current consent record. Service delivery, audit logging and safety monitoring do not depend on that consent; training does.
3. **Redact twice.** Redaction happens at the Input Guard before NLU (Day 4) and again at dataset build, because a rule that was fixed later must also clean older data.
4. **Everything is versioned and traceable.** Every dataset, label set, feature definition and model can be traced to its inputs (A11.3 accountability: "Every AI decision must be traceable to specific inputs, model versions, and KB entries").
5. **Deletion reaches everything derived.** A deleted customer leaves datasets, features, backups and, by retraining, models.
6. **No gate, no release.** A dataset version that fails a quality gate is not published and cannot be used by a candidate (gate G1 of `safety-invariants.md`).

## 2. Stages

```
sources -> collect -> redact (2nd pass) -> consent filter -> pseudonymise and minimise
        -> join labels (corrections, CSAT, outcomes) -> feature engineering
        -> dataset build (splits by customer) -> quality gates QG-01..QG-08 -> versioned release
        -> consumers: U4 and U5 candidates, evaluation sets, pCSAT, attribution, experiment analysis
deletion requests -> tombstone registry -> every stage above (filter and purge)
```

## 3. Collection

| Source | Fields taken | From | Notes |
|---|---|---|---|
| Conversation log (A10.1) | `conversation_id`, pseudonymised `customer_id`, `channel`, `authentication_level`, `primary_intent`, `resolution_status`, `guardrails_activated`, `csat_score`, `model_version`, `turn_count`, `pii_detected` | Audit and Telemetry Bus | read-only copy; the audit store itself is never modified by the pipeline |
| Turn log (A10.2) | `turn_id`, `speaker`, redacted `raw_message`, `intent_classification` (label, confidence, alternatives), `entities_extracted`, `sentiment_score`, `knowledge_items_retrieved`, `retrieval_confidence`, `agent_response`, `response_generation_method`, `guardrails_checked`, `guardrails_triggered`, `response_latency_ms`, `action_taken` | Audit and Telemetry Bus | entity values arrive in their stored form: masked or reference only for HIGH and CRITICAL tiers (`config/entities.yaml`) |
| State snapshots | `versions` (prompt, model, KB entry ids with versions), `dialogue_phase`, `consecutive_low_conf`, `human_request_count`, `clarification_attempts`, `escalation_proximity`, sentiment trajectory | State Tracker events | no `slots` values of HIGH or CRITICAL tier |
| Supervisor corrections | the record of `supervisor-corrections.md` section 3.1 | review tool | reviewer reference is pseudonymous |
| CSAT and check-ins | rating, redacted comment, check-in events | survey service, turn log | `csat-signals.md` |
| Outcomes | `outcome_class`, repeat-contact links, follow-up answers, ticket closure events | `outcome-tracking.md` | human-channel joins use the pseudonymised id |
| Experiment assignment | experiment id, arm, bucket | experiment service | `ab-testing.md` |
| Consent and deletion | consent records, tombstones | consent service, deletion workflow | sections 5 and 9 |

Not collected: raw audio, device contact lists, location beyond what the channel already provides, behavioural-biometric raw signals (GR-ATK-11 keeps only a score), and any field the Input Guard marks `never` (full card, CVV, Aadhaar, PIN, password, OTP, PAN, full account number). Data stays in the India region (system-architecture.md section 6; DPDP "data localisation" as summarised in the brief). Transport is TLS 1.3 and storage AES-256, with PII fields under a separate key (A10.3).

## 4. Redaction and anonymisation

| Step | Rule |
|---|---|
| Input-side redaction (already in place) | RED-01 full card number, RED-02 CVV, RED-03 full Aadhaar, RED-04 PIN or password (postal-code exception, D-35), RED-05 OTP in chat, RED-06 full PAN, RED-07 full account number are replaced by typed placeholders before NLU and before the turn log (`config/entities.yaml`) |
| Second pass at dataset build | the current version of RED-01 to RED-07, with the D-21 normalisation (native-script digits, separators, spelled digits), is run over every text field again: `raw_message`, `agent_response`, correction free text, CSAT comments. A hit replaces the value with the placeholder and raises QG-03 (case SS-PII-07) |
| Residual personal data scrub | names, phone numbers, email addresses, street addresses, dates of birth and reference numbers that the RED rules do not target are replaced by typed tokens (`[NAME]`, `[PHONE]`, `[EMAIL]`, `[ADDRESS]`, `[DOB]`, `[REF]`) by a recogniser tuned for Indian names and Hinglish text. These tokens are dataset-level only and are not new RED rules: the rule layer is not changed by the pipeline |
| Pseudonymisation | `customer_id` arrives hashed (A10.1). The pipeline re-keys it with a pipeline-specific keyed hash so that a dataset cannot be joined back to the audit store without the key, which Data Engineering does not hold alone |
| Sensitive attributes | no feature, label or note may encode religion, politics or health (A11.3). A recogniser flags such content in free text; flagged spans are dropped, not tokenised, and the row is excluded from training if the span is the substance of the message |
| Quasi-identifiers | amounts are bucketed, timestamps are reduced to hour-of-week and day index, rare merchant or place names are tokenised. Evaluation sets shown to people outside the review queue use only synthetic or fully scrubbed text |
| Free-form generation data | no customer text is used verbatim as a template or few-shot example in a prompt layer; examples in prompts are synthetic (assumption A3 in `docs/assumptions-and-decisions.md` and the README conventions: no real customer data) |

"Anonymised" in A11.3 is read as: redacted, scrubbed and pseudonymised as above, with re-identification tested (QG-03). The pipeline does not claim mathematical anonymity; a customer's own unusual wording can remain identifying, which is one reason deletion must reach the datasets.

## 5. Consent

The brief requires consent for training data and names consent management as a DPDP requirement, without mechanics (dependency G-05). Proposal (D-104):

| Aspect | Design |
|---|---|
| Purposes kept separate | P1 service delivery and security; P2 audit and regulatory record (A10 retention); P3 quality monitoring by supervisors and aggregated metrics; P4 use of the customer's conversations to train and evaluate models. Only P4 is optional for the customer |
| Consent record | `customer_ref`, purpose, status (granted, refused, withdrawn), timestamp, channel, version of the notice shown, language of the notice. Held by the consent service; the pipeline reads a snapshot with an id |
| Default | no P4 record means no training use. The row can still appear in aggregate metrics (P3) |
| Asking | at onboarding or in the app's privacy settings, in plain language and in the customer's language. The agent does not collect consent inside a support conversation and never makes service depend on it. A customer who asks how data is used gets the short answer of KB-POL-009 and KB-REG-007 and a pointer to the privacy notice |
| Withdrawal | takes effect for all dataset builds from the next snapshot (at most 24 hours, proposal). Rows already in released dataset versions are purged on the weekly purge run and models follow the retrain rule of section 9. Withdrawal is treated as a deletion request limited to purpose P4 |
| Anonymous conversations | there is no customer to hold consent, so the text is never used for P4 training. It is used for aggregate metrics, and scrubbed text may be used to write synthetic utterances by hand |
| Minors and third parties | a conversation on behalf of another person is never used for P4 |
| Gate | QG-02: every row of a training or evaluation dataset has a P4 "granted" record in the consent snapshot the dataset names (case SS-LRN-14) |

Consequence for volume: datasets are smaller than traffic. All sample-size reasoning for experiments uses experiment metrics (P1 and P3 purposes), not P4 training data, so the consent rate does not reduce experiment power. It does reduce training rows, which QG-05 checks.

## 6. Feature engineering

Features are defined once in a feature registry (name, definition, source fields, owner, version) and computed the same way offline and online.

| Consumer | Rows | Features | Label |
|---|---|---|---|
| Intent and entity models (U4) | customer turns | redacted, scrubbed text; language and code-switch flags; previous agent action; dialogue phase | adjudicated intent and entities from corrections; high-confidence production labels are used only as weak labels and never for the evaluation set |
| Sentiment model (U4) | customer turns | text, language, previous turn polarity | human polarity labels from double review |
| Retrieval models (U4) | query and entry pairs | rewritten query, entry id and version, rank, scores | supervisor "right entry / wrong entry" and gold query set (`docs/knowledge-base/retrieval-pipeline.md` section 15) |
| Policy ranker (U5) | decision points | intent, confidence, phase, slots filled (as flags), auth level, sentiment, candidates allowed by the rules | chosen action and the outcome class; logged with the action propensities so off-policy evaluation is possible |
| pCSAT and silent-dissatisfaction (`csat-signals.md` section 5) | conversations | implicit signals, turn count against the norm, action-type counts, last sentiment, check-in polarity | rating, weighted for non-response |
| Attribution (`csat-signals.md` section 7) | conversations and turns | action types, template ids, KB entry ids, version tuple, controls | weighted rating, sentiment change |
| Drift monitoring | daily aggregates | score distributions, intent mix, language mix, out-of-scope share | none |

Excluded from every feature set: name, age, gender, location below state level, balance or balance band, product holding, tenure, inferred income, any sensitive attribute, and any customer-history score (A11.3 "must not exhibit differential treatment based on demographics, balance, or history"). Language and channel are allowed because the system must work in each of them; they are monitored as fairness slices. The policy ranker never sees features that could let it learn to skip an auth step, a confirmation or an escalation: those are decided by rules before it runs (system-architecture.md section 4, step 5).

Guardrail-related data: turns flagged by GR-ATK guardrails are never used as positive training examples for the NLU intent models (an attacker must not be able to teach the classifier), and a session in safe mode (GR-ATK-04) is excluded from P4 datasets. They are kept, under the same redaction, for the red-team corpus owned by Security.

## 7. Dataset versioning

| Element | Rule |
|---|---|
| Identity | `dataset_id` (for example `nlu-intent-train`), semantic version, and a content hash over the sorted row hashes |
| Manifest per version | source window (dates), row counts by intent, language, channel and label source; consent snapshot id; tombstone snapshot id; redaction rules version; feature registry version; label schema version; build code version; quality gate report; builder and approver; parent version |
| Immutability | a released version is never edited in place. A purge (section 9) produces a new revision with a new hash and a reference to the tombstone batch; the old revision's data is destroyed and only its manifest stub remains |
| Splits | train, validation and test are split by customer (all of one customer's rows fall in one split) and stratified by intent and language class, as the Day 6 utterance library is. Time-based test sets (the most recent weeks) are kept for drift |
| Frozen evaluation sets | the NLU held-out split, the retrieval gold set, the benign evaluation set for the false-positive gate (D-64) and the fixed safety suite are frozen assets with their own versions. Training data is checked for overlap with them (QG-06). They change only by reviewed addition |
| Lineage | each model version records the dataset versions, code version, base model and hyper-parameters that produced it; each release records the model, prompt and KB epoch (A12.2). From a conversation's `versions` field an auditor can walk back to the training data |
| Retention | a dataset version is kept no longer than its shortest-lived source: CSAT-derived rows 3 years, log-derived rows 7 years (A10.1). Proposal: training datasets are kept for 24 months and then rebuilt or destroyed, since older conversations describe an older product and agent |
| Storage and access | India region, AES-256, separate key for any remaining PII field, least privilege, every read logged (A10.3). Training jobs run in an environment with no outbound network path to customer-facing systems |

## 8. Quality gates

A dataset version is published only if every gate passes. Thresholds are proposals to be calibrated on the first builds.

| Gate | Checks | Pass criterion | On failure |
|---|---|---|---|
| QG-01 schema and joins | required fields present and typed; every row joins to a conversation, a version tuple and, for labelled rows, a correction record | 100% of required fields; join completeness 99.5% or more | build fails; missing joins listed |
| QG-02 consent | P4 "granted" in the named consent snapshot for every row | 100%; one row without consent fails the build | build fails; row source investigated as an incident if it recurs |
| QG-03 redaction | re-scan with RED-01 to RED-07 and the residual scrub; a re-identification probe on a sample (can a reviewer with the pseudonymised dataset find a person) | zero RED hits after the second pass; zero raw identifiers in a 1,000-row manual sample | build fails; the upstream miss is reported to the rule owner as an observation |
| QG-04 label quality | only agreed or adjudicated labels in evaluation sets; reviewer-pair kappa for the weeks covered; reviewer outlier filter | kappa 0.70 or more for the label source, or the affected weeks held out; no label from a reviewer under an open outlier flag | affected rows held out |
| QG-05 coverage and balance | rows per intent, per language class and per channel against minimums; population stability index of the feature and label distributions against the previous version; no single customer above a row cap | at least 200 training rows per intent and 30 per intent in each primary language (proposal); PSI below 0.25 or an explained change; at most 20 rows per customer per intent | warning or failure by size; a candidate may not claim a gain on a slice below the minimum |
| QG-06 leakage | no exact or near-duplicate text shared between training data and any frozen evaluation set or safety-suite case; no customer in two splits | zero overlaps | overlapping rows removed from training, never from the frozen set |
| QG-07 deletion | no row belongs to a customer in the named tombstone snapshot | zero; one row fails the build (case SS-LRN-15) | build fails |
| QG-08 poisoning and anomaly | adversarial-flagged turns excluded; label-flip rate against the previous version; bursts of identical text from few customers; corrections concentrated on one guardrail or intent from one reviewer | no excluded source present; label changes on previously adjudicated rows are individually justified | affected batch quarantined (playbook runbook R7) |

Gate reports are stored with the manifest and shown on the weekly dashboard (A8.5 learning pipeline metrics).

## 9. Right to deletion in training data

### 9.1 What the brief requires

Requests are processed within 30 days; deletion includes all copies, backups and derived data including model training data; a deletion certificate is generated and stored (A10.3). The agent's part is to acknowledge and route the request without claiming immediate deletion (case GR-REG-13-02). This section covers the learning pipeline's part.

### 9.2 Propagation (proposal, D-104)

| Day | Step | Owner |
|---|---|---|
| 0 | request verified and accepted by the deletion workflow; a tombstone for the customer's pseudonymised id (and its pipeline re-key) is written to the tombstone registry | Data Protection lead |
| 0 to 1 | the next tombstone snapshot (at most 24 hours later) is used by every dataset build from then on: QG-07 guarantees no new dataset version contains the customer | Data Engineering |
| 1 to 7 | weekly purge run: the customer's rows are removed from every stored dataset revision, the feature store, label stores (corrections keep the verdict counts but lose the conversation link), CSAT and outcome tables, experiment assignment tables, and review-tool caches. Each affected dataset gets a new revision | Data Engineering |
| 1 to 21 | models: every production model whose lineage includes a purged row is replaced by a model trained on a purged dataset revision. The 21-day full-retrain cycle of `overview.md` section 5 does this by design; a model outside that cycle (retrieval, policy ranker, pCSAT) is retrained on a deletion-triggered run if its next scheduled build would fall after day 30 | NLU Team, ML Team |
| by 30 | backups: backup sets that contain the rows expire or are purged; backup retention for learning stores is set below 30 days so that expiry completes the deletion (proposal) | Data Engineering |
| by 30 | deletion certificate: lists the stores purged, the dataset revisions replaced (old and new hashes), the model versions retired and their replacements, the backup expiry dates, and any item under legal hold | Data Protection lead |

### 9.3 Design choices that make this possible

1. **Row-level lineage.** Every dataset row carries the pipeline re-key of the customer id, so the rows of a customer can be found in every revision without re-identifying anyone else.
2. **Models are treated as derived data.** The strict reading is the default: a model trained on a deleted customer's rows is replaced inside the 30 days. If Legal advises that trained weights are outside "derived data", the retrain trigger can be relaxed to the normal schedule; the purge of datasets cannot.
3. **No warm start across a purge.** A checkpoint that saw purged rows is not used to initialise the replacement (`overview.md` section 5).
4. **Aggregates.** Published aggregate metrics (a weekly CSAT mean) are not recomputed for a single deletion; they contain no personal data. Tables at conversation grain are purged.
5. **Evaluation sets and the safety suite** contain synthetic text only, so deletions do not touch them. This is a reason, beyond privacy, why real customer text never enters the suite.
6. **Audit logs.** The A10 retention periods and the deletion duty meet in the audit store, which is outside the learning pipeline (Day 14 audit specification). The pipeline's rule is simple: it keeps nothing the audit store has deleted.
7. **Legal hold.** Rows under an incident legal hold follow D-87: they are frozen, excluded from all training and analysis, listed on the certificate as held, and deleted when the hold ends. The pipeline never trains on held data.
8. **Batching.** With 2.7 million customers, deletion requests are expected continuously; they are handled as weekly batches, so the purge and retrain cost does not grow with the number of requests in a week.

### 9.4 Checks

QG-07 on every build; a monthly reconciliation that samples tombstones and searches every store for them; a drill, twice a year (proposal), that plants a synthetic customer, requests deletion and verifies the certificate against the stores; suite cases SS-LRN-14 and SS-LRN-15.

## 10. Decisions and open items

D-104 (consent purposes, default exclusion, deletion propagation, models as derived data), D-105 (dataset manifest, splits by customer, quality gates QG-01 to QG-08 and their thresholds).

1. The consent notice, its legal basis and the handling of customers who never answer it are for the Data Protection lead and Legal (dependency G-05).
2. Whether trained model weights are "derived data" under A10.3 needs a legal reading; the default here is yes.
3. Backup retention below 30 days for learning stores must be agreed with the platform team; where a backup must live longer, it needs a purge procedure instead.
4. The interaction between the 7-year audit retention and a deletion request is specified with audit logging on Day 14 and is not decided here.
