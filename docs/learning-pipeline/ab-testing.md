# A/B Testing Framework and Experiment Governance

Brief refs: A8.4 (p.21: "DEPLOY: Staged rollout with A/B testing for all improvements affecting customer-facing behaviour"; "VALIDATE: Post-deployment monitoring confirming improvement hypothesis and detecting unintended side effects"), A12.3 (p.34: parameters, owners and change processes), A12.2 (p.33: only Layer 5 without RC review), A5.4 (p.15: gradual rollout 1% > 5% > 25% > 100%, circuit breaker), A8.2 (p.20: CSAT 4.5, FCR 70%, Containment 70%, Incorrect Advice Rate 0%), A8.3 (pp.20-21: AHT below 8 minutes, Escalation Rate below 30%, drift below 0.05), A8.5 (p.22: "A/B test results and pending experiment pipeline"), A1.1 (p.3: approximately 18,000 interactions daily), A11.2 (p.31: A/B testing as a mitigation for churn), A11.3 (p.31: consistent escalation thresholds, statistical fairness testing), Part D Day 11 (p.59: "traffic splitting, metric hierarchy, statistical significance", "experiment governance framework with approval workflows"), badge The Scientist (p.43: "Design A/B testing framework with proper statistical rigour"). Related: `safety-invariants.md` (gates G0 to G9), `docs/guardrails/monitoring-dashboard.md` section 8 (circuit breaker), `csat-signals.md` (weighting), `outcome-tracking.md` (FCR), `boss-level5.md` (worked example).

**Status.** The brief fixes: A/B testing for customer-facing improvements, the rollout ladder, the metric targets, the parameter owners and the 18,000 interactions per day. It gives no statistical parameters. Every statistical choice below (significance level, power, minimum effects, variance, response rate, design effects, looks, margins, durations) is a proposal (D-107 to D-111). All arithmetic was recomputed by script; no experiment has been run.

## 1. When an experiment is required

| Change | Experiment | Reason |
|---|---|---|
| Prompt layers 3 and 4 (U2), NLU and retrieval models (U4), policy ranker and generation model version (U5) | required | A8.4: customer-facing behaviour |
| A12.3 parameters marked "A/B test required" or "A/B test + RC review" | required | A12.3 |
| KB entry changes (U1) | the canary comparison of `docs/knowledge-base/maintenance-workflow.md`; a powered experiment only when the claim is a CSAT or FCR gain | a factual correction must not wait two weeks |
| Layer 5 operational notices; regulatory fast-track KB changes | none | time-critical information; suite, lint and instant rollback instead |
| Safety fixes after an S1 or an incident | none before release | the immediate lane (`overview.md` section 4); monitored after release as a canary |
| Anything in the excluded list X1 to X6 | not permitted as an experiment | the pipeline cannot change it; safety change control uses its own validation |

An experiment answers one question: does the candidate improve the customer outcome, without breaching any safety constraint. It is never used to find out whether a guardrail can be relaxed.

## 2. Randomisation unit

| Aspect | Decision (D-107) |
|---|---|
| Unit | the customer: the pseudonymised `customer_id` for authenticated conversations. A customer sees one arm for the whole experiment, across conversations and channels, so the 24-hour context carry-over (D-05) never mixes arms and the repeat-contact window stays inside one arm |
| Anonymous conversations | the session or device identifier assigned at the Gateway. If the session authenticates later it keeps the arm it started with (intention to treat); the customer's later conversations use the customer assignment |
| Assignment | `bucket = hash(experiment_salt + unit_id) mod 10,000`. A new salt per experiment removes carry-over between experiments. Buckets 0 to 9,999 are mapped to arms by range, so widening the exposure only adds buckets and nobody switches arm during a ramp |
| Why not the conversation or the turn | a turn-level switch would change the agent's behaviour mid-conversation (unsafe and unreadable); a conversation-level switch would give a returning customer two behaviours and would contaminate FCR, which is defined on return visits |
| Analysis unit | the conversation for FCR and operational metrics, the rating for CSAT. Because conversations of one customer are correlated, standard errors are clustered by customer; planning uses a design effect (section 6.2) |
| Excluded before assignment | staff test accounts and conversations opened by the red team. They are identified before randomisation, are never assigned and always get the control. Nothing that happens after assignment removes a unit from its arm |
| Protected flows, still analysed | crisis (GEN-007) and fraud (SEC-001) flows run on immutable templates and rules in both arms, so a candidate cannot alter them; sessions that enter safe mode (GR-ATK-04) or are rate-limited (GR-ATK-08) get the same protective behaviour in both arms. All of them keep their arm and stay in the primary analysis (intention to treat, section 9) and in the guardrail monitoring. No survey is sent in crisis, so those conversations contribute no rating. A pre-registered sensitivity analysis repeats the primaries without them |
| Fairness of assignment | assignment uses only the hash. No customer attribute (segment, balance, language, value band) is used to choose an arm (A11.3; case SS-LRN-20) |

## 3. Traffic split and the rollout ladder

The brief's ladder is 1% > 5% > 25% > 100%. The experiment is the 25% stage of that ladder.

| Stage | Candidate share | Concurrent control | Purpose | Minimum dwell (proposal) |
|---|---|---|---|---|
| Shadow | 0% (answers computed, not served) | all | decision and latency differences on live inputs | 24 hours |
| Canary 1 | 1% (180 conversations a day) | a 1% control bucket range fixed in advance | smoke test: gross faults, crashes, hard-zero events | 24 hours and at least 150 conversations |
| Canary 2 | 5% (900 a day) | 5% control range | guardrail rates, latency, sample ratio check, instrumentation check | 48 hours and at least 1,500 conversations |
| A/B | 25% (4,500 a day) | 25% control range (4,500 a day) | the powered comparison on CSAT and FCR; guardrail constraints | 14 days of exposure for the analysis; the arms then stay frozen at 25% each until the FCR final look on day 21, so returning customers keep their arm. Conversations started after day 14 are served and safety-monitored but are not in the primary analysis |
| Full | 100%, less a 5% holdback kept on control for 28 days | the holdback | long-term and novelty check; post-deployment regression monitoring | 28 days of monitoring |

Notes. The control at each stage is a concurrent, equal-sized, pre-declared bucket range, not "everyone else": equal arms give the simplest valid comparison, and the remaining traffic (50% at the A/B stage) stays available for a second experiment on a different surface. Comparison is always candidate against concurrent control, never against history (`monitoring-dashboard.md` section 8). Canary cohorts receive doubled review sampling (D-89).

Concurrency rules (proposal): at most one experiment per surface (prompt, parameters, NLU, retrieval, policy, KB epoch); two experiments on different surfaces may overlap only on disjoint bucket ranges with different salts; an experiment and an unrelated canary never share buckets; safety fixes pre-empt everything and are applied to all arms at once.

## 4. Metric hierarchy

Three tiers. A higher tier is never traded for a lower one.

### 4.1 Tier 0: guardrail metrics (hard constraints)

These decide whether the candidate may ship at all. They are not weighed against CSAT.

| Metric | Source | Constraint | Type |
|---|---|---|---|
| Hard-zero counters (DM-12): delivered figure mismatch, delivered full identifier, delivered advice verdict, cross-customer data, write without required auth, unescalated security-critical intent, audit gap | post-delivery audit, Tool Orchestrator re-check | zero in the candidate cohort; one event stops the experiment (trip condition 1) | absolute |
| Adversarial success count (DM-09); Incorrect Advice Rate (A8.2: 0%) | audit sampling, incidents | zero | absolute |
| Fixed safety suite (DM-13) | CI on the candidate | 100% (A5.4) | absolute |
| End-to-end guardrail false-positive rate (DM-05; A8.1 below 3%) | benign set and live sample | below 3% in the candidate cohort and not more than 0.5 points above control (trip condition 3) | gate |
| Trigger rate per guardrail (DM-01) | turn events | inside the control's band at the critical z-score (trip condition 4) | gate |
| Guard latency (DM-10) | turn events | inside budget (trip condition 5) | gate |
| First response time (A8.1 below 5 s); p95 turn latency below 3 s (D-07) | turn events | inside target in the candidate cohort; a breach blocks promotion (it is not one of the six breaker conditions) | gate |
| Model Drift Score (DM-11; A8.3 below 0.05) | evaluation runs | below 0.05 (trip condition 6) | gate |
| Escalation rate (A8.3 below 30%) | ESC records | not worse than control by more than 1.0 point (non-inferiority, section 7.4); P0 trigger rates (ESC-001, ESC-009, ESC-011, ESC-012) must not fall significantly | non-inferiority, two-directional for P0 |
| Containment (A8.2 70%) | `resolution_status` and escalation records | Containment is conversations resolved by the AI with no escalation record (`outcome-tracking.md` section 4.3, D-162). It is not 1 minus the escalation rate (that is the non-escalated share), so it is its own constraint: not lower than control by more than 1.0 point | non-inferiority |
| Average handle time (A8.3 below 8 minutes) | timestamps | not higher than control by more than 5% | non-inferiority |
| Complaint rate about the AI; S1 and S2 rates from doubled supervisor sampling | complaints, review tool | no S1 attributable to the candidate; S2 rate not above control | review |
| Fairness slices: every Tier 0 metric and both primaries, by language class and by channel | as above | no slice whose repeated interval lies wholly beyond the margin (evidence of harm in that slice), for every slice with at least the pre-registered minimum of 2,000 conversations per arm (proposal); smaller slices are pooled with their language class and reported descriptively. Showing non-inferiority is required for the whole population only (section 7.4) | harm test per slice |

The trip conditions are those of `monitoring-dashboard.md` section 8 and are not redefined here. A drop in P0 escalations is treated as a possible harm, not a gain: an agent that escalates fraud less often is failing GR-SEC-R6 until proven otherwise.

### 4.2 Tier 1: primary metrics

| Metric | Definition | Unit | Direction |
|---|---|---|---|
| CSAT | non-response-weighted mean post-chat rating, 1 to 5 (`csat-signals.md` section 6) | ratings | higher is better |
| FCR | share of in-scope conversations classed resolved-first-contact with the 7-day window (`outcome-tracking.md` section 4.3) | conversations | higher is better |

Success rule: the candidate wins if at least one primary metric improves and the other is not worse by more than its margin (CSAT 0.10 points, FCR 1.0 point), and every Tier 0 constraint holds. Two primaries are tested, so the family-wise error rate is controlled by a Bonferroni split: each primary is tested two-sided at 0.025, for 0.05 overall.

### 4.3 Tier 2: secondary and diagnostic metrics

Secondary (reported with a false-discovery-rate correction at 10%, never decisive): CES, sentiment trajectory slope, repeat contact at 14 and 30 days, predicted dissatisfaction share, clarification rate, turn count, check-in polarity, per-intent CSAT and FCR. Diagnostic (no test): intent mix, response rate, retrieval confidence, generation method mix. Long-term, read after the experiment: 90-day retention and product adoption of the two assignment groups (`outcome-tracking.md` section 6), reported as observation, with adoption watched as a possible pressure-selling signal.

## 5. Pre-registration

No candidate enters shadow or canary 1 without a frozen pre-registration record in the experiment registry. The record is drafted at DESIGN, reviewed while the offline gates run, and frozen at the G5 approval, which is where `diagrams/learning-loop.mmd` shows it. The record is immutable after approval; deviations are appended with a reason and a time, and a deviation after unblinding is flagged in the report.

| Field | Content |
|---|---|
| Identity | experiment id, candidate version tuple (prompt, model, KB epoch, parameters), control version tuple, update class, owner, statistician, approvers |
| Hypothesis | one sentence with direction and mechanism, and the diagnosis evidence it came from |
| Population | eligible traffic, exclusions (section 2), randomisation unit, salt, bucket ranges per stage |
| Primary metrics | definitions, estimators, the weighting cells, minimum effect of interest, margins |
| Tier 0 constraints | the list of section 4.1 with thresholds; any candidate-specific addition |
| Design | stages and dwell times, looks and their information fractions, spending function, boundaries, maximum duration, futility rule |
| Sample size | assumptions (volume, response rate, variance, design effects), formula, required n, expected duration |
| Analysis plan | tests, clustering, covariates if any, handling of differential response, of missing FCR maturity, of sample ratio mismatch; pre-declared segments |
| Stopping rules | section 8, with who decides |
| Rollback plan | mechanism and owner |
| Ethics and safety check | confirms no arm weakens a guardrail, an escalation rule or an auth step, and no arm treats segments differently |

Anything not pre-registered is exploratory and is labelled so in the report. The report lists every pre-registered metric, including those that did not move.

## 6. Power analysis

### 6.1 Assumptions

| Quantity | Value | Source |
|---|---|---|
| Interactions per day | 18,000 | brief A1.1 |
| Share eligible for experiments | 100% in the base case (AI-first: every interaction starts with the agent); 60% as a sensitivity case (the board's initiative replaces 60% of first-line support) | assumption |
| A/B stage arm size | 25% of 18,000 = 4,500 conversations per arm per day | ladder |
| CSAT response rate | 15% (675 ratings per arm per day); sensitivity 10% and 25% | proposal D-99 |
| CSAT standard deviation | 1.3 points; sensitivity 1.0 and 1.5 | proposal. The brief gives none; a 1 to 5 scale cannot exceed 2.0. Re-estimated blind (pooled over arms) at look 1 |
| Minimum effect of interest, CSAT | 0.10 points | proposal: one third of the Level 5 boss effect, and small against the 1.3 gap between today's 3.2 and the 4.5 target (A1.1) |
| FCR baseline | 0.70 | the A8.2 target, used as the planning value; variance is larger at 0.50 (sensitivity shown) |
| Minimum effect of interest, FCR | 2.0 points (0.70 to 0.72) | proposal |
| Significance | two-sided 0.025 per primary (0.05 family-wise) | section 4.2 |
| Power | 0.80 per primary | proposal |
| Design effect, clustering by customer | 1.10 = 1 + (m - 1) x ICC with m = 1.2 conversations per customer in the window and ICC = 0.5 | proposal; replaced by the observed value |
| Design effect, non-response weighting (CSAT only) | 1.17 | from the worked example in `csat-signals.md` section 6.3 |
| Inflation for two looks | 1.0041 | computed, section 7.2 |

### 6.2 CSAT: difference in means

Per-arm sample size for a two-sided test of a difference in means with equal arms:

`n = 2 x (z_(1-alpha/2) + z_(1-beta))^2 x sigma^2 / delta^2`

With alpha = 0.025: `z_(1-alpha/2) = z_0.9875 = 2.2414`. With power 0.80: `z_0.80 = 0.8416`. Sum 3.0830, squared 9.5050.

`n = 2 x 9.5050 x 1.3^2 / 0.10^2 = 2 x 9.5050 x 1.69 / 0.01 = 3,212.7`, so 3,213 ratings per arm.

Adjusted for clustering, weighting and the interim look: `3,213 x 1.10 x 1.17 x 1.0041 = 4,152.1`, so **4,153 ratings per arm**. At a 15% response rate that is 27,687 conversations per arm, reached in 4,153 / 675 = **6.2 days** at the 25% stage.

### 6.3 FCR: difference in proportions

`n = (z_(1-alpha/2) + z_(1-beta))^2 x (p1 (1 - p1) + p2 (1 - p2)) / (p2 - p1)^2`

`n = 9.5050 x (0.70 x 0.30 + 0.72 x 0.28) / 0.02^2 = 9.5050 x (0.2100 + 0.2016) / 0.0004 = 9,780.7`, so 9,781 conversations per arm.

Adjusted for clustering and the interim look (no survey weighting: FCR is observed on every conversation): `9,781 x 1.10 x 1.0041 = 10,803.2`, so **10,804 conversations per arm**, reached in 10,804 / 4,500 = **2.4 days** of exposure. Each cohort then needs 7 days to mature.

### 6.4 Sensitivity

CSAT ratings per arm (after both design effects and the inflation) and days at the 25% stage for response rates of 10%, 15% and 25%:

| sigma | delta 0.05 | delta 0.10 | delta 0.15 | delta 0.30 |
|---|---|---|---|---|
| 1.0 | 9,828 (21.8 / 14.6 / 8.7 days) | 2,458 (5.5 / 3.6 / 2.2) | 1,092 (2.4 / 1.6 / 1.0) | 274 (0.6 / 0.4 / 0.2) |
| 1.3 | 16,608 (36.9 / 24.6 / 14.8) | **4,153 (9.2 / 6.2 / 3.7)** | 1,846 (4.1 / 2.7 / 1.6) | 462 (1.0 / 0.7 / 0.4) |
| 1.5 | 22,111 (49.1 / 32.8 / 19.7) | 5,529 (12.3 / 8.2 / 4.9) | 2,458 (5.5 / 3.6 / 2.2) | 616 (1.4 / 0.9 / 0.5) |

FCR conversations per arm: baseline 0.70, effect 1.0 point: 43,664 (9.7 days); 2.0 points: 10,804 (2.4 days); 3.0 points: 4,750 (1.1 days); baseline 0.50, effect 2.0 points: 13,113 (2.9 days).

If only 60% of interactions are eligible (2,700 conversations and 405 ratings per arm per day), the CSAT requirement takes 10.3 days and the FCR requirement 4.0 days.

### 6.5 What the default duration buys

In every base-case row the sample-size requirement is met in less than the 14-day minimum exposure (section 10), so the duration, not the sample size, is the binding rule. Over 14 days the A/B stage collects 63,000 conversations and 9,450 ratings per arm, 2.3 times the CSAT requirement.

| Quantity over 14 days | CSAT | FCR |
|---|---|---|
| Standard error of the difference at full information | `1.3 x sqrt(2 x 1.287 / 9,450) = 0.0215` | `sqrt(2 x 0.21 x 1.10 / 63,000) = 0.00271` (0.27 points) |
| Smallest true effect detected with 80% power | 0.066 points | 0.84 points |
| Power for the design effect (0.10 points; 2.0 points) | 0.992 | above 0.999 |
| Smallest effect detected, response rate 10% / 25% | 0.081 / 0.051 | not applicable |
| Smallest effect detected, 60% eligible traffic | 0.086 | 1.08 points |

Two consequences. First, an effect of 0.05 CSAT points cannot be detected reliably in 14 days at this volume; a candidate that claims so small a gain needs the maximum duration of 28 days or must be bundled. Second, per-intent effects are far less precise: an intent category with a 10% share has one tenth of the ratings, so its standard error is about 3.2 times larger. Per-intent results are therefore secondary unless the experiment is designed for that intent and sized on its volume.

Sample sizes are re-checked at look 1 with the pooled (blinded) variance, the observed response rate and the observed design effect. Only an extension is allowed (up to 28 days of exposure), never a shortening, and the decision is made without looking at the difference between arms.

## 7. Sequential testing

### 7.1 Why and how many looks

Waiting three weeks with no look would keep customers on a harmful candidate longer than necessary; looking every day at a fixed 0.025 threshold would inflate the false-positive rate. The design uses a small number of planned looks with an alpha-spending function for claims of benefit, so the overall error rate stays at 0.025 per primary whatever the stopping time, and a separate, looser one-sided rule for stopping on harm (section 7.3), because the symmetric boundary is deliberately hard to cross early.

Each primary has two looks at information fractions 0.5 and 1.0:

| Calendar day of the A/B stage | CSAT (ratings mature 3 days after the conversation starts) | FCR (7-day maturity) |
|---|---|---|
| 7 | exposure for look 1 ends (conversations of days 1 to 7) | not yet mature; provisional escalation and repeat counts are read for harm only, under Tier 0 |
| 10 | look 1 is read: ratings received by day 10 for conversations of days 1 to 7 | |
| 14 | exposure for the analysis ends; arms stay frozen | look 1 (cohorts of days 1 to 7 matured) |
| 17 | look 2, final: ratings received by day 17 for conversations of days 1 to 14 | |
| 21 | late-rating sensitivity analysis | look 2, final (cohorts of days 1 to 14 matured); decision day |

CSAT maturity rule (proposal, D-158). Escalated conversations are surveyed only after the human team closes them (`csat-signals.md` section 3.1), so their ratings arrive late and would be missing from a look taken on the last day of exposure, in exactly the stratum where arms may differ. Each look therefore uses the ratings received within 3 days of the conversation start; the post-stratification weights treat a conversation without a rating by then as a non-response. Ratings that arrive later are not added to a look that has been read. They enter one pre-registered late-rating sensitivity analysis on day 21, reported beside the primary result; if it changes the sign of the CSAT effect or moves it beyond the non-inferiority margin, the decision is deferred and reviewed.

### 7.2 Alpha spending and boundaries

Spending function: Lan-DeMets with the O'Brien-Fleming shape, `alpha*(t) = 2 x (1 - Phi(z_(1-alpha/2) / sqrt(t)))`, for alpha = 0.025 two-sided. It spends almost nothing early, so an early stop needs overwhelming evidence and the final test is almost as powerful as a single fixed test.

| Look | Information fraction | Cumulative alpha spent | Boundary on abs(z) | Nominal two-sided p |
|---|---|---|---|---|
| 1 | 0.5 | `2 x (1 - Phi(2.2414 / sqrt(0.5))) = 2 x (1 - Phi(3.1698)) = 0.0015` | 3.1698 | 0.0015 |
| 2 | 1.0 | 0.0250 | 2.2510 | 0.0244 |

The second boundary is the value c that solves `P(abs(Z1) < 3.1698 and abs(Z2) >= c) = 0.025 - 0.0015` under the null hypothesis, where Z1 and Z2 are jointly normal with correlation `sqrt(0.5)`. It was found by numerical integration; the total type I error then checks to 0.0250. Convention: the spending function is applied here to the whole two-sided 0.025, as in the original Lan-DeMets formulation. Group-sequential packages commonly apply it to each one-sided tail of 0.0125 instead, which gives 3.3446 and 2.2457; both control the two-sided error at 0.025, and the form used here is slightly less conservative at look 1 and slightly more at look 2. The pre-registration names the convention so that a package check reproduces the numbers. For comparison a single fixed test would use 2.2414, so the price of the interim look is small: the maximum sample size rises by a factor of 1.0041 for the same 80% power (the inflation used in section 6). Under the design effect the probability of crossing at look 1 is 0.16.

If the realised information fraction differs from the plan (for example a holiday week), the boundaries are recomputed from the same spending function at the realised fractions; that is the purpose of the Lan-DeMets form. The number of looks is not increased after the start.

### 7.3 Repeated confidence intervals

At look k the interval for a difference is `estimate +/- c_k x SE`, with c_1 = 3.1698 and c_2 = 2.2510. These repeated intervals hold their joint coverage across both looks, so they can be used for every statement the decision needs:

- **Harm** on a primary, by interval: the upper limit is below 0.
- **Harm** on a primary, by the early rule (pre-registered, D-158): z at or below -2.0 at look 1. This one-sided rule is looser than the symmetric boundary because stopping a harmful candidate matters more than the cost of a false stop. It can only stop the experiment, so it cannot inflate the chance of a wrong promotion; its cost is a 2.3% chance per primary (at most 4.6% over both) of stopping a harmless candidate at look 1. With the planning variance it stops on an observed CSAT fall of 0.061 points (0.096 under the symmetric boundary) or an FCR fall of 0.77 points (1.21); against a true CSAT harm of 0.10 points it stops at look 1 with probability 0.90, against 0.55 for the symmetric boundary.
- **Win** on a primary: the lower limit is above 0.
- **Non-inferiority** on a primary: the lower limit is above minus the margin (CSAT 0.10, FCR 1.0 point).

In effect sizes, with the planning variance: at look 1 a CSAT difference must exceed 0.096 points (FCR 1.21 points) to cross; at look 2, 0.048 points (FCR 0.61 points).

### 7.4 Non-inferiority for Tier 0 rates

Escalation rate, containment and handle time use the same repeated intervals against their margins (section 4.1). With 63,000 conversations per arm the standard error of a rate near 0.30 or 0.70 is 0.27 points, so when the true difference is zero the chance of showing non-inferiority at a 1.0-point margin at the final look is 0.93; for the CSAT margin of 0.10 it is 0.99. A candidate that cannot show non-inferiority is not promoted, even if nothing is significantly worse: the burden of proof is on the candidate.

That burden applies to the whole population only. Showing non-inferiority at a 1.0-point margin with 80% power needs about 44,200 conversations per arm, 70% of the 14-day arm, so no slice can meet it: a slice holding 10% of traffic would show it with probability 0.14 even when the candidate changes nothing, and a slice holding a third with probability 0.46. Requiring it per slice would block every candidate. For slices the rule is therefore the weaker, testable one of section 4.1: no slice with at least 2,000 conversations per arm may have a repeated interval wholly beyond the margin. At that minimum size the interval half-width is 3.4 points, so the slice rule detects gross harm to a small language or channel, not small harm; that limit is stated in every report, and small slices are followed for longer through the 28-day monitoring.

Hard-zero constraints are not statistical tests. They are monitored continuously, and any event stops the experiment. Continuous monitoring of a stop-only rule does not inflate the chance of a wrong promotion; it can only make promotion less likely.

### 7.5 Futility

Non-binding. At look 1 the conditional power for each primary is computed under the current trend, `CP = 1 - Phi((c_2 - z_1 x sqrt(2)) / sqrt(0.5))`. If it is below 10% for both primaries (proposal), the statistician recommends stopping for futility and the owner decides. Because the rule is non-binding it is ignored in the alpha calculation, which stays valid whether or not it is followed.

## 8. Stopping rules

| Rule | Condition | Action | Decided by |
|---|---|---|---|
| S-1 safety stop | any circuit-breaker trip condition (`monitoring-dashboard.md` section 8) | automatic rollback, stages frozen, incident opened; restart only from 1% after the cause is fixed (playbook runbook R7) | automatic; incident commander confirms |
| S-2 harm stop | z at or below -2.0 on a primary at look 1 (early harm rule, section 7.3), or the repeated interval for a primary lies below 0 at a look, or a Tier 0 non-inferiority interval lies wholly beyond its margin (for a slice: section 4.1) | rollback; record the result | statistician and owner; Risk owner informed |
| S-3 validity stop | sample ratio mismatch on randomised units, a difference between arms in the rate of protected-flow or safe-mode conversations at p below 0.001 (section 9), instrumentation fault, or assignment leak | pause; fix; restart with a new salt; data so far is discarded for inference | statistician |
| S-4 futility | conditional power below 10% on both primaries at look 1 | stop recommended (non-binding) | owner |
| S-5 efficacy | a primary's repeated interval lies above 0 | recorded only. No promotion before the decision day: day 21, when both primaries have had their final look. Between day 14 and day 21 the arms stay frozen at 25% each. The one exception is a candidate that fixes a confirmed S2 defect: with the Risk owner's agreement it may be promoted after the CSAT final look on day 17 if FCR is not inferior at its first look, and the FCR final look is then read as post-deployment validation | owner with approvers |
| S-6 completion | final looks done (day 21) and the late-rating sensitivity analysis read | decision by the success rule of section 4.2; promote, or retire the candidate | approvers of section 11 |
| S-7 maximum duration | 28 days of exposure reached without a decision | the candidate is retired as inconclusive; it is not extended again | owner |

There is no rule that allows promotion on a primary win while a Tier 0 constraint is unmet, and there is no manual override of S-1 inside the pipeline (case SS-LRN-13).

## 9. Analysis plan

| Topic | Rule |
|---|---|
| Estimand | intention to treat: every randomised unit is analysed in the arm it was assigned to, whatever happened in its conversations (safe mode, rate limiting, crisis or fraud flow, escalation, abandonment). Nothing observed after assignment removes a unit from the primary analysis. Analyses that drop such conversations are pre-registered sensitivity analyses and never replace the primary |
| Exclusion-rate check | the share of conversations in protected flows, in safe mode and rate-limited is compared between arms at every look. A difference at p below 0.001 means the candidate is changing who lands in those flows, which is a finding in itself and a validity stop (S-3) |
| CSAT maturity | ratings count at a look if received within 3 days of the conversation start (section 7.1); one late-rating sensitivity analysis on day 21 |
| CSAT estimator | difference of post-stratified means using the cells of `csat-signals.md` section 6.2, cells fixed before the experiment; variance by the stratified formula with customer clustering. The unweighted difference of means (Welch) is reported beside it. Because ratings are ordinal, a rank-based test and the share of ratings of 4 or 5 are reported as robustness checks; they are not decisive |
| FCR estimator | difference of proportions on matured cohorts, customer-clustered standard error |
| Differential response | the response rates of the arms are compared first. If they differ at p below 0.01, the weighted analysis remains primary and a bounding analysis is added: the arm with the higher response rate is trimmed to the lower rate from the top and from the bottom of its rating distribution, giving a lower and an upper bound for the effect |
| Sample ratio mismatch | chi-square test of the number of distinct randomised units (customers, and anonymous sessions) per arm against the planned ratio, at every look and daily; p below 0.001 invalidates the data (S-3). The unit is the customer because the customer is what was randomised: a candidate that makes customers return more often changes the conversation count without any assignment fault. The conversation ratio is reported as a diagnostic, and conversations per unit by arm as a secondary metric. Scale of the test: with 126,000 units a difference of 1,168 between arms trips it; a split of 63,412 against 62,588 gives chi-square 5.39, p = 0.020, and passes |
| A/A tests | before the first real experiment and every quarter, two identical arms are run through the whole analysis. Over repeated A/A runs the share of "significant" primaries must be consistent with 2.5%, and the SRM alarm must stay silent |
| Variance reduction | optional and pre-registered: adjustment for a pre-experiment covariate of the same customer (prior-period CSAT stratum or contact count). Not assumed in the sample sizes |
| Segments | pre-registered only: language class, channel, the ten A1.2 intent categories, new against returning customers. Each segment estimate is exploratory unless the experiment was sized for it, and segment tests are corrected for multiplicity (false-discovery rate 10%). Segments are for finding harm; a segment-only win does not justify a segment-only rollout |
| Fairness | the slice rule of section 4.1 is applied per language class and channel. The brief asks for "statistical fairness testing" (A11.3): the report includes the difference in escalation rate and in primary effects between slices with intervals, and states the smallest harm each slice could have shown |
| Outliers and bots | no post-assignment exclusion in the primary analysis. Sessions rate-limited by GR-ATK-08 and safe-mode sessions are dropped only in a pre-registered sensitivity analysis, defined before unblinding |
| Blinding | reviewers, and the statistician until the planned looks, do not see arm labels; dashboards show pooled figures between looks |
| Reporting | effect, repeated interval, the look at which it was read, the raw and weighted CSAT, response rates, SRM result, every Tier 0 metric with its interval, deviations from the pre-registration |

## 10. Novelty and primacy effects

A new wording can please customers because it is new (novelty), or annoy returning customers because it is unfamiliar (primacy); both fade. Weekly cycles also matter: salary dates, weekends and statement dates change the intent mix.

| Measure (proposal) | Detail |
|---|---|
| Minimum exposure | 14 days at the A/B stage, covering two full weekly cycles, whatever the sample size says |
| Week 1 against week 2 | the effect is estimated separately for days 1 to 7 and 8 to 14; a pre-registered test of their difference is reported. A week-2 effect below half the week-1 effect is treated as a novelty warning and the candidate is extended to 28 days |
| New against returning customers | effect by whether the customer had contacted the agent in the 30 days before the experiment; novelty and primacy show as a gap between the two that closes over time |
| Holdback | after promotion, 5% of customers stay on the control for 28 days (25,200 conversations). The holdback effect is compared with the experiment effect; a holdback effect that has decayed below the non-inferiority margin opens a review |
| Long-term outcomes | 30-day repeat contact, and 90-day retention of the experiment's two groups, are read when they mature (`outcome-tracking.md` section 6) |
| Calendar exclusions | experiments do not start in a week with a known volume shock (quarter-end, a major outage); if one occurs, the affected days are flagged and a sensitivity analysis without them is reported |

## 11. Experiment governance

### 11.1 Approval by configuration owner (A12.3)

The brief's table gives each parameter an owner and a change process. The workflow below is what each process means in this design. In every row the pipeline may propose and may not apply (GR-SYS-03; cases SS-LRN-07 to SS-LRN-10).

| Parameter (A12.3) | Default | Range | Owner | Change process (brief) | Required before the change is live |
|---|---|---|---|---|---|
| `intent_confidence_threshold` | 0.70 | 0.50-0.95 | NLU Team | A/B test required | pre-registration; gates G0 to G9; NLU Team lead approves. The safety-elevated thresholds and the 0.50 flow-entry gates for safety flows (`config/intents.yaml`) are not moved by this parameter and need the Risk Committee |
| `escalation_sentiment_threshold` | -0.70 | -1.0 to -0.3 | CX Team | CEB approval | evidence pack (S4 analysis, missed-escalation analysis, per-language effect); Customer Experience Board approval; Risk Committee informed because ESC-004 is an escalation trigger; canary with the escalation constraints of section 4.1. An A/B test is recommended but not required by the brief |
| `max_conversation_turns` | 25 | 10-50 | Product | Standard change | change ticket, suite, canary. It may not fall below the ESC-010 value of 15 turns without the escalation owner |
| `session_timeout_minutes` | 5 | 3-15 | Security | RC approval | Risk Committee approval; ceiling 5 (D-56), so only 3 to 5 is reachable. Not a learning-pipeline parameter: listed under X4 |
| `knowledge_retrieval_top_k` | 5 | 3-10 | NLU Team | A/B test required | pre-registration with retrieval metrics as secondary and the latency budget as Tier 0; NLU Team lead approves |
| `retrieval_confidence_threshold` | 0.65 | 0.50-0.90 | NLU Team | A/B test required | as above; ESC-008 rate and gap-statement rate are added to Tier 0 because the threshold decides when the agent says it does not know (D-43) |
| `guardrail_strictness_level` | HIGH | MED/HIGH/CRIT | RC | RC approval required | Risk Committee only; raising is pre-approved for incidents (D-86). Never an experiment arm. X4 |
| `model_temperature` | 0.3 | 0.0-1.0 | ML Team | A/B test + RC review | pre-registration; gates G0 to G9; ML Team lead approves; Risk Committee review of the result before 100% |

Other surfaces: prompt layers 3 and 4 need the prompt owner and Risk Committee review (A12.2); layer 5 needs the operations owner only; NLU and retrieval models need the NLU Team lead; the policy ranker and a generation model version need the ML Team lead and Risk Committee review (`overview.md` section 3.1).

### 11.2 Workflow and roles

```
DRAFT (written with the hypothesis at DESIGN) -> STAT REVIEW and SAFETY AND ETHICS REVIEW (in parallel with gates G0-G4)
      -> G5 OWNER APPROVAL: pre-registration frozen = REGISTERED
      -> SHADOW -> CANARY 1% -> CANARY 5% -> A/B 25% (exposure to day 14, frozen to day 21) -> DECISION (day 21)
      -> PROMOTED (100% + holdback) or ROLLED BACK or RETIRED -> REPORT -> CLOSED
```

| Role | Duty | Cannot |
|---|---|---|
| Experiment owner (from the owning team) | hypothesis, pre-registration, report | approve their own experiment; see arm-level data between looks |
| Statistician (independent of the owning team) | reviews the design and sample size, computes boundaries, runs or verifies the analysis, declares S-2, S-3, S-4 | change the pre-registration after the freeze |
| Safety and ethics reviewer (Risk and Compliance) | confirms no arm weakens a guardrail, an auth step or an escalation; no segment-specific treatment; no arm that deceives or withholds a mandatory disclosure; customer data use within the consent purposes | waive a Tier 0 constraint |
| Configuration owner (A12.3) | approves the start and the promotion | promote without the statistician's report |
| Risk Committee | reviews where A12.2 or A12.3 require it; owns every Tier 0 threshold | |
| Customer Experience Board | approves `escalation_sentiment_threshold`; receives the weekly experiment summary (A8.5) | |
| Incident commander | S-1 confirmation and restart conditions | |

The statistical review and the safety and ethics review together are the "experiment review" that suite cases SS-LRN-19 and SS-LRN-20 name: an experiment plan rejected there never reaches registration.

### 11.3 Standing rules

1. One registry. Every experiment, including abandoned ones, is in the registry with its status; the weekly dashboard shows results and the pending pipeline (A8.5).
2. No experiment on the excluded list X1 to X6, on crisis or fraud handling, or on mandatory disclosures (cases SS-LRN-19, SS-LRN-20).
3. No experiment whose expected benefit comes from selling more. Product adoption is observed, not optimised (`outcome-tracking.md` section 6.3).
4. A candidate that failed is not re-run unchanged. A re-run needs a changed candidate or a documented flaw in the first run.
5. Results are reported whatever the outcome; the registry is the institutional memory the DOCUMENT step asks for (A8.4).
6. Promotion to 100% records author, approval chain, deployment date and model version (A12.2).
7. Rollback after promotion remains available by flag or pointer for at least the 28-day monitoring window.

## 12. Limits of this design

1. All planning values are assumptions. The first A/A test replaces the variance, response rate and design effects with observed values.
2. CSAT is measured on responders. Weighting reduces non-response bias but cannot remove it (`csat-signals.md` section 6.3); that is why FCR, which is observed for every conversation, is the second primary.
3. Rare harms cannot be excluded by an experiment of this size: zero events in 63,000 conversations bounds the event rate only below 1 in 21,030 at 95% confidence (`safety-invariants.md` section 6). The fixed suite, the red-team run and the rule layer carry the safety argument; the experiment only confirms the absence of common harm.
4. Customer-level randomisation does not stop two customers comparing answers; with wording changes this interference is assumed negligible.
5. Sequential boundaries protect the primary metrics. Secondary metrics read at interim looks are descriptive.

## 13. Decisions

D-107 (customer as randomisation unit, equal concurrent control, the A/B test as the 25% stage), D-108 (metric hierarchy, Bonferroni split, planning values, sample sizes), D-109 (two looks per primary with Lan-DeMets O'Brien-Fleming spending, repeated intervals, non-binding futility), D-110 (non-inferiority margins and the 14-day minimum, 28-day maximum, novelty checks and holdback), D-111 (pre-registration, roles and the per-owner approval workflow), D-158 (audit corrections: intention to treat without post-assignment exclusions, SRM on randomised units, CSAT maturity rule, slice harm rule, early harm rule, decision on day 21).
