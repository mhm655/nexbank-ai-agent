# Dashboards

Brief refs: A8.5 p.22 (Dashboard Specification: Real-Time Operations, Daily Performance, Weekly Strategic, with the content of each), A8.4 p.21 (detection within 15 minutes), A8.1 to A8.3 pp.19-21 (the metrics), A1.4 p.5 (industry benchmark for "competitive benchmarking"), A10.3 p.28 (access control: "Customer-facing staff access only anonymised, aggregated metrics"; "Supervisors access full logs only for conversations in their review queue"; "All log access itself is logged"), A1.3 p.4 (Customer Experience Board and Risk Committee), Part D Day 12-13 p.60 ("Design 3 dashboards: real-time operations, daily performance, weekly strategic"; deliverable "CSAT framework with dashboard wireframes"). Related: `kpi-framework.md` (KPI-L, KPI-G, KPI-O, KPI-A), `improvement-cycle.md`, `docs/guardrails/monitoring-dashboard.md` (heat map and DM-01 to DM-16), `docs/escalation/queue-management.md` (EQ-01 to EQ-12 and queue alerts), `docs/learning-pipeline/` (experiments, corrections, pipeline health).

**Status.** The brief lists what each of the three dashboards must show. The lists are quoted in each section and every listed item is mapped to a panel. Audiences, refresh rates, drill-down paths, panel layout and alert behaviour are proposals (D-133). The wireframes show layout only: every value position holds a placeholder (`--`), because no system exists and nothing has been measured. Tooling is not specified.

## 1. Common rules

| Topic | Rule |
|---|---|
| One definition per metric | A panel shows a metric by its ID. Formulas live in `kpi-framework.md`, `monitoring-dashboard.md` and `queue-management.md`; a dashboard never carries its own variant |
| Target and state | Every tile shows the value, the brief target, and a state: within target, warn, critical, or insufficient sample. States use a symbol as well as colour (`ok`, `!`, `!!`, `n<30`) |
| Counter-metrics | A headline metric is shown with its partner from `kpi-framework.md` section 8 on the same panel |
| Sample size | Sample-based values show `n` and an interval; a rolling CSAT with under 30 ratings shows the count and "insufficient sample" (`csat-signals.md` section 9) |
| Version marker | Every time series carries release markers for the prompt, model and KB epoch, so a step change can be tied to a release (`monitoring-dashboard.md` section 7) |
| Segments | Filters: intent, channel, language, authentication level, trigger, queue, version. Demographic cuts exist only in the fairness view, for the Risk Committee and the annual audit |
| Access (A10.3) | Tiles are anonymised aggregates. Drill-down to a conversation is allowed only to roles entitled to it: supervisors for conversations in their review queue, queue staff for their own handoffs, incident roles during an incident. Every drill-down is written to the meta-audit trail |
| No personal data on tiles | No names, no account or card fragments, no free text from customers on any tile. The PEP flag and AML cases never appear outside the Enhanced Due Diligence and AML Compliance views |
| Time | IST; the daily cut is 06:00 local, shared with the guardrail and learning dashboards |
| Alerts | Thresholds are defined with the metrics (`kpi-framework.md` sections 3.2, 4.2, 5.2; `monitoring-dashboard.md` section 6; `queue-management.md` section 9). The dashboards display and route them; they do not redefine them |

## 2. Real-Time Operations dashboard

The brief (A8.5): "Live conversation volume, active escalations, system health indicators"; "Rolling 1-hour CSAT, containment rate, and escalation rate"; "Guardrail trigger heat map showing most frequently activated safety boundaries"; "Alert panel for anomalous patterns (fraud report spikes, unusual escalation volume, system errors)".

| Aspect | Specification |
|---|---|
| Audience | Platform on-call, queue supervisors, the operations lead on shift, the Incident Commander during an incident, Security Operations for the adversarial panel |
| Question it answers | Is the service healthy right now, are customers reaching humans inside the SLA, and is anything unusual happening? |
| Refresh | Metric stream; panels redraw every 60 seconds (the Day 10 proposal); alert panel pushes at once |
| Window | Now, last 5 minutes, rolling 1 hour, with the same hour last week as the reference band |
| Detection duty | This is the DETECT surface for the 15-minute requirement (`improvement-cycle.md` section 2.2) |

### 2.1 Wireframe (layout only; no values)

```
+--------------------------------------------------------------------------------------------------------------+
| REAL-TIME OPERATIONS        window: rolling 1 h       as of --:--:-- IST      versions: p-- / m-- / kb e--   |
| mode: NORMAL | SAFE | TEMPLATE-ONLY | SURGE(queue)                              filters: channel language intent |
+----------------------------+----------------------------+----------------------------+-----------------------+
| A  LIVE VOLUME             | B  SYSTEM HEALTH           | C  ROLLING 1 H OUTCOMES    | D  ALERTS (newest)    |
| active conversations   --  | uptime (30 d)      --   ok | CSAT (n=--)        --   ok | !! --:-- fraud spike  |
| started / 5 min        --  | first response p95 --s  ok | containment        --%  ok | !  --:-- ESC volume   |
| vs same hour last wk   --% | turn latency p95   --s  ok | escalation rate    --%  ok | !  --:-- tool errors  |
| concurrent / capacity  --% | error rate         --%  ok | non-escalated      --%     | ok --:-- resolved     |
| [sparkline 60 min]         | tools: -- up  -- degraded  | unresolved-dropped --%     | [ack] [runbook] [mute]|
|                            | KB epoch age       --      | [3 sparklines 60 min]      |                       |
+----------------------------+----------------------------+----------------------------+-----------------------+
| E  ACTIVE ESCALATIONS                                                                                        |
| queue                   pri  waiting  oldest   SLA    attain 1h  agents  overflow  state                     |
| Crisis Response         P0     --      --s    IMMED     --%       --       --      ok                        |
| Security Operations     P0     --      --s    <2m       --%       --       --      ok                        |
| Fraud Investigation     P0     --      --s    <2m       --%       --       --      !                         |
| AML Compliance (cases)  P0     --      --s    <2m       --%       --       --      ok                        |
| ... 11 more queues in precedence order (P1, then P2) ...                                                     |
| totals: P0 --   P1 --   P2 --     pending de-escalation --     callbacks open --     failed handoffs 1h --   |
+-------------------------------------------------------+------------------------------------------------------+
| F  ESCALATIONS BY TRIGGER (last 60 min vs baseline)   | G  GUARDRAIL TRIGGER HEAT MAP (guardrail x hour)     |
| ESC-001 [bar] --  x--     ESC-009 [bar] --  x--       | view A of monitoring-dashboard.md section 3          |
| ESC-004 [bar] --  x--     ESC-006 [bar] --  x--       | symbols . o O # -   rows by severity C/H/M           |
| ... all 15 triggers and XTR additions ...             | hard-zero counters: --  (must be 0)                  |
| premature flags today --   rule-replay misses --      | adversarial attempts /1,000 sessions: --             |
+-------------------------------------------------------+------------------------------------------------------+
```

### 2.2 Panels

| Panel | Brief item | Metrics | Drill-down | Alerts shown |
|---|---|---|---|---|
| A Live volume | "Live conversation volume" | Active conversations; conversations started per 5 minutes; deviation from the same-hour baseline; concurrent conversations as a share of tested capacity (KPI-O4) | By channel, language, intent | Volume above or below band; capacity above 80 percent of the tested level |
| B System health | "system health indicators" | KPI-O3 uptime; KPI-L1 first response time; per-turn latency; error rate; tool and queue-platform status; KB epoch age; guard latency (DM-10); fallback load (DM-15) | By component and tool; to the incident if one is open | Uptime, latency, tool circuit open, template-only mode |
| C Rolling 1-hour outcomes | "Rolling 1-hour CSAT, containment rate, and escalation rate" | KPI-G1 (rolling, with `n`), KPI-G4, KPI-O2, with the non-escalated and unresolved-dropped shares as counter-metrics | By intent and language; to the daily dashboard | KPI thresholds for the rolling window |
| D Alert panel | "Alert panel for anomalous patterns (fraud report spikes, unusual escalation volume, system errors)" | Open alerts from all three threshold sources, deduplicated per signal, with severity, age, owner and runbook link | To the panel that owns the signal; acknowledge, mute with reason | Fraud reports (ESC-001 plus ESC-009) against baseline; trigger volume; SLA breach; system errors; hard-zero events; rule-replay miss |
| E Active escalations | "active escalations" | Per queue: waiting count, oldest wait, SLA, rolling attainment (EQ-07), agents available, overflow in use, state; totals by priority; pending de-escalations (EQ-09); callbacks; failed handoffs (EQ-06) | To the queue view (entitled roles only); to a handoff package for the receiving agent | Warn at 70 percent of an SLA; breach; queue unavailable; surge |
| F Escalations by trigger | "unusual escalation volume" | Count per trigger and addition against the same-hour baseline; premature flags from wrap-up codes; rule-replay misses | By sub-rule, source (customer or system), language | 2 times and 3 times baseline |
| G Guardrail heat map | "Guardrail trigger heat map showing most frequently activated safety boundaries" | Defined in `monitoring-dashboard.md` section 3 (views A and B), with DM-12 hard-zero counters and DM-08 adversarial rate | Cell to the guardrail's samples (entitled roles) | As `monitoring-dashboard.md` section 6 |

Operating notes: the mode banner shows safe mode, template-only mode or a queue surge when one is active, with who declared it and when. A panel whose data is older than 2 refresh cycles greys out and says so; stale data is never shown as current. During an incident the Incident Commander can pin the affected panels.

## 3. Daily Performance dashboard

The brief (A8.5): "24-hour trend lines for all leading and lagging indicators"; "Conversation funnel analysis: started > engaged > resolved > satisfied"; "Top 10 unresolved intents and top 10 low-confidence interactions for review"; "Supervisor correction summary with categorisation of correction types".

| Aspect | Specification |
|---|---|
| Audience | CX Team, NLU Team, ML Team, KB owners, review leads, queue owners, the Regulatory Compliance Manager for the incorrect-advice row |
| Question it answers | How did yesterday go against the targets, where did conversations fail, and what should be reviewed or fixed today? |
| Refresh | Daily at 06:00 local for the previous 24 hours; trend lines are hourly points; a rerun is possible on demand |
| Window | Previous 24 hours, with the 7-day and 28-day averages as reference |
| Role in the cycle | Input to the daily triage (`improvement-cycle.md` section 8) |

### 3.1 Wireframe (layout only; no values)

```
+--------------------------------------------------------------------------------------------------------------+
| DAILY PERFORMANCE      day: ----------      cut 06:00 IST      releases yesterday: --      conversations: -- |
+--------------------------------------------------------------------------------------------------------------+
| A  LEADING INDICATORS (24 h trend, hourly)                 value   target      7 d    28 d   state          |
| L1 first response time p95     [trend .........]            --s    <5 s        --     --      ok            |
| L2 intent accuracy (n=--)      [trend .........]            --%    >92%        --     --      ok            |
| L3 entity accuracy (n=--)      [trend .........]            --%    >95%        --     --      ok            |
| L4 sentiment slope             [trend .........]            --     pos/stable  --     --      ok            |
| L5 retrieval relevance         [trend .........]            --     >0.85       --     --      ok            |
| L6 guardrail false positives   [trend .........]            --%    <3%         --     --      ok            |
| L7 confidence above 0.7        [trend .........]            --%    >80% (wk)   --     --      ok            |
+--------------------------------------------------------------------------------------------------------------+
| B  LAGGING AND OPERATIONAL (24 h trend; weekly and monthly metrics show the running value)                  |
| G1 CSAT (n=--, resp --%)  --  >=4.5 | G3 FCR (provisional) --% >=70% | G4 containment --% >=70%            |
| G6 incorrect advice  -- cases  0%   | O1 handle time  --m  <8 m      | O2 escalation   --% <30%            |
| G2 NPS, G5 CES, G7 retention: last reported value and date            | O3 uptime --% | O5 coverage --%    |
+------------------------------------------------+-------------------------------------------------------------+
| C  CONVERSATION FUNNEL                         | D  ESCALATION QUALITY                                       |
| started     ######################  --   100%  | by trigger: fired  handed off  de-esc  SLA met  premature  |
| engaged     ###################     --   --%   | ESC-001      --       --         -       --%       --      |
| resolved    ##############          --   --%   | ESC-004      --       --        --       --%       --      |
|   by AI --   by human --                       | ... all triggers ...                                       |
| satisfied   #########               --   --%   | EQ-01 premature --%   EQ-02 missed --   replay misses --   |
| drop-off: engaged>resolved by intent [top 5]   | EQ-03 wrong queue --%  EQ-05 repeated info --%  EQ-08 --%  |
+------------------------------------------------+-------------------------------------------------------------+
| E  TOP 10 UNRESOLVED INTENTS                   | F  TOP 10 LOW-CONFIDENCE INTERACTIONS (for review)          |
| #  intent / tertiary     unresolved  share gap | #  conv ref   min conf  intent guess   lang   outcome       |
| 1  -------------------      --        --%  --% | 1  --------     --      ----------     --     ---------    |
| ...                                            | ...                                          [send to queue]|
+------------------------------------------------+-------------------------------------------------------------+
| G  SUPERVISOR CORRECTION SUMMARY               | H  GUARDRAILS (24 h)                                        |
| reviewed --  of sampled --   backlog --        | top 10 by trigger; FP estimate vs bound; near-misses        |
| severity: S1 --  S2 --  S3 --  S4 --  none --  | (monitoring-dashboard.md, daily view)                       |
| component: nlu -- retrieval -- kb -- gen --    |                                                             |
|   policy -- escalation -- guardrail -- tool -- |                                                             |
| escalation verdict: missed -- unnecessary --   |                                                             |
+------------------------------------------------+-------------------------------------------------------------+
```

### 3.2 Panels

| Panel | Brief item | Metrics | Drill-down | Alerts shown |
|---|---|---|---|---|
| A Leading indicators | "24-hour trend lines for all leading ... indicators" | KPI-L1 to KPI-L7, each with value, brief target, 7-day and 28-day references, sample size where labelled | By intent, language, channel, version; KPI-L2 to the confusion matrix; KPI-L6 to DM-04 and DM-05 | Thresholds of `kpi-framework.md` section 3.2 |
| B Lagging and operational | "24-hour trend lines for all ... lagging indicators" | KPI-G1, KPI-G3 (provisional until the 7-day window matures), KPI-G4, KPI-G6, KPI-O1, KPI-O2 as daily trends; KPI-G2, KPI-G5, KPI-G7, KPI-O3 to KPI-O6 as the last reported value with its date | By outcome class and intent category; KPI-A8 against the A1.2 baselines | Thresholds of sections 4.2 and 5.2 |
| C Conversation funnel | "Conversation funnel analysis: started > engaged > resolved > satisfied" | Counts and stage-to-stage conversion: started (at least one customer message); engaged (at least one in-scope intent recognised beyond a greeting); resolved (`resolved_ai` or `resolved_human`); satisfied (rating of 4 or 5, shown as a count of rated conversations and as the weighted estimate) | Drop-off by intent, language and stage; to example conversations for entitled roles | A stage conversion below its 28-day band |
| D Escalation quality | (supports "top unresolved" and the cycle) | Per trigger: fired, handed off, de-escalated, SLA attainment; EQ-01 to EQ-08 | By sub-rule, queue, language | `queue-management.md` section 9 |
| E Top 10 unresolved intents | "Top 10 unresolved intents" | Intents and tertiaries ranked by unresolved-dropped plus unresolved-escalated count, with share of that intent's volume and gap-decision share | To retrieval decisions and KB entries for the intent; opens a finding | Any intent new to the list for 3 days |
| F Top 10 low-confidence interactions | "top 10 low-confidence interactions for review" | Conversations ranked by lowest intent or retrieval confidence, with the guessed intent, language and outcome; always included in review stream C (`supervisor-corrections.md` section 2.1) | "Send to review queue" for entitled roles only | None; it is a work list |
| G Supervisor correction summary | "Supervisor correction summary with categorisation of correction types" | Reviewed against sampled and backlog (DM-14, KPI-A5); counts by severity S1 to S4 (the A5.1 classes), by component, by escalation verdict; reviewer agreement | By stream, reviewer group, intent, language | Any S1; backlog thresholds |
| H Guardrails | (Day 10 daily view) | As `monitoring-dashboard.md` section 1: 24-hour trends of DM-01 to DM-12, top 10 guardrails, near-misses | As Day 10 | As Day 10 |

Funnel definitions are proposals. "Satisfied" is the weakest stage because only rated conversations are observed; the panel shows the response rate beside it and never extrapolates silently.

## 4. Weekly Strategic dashboard

The brief (A8.5): "Week-over-week improvement trends for all KPIs"; "A/B test results and pending experiment pipeline"; "Knowledge base gap analysis with recommended updates"; "Competitive benchmarking against industry metrics"; "Learning pipeline metrics: training data volume, model version history, safety test pass rates".

| Aspect | Specification |
|---|---|
| Audience | Customer Experience Board, Risk Committee, the Chief Technology Officer, team leads |
| Question it answers | Are we improving, is it safe, what are we testing, and what should we decide this week? |
| Refresh | Weekly, Monday 06:00 local, for the previous Monday to Sunday; monthly and quarterly metrics update when they report |
| Window | Last complete week against the previous week, the 4-week and 13-week trends |
| Role in the cycle | The agenda of the weekly improvement review (`improvement-cycle.md` section 8) |

### 4.1 Wireframe (layout only; no values)

```
+--------------------------------------------------------------------------------------------------------------+
| WEEKLY STRATEGIC      week: ------ to ------      conversations: --      releases: --      incidents: --    |
+--------------------------------------------------------------------------------------------------------------+
| A  KPI SCORECARD (week over week)             this wk   last wk   change   13-wk trend     target   state   |
| CSAT (G1)                                       --        --       --      [..........]     >=4.5    ok      |
| First contact resolution (G3)                   --%       --%      --      [..........]     >=70%    ok      |
| Containment (G4) / non-escalated share          --% / --% --%      --      [..........]     >=70%    ok      |
| Incorrect advice (G6)                           --        --       --      [..........]     0%       ok      |
| Escalation rate (O2) / premature / missed       --% --% -- --%     --      [..........]     <30%     ok      |
| Handle time (O1)                                --m       --m      --      [..........]     <8 m     ok      |
| First response time p95 (L1)                    --s       --s      --      [..........]     <5 s     ok      |
| Intent (L2) / entity (L3) accuracy              --% / --% --%      --      [..........]     >92/95%  ok      |
| Sentiment slope (L4)                            --        --       --      [..........]     pos/stbl ok      |
| Confidence above 0.7 (L7)                       --%       --%      --      [..........]     >80%     ok      |
| Retrieval relevance (L5) / KB coverage (O5)     -- / --%  --       --      [..........]     >0.85/90 ok      |
| Guardrail FP (L6) / hard-zero events            --% / --  --%      --      [..........]     <3% / 0  ok      |
| Uptime (O3) / capacity test (O4) / drift (O6)   --% -- -- --       --      [..........]     99.9/10k ok      |
| NPS (G2) / CES (G5) / retention (G7)            last reported: -- / -- / --  (date)         50/5.5/+        |
+------------------------------------------------+-------------------------------------------------------------+
| B  EXPERIMENTS                                 | C  KNOWLEDGE BASE GAP ANALYSIS                              |
| running:   id  surface  stage  day  T0 state   | top gaps by volume: topic  queries  gap%  recommended action|
| ---------  --  -------  --%    --    ok        | 1 ------------------  --     --%   new entry / owner ----  |
| decided this week:  id  result  CSAT  FCR      | 2 ------------------  --     --%   update / expiring ----  |
| ---------  kept / rolled back   -- (CI)  --    | entries expiring in 30 d: --   stale flags: --             |
| pending pipeline: -- registered  -- in review  | change requests open: --   median age: -- d                |
+------------------------------------------------+-------------------------------------------------------------+
| D  COMPETITIVE BENCHMARK                       | E  LEARNING PIPELINE                                        |
| containment: NexBank --% | industry 65%        | training data: rows --  by source --  by language --       |
|   A 35%  B 52%  C 48%  | target 70%            | versions live: prompt --  model --  kb epoch --            |
| CSAT: NexBank -- | industry 4.0+ | target 4.5  | version history: [timeline of releases and rollbacks]      |
| incorrect advice: NexBank -- | industry <2%    | safety suite: -- / -- cases  --%  (must be 100%)           |
|   target 0%                                    | red-team run: -- breaches   reviewer agreement: --         |
| first reply: NexBank --s | target <30 s        | corrections this week: S1 -- S2 -- S3 -- S4 --             |
+------------------------------------------------+-------------------------------------------------------------+
| F  ESCALATION AND QUEUES (week)                | G  DECISIONS NEEDED                                         |
| SLA attainment P0 --%  P1 --%  P2 --%          | 1 ------------------------------  owner ----  by ----      |
| volume by trigger [bars]   overflow --%        | 2 ------------------------------  owner ----  by ----      |
| capacity: planned FTE -- vs worked --          | improvement records closed: --   findings open: --         |
+------------------------------------------------+-------------------------------------------------------------+
```

### 4.2 Panels

| Panel | Brief item | Metrics | Drill-down | Alerts shown |
|---|---|---|---|---|
| A KPI scorecard | "Week-over-week improvement trends for all KPIs" | Every KPI-L, KPI-G and KPI-O metric with this week, last week, change, 13-week trend, brief target and state; counter-metrics on the same row | To the daily dashboard for the week; by segment; fairness view for entitled roles | Any KPI outside target for 2 consecutive weeks; any gate metric above zero |
| B Experiments | "A/B test results and pending experiment pipeline" | From the experiment registry: running experiments with stage, day and Tier 0 state; decisions of the week with effect sizes and intervals; registered and in-review counts (`ab-testing.md` section 11) | To the experiment record | A breaker event; an experiment past its planned duration |
| C KB gap analysis | "Knowledge base gap analysis with recommended updates" | KPI-O5; top gap topics by query volume and gap-decision share, each with a recommended action (new entry, update, translation) and the owning approval chain; expiring and stale entries; open change requests | To the queries behind a gap (aggregated) and to the KB entry | Coverage thresholds; a regulatory entry within 14 days of expiry |
| D Competitive benchmark | "Competitive benchmarking against industry metrics" | KPI-A9: containment, CSAT and incorrect-advice rate against the brief's industry benchmark (65 percent, 4.0+, below 2 percent), the three competitors' containment (35, 52, 48 percent) and the design targets (A1.4) | None | None |
| E Learning pipeline | "Learning pipeline metrics: training data volume, model version history, safety test pass rates" | The pipeline health metrics of `docs/learning-pipeline/overview.md` section 7: training data volume, version history, safety suite pass rate (DM-13), plus corrections by severity and reviewer agreement | To the release record and the suite report | Suite below 100 percent; drift at or above 0.04 |
| F Escalation and queues | (supports the brief's KPI list) | EQ-07 by priority; volume by trigger; overflow and after-hours share; planned capacity against worked (`queue-management.md` section 6) | To the daily escalation panel | Attainment below target for the week |
| G Decisions needed | (supports DESIGN and DOCUMENT) | Open decisions with owner and date; improvement records closed; open findings | To the record | Overdue decisions |

Benchmark figures are the brief's (A1.4) and are fixed labels on the panel; no external market data is introduced. The comparison is indicative: competitors' definitions of containment are not known.

## 5. Views by audience

| Audience | Default view | What they may open |
|---|---|---|
| Platform on-call | Real-time A, B, D | Component metrics; no conversation content |
| Queue supervisors | Real-time E, F | Their own queue's handoffs and packages |
| Review leads and supervisors | Daily F, G | Conversations in their review queue (A10.3) |
| NLU Team, ML Team, KB owners | Daily A, E; weekly C, E | Aggregates; labelled samples through the review tool |
| CX Team | Daily B, C, D; weekly A | Aggregates |
| Customer Experience Board | Weekly A, B, D, G | Aggregates only |
| Risk Committee | Weekly A (gate rows), E, F; the guardrail dashboard; the fairness view | Aggregates; incident evidence through the playbook |
| Customer-facing staff | A summary tile set | Anonymised, aggregated metrics only (A10.3) |

## 6. Alert handling on the dashboards

1. Each alert carries: the metric ID, the segment, the window, the value against threshold or baseline, the version tuple, the owner, the runbook or section link and a severity (SEV levels of the playbook where it is an incident).
2. Alerts are deduplicated per signal and segment, auto-resolve only after two clean windows, and can be muted only with a reason and an expiry; muting is logged.
3. An alert acknowledged but not resolved inside its window escalates to the owner's lead. A hard-zero event cannot be muted.
4. Alert volume is itself watched: more than a set number of alerts per shift that led to no action opens a threshold review, because an ignored alert panel defeats the 15-minute requirement.
5. Every alert that leads to action becomes a finding (`improvement-cycle.md` section 2.3).

## 7. Coverage of the brief's list

| Brief item (A8.5) | Dashboard | Panel |
|---|---|---|
| Live conversation volume | Real-time | A |
| Active escalations | Real-time | E |
| System health indicators | Real-time | B |
| Rolling 1-hour CSAT, containment rate, escalation rate | Real-time | C |
| Guardrail trigger heat map | Real-time | G |
| Alert panel: fraud report spikes, unusual escalation volume, system errors | Real-time | D, F |
| 24-hour trend lines for all leading and lagging indicators | Daily | A, B |
| Conversation funnel: started > engaged > resolved > satisfied | Daily | C |
| Top 10 unresolved intents | Daily | E |
| Top 10 low-confidence interactions for review | Daily | F |
| Supervisor correction summary with categorisation | Daily | G |
| Week-over-week improvement trends for all KPIs | Weekly | A |
| A/B test results and pending experiment pipeline | Weekly | B |
| Knowledge base gap analysis with recommended updates | Weekly | C |
| Competitive benchmarking against industry metrics | Weekly | D |
| Learning pipeline metrics: training data volume, model version history, safety test pass rates | Weekly | E |

All 16 items the brief lists are mapped. Panels not asked for by the brief (escalation quality, queues, decisions) are additions that serve the improvement cycle.

## 8. Decisions and open items

Decision: D-133 (audiences, refresh, windows, panel content beyond the brief's list, funnel stage definitions, alert handling).

Open items:

1. Tooling, rendering and the telemetry pipeline are implementation choices.
2. The funnel's "engaged" and "satisfied" definitions need CEB agreement.
3. The fairness view's access list is a Risk Committee decision.
4. The wireframes hold no values by design; first real values come from the shadow period.
