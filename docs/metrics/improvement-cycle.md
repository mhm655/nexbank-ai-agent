# Improvement Cycle

Brief refs: A8.4 p.21 ("Candidates must specify a closed-loop improvement cycle connecting metrics to actions": DETECT, DIAGNOSE, DESIGN, DEPLOY, VALIDATE, DOCUMENT), A8.5 p.22 (dashboards that feed it), A5.1 p.15 (propagation: "immediate for safety issues, batched daily for quality, weekly for style"), A5.4 p.15 (safety suite, gradual rollout 1% > 5% > 25% > 100%, circuit breaker), A11.3 pp.31-32 (accountability: decisions traceable; who designed, who approved), A12.3 p.34 (parameter owners and change processes), A1.3 p.4 (Customer Experience Board and Risk Committee), Part D Day 12-13 p.60. Related: `kpi-framework.md` (the metrics), `dashboards.md` (where anomalies appear), `docs/learning-pipeline/overview.md` section 2 (the same six steps as run by the learning pipeline), `docs/learning-pipeline/safety-invariants.md` section 5 (gates G0 to G9), `docs/learning-pipeline/ab-testing.md` (experiments), `docs/guardrails/incident-response-playbook.md` (incidents), `docs/knowledge-base/maintenance-workflow.md` (KB changes).

**Status.** The brief names the six stages and gives one number: anomalies surfaced "within 15 minutes of occurrence". Roles, artefacts, timings other than the 15 minutes, the diagnosis table and the prioritisation score are proposals (D-133). The Day 11 learning-pipeline documents already specify how a candidate change is built, gated, rolled out and monitored; this document does not repeat them. It specifies the part that starts from a metric: how an anomaly becomes a finding, how the finding is traced to a component, how competing fixes are ranked, and what is written down at the end. The two worked examples are illustrative: their figures are invented to show the process and are not measurements.

## 1. The cycle at a glance

| Stage | The brief's text (A8.4) | Input | Output artefact | Accountable (proposal) | Timing |
|---|---|---|---|---|---|
| DETECT | "Automated monitoring dashboards surfacing metric anomalies and performance degradation patterns within 15 minutes of occurrence" | Metric streams; alert rules | Finding (section 2.3) | Platform on-call for delivery; the metric's owner for the finding | 15 minutes (brief) for real-time signals; next daily or weekly report for sample-based metrics |
| DIAGNOSE | "Root cause analysis framework connecting metric degradation to specific system components (NLU accuracy, knowledge gaps, generation quality, escalation logic)" | Finding; logs; review labels | Diagnosis with one named component and evidence | Finding owner, with the component's team | First diagnosis within 1 working day (proposal); incidents follow the playbook timings |
| DESIGN | "Improvement hypothesis generation and prioritisation framework based on impact (metric improvement potential), effort (engineering resources), and risk (potential for unintended consequences)" | Diagnosis | Scored hypothesis and a pre-registration draft | Component owner | Ranked at the weekly improvement review (proposal) |
| DEPLOY | "Staged rollout with A/B testing for all improvements affecting customer-facing behaviour" | Approved candidate | Released version or rejection | Per gate: `safety-invariants.md` section 5 | The ladder and dwell times of `ab-testing.md` section 3 |
| VALIDATE | "Post-deployment monitoring confirming improvement hypothesis and detecting unintended side effects" | Cohort metrics; counter-metrics | Confirmed, partly confirmed or rolled back | Experiment owner; Risk owner for safety | 28 days of monitoring (Day 11 proposal) |
| DOCUMENT | "Knowledge capture documenting what was learned from each improvement cycle for institutional memory" | All of the above | Improvement record (section 7) | Experiment owner | Within 5 working days of the decision (proposal) |

The cycle is closed in two ways. Every VALIDATE result updates the baselines and alert bands that DETECT uses, and every confirmed defect becomes a regression case, so the same failure is detected automatically next time.

## 2. DETECT

### 2.1 Three detection lanes

| Lane | Metrics | Mechanism | Detection time |
|---|---|---|---|
| Real-time | First response time, uptime, escalation volume and rate, SLA attainment, guardrail trigger rates, hard-zero counters, rolling 1-hour CSAT and containment, fallback load | Stream aggregation in 5-minute windows; threshold and baseline-deviation alerts (`kpi-framework.md`, `monitoring-dashboard.md` section 6, `queue-management.md` section 9) | Within 15 minutes (brief) |
| Daily | The leading indicators that need labels (intent and entity accuracy), sentiment slope, retrieval relevance, handle time, incorrect-advice audit, top unresolved intents, supervisor correction summary | Daily batch at 06:00 local (the Day 10 and Day 11 cut) | Next daily report |
| Weekly and slower | CSAT, first contact resolution, containment, confidence distribution, drift, KB coverage, NPS, CES, retention | Weekly review; monthly and quarterly surveys | Next report; a 7-day window must mature for first contact resolution |

The 15-minute requirement can only bind the first lane: a metric that needs human labels or a 7-day window cannot be detected in 15 minutes. Each slow metric therefore has a fast proxy on the real-time lane, so degradation is seen early and confirmed later.

| Slow metric | Fast proxy |
|---|---|
| CSAT (weekly) | Rolling 1-hour CSAT (shown only with 30 or more ratings); predicted-dissatisfaction share; sentiment slope |
| First contact resolution (weekly, 7-day window) | Provisional resolution at close; unresolved-dropped share; repeat contacts arriving today |
| Containment (weekly) | Rolling 1-hour containment and escalation rate (A8.5) |
| Intent accuracy (daily, labelled) | Share of turns below 0.70 and below 0.40; clarification rate; ESC-003 volume |
| KB coverage (monthly) | Gap and degrade decision share; ESC-008 volume; top unresolved intents |
| Incorrect advice (daily audit) | Hard-zero counters on every conversation (DM-12); output-layer catch rate (DM-07) |
| Drift (weekly) | Score-distribution shift and trigger-rate z-scores (DM-11 b and c) |

### 2.2 The 15-minute budget

| Step | Budget (proposal) |
|---|---|
| Event written to the Audit and Telemetry Bus and available to the aggregator | 1 minute |
| Evaluation: two consecutive 5-minute windows (one window for "immediate" signals such as a hard-zero counter) | 10 minutes |
| Alert routed and delivered to the owner | 1 minute |
| Margin | 3 minutes |
| Total | 15 minutes |

Time to detect is itself measured (KPI-A4). Requiring two windows trades about 5 minutes for fewer false alerts; signals marked immediate skip the second window.

### 2.3 What counts as an anomaly, and the finding

An anomaly is any of: a brief target breached; a warn or critical threshold crossed; a deviation from the metric's own same-hour, same-weekday baseline beyond its band; a gap between segments (language, channel) beyond the fairness margin; a counter-metric moving against its headline (`kpi-framework.md` section 8); a sudden fall to zero of something that normally fires.

A finding is the record that starts the cycle. Fields: finding ID; metric and segment; observed value, baseline and window; first seen; detection lane; severity (SEV0 to SEV3 as in the playbook, or "trend" for non-incident findings); version tuple (prompt, model, KB epoch) in force; linked alert; owner; status.

Routing: a finding that involves a hard-zero counter, a missed P0 escalation or a safety suite failure is an incident and follows `incident-response-playbook.md` (the immediate lane of A5.1). Everything else enters the daily triage (quality lane) or the weekly review (style lane).

## 3. DIAGNOSE

### 3.1 Method

Five questions, asked in this order, each answered with evidence from the logs. The answer to the first that says "yes" usually names the component.

1. **Did something change?** Compare with the version tuple and the release calendar (model, prompt, KB epoch, parameter, rule file, queue staffing, an upstream banking API). A step change at a release points at that release.
2. **Is it localised?** Cut by intent, language, channel, authentication level, time of day. A problem in one language or one intent points at NLU data or a KB entry, not at the platform.
3. **Which stage first went wrong?** Walk a sample of affected conversations turn by turn through the pipeline order: input guard, NLU, state, policy, retrieval, tools, generation, output safety, escalation. The supervisor correction record's `component` field (`supervisor-corrections.md`) records the answer.
4. **Is the rule right but the input wrong, or the reverse?** For escalation and guardrail findings, the rule-replay job separates a correct rule fed a wrong score (an NLU problem) from a rule that was not applied (a router defect) and from a rule that is itself too tight or too loose (an owner decision).
5. **Is it the customer mix?** A marketing campaign, an outage at a payment network or a fraud wave changes what customers ask. The metric moved; the system did not.

### 3.2 From metric to component

The brief names four components (NLU accuracy, knowledge gaps, generation quality, escalation logic). The table adds the others the architecture has. "Evidence" is what must be shown before the diagnosis is accepted.

| Symptom | Likely component | Evidence to collect | Typical fix class (Day 11) |
|---|---|---|---|
| KPI-L2 or KPI-L7 down; clarification rate or ESC-003 up | **NLU accuracy** | Confusion matrix on the labelled sample; per-language and per-intent cut; new phrasings in low-confidence turns | U4 retrain with new utterances; U3 threshold only with an A/B |
| KPI-L3 down; wrong amounts or dates confirmed back | NLU (entities) | Entity-level errors by type; validator rejections | U4; validator rule through safety change control if it is a rule |
| KPI-L5 down; gap or degrade share up; KPI-O5 down; ESC-008 up | **Knowledge gaps** | Top unanswered queries; entries near expiry; stale flags; retrieval gold-set results | U1 KB change request; U4 retrieval model if the content exists but is not found |
| Output-layer catch rate up (DM-07); tone or commitment faults; CSAT down with accuracy steady | **Generation quality** | Rung distribution; failing check (C1 to C7); template share; prompt version diff | U2 prompt layers 3 and 4; U5 generation model version |
| EQ-01 up (premature) | **Escalation logic** or its inputs | Rule replay: was the condition true? If not, which score was wrong (sentiment, sarcasm, amount) | U4 for the score; an owner decision for a threshold (ESC-004 threshold is CEB-owned, A12.3); never an automatic change |
| EQ-02 above zero (missed) | **Escalation logic** | Rule replay miss (router defect) or classifier miss (NLU or Input Guard) | Defect fix; new suite case; U4 |
| EQ-03 up (wrong queue) | Escalation logic (precedence) | Owner trigger against the precedence table; secondary triggers present | Change to `config/escalation_rules.yaml` through its owner and the Risk Committee (excluded class X5) |
| EQ-07 down (SLA attainment) with EQ-01 and EQ-02 steady | Queue operations, not the agent | Arrivals against staffing; overflow and after-hours share | Staffing or rebalancing (`queue-management.md` section 7) |
| KPI-L1 or KPI-O3 down; ESC-014 or fallback load (DM-15) up | Platform or an upstream API | Stage latency; tool error codes; circuit state | Engineering fix; no behaviour change, so no A/B |
| KPI-L6 up (false positives) | Guardrail | Per-guardrail estimate (DM-04); reviewed samples | Safety change control only (excluded class X3) |
| KPI-G3 down with KPI-G4 steady | False resolutions or abandonment | Outcome classes; repeat-contact reasons; where conversations stop | Depends on the cause; often U1 or U2 |
| KPI-O1 up | Any of: clarification loops (NLU), long tool waits (platform), queue wait (operations) | Time split by stage and by outcome | By cause |
| KPI-G1 down in one language only | NLU or templates for that language | Per-language intent accuracy, sentiment confidence, template review | U4; native review of templates |

A diagnosis names one primary component, the evidence, the conversations examined, what was ruled out, and the confidence (high, medium, low). A low-confidence diagnosis leads to a cheap test of the diagnosis, not to a fix.

## 4. DESIGN

### 4.1 Hypothesis

One sentence in a fixed shape: "If we change [one thing] for [which conversations], then [primary metric] will move from [baseline] to [target] within [window], and [counter-metrics and gates] will not get worse, because [mechanism from the diagnosis]." A hypothesis that cannot name its counter-metrics is not ready.

### 4.2 Prioritisation on impact, effort and risk

The brief names the three factors. The scoring below is a proposal.

| Factor | 1 | 3 | 5 |
|---|---|---|---|
| Impact (metric improvement potential) | Affects under 1 percent of conversations, or a diagnostic metric only | Affects 1 to 10 percent, or moves one brief KPI inside its target | Affects over 10 percent, or brings a breached brief target back, or removes a safety gap |
| Confidence in the diagnosis | Low: plausible, untested | Medium: consistent evidence from a sample | High: reproduced, or confirmed by rule replay |
| Effort (engineering resources) | Days: a KB entry, a template, a notice | Weeks: a prompt layer, a parameter with its A/B | Months: a retrain with new data, a new integration |
| Risk (potential for unintended consequences) | Content-only change, instantly reversible | Changes wording or a non-safety threshold; needs an A/B | Touches a model for a CRITICAL intent, a parameter a trigger reads, or anything in the excluded list |

Score = Impact x Confidence / Effort. Risk is not averaged into the score: it sets the path. Risk 1 or 3 follows the gates of its update class; risk 5 needs the Risk Committee at gate G5 and cannot be the first choice if a lower-risk hypothesis addresses the same finding. This follows the Day 11 order of preference: fix with the lowest update class that works (U1 before U2 before U3 before U4 and U5).

Three rules override the score:

1. A safety finding is fixed first, whatever its score (A5.1 immediate lane). Containment by a tighten-only lever comes before any redesign.
2. A change that would raise a brief KPI by weakening a gate metric is rejected at design time (`kpi-framework.md` section 8).
3. No hypothesis may give a customer segment a different threshold (A11.3).

### 4.3 Who may change what

| Change | Owner and process | Source |
|---|---|---|
| KB entry | The entry's approval chain; KB workflow | `maintenance-workflow.md` |
| Prompt layers 3 to 5 | Prompt owner; Risk Committee review for layers 3 and 4 | A12.2; `overview.md` section 3.1 |
| `intent_confidence_threshold`, `knowledge_retrieval_top_k`, `retrieval_confidence_threshold` | NLU Team; A/B test required | A12.3 |
| `escalation_sentiment_threshold` | CX Team; CEB approval | A12.3 |
| `max_conversation_turns` | Product; standard change; not below 15 without the escalation owner | A12.3; `ab-testing.md` section 11.1 |
| `model_temperature` | ML Team; A/B test and Risk Committee review | A12.3 |
| `session_timeout_minutes`, `guardrail_strictness_level` | Security, Risk Committee; Risk Committee approval | A12.3 |
| Escalation rules (precedence, sub-rules, additions, overflow, hours) | Escalation owner with the Risk Committee; queue hours and staffing with CX operations | `overview.md` section 3.2 (X5) |
| Guardrails, rule layer, prompt layers 0 to 2, the safety suite | Safety change control only | `safety-invariants.md` section 9 |
| Queue staffing and rebalancing | Queue owners | `queue-management.md` |

## 5. DEPLOY

The brief requires "staged rollout with A/B testing for all improvements affecting customer-facing behaviour". The mechanics are specified on Day 11 and are used as they stand:

| Element | Where it is specified |
|---|---|
| Gates G0 to G9 (scope, data, regression evaluation, fixed safety suite at 100 percent, red-team run, approval, shadow, canary 1 and 5 percent, A/B at 25 percent, full rollout) | `safety-invariants.md` section 5 |
| Rollout ladder 1% > 5% > 25% > 100% with minimum dwell and sample floors | `ab-testing.md` section 3 |
| Pre-registration, power, sequential looks, stopping rules | `ab-testing.md` sections 5 to 8 |
| Tier 0 constraints, including escalation rate non-inferiority and "P0 trigger rates must not fall" | `ab-testing.md` section 4.1 |
| Circuit breaker and automatic rollback | `monitoring-dashboard.md` section 8; `safety-invariants.md` section 7 |

What this document adds for escalation and metrics changes:

1. A change to `config/escalation_rules.yaml` is customer-facing behaviour. It is replayed against logged conversations before any exposure (the deterministic rules make this exact), and the replay report shows, per trigger, how many past conversations would have been routed differently.
2. Escalation-quality metrics are added to the experiment's constraints when a candidate touches sentiment, intent or the router: EQ-02 for P0 at zero, rule-replay misses at zero, EQ-01 and EQ-03 not worse than control.
3. Changes that do not alter what any customer is told or where they are routed (dashboard definitions, alert thresholds, staffing) need no A/B. They are logged in the change log with their owner.
4. A tighten-only containment lever (playbook section 5) is not an improvement and is not A/B tested; it is applied at once and reviewed afterwards.

## 6. VALIDATE

| Check | Question | Evidence |
|---|---|---|
| Hypothesis | Did the primary metric move as pre-registered? | The experiment report; matured cohorts for first contact resolution |
| Counter-metrics | Did any paired metric move the wrong way? | `kpi-framework.md` section 8 pairs for the changed component |
| Gates | Did any safety or Tier 0 metric move? | Hard-zero counters, suite status, EQ-02, false-positive rate |
| Segments | Did every language and channel share the gain? Did any get worse? | Per-slice results (A11.3) |
| Neighbours | Did the fix for one intent hurt adjacent intents? | Confusion pairs of `disambiguation.md`; per-intent cuts |
| Operations | Did queue load, handle time or SLA attainment shift? | `queue-management.md` section 8 |
| Persistence | Does the effect hold after novelty wears off? | 28-day monitoring and the holdback (`ab-testing.md` section 10) |

Outcomes: confirmed (keep; update baselines and alert bands); partly confirmed (keep or iterate, with the unexplained part recorded as a new finding); not confirmed (roll back or retire; the diagnosis is reopened); harmful (rolled back by the breaker or by decision; an incident review if a gate moved). A result is reported with its interval and sample size. "No significant change" is a result and is recorded as one.

## 7. DOCUMENT

One improvement record per cycle, kept in the experiment registry (`ab-testing.md` section 11.3) and summarised in the change log. It is written for someone who was not there.

| Field | Content |
|---|---|
| ID and title | `IC-<year>-<number>`; one line |
| Finding | Metric, segment, values, when detected, by which lane, time to detect |
| Diagnosis | Component, evidence, what was ruled out, confidence |
| Hypothesis and score | The sentence of section 4.1; impact, confidence, effort, risk; alternatives considered and why not chosen |
| Change | Update class, artefact and version before and after, approvals (who designed, who approved, A11.3) |
| Rollout | Stages, dates, cohort sizes, any breaker event |
| Result | Primary metric, counter-metrics, gates, segments, with intervals |
| Decision | Kept, iterated, rolled back, retired; by whom |
| What was learned | What was true that we did not know; what we believed that was false; what to check first next time |
| Follow-ups | New regression or suite cases (IDs), KB entries, alert or baseline changes, open findings |

Rules: a record is written for failed and abandoned cycles too; every confirmed defect yields at least one new test case (D-79 convention: new ID, never a reused one); records are never edited after closure, only appended; the weekly dashboard lists the records closed that week (A8.5).

## 8. Roles and cadence

| Role | DETECT | DIAGNOSE | DESIGN | DEPLOY | VALIDATE | DOCUMENT |
|---|---|---|---|---|---|---|
| Platform on-call | Responsible (alert delivery) | Consulted | | Responsible (rollout mechanics, rollback) | Consulted | |
| Metric owner (`kpi-framework.md`) | Accountable for the finding | Responsible | Consulted | Informed | Responsible (reads the metric) | Consulted |
| Component team (NLU Team, ML Team, KB owners, CX Team, Product Engineering) | Informed | Responsible | Responsible (hypothesis) | Responsible (candidate) | Consulted | Consulted |
| Experiment owner | | | Responsible (pre-registration) | Accountable | Accountable | Responsible |
| Statistician (independent) | | | Consulted | Consulted | Responsible (analysis) | Consulted |
| Supervisors and review leads | Responsible (labels for the daily lane) | Consulted | | Responsible (doubled sampling in canaries) | Consulted | |
| Risk Committee | Informed of SEV0 and SEV1 | Consulted on safety | Approves risk 5 and excluded-list changes | Gate G5 where required | Accountable for gate metrics | Informed |
| Customer Experience Board | Informed weekly | | Approves `escalation_sentiment_threshold`; consulted on tone | Informed | Informed of CSAT and effort results | Informed |
| Incident Commander | Accountable during an incident | Accountable during an incident | | Levers only | | Post-incident review |

Cadence (proposals, aligned with the Day 10 and Day 11 documents):

| Meeting or run | When | What happens |
|---|---|---|
| Real-time watch | Continuous | Alerts handled by on-call and queue supervisors |
| Daily triage | After the 06:00 batch | New findings assigned; quality-lane corrections turned into change requests |
| Weekly improvement review | Weekly, with the Weekly Strategic dashboard | Findings ranked by score; experiments reviewed; records closed; CEB and Risk Committee representatives attend |
| Monthly metric review | Monthly | NPS, CES, KB coverage; thresholds and baselines re-examined |
| Quarterly review | Quarterly | Retention impact; alert thresholds and the diagnosis table revised from the records |

## 9. Worked example 1 (illustrative): premature ESC-004 escalations in Hinglish

All figures in this example are invented to show the process. Nothing was measured.

| Stage | What happens |
|---|---|
| DETECT | The daily dashboard shows EQ-01 (a), detection error, for ESC-004 at an illustrative 24 percent for Hinglish against 9 percent for English; the bound for ESC-004 is 15 percent and the fairness margin is 2 points. Customer Retention queue arrivals are up in the same hours. Lane: daily (labels needed). The real-time proxy, ESC-004 volume by language, had drifted for several days without crossing its band. A finding is opened as "trend", owner CX Team |
| DIAGNOSE | Question 1: no release in the window. Question 2: localised to Hinglish. Question 3: reviewed conversations show the turns that fired contain emphatic idioms that the sentiment head scored below -0.7 with confidence above 0.70. Question 4: rule replay confirms the router applied ESC-004 correctly to the scores it was given, so the rule is right and the input is wrong. Component: NLU accuracy (sentiment head), not escalation logic. Confidence: high |
| DESIGN | H1: add labelled Hinglish idiom examples and retrain the sentiment head (U4). Impact 3, confidence 5, effort 3, risk 3: score 5.0. H2: lower `escalation_sentiment_threshold` (U3, CEB approval). Impact 3, confidence 3, effort 1, risk 5: score 9.0, but risk 5 and it would raise missed escalations in every language, so it is not chosen while H1 addresses the cause. H3: require 3 turns instead of 2. Rejected: it changes the brief's trigger. Hypothesis: "If the sentiment head is retrained with the new examples, EQ-01 (a) for ESC-004 in Hinglish will fall to 15 percent or less within the A/B window, and EQ-02 for ESC-004 will stay at or below 10 percent in every language, because the false streaks come from idioms the model has not seen." |
| DEPLOY | Gates G0 to G9 for class U4. The regression evaluation includes the ESC-004 precision and recall targets of `sentiment.md` section 9 and the counterfactual language-swap test. The fixed suite must pass at 100 percent, including the crisis cases, because the sentiment head shares an encoder with the crisis classifier. Ladder 1, 5, 25 percent with doubled supervisor sampling; escalation constraints from section 5 added |
| VALIDATE | Primary: EQ-01 (a) for Hinglish. Counter-metrics: EQ-02 for ESC-004 by language, CSAT of Hinglish conversations, Customer Retention arrivals. Gates: ESC-011 recall on the suite unchanged; no P0 trigger rate lower than control. Segments: the secondary languages checked for collateral change. Decision after matured cohorts and the 28-day monitoring |
| DOCUMENT | Record `IC-<year>-<number>`: the finding, the ruled-out threshold change and why, the new idiom examples as data lineage, the result with intervals, and new regression cases reserved after ESC-T-004-04 in `tests/escalation/`. Learned: a premature-escalation spike in one language is a data problem before it is a threshold problem; check rule replay first |

## 10. Worked example 2 (illustrative): a knowledge gap behind unresolved product conversations

All figures in this example are invented to show the process. Nothing was measured.

| Stage | What happens |
|---|---|
| DETECT | The Daily Performance dashboard's "top 10 unresolved intents" has PRD-003 `fd_rate_by_tenure` first for a week; the gap-decision share for PRD-003 is an illustrative 38 percent against 12 percent across product intents; XTR-01 human requests after a PRD-003 turn are up. KB coverage (monthly) has not yet reported; the proxy caught it. Finding opened as "trend", owner KB owners |
| DIAGNOSE | Question 1: no release. Question 2: localised to one tertiary intent, all languages. Question 3: retrieval returns the gap entry KB-ESC-014 with high confidence, and the agent correctly declines to state a rate. Nothing malfunctioned: the knowledge base holds the NexFD range and one illustration, and not a rate per tenure (D-26). Component: knowledge gap. Confidence: high |
| DESIGN | H1: publish a tenure-wise rate entry supplied and approved by the product owner (U1). Impact 3, confidence 5, effort 1, risk 3: score 15.0. The content cannot be written by the team; a rate that is not authoritative would be an AUTO-FAIL (A9.2), so the request goes to the entry's approval chain and the cycle waits for it. H2: reword the gap statement so it states the range first and offers a human second (U1, wording only). Impact 1, confidence 3, effort 1, risk 1: score 3.0; it can ship while H1 is pending. H3: let the model interpolate a rate. Rejected at design time: it weakens a gate metric (KPI-G6) |
| DEPLOY | KB workflow: candidate epoch, publish gates, shadow run, KB canary ladder, with the financial-accuracy check (GR-OUT-01) comparing every delivered rate with the entry. Rates entries carry a 90-day TTL and hard expiry, so the entry cannot outlive its review |
| VALIDATE | Primary: gap-decision share and unresolved-dropped share for PRD-003. Counter-metrics: KPI-G6 at zero and the delivered-figure counter (DM-12) at zero; ESC-013 offer acceptance (a clearer rate answer should not turn into advice); KPI-L5 for the new entry. If no approved content arrives, the record closes as "blocked on source" and the gap stays honestly handled |
| DOCUMENT | Record with the gap evidence, the dependency on the product owner, the two hypotheses and the rejected third. Follow-up: a staleness alert for the new entry and a hallucination-trap case for a tenure outside the table. Learned: an unresolved-intent spike with correct gap behaviour is a content request, not a model fault; the fix is slower because its author is outside the team |

In this specification no tenure-wise rate exists (A13.1 gives a range only), so example 2 shows the process and not a planned entry.

## 11. Decisions and open items

Decision: D-133 (detection lanes and proxies, the 15-minute budget, the five diagnosis questions and the symptom table, the prioritisation score, the improvement record, roles and cadence).

Open items:

1. The 15-minute budget depends on the telemetry pipeline's latency, which is an implementation choice; KPI-A4 measures whether it is met.
2. The scoring scales need a few real cycles before their cut-offs mean anything; they are reviewed quarterly.
3. Named owners for findings and the weekly review's membership are dependencies, as in the Day 10 and Day 11 documents.
4. The registry and the change log are specified as records, not as tools.
