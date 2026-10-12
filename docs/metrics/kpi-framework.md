# KPI Framework

Brief refs: A8.1 p.19 (seven leading indicators), A8.2 p.20 (seven lagging indicators), A8.3 pp.20-21 (six operational metrics), A1.4 p.5 (design targets: "70%+ containment rate, 4.5+ CSAT, 0% incorrect financial advice rate, <30-second first reply"; industry benchmark), A1.1 p.3 (CSAT baseline 3.2, target 4.5; the Customer Experience team "owns satisfaction metrics"), A1.2 pp.3-4 (per-category resolution and CSAT in the transcripts), A2.3 p.7 (retrieval "maximum 200ms latency at 95th percentile"), A5.1 to A5.4 p.15 (supervisor reviews, CSAT signal, outcome classes, repeat contact at 7/14/30 days, safety suite), A8.4 p.21 (detection within 15 minutes), A10.1 and A10.2 pp.27-28 (log fields), A10.3 p.29 (regulatory reporting), A12.3 p.34 (parameter owners), Part D Day 12-13 p.60 ("Design complete metrics framework: leading, lagging, and operational indicators"). Related: `improvement-cycle.md`, `dashboards.md`, `docs/guardrails/monitoring-dashboard.md` (DM-01 to DM-16), `docs/escalation/queue-management.md` section 8 (EQ-01 to EQ-12), `docs/intent-taxonomy/sentiment.md`.

**Status.** For each metric the brief gives a name, a one-line definition, a target and a frequency. Those four are quoted unchanged. Exact formulas, numerator and denominator rules, data sources, owners, alert thresholds and anti-gaming notes are proposals (D-132). No metric has been measured: no system exists, so every value in this repository is a target or a planning figure, never a result.

## 1. Conventions

| Term | Definition |
|---|---|
| Conversation | One `conversation_id` (A10.1) with at least one customer message. Load-test, synthetic-probe and internal test traffic are excluded by a traffic tag. Sessions cut by rate limiting (GR-ATK-08) are kept and tagged |
| Turn | One logged message (A10.2 turn record). Customer turns carry intent, entities and sentiment |
| `N` | Conversations that ended in the period. A conversation ends at closure, at handoff completion, or after the inactivity timeout with no return |
| Period | The brief's frequency for the metric. Real-time means a rolling window (1 hour unless stated) |
| Brief target | The brief's number. A comparison written "<" or ">" in the brief is kept strict; "at least" is used where the brief's table shows the greater-than-or-equal sign |
| Alert thresholds | Proposals. "Warn" raises a ticket and a dashboard marker; "critical" pages the owner. Detection inside 15 minutes is the brief's requirement (A8.4) for the real-time metrics |
| Sample-based metric | A metric that needs human labels. It is reported with its sample size and a 95 percent interval, and is not shown as a point value when the sample is under 30 |
| Segments | Every metric can be cut by intent, channel, language, authentication level, model version and prompt version (A10.1 fields). Cuts by demographic attributes are used only for fairness testing (A11.3), never for targeting |

### 1.1 Outcome classes and the shares built on them

Containment, escalation rate and first contact resolution are shares of the same population. The outcome classes are defined once, in `docs/learning-pipeline/outcome-tracking.md` section 2 (the five A5.3 classes over the four A10.1 values), and are used here unchanged.

| A5.3 outcome class | A10.1 `resolution_status` at close | Escalation record | Counted in |
|---|---|---|---|
| resolved-first-contact | `resolved_ai` | none | Containment; non-escalated share; first contact resolution |
| unresolved-dropped | `unresolved` | none | Non-escalated share only. Not containment: nothing was resolved |
| false-resolution (reclassified after a repeat contact) | `resolved_ai` or `resolved_human` | either | Counted at close like its original class; removed in verified containment; never first contact resolution |
| resolved-with-escalation | `resolved_human` | yes | Escalation rate |
| unresolved-escalated | `escalated` | yes | Escalation rate |

"Escalation record" in these metrics means a record created by a brief trigger or by an addition with a live or case route (XTR-01 to XTR-04, XTR-06), whose outcome is not de-escalated or withdrawn (`docs/escalation/triggers.md` section 8). A `silent_case` counts, because human work was required. Referrals (XTR-05, XTR-07) are reported separately and are not escalations. `outcome-tracking.md` writes "no ESC record"; that wording predates the additions and the cancellation outcomes and is read in this sense (D-132).

Containment follows the brief's glossary (p.68): "Containment Rate: Percentage of customer interactions fully resolved by AI without human intervention"; A8.2 words it "Conversations fully handled by AI". It is therefore `resolved_ai` with no escalation record, over `N` (D-162). The share of conversations with no escalation record, resolved or not, is kept as a named secondary, the non-escalated share.

Consequences: non-escalated share plus escalation rate is 100 percent by construction, but containment is smaller than the non-escalated share by the unresolved-dropped conversations. "Containment at least 70 percent" and "escalation below 30 percent" are therefore two constraints: an agent can stay under the escalation ceiling and still miss containment by leaving customers unresolved. First contact resolution is stricter again: it is containment less the conversations that return within 7 days (and it uses the in-scope denominator).

## 2. Brief targets at a glance

| Metric | Target (brief) | Frequency (brief) | Class | Source |
|---|---|---|---|---|
| First Response Time | <5 seconds | Real-time | Leading | A8.1 |
| Intent Recognition Accuracy | >92% | Daily | Leading | A8.1 |
| Entity Extraction Accuracy | >95% | Daily | Leading | A8.1 |
| Sentiment Trajectory Slope | Positive or stable | Daily | Leading | A8.1 |
| Knowledge Retrieval Relevance | >0.85 | Daily | Leading | A8.1 |
| Guardrail False Positive Rate | <3% | Daily | Leading | A8.1 |
| Agent Confidence Distribution | >80% above 0.7 | Weekly | Leading | A8.1 |
| CSAT Score | at least 4.5 (1-5 scale) | Weekly | Lagging | A8.2, A1.4 |
| Net Promoter Score | at least 50 | Monthly | Lagging | A8.2 |
| First Contact Resolution | at least 70% | Weekly | Lagging | A8.2 |
| Containment Rate | at least 70% | Weekly | Lagging | A8.2, A1.4 |
| Customer Effort Score | at least 5.5 (1-7 scale) | Monthly | Lagging | A8.2 |
| Incorrect Advice Rate | 0% | Daily | Lagging | A8.2, A1.4 |
| Customer Retention Impact | Positive | Quarterly | Lagging | A8.2 |
| Average Handle Time | <8 minutes | Daily | Operational | A8.3 |
| Escalation Rate | <30% | Daily | Operational | A8.3 |
| System Uptime | at least 99.9% | Real-time | Operational | A8.3 |
| Concurrent Capacity | at least 10,000 | Weekly load test | Operational | A8.3 |
| Knowledge Base Coverage | at least 90% | Monthly | Operational | A8.3 |
| Model Drift Score | <0.05 | Weekly | Operational | A8.3 |
| First reply (business ceiling) | <30 seconds | not stated | Design target | A1.4 |
| KB retrieval latency, 95th percentile | maximum 200 ms | not stated | Design requirement | A2.3 |

## 3. Leading indicators (A8.1)

Leading indicators move before customer outcomes do; they are the DETECT inputs of the improvement cycle.

### 3.1 Definitions

| ID | Metric | Brief definition | Formula | Numerator / denominator | Data source |
|---|---|---|---|---|---|
| KPI-L1 | First Response Time | "Time from customer message to first agent response" | 95th percentile of (timestamp of the first agent response minus timestamp of the customer message), over first exchanges in the window. Mean and median also shown | Per conversation: one duration. A typing indicator or a holding line is not a response; the greeting with AI disclosure is | A10.2 `response_latency_ms` of the first agent turn; gateway timestamps |
| KPI-L2 | Intent Recognition Accuracy | "Percentage of intents correctly classified on first attempt" | correct / labelled | Numerator: labelled customer turns whose top secondary-layer intent, as first classified (before any clarification answer), equals the reference label. Denominator: labelled customer turns, excluding turns the labeller marks as truly ambiguous | A10.2 `intent_classification` (label, confidence, alternatives); daily labelled sample (A5.1 review); the fixed gold set is reported as a separate line |
| KPI-L3 | Entity Extraction Accuracy | "Percentage of entities correctly extracted and validated" | correct / reference | Numerator: reference entities extracted with the exact normalised value and a passed validation. Denominator: reference entities in the labelled sample. Precision (extracted entities that are correct) is shown as the counter-metric | A10.2 `entities_extracted` (type, value, confidence, validation); labelled sample |
| KPI-L4 | Sentiment Trajectory Slope | "Average rate of sentiment change during conversations" | mean over conversations of the least-squares slope of the raw per-turn sentiment score against customer-turn index (`sentiment.md` section 4) | Numerator: sum of slopes. Denominator: conversations with 3 or more scored customer turns | A10.2 `sentiment_score` |
| KPI-L5 | Knowledge Retrieval Relevance | "Average relevance score of retrieved knowledge items" | mean of the calibrated relevance of cited entries (`synthesis_confidence`, D-42) | Numerator: sum over retrievals with decision `answer`. Denominator: those retrievals. Gap and degrade decisions are counted in KPI-O5, not here | A10.2 `retrieval_confidence`, `knowledge_items_retrieved` |
| KPI-L6 | Guardrail False Positive Rate | "Percentage of safe responses blocked by guardrails" | Defined once, as DM-05 in `monitoring-dashboard.md` section 4 (end-to-end rate on the labelled benign set, with the live estimate). Not redefined here | See DM-05; per-guardrail diagnostics are DM-04 | A10.2 `guardrails_checked`, `guardrails_triggered`; review labels |
| KPI-L7 | Agent Confidence Distribution | "Distribution of confidence scores across all interactions" | share of customer turns with top intent confidence above 0.7; the full decile histogram is shown | Numerator: customer turns with secondary-layer confidence above 0.7. Denominator: customer turns with a classification | A10.2 `intent_classification.confidence` |

### 3.2 Targets, owners, alerts and anti-gaming

| ID | Target (brief) | Frequency (brief) | Owner (proposal) | Warn / critical (proposal) | Anti-gaming notes |
|---|---|---|---|---|---|
| KPI-L1 | <5 seconds; business ceiling <30 seconds (A1.4); engineering budget under 3 s at the 95th percentile per turn (D-07) | Real-time | Product Engineering (platform) | p95 above 4 s for 2 windows / p95 above 5 s, or any response above 30 s | Holding messages do not stop the clock. The percentile is stated, so a good mean cannot hide a slow tail. Template-only mode is fast but lowers quality, so it is shown on the same panel |
| KPI-L2 | >92% | Daily | NLU Team | below 93 / below 92; any safety-critical intent (SEC-001, GEN-007, PRD-005) below its own gate | Macro-average across intents and per-language values are shown beside the headline, so frequent easy intents cannot mask rare critical ones. Raising thresholds to avoid errors shows up as a higher clarification rate (KPI-A6) |
| KPI-L3 | >95% | Daily | NLU Team | below 96 / below 95; amount or card-last-4 errors reported separately | Recall and precision are both shown. Entities confirmed only after the customer corrected them count as incorrect |
| KPI-L4 | Positive or stable | Daily | CX Team | mean slope below 0 for 2 days / below -0.02 per turn for 2 days (stable is read as at or above -0.01) | Conversations that end in abandonment are included. Shown by starting-sentiment band, because a conversation that starts happy cannot rise. Not improvable by ending conversations early: needs 3 turns |
| KPI-L5 | >0.85 | Daily | NLU Team with KB owners | below 0.87 / below 0.85 | Only cited entries count, so retrieving more entries cannot raise it. Declining to answer more often raises this metric and lowers KPI-O5; the two are shown together |
| KPI-L6 | <3% | Daily | Chief Risk Officer; ML Team day to day | as DM-05: 2.1 percent / 3 percent | As DM-05. Loosening a guardrail to cut false positives is a Risk Committee change (GR-SYS-03) and is checked against the hard-zero counters (DM-12) |
| KPI-L7 | >80% above 0.7 | Weekly | NLU Team | below 82 / below 80 | An over-confident model inflates the share. Accuracy among turns above 0.7 and the calibration error are shown beside it; a rise in this metric with a fall in that accuracy is a regression, not an improvement |

## 4. Lagging indicators (A8.2)

Lagging indicators are the outcomes the board set. They confirm or refute what the leading indicators suggested.

### 4.1 Definitions

| ID | Metric | Brief definition | Formula | Numerator / denominator | Data source |
|---|---|---|---|---|---|
| KPI-G1 | CSAT Score | "Average post-conversation rating (1-5 scale)" | mean of `csat_score` | Numerator: sum of ratings. Denominator: conversations with a rating. Response rate (rated / asked) and the non-response-weighted mean of `csat-signals.md` section 6 are always shown with it | A10.1 `csat_score`; survey rules in `docs/learning-pipeline/csat-signals.md` section 3 |
| KPI-G2 | Net Promoter Score | "Likelihood to recommend NexBank AI support" | percent promoters minus percent detractors on a 0 to 10 likelihood-to-recommend question (promoters 9 to 10, detractors 0 to 6). This is the standard NPS construction; the brief gives only the name and the target | Numerator: promoters minus detractors. Denominator: respondents in the month | Monthly survey to a random sample of customers who used the agent |
| KPI-G3 | First Contact Resolution | "Issues resolved without escalation or return" | Defined once in `outcome-tracking.md` section 4.3 (D-103): conversations classed resolved-first-contact divided by conversations in scope. Not redefined here | Numerator: `resolved_ai`, no escalation record, no repeat contact on the same issue within 7 days. Denominator: conversations in scope (out-of-scope conversations are excluded, `outcome-tracking.md` section 2.2) | A10.1 `resolution_status`, `primary_intent`, `customer_id`; repeat-contact job (A5.3) |
| KPI-G4 | Containment Rate | "Conversations fully handled by AI" (A8.2); "fully resolved by AI without human intervention" (glossary p.68) | conversations resolved by the agent with no escalation record / `N` | Numerator: `resolution_status` = `resolved_ai` and no escalation record in the sense of section 1.1. Unresolved-dropped conversations are not counted. Denominator: `N`. Shown beside it: the non-escalated share (no escalation record / `N`), verified containment (less false resolutions) and the false-resolution rate | A10.1 `resolution_status`; escalation records |
| KPI-G5 | Customer Effort Score | "Ease of issue resolution (1-7 scale)" | mean ease rating, 7 = very easy | Numerator: sum of ratings. Denominator: respondents | Monthly survey item; implicit effort (turn count, repeat contacts) shown as context |
| KPI-G6 | Incorrect Advice Rate | "Conversations containing wrong financial info" | conversations with at least one confirmed incorrect financial statement or personalised advice, divided by conversations checked. The count is reported as well, because the target is zero | Numerator: confirmed cases from (a) the automated delivered-figure and advice checks on every conversation and (b) the compliance audit sample. Denominator: `N` for (a); the audit sample for (b) | DM-12 hard-zero counters (GR-OUT-01, GR-ADV-06); audit labels; incident records |
| KPI-G7 | Customer Retention Impact | "Correlation between AI support experience and retention" | Measures and analysis are defined in `outcome-tracking.md` section 6: retention at 90 days by support-experience group for the quarter, reported as a correlation, with the adjusted comparison beside it | Population: identified customers with at least one conversation in the quarter | A10.1 fields joined to the customer record by pseudonymised ID; retention flag from the bank's records |

### 4.2 Targets, owners, alerts and anti-gaming

| ID | Target (brief) | Frequency (brief) | Owner (proposal) | Warn / critical (proposal) | Anti-gaming notes |
|---|---|---|---|---|---|
| KPI-G1 | at least 4.5 (baseline 3.2, A1.1) | Weekly | Head of Customer Experience | rolling 1-hour CSAT below 4.3 with 30 or more ratings / weekly below 4.5; response rate below 15 percent is its own warning | The ask rule is fixed in `csat-signals.md` section 3.1 and does not depend on sentiment: escalated conversations are surveyed after the human closes, and only the listed exclusions apply (for example ESC-011). Shown by outcome class with the response rate. The agent never asks for a high rating. Bias correction is `csat-signals.md` section 6 |
| KPI-G2 | at least 50 | Monthly | Head of Customer Experience | below 55 / below 50 | Random sampling, not sampling of satisfied customers; sample size and interval shown. Asked about "NexBank AI support", as the brief words it |
| KPI-G3 | at least 70% | Weekly | CX Team with Product | below 72 / below 70 | "Return" is checked by a job, not declared by the agent. Closing a conversation early lowers this metric once the 7-day window matures. Anonymous conversations cannot be linked to a return and are reported as a separate line. Reported with and without the mandatory-escalation intents (`outcome-tracking.md` section 2.2) |
| KPI-G4 | at least 70% (industry benchmark 65, A1.4) | Weekly | CX Team with Product | rolling 1-hour below 70 for 2 windows / weekly below 70 | Shown with the non-escalated share, KPI-G3, the missed-escalation rate (EQ-02) and the de-escalation rate (EQ-09). The gap between the non-escalated share and containment is the dropped share and is watched as its own number. Containment gained by not escalating is caught by EQ-02; gained by false closure, by KPI-G3 and verified containment. "Resolved" is decided by evidence in the state, not by the agent's wording (`outcome-tracking.md` section 2.2). No team is rewarded on containment alone |
| KPI-G5 | at least 5.5 | Monthly | CX Team | below 5.7 / below 5.5 | Shown with turn count and repeat contacts so a short but unhelpful conversation is not read as low effort |
| KPI-G6 | 0% (industry benchmark below 2, A1.4) | Daily | Regulatory Compliance Manager | not applicable / any confirmed case: immediate page, at least SEV1 (`incident-response-playbook.md` section 2) | A zero from too small an audit sample is not a zero: the audited count and its upper bound are shown. Cases are never reclassified as "tone" to avoid the count; the reviewer, not the owning team, assigns the class |
| KPI-G7 | Positive | Quarterly | Head of Customer Experience with analytics | correlation not above 0 / significantly negative | A correlation is not a cause; the matched comparison and the confidence interval are reported, and the metric is never used to rank teams |

### 4.3 Customer satisfaction framework

The brief calls this folder the "Customer satisfaction framework and dashboard specifications" (repository structure, p.62) and the Day 12-13 deliverable the "CSAT framework with dashboard wireframes" (p.60). The framework is the three survey measures below, the signals around them and the panels that show them. Survey mechanics and weighting are specified once, in `docs/learning-pipeline/csat-signals.md`, and are linked here, not restated.

| Element | Specification | Where it is defined |
|---|---|---|
| CSAT (KPI-G1) | One rating, 1 to 5, with an optional comment, asked when the conversation closes; for an escalated conversation, after the human closes it, with the AI part and the human part asked separately. Target at least 4.5 (A8.2, A1.4); baseline 3.2 (A1.1); reported weekly, with a rolling 1-hour value on the real-time dashboard | `csat-signals.md` section 3.1 |
| Not asked | Conversations that ended in ESC-011; fraud and security conversations still open with a human team (asked after the case closes); sessions with no customer message; a customer surveyed in the last 7 days; opted-out customers. The ask never depends on sentiment | `csat-signals.md` section 3.1 |
| Response rate | Planning assumption 15 percent (D-99), shown beside every CSAT value; a fall of a quarter against the 28-day mean is a survey-fault alert | `csat-signals.md` sections 3.3 and 9 |
| Bias correction | The raw mean is the brief's metric; the non-response-weighted mean is shown beside it, and a gap above 0.3 is an alert | `csat-signals.md` section 6 |
| NPS (KPI-G2) | Monthly, a separate survey to a random sample of customers who used the agent in the month; one 0 to 10 likelihood-to-recommend question about "NexBank AI support"; never in the post-chat prompt; a customer is asked at most once a quarter (proposal). Target at least 50 | This document, section 4.1 |
| CES (KPI-G5) | Monthly, on the same separate survey as NPS: one 1 to 7 ease question about the most recent resolved issue, 7 = very easy (proposal). Target at least 5.5 | This document, section 4.1 |
| Signals without a survey | In-conversation sentiment check at natural breakpoints; implicit signals (resolution without escalation, return visits, time to resolution); the silent-dissatisfaction detector; sentiment trajectory slope (KPI-L4) and recovery rate (KPI-A7) | `csat-signals.md` sections 2, 4 and 5; `sentiment.md` |
| Attribution | A rating is evidence about a conversation handled by one version tuple; attribution to agent actions follows the Day 11 method. A rating is never a training label by itself | `csat-signals.md` sections 3.2 and 7 |
| Satisfaction after escalation | EQ-12 compares escalated and contained CSAT; EQ-05 (customer had to repeat) explains much of a gap | `docs/escalation/queue-management.md` section 8 |
| Where it is shown | Real-time panel C (rolling 1-hour CSAT with `n`); Daily panels B and C (trend, funnel "satisfied" stage); Weekly panel A (week over week, with NPS and CES) and panel D (benchmark 4.0+) | `dashboards.md` sections 2 to 4 |
| Retention link (KPI-G7) | Quarterly correlation of support experience with retention, with the adjusted comparison | `outcome-tracking.md` section 6 |
| Owner | The Customer Experience team "owns satisfaction metrics" (A1.1); the CEB receives the weekly view | A1.1, A1.3 |

## 5. Operational metrics (A8.3)

### 5.1 Definitions

| ID | Metric | Brief definition | Formula | Numerator / denominator | Data source |
|---|---|---|---|---|---|
| KPI-O1 | Average Handle Time | "Conversation duration from start to resolution" | mean of (resolution time minus first customer message time) over resolved conversations | Numerator: sum of durations, including queue wait and human handling for escalated conversations; time after an inactivity timeout is excluded. Denominator: conversations with `resolution_status` `resolved_ai` or `resolved_human`. Reported in total and for each of the two | Gateway timestamps; A10.1 `resolution_status`, `turn_count` |
| KPI-O2 | Escalation Rate | "Conversations requiring human handoff" | conversations with an escalation record / `N` (as `outcome-tracking.md` section 4.3) | Numerator: conversations with an escalation record in the sense of section 1.1. Denominator: `N`. Split into mandatory and discretionary triggers, and by trigger, priority and queue | Escalation records (`EscalationDecision`); A10.1 `resolution_status`; A10.2 `action_taken` = escalate |
| KPI-O3 | System Uptime | "AI agent availability and responsiveness" | (minutes in period minus down minutes) / minutes in period | A minute is down when the synthetic probe conversation fails, or its first response exceeds 30 seconds, or more than 5 percent of live turns in that minute return an error (proposal). Planned maintenance counts as down. Minutes in template-only mode are up and are reported as degraded | Synthetic probe every minute; turn error counts |
| KPI-O4 | Concurrent Capacity | "Simultaneous conversations without degradation" | the highest number of simultaneous conversations held for 30 minutes in the weekly load test with no degradation | No degradation = 95th percentile turn latency inside the 3-second budget (D-07), error rate below 0.1 percent and no lost sessions (proposals) | Load-test harness; A10.2 `response_latency_ms` |
| KPI-O5 | Knowledge Base Coverage | "Customer queries addressable by current KB" | addressable / sampled | Numerator: sampled knowledge-seeking customer queries for which retrieval returns decision `answer` and a grounded answer is delivered. Denominator: a monthly random sample of real knowledge-seeking queries, weighted by volume. A gap entry is not coverage | Retrieval decision log (`retrieval-pipeline.md` section 14); A10.2 `knowledge_items_retrieved`; reviewer check on the sample |
| KPI-O6 | Model Drift Score | "Performance drift from baseline" | absolute difference between the baseline value and the current value of each model's primary metric on the fixed evaluation set; the largest value across models is the headline | One value per model: intent classifier, entity extractor, sentiment, advice classifier, retrieval. Guardrail classifiers are DM-11 (a) | Weekly evaluation runs; release metadata. The Day 11 learning-pipeline specification owns the drift method; where it differs, it prevails and this row links to it |

### 5.2 Targets, owners, alerts and anti-gaming

| ID | Target (brief) | Frequency (brief) | Owner (proposal) | Warn / critical (proposal) | Anti-gaming notes |
|---|---|---|---|---|---|
| KPI-O1 | <8 minutes | Daily | CX Team (operations) | above 7 / above 8 for the day | Shown with KPI-G3 and false resolutions: shortening conversations by closing early is visible at once. Queue wait is included, so slow handoffs cannot be hidden in a separate number |
| KPI-O2 | <30% | Daily | CX Team; Risk Committee for P0 mix | rolling 1-hour at or above 27 / at or above 30 for 2 windows | Always shown with EQ-01 (premature) and EQ-02 (missed). The rate must not be lowered by suppressing triggers: P0 and rule-replay misses are hard zeros. Cancelled escalations are shown, not hidden |
| KPI-O3 | at least 99.9% (43.2 minutes of downtime in a 30-day month) | Real-time | Product Engineering | 50 percent of the monthly allowance used / allowance exhausted, or any outage of 5 minutes | Maintenance is not excluded. Responsiveness is part of the definition, so a system that answers after the 30-second ceiling is down |
| KPI-O4 | at least 10,000 | Weekly load test | Product Engineering | below 11,000 / below 10,000 | The test uses a realistic turn mix with tool calls and retrieval, not idle sessions; the script and mix are versioned |
| KPI-O5 | at least 90% | Monthly | KB owners (Customer Experience) with NLU Team | below 91 / below 90 | Measured on real queries, not on the evaluation set the KB was tuned on. Publishing an entry without approved content does not count; an answer that is ungrounded fails the reviewer check |
| KPI-O6 | <0.05 | Weekly | ML Team | 0.04 or more / 0.05 or more (same levels as DM-11) | The evaluation set is fixed and versioned; changing it resets the baseline through change control, never silently |

The 43.2-minute figure is 30 days times 24 hours times 60 minutes times 0.001, recomputed by script.

## 6. Other measures the brief names

These are not in the A8 tables but the brief states a figure or a duty for each. IDs use the letter A (additions to the A8 list).

| ID | Measure | Brief source | Formula | Target | Owner (proposal) |
|---|---|---|---|---|---|
| KPI-A1 | KB retrieval latency | A2.3 p.7; task statement p.1 ("sub-200ms retrieval") | 95th percentile of retrieval latency per request | maximum 200 ms (brief). The 150 ms badge figure and the stage budget are in `retrieval-pipeline.md` | NLU Team |
| KPI-A2 | Repeat contact rate | A5.3 p.15 ("repeat contact tracking (7/14/30 days)") | identified customers with a further conversation on the same issue within 7, 14 and 30 days, divided by identified customers with a resolved conversation | Reported; feeds KPI-G3 and false-resolution detection | CX Team |
| KPI-A3 | Safety suite pass rate | A5.4 p.15 (minimum 200 cases that "must pass before any model update") | Defined once as DM-13 | 100 percent (brief) | ML Team; Risk Committee gate |
| KPI-A4 | Time to detect | A8.4 p.21 ("within 15 minutes of occurrence") | time from the start of an anomaly to the alert reaching its owner, per alert | within 15 minutes (brief) | Platform on-call |
| KPI-A5 | Supervisor review throughput | A5.1 p.15 ("target: 50 reviews per supervisor per day") | reviews completed / supervisors on shift; and the share of sampled items reviewed within 24 hours (DM-14) | 50 per supervisor per day (brief) | Review leads |
| KPI-A6 | Clarification rate | A9.2 p.24 (Robotic Loop) | customer turns answered with a clarification question / customer turns; and conversations with 3 or more consecutive rephrase requests (must be 0) | Reported; counter-metric to KPI-L2 | NLU Team |
| KPI-A7 | Sentiment recovery rate | Case Study 5 p.54 | conversations that start below -0.5 and meet the recovery definition of `sentiment.md` section 4 / conversations that start below -0.5 | Reported | CX Team |
| KPI-A8 | Resolution rate by category | A1.2 pp.3-4 | resolved conversations (by the agent or a human) / conversations, per A1.2 category, against the transcript baseline (for example 94 percent for balance and statement, 58 percent for complaints, 42 percent for product recommendation) | At or above the A1.2 baseline in every category (proposal) | CX Team |
| KPI-A9 | Benchmark comparison | A1.4 p.5 | containment, CSAT and incorrect-advice rate against the industry benchmark (65 percent, 4.0+, below 2 percent) and competitors A to C (35, 52 and 48 percent containment) | Shown on the weekly dashboard (A8.5 "competitive benchmarking") | Head of Customer Experience |

## 7. Guardrail and escalation metrics (linked, not redefined)

| Area | Metrics | Where defined | How this framework uses them |
|---|---|---|---|
| Guardrails | DM-01 trigger rate, DM-02 action mix, DM-03 block and redirect rate, DM-04 per-guardrail false positives, DM-05 end-to-end false positives, DM-06 near-miss rate, DM-07 output-layer catch rate, DM-08 adversarial attempt rate, DM-09 adversarial success count, DM-10 guard latency, DM-11 drift, DM-12 hard-zero counters, DM-13 safety suite status, DM-14 review coverage, DM-15 fallback load, DM-16 viral-risk indicator | `docs/guardrails/monitoring-dashboard.md` section 4 | KPI-L6 is DM-05. KPI-G6 reads DM-12. KPI-O6 for guardrail classifiers is DM-11. KPI-A3 is DM-13. DM-15 counts ESC-003 and ESC-014 fallbacks and is shown beside KPI-O2 |
| Escalation quality | EQ-01 premature, EQ-02 missed, EQ-03 wrong queue, EQ-04 late, EQ-05 repeat information, EQ-06 failed handoff, EQ-07 SLA attainment, EQ-08 package completeness, EQ-09 de-escalation, EQ-10 queue abandonment, EQ-11 time to protective action, EQ-12 post-escalation CSAT | `docs/escalation/queue-management.md` section 8 | Counter-metrics to KPI-O2 and KPI-G4 |
| Retrieval | Recall@5, MRR, nDCG@5 and the hard-zero retrieval counters | `docs/knowledge-base/retrieval-pipeline.md` (D-47) | Diagnostics under KPI-L5 and KPI-O5 |
| Sentiment model | agreement with human labels, ESC-004 precision and recall, sarcasm recall | `docs/intent-taxonomy/sentiment.md` section 9 | Diagnostics under KPI-L4 and EQ-01, EQ-02 |

## 8. Metrics that must be read together

A single number can be improved by damaging another. The pairs below are shown on the same panel, and no metric in the left column is reported without its partner.

| Headline | Counter-metric | The failure it exposes |
|---|---|---|
| KPI-G4 containment | EQ-02 missed escalations; KPI-G3; non-escalated share; verified containment | Containing what should have been escalated; false closure counted as success; a low escalation rate hiding dropped customers |
| KPI-O2 escalation rate | EQ-01 premature; EQ-02 missed | Over-escalation or suppression |
| KPI-O1 handle time | KPI-G3; KPI-A2 | Rushed closures |
| KPI-L2 intent accuracy | KPI-A6 clarification rate | Asking instead of deciding |
| KPI-L5 retrieval relevance | KPI-O5 coverage | Answering only the easy questions |
| KPI-L6 guardrail false positives | DM-12 hard zeros; DM-09 | Loosening safety to look smoother |
| KPI-L7 confidence distribution | accuracy above 0.7; calibration error | Over-confidence |
| KPI-G1 CSAT | response rate; CSAT by outcome class | Selective surveying |
| KPI-L1 first response time | share of template-only turns | Speed bought with quality |

Two rules for use: targets are never set on a counter-metric-free basis in objectives for a team, and the safety metrics (KPI-G6, DM-12, EQ-02 for P0, KPI-A3) are gates, not trade-offs. An improvement that raises CSAT but moves a gate is rejected (A5.4, Part B Level 5 unlock condition).

## 9. Regulatory reporting (A10.3)

The brief lists four reports. This table maps each to the metrics that feed it; the report format and filing are compliance processes (dependency G-04 in `regulatory-mapping.md`).

| Report (A10.3) | Content the brief names | Metrics used |
|---|---|---|
| Monthly AI interaction summary for RBI | volume, escalation rates, complaint categories | `N` by channel and intent; KPI-O2 by trigger and priority; complaint tickets by CMP-001 tertiary category (GR-REG-19) |
| Quarterly customer complaint analysis per Banking Ombudsman requirements | complaint analysis | Complaint counts, categories, ages and outcomes; ESC-002 and ESC-010 volumes; KPI-A2 for complaints |
| Annual AI system audit report | accuracy, fairness and safety metrics | KPI-L2, KPI-L3, KPI-L5, KPI-G6; fairness cuts of EQ-01, EQ-02 and GR-REG-17 test results; DM-12, KPI-A3 |
| Ad-hoc regulatory query responses within 48 hours | not specified | Any metric by conversation ID through the audit trail (Day 14) |

## 10. Decisions and open items

Audit amendment: D-162 (containment is resolved by the AI, glossary p.68; the non-escalated share is a named secondary). Decision: D-132 (formulas where the brief gives one line, the reading of "escalation record", percentile for first response time, handle-time scope, uptime definition, owners, alert thresholds, anti-gaming pairs). Definitions owned by the Day 11 documents (outcome classes, first contact resolution, CSAT weighting, retention analysis, drift) are linked, not restated.

Open items:

1. Owners are proposals based on A1.1, A1.3 and the A12.3 parameter owners; the brief names no metric owners except that the Customer Experience team owns satisfaction metrics.
2. Alert thresholds need calibration in the shadow period, as do the guardrail thresholds they sit beside.
3. First contact resolution cannot be verified for anonymous conversations; the share affected must be measured.
4. The NPS and CES survey design (sampling, timing, wording) is a CEB decision.
5. The drift method is owned by the Day 11 specification; KPI-O6 must be reconciled with it at the Day 15 audit.
6. Whether a `silent_case` should count in the escalation rate is a definitional choice made here on the conservative side.
7. Containment is read from the brief's glossary as resolved by the AI (D-162). The Day 11 documents first defined it as "no escalation record"; `outcome-tracking.md` section 4.3 and `ab-testing.md` section 4.1 carry the matching edit, and any other Day 11 text that treats containment as 1 minus the escalation rate should be read as the non-escalated share.
