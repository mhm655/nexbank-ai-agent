# Guardrail Monitoring Dashboard

Brief refs: A8.1 (Guardrail False Positive Rate, below 3 percent, daily), A8.3 (Model Drift Score below 0.05, uptime), A8.4 (detect within 15 minutes; DETECT/DIAGNOSE loop), A8.5 (dashboard specification: real-time panel with "guardrail trigger heat map showing most frequently activated safety boundaries"), A5.4 (regression monitoring, circuit breaker with automatic rollback), A10.1 and A10.2 (log fields), A11.1 and A11.2 (hallucination, drift, viral conversations). Registry: `config/guardrails.yaml` (45 guardrails; `fp_target_pct`, `parameters.fp_class_bounds_pct`, `parameters.fp_overall_target_pct`). False-positive budget: D-64. Companion docs: `output-safety-layer.md`, `incident-response-playbook.md`, `financial-advice.md` section 10, `account-security.md` section 10, `regulatory-mapping.md`.

**Status.** The brief fixes: the heat map exists, detection within 15 minutes, FP below 3 percent, drift below 0.05, safety suite 100 percent, 0 percent incorrect advice. Every other threshold below is a proposal (marked) for Risk Committee review. Decisions: D-85, D-86, D-88, D-89.

## 1. Purpose and where it sits

The guardrail dashboard is a view inside the A8.5 dashboard family, not a separate product. It answers four questions: which boundaries are firing and where (heat map), are the guardrails too loose or too tight (FP against D-64, hard-zero counters), is someone attacking (adversarial rate), and is anything degrading (latency, drift, regression after a release). It is also the data source the circuit breaker reads (section 8).

| A8.5 dashboard | Guardrail content (this document) | Refresh |
|---|---|---|
| Real-time Operations | trigger heat map (section 3), alert panel, hard-zero counters, guard latency, adversarial rate, circuit breaker state | metric stream, panel redraw every 60 s (proposal) |
| Daily Performance | 24-hour trends of DM-01 to DM-12, FP estimate per guardrail against D-64 bounds, top 10 guardrails by trigger, top 10 near-misses for review, review-queue status | daily at 06:00 local (proposal), plus the A8.1 daily FP row |
| Weekly Strategic | week-over-week guardrail trends, drift report, A/B and canary guardrail results, safety suite pass rates (A5.4, A8.5 learning pipeline panel), reviewer agreement, open guardrail change requests | weekly |

## 2. Data sources

| Source | What it provides | Fields (A10 schema) |
|---|---|---|
| Audit & Telemetry Bus (component 11) turn events | triggers, evaluations, latency, actions | `guardrails_checked`, `guardrails_triggered`, `response_generation_method`, `response_latency_ms`, `action_taken`, `turn_id` |
| Conversation records | per-conversation union, resolution | `guardrails_activated`, `resolution_status`, `primary_intent`, `authentication_level`, `channel`, `model_version`, `pii_detected` |
| Output Safety Layer verdict stream | per-check outcome, score, rung reached, stage latency, near-misses | `output-safety-layer.md` sections 7 and 9 |
| Input Guard verdict stream | flags, adversarial class, sanitise events | component-interfaces.md row 2 |
| Escalation Router | ESC records created, priority, SLA outcome | row 8; cross-check R6 triggers against escalations |
| Tool Orchestrator | auth re-check rejections (should be near zero when the Policy Engine works), audit write failures | row 7, row 11 |
| Review tool (supervisor loop, A5.1) | human labels on sampled triggers: true positive, false positive, severity | sampling plan, section 5 |
| Benign evaluation set | labelled benign messages for the end-to-end FP gate | D-64, `financial-advice.md` section 10 |
| Release metadata | prompt_version, model_version, KB epoch, flag state, cohort (canary stage) | cross-cutting versioning rule |

No new personal data is introduced: the dashboard reads pseudonymised ids and aggregated counts. Customer-facing staff see only anonymised aggregates; supervisors open full logs only for conversations in their review queue; every log access is itself logged (A10.3).

## 3. Trigger heat map

Purpose: show at a glance which safety boundaries fire most, and where each deviates from its own baseline. Two views share one colour rule.

**Cell value.** `rate = triggers / evaluations` for the guardrail in the bucket. **Colour (symbol) is the deviation from the guardrail's own 28-day, same-hour baseline**, not the raw rate, so rare and CRITICAL guardrails are readable beside common ones. Symbols (proposal): `.` below 1.5 sigma, `o` 1.5 to 3 sigma, `O` 3 to 5 sigma, `#` above 5 sigma or above 3 times baseline, `-` fewer than 20 evaluations in the bucket (not scored). A row label carries the severity from the registry (C critical, H high, M medium).

### View A: guardrail by hour (last 24 hours), illustrative layout only

The values below are invented to show the layout; they are not measurements.

```
GUARDRAIL HEAT MAP  view A  window: last 24 h, bucket 1 h   sort: family, then severity
                         hour of day (local)
ID           sev  trig/1k   00 02 04 06 08 10 12 14 16 18 20 22  | acts: B R E M
GR-ADV-01    C    1.8       .  .  .  .  o  .  .  .  o  .  .  .  |  0 14  2 0
GR-ADV-06    C    0.6       .  .  .  .  .  .  .  .  .  .  .  .  |  0  6  3 0
GR-SEC-R1    C    4.2       .  .  .  .  .  o  .  .  .  .  .  .  |  1  0  0 31
GR-SEC-R3    C    0.9       .  .  .  .  .  .  .  O  O  .  .  .  |  9  9  4 0
GR-SEC-R8    C    0.4       .  .  .  .  .  .  .  .  .  .  .  .  |  5  0  1 0
GR-REG-03    H    7.5       .  .  .  .  .  .  .  .  .  .  .  .  |  0 61  0 0
GR-OUT-01    C    0.3       -  -  .  .  .  .  .  .  .  .  .  .  |  0  3  0 0
GR-OUT-02    C    2.1       .  .  .  .  .  .  .  .  .  .  .  .  |  1  0  0 14
GR-OUT-03    C    0.5       .  .  .  .  .  .  o  .  .  .  .  .  |  0  4  2 0
GR-OUT-04    M    3.3       .  .  .  .  .  .  .  .  .  .  .  .  |  0 22  0 0
GR-OUT-05    H    1.1       .  .  .  .  .  .  .  .  #  #  O  .  |  0 17  0 0
GR-SYS-01    H    0.8       .  .  .  .  .  .  .  .  o  O  O  .  |  0  7  5 0
legend: . normal  o elevated  O high  # extreme  - low volume
        acts: B block, R redirect, E escalate, M mask (counts in the window)
```

Reading the illustration: GR-OUT-05 (commitment) is extreme from 16:00 to 20:00, GR-SYS-01 (fallback ladder) rises with it. Together they suggest a new draft behaviour (a prompt or model change that made the generator promise timelines) and the ladder absorbing it. The dashboard links such a pattern to the release metadata row (section 7) so the first diagnostic question, "what changed at 15:50", is answered on the same screen.

### View B: guardrail by intent

```
GUARDRAIL HEAT MAP  view B  window: last 7 days   top 12 guardrails x top 12 intents by volume
             PRD-001 PRD-003 PRD-005 TXN-002 TXN-003 CMP-001 CRD-001 SEC-001 ACC-001 GEN-004 ...
GR-ADV-01      o       .       #       .       .       .       .       .       .       .
GR-ADV-06      .       .       O       .       .       .       .       .       .       .
GR-OUT-01      .       o       .       .       .       .       .       .       o       .
GR-OUT-05      .       .       .       O       O       o       .       .       .       .
GR-SEC-R3      .       .       .       o       O       .       .       o       .       .
GR-REG-03      .       .       .       .       .       #       .       .       .       .
click a cell: open the sampled triggers for that (guardrail, intent) pair, with the review labels
```

Interactions: filter by channel, language, auth level, model_version, cohort; click a cell to open the sample list (pseudonymised, PII redacted); a toggle shows the raw rate instead of the deviation; a "CRITICAL only" filter. Rows are the registry IDs, so the heat map and the audit field `guardrails_triggered` use one vocabulary.

## 4. Metrics, formulas and sources

Notation: for a guardrail i and a window w: `E_i` evaluations (from `guardrails_checked`), `T_i` triggers (from `guardrails_triggered`), `N` turns. Metric IDs DM-01 to DM-16 are local to this document.

| ID | Metric | Formula | Source | Granularity |
|---|---|---|---|---|
| DM-01 | Trigger rate per GR ID | `T_i / E_i`; also per 1,000 turns: `1000 * T_i / N` | turn events | 5 min, hour, day; by intent, channel, language, version |
| DM-02 | Action mix per GR ID | share of block, redirect, escalate, mask among `T_i` | turn events (`action_taken`) | hour, day |
| DM-03 | Block rate / redirect rate | turns with at least one block (resp. redirect) divided by `N`; separately for the Input Guard and the OSL | turn events | hour, day |
| DM-04 | Estimated FP rate per guardrail (diagnostic) | `p_i = (T_i / E_i) * f_i` where `f_i` is the share of sampled triggers labelled false positive; Wilson 95 percent interval on `f_i`. Compare with `fp_target_pct` of guardrail i | turn events plus review labels (section 5) | day, 7-day rolling |
| DM-05 | End-to-end FP rate (the gate) | on the labelled benign set: benign messages blocked, redirected, escalated or wrongly masked by any guardrail divided by benign messages. On live traffic (estimate): `(I / N) * f_I` where `I` is turns with an intervention and `f_I` the reviewed share judged benign. Union bound `sum(p_i)` shown beside it as a cross-check | benign set run (release and weekly), live sample (daily) | day, week |
| DM-06 | Near-miss rate | turns with a near-miss (D-88) divided by `N`, per guardrail | turn events, OSL verdict stream | day |
| DM-07 | OSL catch rate | `1 - (turns where a rung above 0 was used) / N`, split by rung; a rise means the generator is drafting more violations | OSL stream | hour, day |
| DM-08 | Adversarial attempt rate | flagged attempts per 1,000 sessions, by class (the six A4.4 vectors; classes map to GR-SEC-R5, GR-SEC-R8 and GR-ATK-01 to GR-ATK-11) and by session (repeat offenders) | Input Guard stream | 5 min, hour, day |
| DM-09 | Adversarial success count (hard zero) | sessions in which a draft that violates a CRITICAL guardrail reached the channel, found by post-delivery audit and by incident | audit sampling, incidents | continuous |
| DM-10 | Guard latency | p50, p95, p99 of Input Guard and OSL, and OSL stage latency S1 to S4 (`output-safety-layer.md` section 4); timeout rate = timeouts / evaluations | turn events (`response_latency_ms`), OSL stream | 1 min, hour |
| DM-11 | Drift | (a) Model Drift Score for guardrail classifiers, the A8.3 metric: performance drift from baseline on the fixed eval set; (b) PSI of classifier score distributions vs the baseline window; (c) trigger-rate z-score vs same-hour baseline | eval runs, score histograms, DM-01 | daily (a, b), 5 min (c) |
| DM-12 | Hard-zero counters | counts of: delivered figure mismatch (GR-OUT-01), delivered full identifier (GR-OUT-02, GR-SEC-R1), delivered advice verdict (GR-ADV-06), delivered cross-customer data (GR-SEC-R4), executed transfer or write without required auth (GR-SEC-R2, GR-SEC-R3), unescalated security-critical intent (GR-SEC-R6: triggers fired minus escalations created), audit gaps (sequence gaps) | post-delivery audit, Tool Orchestrator re-check, bus sequence numbers | continuous |
| DM-13 | Safety suite status | pass rate of the fixed suite (at least 200 cases, A5.4) per candidate and per release; must be 100 percent | CI results | per run |
| DM-14 | Review coverage | sampled triggers reviewed within 24 hours divided by sampled; reviewer agreement (Cohen kappa) | review tool | day, week |
| DM-15 | Fallback load | share of turns using the static status message, ESC-014 or ESC-003 from GR-SYS-01 | turn events | hour |
| DM-16 | Viral-risk indicator | conversations with at least one of: the customer states intent to publish or share (screenshot, social media, press, regulator complaint), sentiment below the ESC-004 threshold with a delivered tone or accuracy fault, a hard-zero event; count and top reasons. External social-media listening is a dependency (section 9) | Input Guard classifier, OSL stream, sentiment | 15 min |

Conventions: a ratio with fewer than 20 evaluations in the window is shown but not alerted on. All trigger counts carry the version tuple (prompt_version, model_version, KB epoch, rules version) so a change can be correlated.

### 4.1 FP estimates against the D-64 budget

The panel "FP budget" shows, per guardrail, `p_i` (DM-04) as a bar against its class bound and per class and typical path the arithmetic of `financial-advice.md` section 10.

| Class | Bound per guardrail (D-64, `fp_class_bounds_pct`) | Warn at 70 percent (proposal) | Typical path | Contribution |
|---|---|---|---|---|
| rule | below 0.10 percent | 0.07 | 10 | 1.00 percent |
| hybrid | below 0.15 percent | 0.105 | 6 | 0.90 percent |
| model | below 0.30 percent | 0.21 | 2 | 0.60 percent |
| Sum of bounds | | | 18 | 2.50 percent |
| Reserve | | | | 0.50 percent |
| ATK guardrails on the typical path (D-76: GR-ATK-01, 02, 03, 05, 06, 07, 08, 09 at their own bounds, below the class bounds) | | | 8 | 0.46 percent, drawn from the reserve |
| Typical path after Day 10 / reserve left | | | 26 | 2.96 percent / 0.04 percent |
| Gate (DM-05) | below 3 percent end to end | warn at 2.1 percent (70 percent, proposal) | | |

Rule of use: the per-guardrail bars are diagnostics (D-64); an ATK guardrail's bar is drawn against its own `fp_target_pct`, which is below the class bound (D-76). The gate is DM-05. A bar over its bound with the gate still met means that guardrail takes from the reserve or another guardrail must be lowered, through safety change control. Estimates are only as good as the review sample; they are shown with intervals and the sample size, and a guardrail with fewer than 30 reviewed triggers in 7 days is marked "insufficient sample" (proposal).

## 5. Sampling and review plan (proposal, D-89)

The FP estimate and the false-negative estimate (FMEA #19) both need human labels; the brief does not size the review effort beyond the supervisor loop of about 50 reviews per supervisor per day (PLAN 3.7).

| Stream | Sample | Purpose |
|---|---|---|
| Triggered turns | up to 30 per guardrail per week (more for CRITICAL), stratified by intent and language | FP estimate `f_i` |
| Intervened turns, all guardrails | random 1 percent of intervened turns per day | DM-05 live estimate |
| Delivered turns with no trigger | random 0.5 percent of turns per day, plus 100 percent of turns in conversations that ended in ESC-001, ESC-002, ESC-008 or a complaint | false-negative search, DM-09 |
| Near-misses | 100 percent of OSL near-misses on CRITICAL guardrails; 10 percent of others | tune thresholds before they fail |
| Canary cohorts | 100 percent of hard-zero candidates; otherwise as above, doubled | circuit breaker evidence |

Reviewers are not the same persons who tune the guardrail. Disagreements go to the guardrail owner; reviewer agreement is tracked (DM-14).

## 6. Alert thresholds (proposals)

Detection target: an anomaly is visible on the panel and delivered to the owner within 15 minutes of occurrence (A8.4). Evaluation windows are 5 minutes; an alert needs two consecutive windows unless marked "immediate". Severity SEV0 to SEV3 is defined in `incident-response-playbook.md` section 2.

| Signal | Warn (SEV3 ticket or SEV2) | Critical (page; SEV1 or SEV0) | Notes |
|---|---|---|---|
| Hard-zero counter (DM-12) | not applicable | any count above 0: immediate page | severity by type in the playbook; delivered full credential, cross-customer data, transfer executed: SEV0 |
| Trigger rate of a guardrail (DM-01) | z-score 3 or more for two windows | z-score 5 or more, or 3 times baseline with at least 20 triggers | a drop to zero on a guardrail that normally fires is also an alert (silent failure) |
| E2E FP (DM-05) | 2.1 percent or more | 3 percent or more | A8.1 gate; breach also opens a tuning ticket |
| Per-guardrail FP (DM-04) | 70 percent of its bound for 7 days | 100 percent of its bound | diagnostic; handled in weekly review |
| Block or redirect rate (DM-03) | 2 times the 28-day baseline for 30 minutes | 4 times for 15 minutes | over-blocking (FMEA #20) and under-blocking both shown |
| OSL catch rate drop (DM-07) | rung-above-0 share doubles in 1 hour | triples | usually a prompt, model or KB release effect |
| Adversarial attempt rate (DM-08) | 3 times baseline for 15 minutes, or one session with 5 flagged attempts in 10 minutes | any success (DM-09) or a coordinated pattern across 20 or more sessions | routes to Security Operations (ESC-009 queue contact) |
| Guard latency (DM-10) | OSL p95 above 210 ms, Input Guard above 70 ms (70 percent of the 300 and 100 ms budgets) | OSL p95 above 300 ms or Input Guard above 100 ms for 10 minutes; timeout rate above 5 percent | template-only mode if sustained (playbook section 5) |
| Drift (DM-11) | Model Drift Score 0.04 or more; PSI 0.10 or more | score 0.05 or more (A8.3 limit); PSI 0.25 or more | PSI cut-offs follow common practice and are proposals |
| Safety suite (DM-13) | any case fails in a candidate | any case fails on production version | blocks the release; circuit breaker if already live |
| Audit gap (DM-12) | buffer depth above 50 percent | sequence gap or write failure on a high-risk action | FMEA #21; high-risk actions are blocked while it lasts |
| Review backlog (DM-14) | oldest unreviewed critical sample above 24 hours | above 72 hours | |
| Viral-risk indicator (DM-16) | 3 conversations flagged in 1 hour | any flagged conversation with a hard-zero event, or 10 in 1 hour | routes to the viral runbook R6 |

Each alert carries: the guardrail ID, the window, the baseline, the version tuple, a link to the heat map cell, the runbook link and the owner. Alerts are deduplicated per (signal, guardrail) and auto-resolve only after two clean windows.

## 7. Release correlation

A release strip along the top of the heat map shows every change to prompt layers 3-5, thresholds, model versions, KB epochs and canary stage with its time. `incident-response-playbook.md` uses the strip as the first diagnostic step. Changes to layers 0-2 and to the rule layer appear only as safety change-control events (GR-SYS-02, GR-SYS-03).

## 8. Link to the circuit breaker

The circuit breaker (A5.4, PLAN 3.7, D-46 for KB changes) reads this dashboard's metrics; it does not use a separate pipeline.

| Aspect | Specification (proposal unless the brief states it) |
|---|---|
| Scope | every staged rollout 1 percent, 5 percent, 25 percent, 100 percent (brief A5.4): learning-pipeline candidates, prompt layers 3-5, thresholds that the pipeline may touch, NLU and ranker models, KB epochs |
| Comparison | candidate cohort vs control cohort at the same time (not vs history), same intents and channels, with the version tuple as the cohort key |
| Trip conditions | (1) any hard-zero counter above 0 in the candidate cohort; (2) safety suite below 100 percent; (3) DM-05 FP in the candidate cohort above the gate or more than 0.5 points above control; (4) a guardrail trigger rate outside the control by the critical z-score; (5) guard latency above budget; (6) drift above 0.05 |
| Action | automatic rollback to the previous version (flag flip or epoch pointer, rollback is drilled, `maintenance-workflow.md`), page the owner, freeze further stages, open an incident at the severity of the trigger |
| Direction | the breaker moves toward the previous, safer state only. It cannot disable a guardrail, relax a threshold or widen a rollout; raising a stage needs the pre-registered gates plus HITL for anything safety-adjacent |
| Production incidents | the same rollback lever is available to the incident commander (playbook section 5); the manual levers (template-only mode, kill switch) are GR-SYS-04 (proposed by D-86, registered by D-90) |
| Evidence | breaker readings (cohort metrics at trip time) are written to the audit bus and attached to the incident record |

## 9. Owners and cadence (proposals)

The brief names the Risk Committee members, the CEB members and the A12.3 parameter owners (NLU Team, CX Team, Product, Security, ML Team); named individuals and a rota are not given and are a dependency (D-84).

| Area | Accountable | Responsible (day to day) | Review cadence |
|---|---|---|---|
| Whole dashboard, FP gate, thresholds | Chief Risk Officer | ML Team with Security | weekly review, quarterly threshold review (Risk Committee approval for any change, GR-SYS-03) |
| Security GRs (SEC, adversarial rate, DM-08, DM-09) | Information Security Officer | Security team, Security Operations queue | daily |
| Regulatory GRs and OUT-01 / OUT-03 (accuracy, grounding) | Regulatory Compliance Manager | Compliance Helpdesk, KB owners | weekly |
| Advice GRs (ADV, REG-20, OUT C7) | Regulatory Compliance Manager | NLU Team for the classifier; Wealth Advisory sample review | weekly |
| Tone and CX-facing FP (OUT-04, REG-04, DM-16) | Head of Customer Experience; Brand Communications Director for viral | CX Team | weekly |
| Latency, drift, circuit breaker | ML Team lead (A12.3 owner of model parameters) | platform on-call | daily |
| Review queue and labels | Supervisors (A5.1) | review leads | daily |
| Audit gaps, retention | Security | audit bus owner | daily |

External social-media listening for viral detection, the on-call rota and paging tooling are dependencies with the owners named in `incident-response-playbook.md` sections 3 and 7.

## 10. Open items

1. All thresholds, sample sizes and the 70 percent warn convention are proposals; they must be calibrated on the dev set and on a shadow period before they page anyone.
2. GR-ATK entries (Day 10, `config/guardrails.yaml`) are rows of the heat map automatically because rows are registry IDs; DM-08 classes map to them.
3. DM-05 on live traffic depends on labelled samples; before launch only the benign-set measurement is available. Until then the live panel shows the union bound and "unmeasured".
4. Heat-map rendering (tool, access control and the 15-minute pipeline) is an implementation choice and is not specified here beyond the metrics and sources.
5. GR-OUT-06 and GR-SYS-04, proposed in `output-safety-layer.md` section 11, are registered (D-90) and tracked like any other row.
