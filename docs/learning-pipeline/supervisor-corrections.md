# Supervisor Correction Loop

Brief refs: A5.1 (p.15: "sampling strategy (random, confidence-based, escalation-triggered, complaint-triggered); correction interface specification; correction taxonomy with severity levels (critical safety error, moderate quality issue, minor style improvement, false positive escalation); correction propagation timeline (immediate for safety issues, batched daily for quality, weekly for style); supervisor agreement metrics; and workload management (target: 50 reviews per supervisor per day)"), A1.1 (p.3: about 18,000 interactions daily), A8.1 and A8.3 (pp.19-21: confidence distribution and escalation rate targets), A8.5 (p.22: "Top 10 unresolved intents and top 10 low-confidence interactions for review", "Supervisor correction summary"), A10.3 (p.28: supervisors see full logs only for conversations in their review queue). Related: `docs/guardrails/monitoring-dashboard.md` section 5 (guardrail sampling, D-89), `data-pipeline.md`, `overview.md`.

**Status.** The brief fixes the four sampling types, the four severities, the propagation timeline and 50 reviews per supervisor per day. Sampling rates, pool sizes, agreement thresholds and staffing are proposals (D-96, D-97, D-98). Volumes are planning assumptions, not measurements.

## 1. Purpose

Supervisor corrections are the highest-quality feedback source: a trained person reads the conversation and says what should have happened. They serve four uses: (1) find safety errors the automated checks missed, (2) produce labels for NLU and evaluation data, (3) produce KB and prompt change requests, (4) estimate true quality rates that CSAT cannot give (CSAT is biased by who answers, `csat-signals.md` section 6).

## 2. Sampling strategy

### 2.1 Streams

Conversations are sampled the day after they close, so that the review sees the outcome. Four streams follow the brief; a fifth is the guardrail stream already specified on Day 10.

| Stream (A5.1) | Pool | Selection | Daily pool (planning assumption) | Rate (proposal) | Reviews per day |
|---|---|---|---|---|---|
| R: random | all closed conversations | simple random, stratified by intent category and language so that every stratum has a minimum | 18,000 (A1.1) | 1% | 180 |
| C: confidence-based | conversations with a turn below `intent_confidence_threshold` 0.70 or `retrieval_confidence_threshold` 0.65, or a clarification loop | weighted towards the lowest confidence; A8.5 "top 10 low-confidence interactions" always included | 3,600 (20% of volume: the most the A8.1 target "above 80% above 0.7" allows) | 4% | 144 |
| E: escalation-triggered | conversations that created an ESC record | stratified by ESC ID; at least 5 per ESC ID per day where that many exist | 5,400 (30% of volume: the A8.3 ceiling "below 30%") | 2% | 108 |
| P: complaint-triggered | (a) conversations named in a complaint about the AI service; (b) conversations rated CSAT 1 or 2 | (a) all; (b) random | (a) 90 (0.5% of volume, assumption); (b) 270 (10% of 2,700 responses, assumption; response rate 15%, `csat-signals.md`) | (a) 100%; (b) 20% | 90 + 54 |
| G: guardrail triggers (D-89) | triggered turns, near-misses, intervened turns | as `monitoring-dashboard.md` section 5 | up to 30 triggers per guardrail per week | fixed | 58 x 30 / 7 = 249 turn reviews |

Conversation reviews: 180 + 144 + 108 + 90 + 54 = 576 per day, which is 3.2% of volume. Stream G reviews one turn in context, not a whole conversation, and is counted at one third of a conversation review (proposal): 83 review equivalents.

### 2.2 Rules

1. **Random is never cut.** Streams C, E and P find problems efficiently but are biased samples. Only stream R gives unbiased rates (defect rate, S1 rate, false-resolution rate). When capacity is short, C and E are reduced first, P(b) next, and R and P(a) last.
2. **A conversation is reviewed once.** If it qualifies for several streams it is assigned to the first of P, E, C, R that selected it, and all its stream tags are kept for analysis.
3. **Always reviewed, outside the percentages (proposal):** any conversation behind a hard-zero counter event, every OSL near-miss on a CRITICAL guardrail (D-88), the 30 conversations the silent-dissatisfaction detector scores highest that day (`csat-signals.md` section 5), and up to 30 false resolutions a day (`outcome-tracking.md` section 2), taken first from the intent categories with the lowest resolution in the brief's data (A1.2: Product Recommendation 42%, Loan Enquiry 55%, Complaint Resolution 58%). These items take the place of stream C and E items in the day's queue, so the total stays inside capacity (section 7).
4. **Canary cohorts are doubled** (D-89): while a candidate is at 1%, 5% or 25%, sampling rates inside the candidate cohort are twice the table above, and the reviewer does not see which cohort a conversation belongs to.
5. **Fair coverage.** Strata include language (English, Hindi, Hinglish and the five secondary languages) and channel, so that a quality problem in a small language is not hidden by volume (A11.3).
6. **Precision of the random stream.** 180 reviews a day give 1,260 a week. For a true defect rate of 5% the weekly 95% interval is plus or minus 1.2 points (1.96 x sqrt(0.05 x 0.95 / 1,260)); the daily interval is plus or minus 3.2 points. Quality rates are therefore reported weekly. If no S1 is found in 1,260 random reviews, the 95% upper bound on the S1 rate is 0.24%, which is far too weak to demonstrate a 0% target; the hard-zero counters and the fixed suite carry that claim, not sampling.

## 3. Correction interface specification

The review tool is an internal web tool. Layout:

```
+--------------------------------------------------------------------------------------------------+
| Queue: 14 of 50 today | stream: C (low confidence) | conversation c-7f3a.. | timer 03:12 | Skip  |
+---------------------------------------------+----------------------------------------------------+
| TRANSCRIPT (redacted, read-only)            | TURN INSPECTOR (turn 4, agent)                     |
|  1 C  My UPI payment failed but money ...   |  intent: TXN-003  conf 0.58  alt: TXN-002 0.31     |
|  2 A  I am sorry about that. To check ...   |  entities: amount 2,400 (valid) txn_ref [masked]   |
|  3 C  [OTP_REDACTED]                        |  sentiment: -0.42   auth: otp_verified             |
|  4 A  The payment shows as pending ...   <  |  KB: KB-TRB-001@1.0.0 (retrieval conf 0.71)        |
|  5 C  so when will i get it back            |  generation: hybrid   guardrails checked: 26       |
|  6 A  The team will review and update ...   |  triggered: GR-OUT-05 (redirect)                   |
|  ...                                        |  action: respond    latency 1,840 ms               |
| outcome: escalated (ESC-014)  CSAT: 2       |  versions: prompt p-41, model m-17, epoch e-203    |
+---------------------------------------------+----------------------------------------------------+
| VERDICT   ( ) S0 no issue  ( ) S1 critical safety  ( ) S2 quality  ( ) S3 style  ( ) S4 false    |
|           positive escalation                                 turn(s): [4] [6]                   |
| COMPONENT [ NLU | retrieval | KB content | generation | policy | escalation | guardrail | tool ] |
| ERROR TYPE [dropdown per component]     CORRECT INTENT [TXN-003 v]   CORRECT ESC [none v]        |
| WHAT SHOULD THE AGENT HAVE SAID OR DONE  [free text, redacted on save                         ]  |
| KB: [wrong entry] [missing entry] [unclear entry]  id: [KB-TRB-001]   NOTE [                  ]  |
| [Save and next]   [Flag for second review]   [Raise incident (S1)]                               |
+--------------------------------------------------------------------------------------------------+
```

| Aspect | Specification |
|---|---|
| What the reviewer sees | the transcript after RED-01 to RED-07 redaction, the pseudonymised customer reference, and per turn the A10.2 fields: intent with confidence and alternatives, entities, sentiment, KB items with retrieval confidence, generation method, guardrails checked and triggered, action, latency, plus the version tuple. Never a raw identifier (case SS-PII-09) |
| What the reviewer does not see | the model's or another reviewer's verdict, the experiment cohort, the customer's name or balance. Blind review protects the agreement measure and the canary comparison |
| Access | only conversations in the reviewer's own queue (A10.3); every open is logged (meta-audit trail); no export, no copy of transcript text out of the tool |
| Required fields | verdict; for S1 to S4 the turn or turns, the component and the error type; for S2 the corrected intent, the corrected answer or the KB pointer, whichever applies |
| Time aids | the turn inspector opens on the lowest-confidence turn; keyboard shortcuts for verdict and next; target 9 minutes per review (450 working minutes divided by 50) |
| S1 button | "Raise incident" opens the incident intake of `docs/guardrails/incident-response-playbook.md` section 4 with the conversation and turn ids filled in; the reviewer does not wait for the daily batch |
| Skip | allowed with a reason (not enough context, language not covered); skips are re-queued to a qualified reviewer and counted |
| Language routing | a conversation is queued only to reviewers qualified in its language; secondary-language capacity is a dependency (D-22) |
| Free text | passes the same redaction before storage; reviewers are told not to paste customer data |
| Outputs | one correction record per conversation (section 3.1) on the audit bus and in the learning store |

### 3.1 Correction record

| Field | Type | Notes |
|---|---|---|
| `correction_id`, `conversation_id`, `turn_ids` | ids | links to the A10 logs |
| `reviewer_ref` | pseudonymous id | needed for agreement and outlier checks |
| `stream` | R, C, E, P, G (all tags kept) | sampling weight is stored so that rates can be re-weighted |
| `severity` | S0 to S4 | section 4 |
| `component` | nlu, retrieval, kb_content, generation, policy, escalation, guardrail, tool, other | the A8.4 DIAGNOSE components plus the rest of the architecture |
| `error_type` | enum per component | section 4.2 |
| `corrected_intent`, `corrected_entities` | intent ID from `config/intents.yaml`, entity list | become NLU training and evaluation rows after adjudication |
| `corrected_response` | redacted text | used as a reference answer for evaluation, never auto-deployed |
| `kb_refs` | KB IDs with wrong, missing or unclear | become KB change requests (U1) |
| `guardrail_refs` | GR IDs with should_have_fired or should_not_have_fired | go to the guardrail owner; never to the pipeline as a change (case SS-LRN-16) |
| `escalation_verdict` | correct, missed (with ESC ID), unnecessary (with ESC ID) | S4 uses "unnecessary" |
| `second_review_of`, `adjudicated` | link, boolean | section 6 |
| `versions` | prompt, model, KB epoch, rules version | from the state schema `versions` |
| `time_spent_s` | integer | workload model |

## 4. Correction taxonomy

### 4.1 Severity (the four levels of A5.1, plus "no issue")

| Code | Brief name | Definition | Examples | Lane (A5.1) |
|---|---|---|---|---|
| S0 | (none) | the agent's handling was acceptable | | none; counts in the denominator |
| S1 | critical safety error | a delivered reply or executed action that breaks a guardrail, a security rule, a regulatory duty or an A9.2 AUTO-FAIL item; or a missed P0 escalation | wrong rate stated; personalised advice given; a full identifier shown; account data without the required auth; a fraud or crisis signal not escalated | immediate |
| S2 | moderate quality issue | the customer's need was not met correctly, with no safety breach | wrong intent; wrong or missing KB entry; an unnecessary clarification loop; a correct answer to a different question; a P1 or P2 escalation missed | daily batch |
| S3 | minor style improvement | the outcome was right but the wording, length, tone or order could be better | no empathy line before a refusal; too long for the channel; awkward Hinglish | weekly |
| S4 | false positive escalation | the agent handed off to a human when it could have resolved safely (A9.2 Premature Escalation) | ESC-003 after a single unclear turn; ESC-004 on sarcasm read as anger | daily batch for analysis; any threshold change follows A12.3 |

Rules. When two severities apply, the higher is recorded and the other goes in the note. S1 always wins. A blocked or repaired draft (the Output Safety Layer caught it) is not S1: it is a catch (D-88) and is labelled S0 or S2 on the delivered reply, with the guardrail noted. An over-block of a benign request (a guardrail false positive) is S2 with component `guardrail` and `should_not_have_fired`.

### 4.2 Component and error type

| Component | Error types | Usual update class (`overview.md` section 3) |
|---|---|---|
| nlu | wrong intent, missed second intent, wrong entity, wrong language, wrong sentiment, out-of-scope missed | U4 label; U3 if the threshold is the cause |
| retrieval | right entry exists but was not retrieved, wrong entry ranked first | U4 retrieval model or U3 `knowledge_retrieval_top_k` |
| kb_content | entry wrong, missing, unclear, out of date, not translated | U1 change request |
| generation | ungrounded statement, wrong wording of a correct fact, tone, length, missing confirmation | U2 layers 3 or 4; S1 cases go to the guardrail owner as well |
| policy | wrong next action, asked for auth too early or too late, lost context | U5, or a deterministic flow fix by Product Engineering |
| escalation | missed, unnecessary, wrong queue, poor handoff summary | escalation owner (X5); `escalation_sentiment_threshold` via A12.3 |
| guardrail | should have fired, should not have fired, wrong action | guardrail owner through safety change control (X3) |
| tool | wrong tool, tool error handled badly | Product Engineering |

## 5. Propagation timeline

| Severity | First action | Then | Becomes |
|---|---|---|---|
| S1 | at once: incident intake; second reviewer confirms within the playbook's acknowledge time; containment by a tighten-only lever (playbook section 5) | root cause; fix through safety change control if a guardrail or rule is involved, or through the normal gates if the cause is a U1 to U5 artefact | a new fixed-suite case before the fix ships (playbook principle 6); a regression row in the evaluation set |
| S2 | queued to the 06:00 daily batch | triage by component into: KB change requests, NLU label rows, layer 4 wording notes, policy defects | U1 the same day where the KB chain allows; labels enter the next dataset version; grouped candidates for U2 to U5 |
| S3 | queued to the weekly style review | CX Team groups findings by pattern; one layer 3 candidate at most | monthly layer 3 release after its A/B (A12.1) |
| S4 | daily batch | counted per ESC ID and per language; a pattern opens a proposal to the trigger's owner | escalation rule review (Day 12 quality metrics); never an automatic threshold change (case SS-LRN-09) |

A correction changes nothing by itself. It is evidence. The record is immutable; a later reversal is a new record that points to the first.

## 6. Inter-rater agreement

### 6.1 Design

Ten percent of reviewed items are double-reviewed (proposal): a second supervisor, blind to the first verdict, reviews the same conversation. Agreement is Cohen's kappa on the five-way severity label, and separately on S1 against everything else, per reviewer pair and overall, weekly.

`kappa = (p_o - p_e) / (1 - p_e)`, where `p_o` is the observed share of items on which both reviewers agree and `p_e` is the agreement expected by chance from each reviewer's own label frequencies.

### 6.2 Worked example (illustrative labels, not data)

Two supervisors, A (rows) and B (columns), 100 double-reviewed conversations:

| A \ B | S0 | S1 | S2 | S3 | S4 | Row total |
|---|---|---|---|---|---|---|
| S0 | 52 | 0 | 3 | 4 | 1 | 60 |
| S1 | 0 | 4 | 1 | 0 | 0 | 5 |
| S2 | 3 | 1 | 10 | 2 | 0 | 16 |
| S3 | 3 | 0 | 2 | 7 | 0 | 12 |
| S4 | 1 | 0 | 0 | 0 | 6 | 7 |
| Column total | 59 | 5 | 16 | 13 | 7 | 100 |

- Observed agreement: `p_o = (52 + 4 + 10 + 7 + 6) / 100 = 0.79`.
- Chance agreement: `p_e = (60 x 59 + 5 x 5 + 16 x 16 + 12 x 13 + 7 x 7) / 100^2 = (3,540 + 25 + 256 + 156 + 49) / 10,000 = 4,026 / 10,000 = 0.4026`.
- `kappa = (0.79 - 0.4026) / (1 - 0.4026) = 0.3874 / 0.5974 = 0.648`.
- Approximate standard error: `sqrt(p_o (1 - p_o) / (n (1 - p_e)^2)) = sqrt(0.79 x 0.21 / (100 x 0.3569)) = 0.068`, so the 95% interval is 0.52 to 0.78. One hundred items do not locate kappa precisely; the weekly pool of about 461 double reviews (section 7) gives a standard error near 0.03.
- S1 against the rest: both say S1 on 4, A only on 1, B only on 1, neither on 94. `p_o = 0.98`, `p_e = (5 x 5 + 95 x 95) / 10,000 = 0.905`, `kappa = 0.075 / 0.095 = 0.789`.

Reading: raw agreement of 79% looks comfortable, but 60% of items are S0, so much of it is chance. Kappa 0.65 is below the target; the confusion is between S0, S2 and S3 (quality against style), which calls for a calibration session on that boundary. S1 agreement is higher, and both S1 disagreements are adjudicated the same day.

### 6.3 Thresholds and actions (proposal, D-98)

| Measure | Target | Below target |
|---|---|---|
| Overall kappa, five labels, weekly | 0.70 or more (the same value `docs/intent-taxonomy/sentiment.md` uses for human label agreement) | 0.60 to 0.70: calibration session and guideline update that week; below 0.60: the pair's single-reviewed labels from that week are held out of training data until re-reviewed (QG-04) |
| S1 against the rest | 0.80 or more | every S1 disagreement is adjudicated by a review lead the same day regardless; below 0.80 for two weeks: S1 guidance is rewritten with Risk and Compliance |
| Per-reviewer drift | each reviewer's label distribution within 2 standard deviations of the pool on the random stream | second review of a sample of that reviewer's work; possible poisoning check (FMEA 23) |

Other rules: a disagreement is settled by a review lead and the adjudicated label is the one used for training; only adjudicated or agreed labels become evaluation-set rows; kappa is reported with its interval and the number of items; for the ordered part of the scale (S3, S2, S1) a weighted kappa is reported beside the unweighted one, because confusing S3 with S1 is worse than confusing S3 with S2. Kappa is depressed when one label dominates, so the per-label agreement table is always shown with it.

## 7. Workload model

The brief sets 50 reviews per supervisor per day. With the planning assumptions of section 2.1:

| Line | Calculation | Per day |
|---|---|---|
| Conversation reviews (R, C, E, P) | 180 + 144 + 108 + 90 + 54 | 576 |
| Guardrail turn reviews (G) at one third weight | 58 x 30 / 7 = 248.6; divided by 3 | 82.9 |
| Review equivalents | 576 + 82.9 | 658.9 |
| Double review, 10% | 658.9 x 1.10 | 724.7 |
| Supervisors on the floor | 724.7 / 50 = 14.5 | 15 |
| With 20% shrinkage (leave, training, calibration, adjudication; proposal) | 14.5 / 0.80 = 18.1 | 19 on the roster |

Fifty reviews in a 7.5-hour working day is 9 minutes per review. Double-reviewed items number about 66 a day, 461 a week.

Workload management rules:

1. **Capacity first.** Each morning the queue builder fills 50 items per rostered reviewer in priority order: always-reviewed items, P(a), R, P(b), E, C, then G. What does not fit is dropped from C and E first (rule 1 of section 2.2) and the shortfall is reported; it is never hidden by raising the daily target.
2. **Backlog alarm.** `monitoring-dashboard.md` already alerts when the oldest unreviewed critical sample is older than 24 hours (warn) or 72 hours (critical).
3. **Elastic rates.** The rates in section 2.1 are the levers: if the low-confidence pool is smaller than the assumed 20% (which the A8.1 target implies), its 4% rate yields fewer reviews and the freed capacity goes to stream R.
4. **Complexity weighting (proposal).** A conversation longer than 15 turns counts as two reviews; the brief's data shows complaint conversations average 11.3 turns against 3.4 for card blocking (A1.2), so an unweighted target would push reviewers towards short conversations.
5. **No speed incentive.** Reviewers are measured on agreement and adjudication outcomes, not on count above 50.
6. **Sensitivity.** If the complaint pool or the low-CSAT share is twice the assumption, stream P grows by 144 reviews and the roster by about 3 (144 x 1.10 / 50); the model is re-run monthly on observed pools.

## 8. Protecting the loop from bad labels

FMEA 23 (feedback poisoning) names reviewer diversity, outlier filters and a HITL gate. In this design: reviewers cannot choose their items; double review is random and blind; a reviewer whose labels on one guardrail or intent depart sharply from the pool is flagged and their batch is second-reviewed (case SS-LRN-16); labels never change a guardrail, a threshold or a prompt directly (`overview.md` section 3); training rows need an agreed or adjudicated label; and the reviewer who labelled a conversation is not the approver of a candidate trained on it.

## 9. Metrics

Reviews completed against capacity; coverage by stream, intent category and language; severity mix on the random stream with weekly intervals (the unbiased quality estimate); S1 count and time from label to containment; correction mix by component (the A8.5 "supervisor correction summary with categorisation of correction types"); kappa overall and for S1; adjudication rate; time per review; share of S2 corrections that produced a released change within 30 days; share of S4 per ESC ID.

## 10. Decisions and open items

D-96 (sampling rates and workload model), D-97 (taxonomy codes, component tags and what "immediate" means), D-98 (double-review share and kappa thresholds).

1. Pool sizes are assumptions taken from the brief's targets; the first month of operation replaces them with observed pools.
2. Reviewers qualified in the five secondary languages are a staffing dependency (D-22); until then those conversations are reviewed through the English pivot with a flag.
3. The review tool is specified by behaviour; its technology is not chosen.
