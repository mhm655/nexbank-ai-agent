# Queue Management

Brief refs: A6 pp.16-17 (15 target queues, priorities and SLAs), Part D Day 12-13 p.60 ("Design queue management: overflow, after-hours routing, priority rebalancing"; "Define escalation quality metrics and de-escalation logic"), A1.1 p.3 (450 call-centre agents, approximately 18,000 interactions daily, replace 60% of first-line support), A1.2 pp.3-4 (category counts in the 500 transcripts), A8.3 p.20 (Escalation Rate below 30 percent, daily), A8.2 p.20 (Containment at least 70 percent), A8.5 p.22 (active escalations; alerts for fraud report spikes and unusual escalation volume), A5.1 p.15 (correction taxonomy includes "false positive escalation"; 50 reviews per supervisor per day), A9.2 p.25 (Premature Escalation), A11.2 p.31 (auto-escalation on negative sentiment as a churn mitigation), Case Study 3 p.51 (30-minute advisor consultation). Rules: `config/escalation_rules.yaml` (`queues`, `queue_hours`, `after_hours`, `proposals`). Triggers: `triggers.md`. Handoff: `routing-and-handoff.md`. Metrics: `docs/metrics/kpi-framework.md`.

**Status.** The brief names the 15 queues and their SLAs and asks for overflow, after-hours routing, priority rebalancing and escalation quality metrics. It gives no operating hours, no staffing, no handling times, no overflow order and no metric definitions. Every such value below is a proposal or an assumption and is labelled (D-122, D-127, D-128, D-130, D-131). The capacity figures are the output of a model run on stated assumptions; they are not measurements, and no queue exists yet.

## 1. Scope

How the 15 queues are operated once the Escalation Router has chosen one: hours, overflow, behaviour at and after an SLA breach, how many people the queues need under stated assumptions, how work is reordered when queues are under pressure, and how the quality of escalation decisions is measured.

## 2. The queues

The queue names, the trigger each serves, the priority and the SLA are the brief's (A6). Mode, hours and languages are proposals.

| Queue (brief) | Trigger | Priority | SLA (brief) | Mode | Hours (proposal) | Notes |
|---|---|---|---|---|---|---|
| Crisis Response | ESC-011 | P0 | IMMEDIATE | live, pre-emptive | 24x7 | Trained crisis handlers; never single-staffed |
| Security Operations | ESC-009 | P0 | <2 min | live | 24x7 | Also receives the adversarial alert feed (`monitoring-dashboard.md` section 6) |
| Fraud Investigation | ESC-001 | P0 | <2 min | live; case for system-sourced records | 24x7 | Largest P0 queue |
| AML Compliance | ESC-012 | P0 | <2 min | case (no customer contact) | 24x7 | SLA measured to analyst acceptance |
| Enhanced Due Diligence | ESC-015 | P1 | <5 min | live, discreet | extended | Sees the PEP flag; other queues do not |
| Senior Resolution Mgr | ESC-002 | P1 | <5 min | live | extended | Legal-threat handling |
| Dispute Resolution | ESC-005 | P1 | <5 min | live | extended | Also receives XTR-05 referrals |
| Relationship Manager | ESC-007 | P1 | <5 min | live | extended | Small volume; callback is common after hours |
| Customer Retention | ESC-004 | P1 | <5 min | live | extended | Language match preferred |
| Compliance Helpdesk | ESC-008 | P1 | <10 min | live | extended | No generalist substitute |
| Wealth Advisory | ESC-013 | P1 | <10 min | live | extended | SEBI-registered advisors only; no generalist substitute |
| Next Available Agent | ESC-006 | P2 | <10 min | live | 24x7 | Also XTR-01, XTR-03 and the after-hours P1 intake |
| Technical Support | ESC-014 | P2 | <10 min | live plus incident feed | extended | One incident per fault, not one per customer |
| General Support | ESC-003 | P2 | <10 min | live | 24x7 | Also XTR-04 and XTR-07 referrals; secondary languages |
| Supervisor Review | ESC-010 | P2 | <15 min | live | extended | Also receives XTR-06 |

`extended` is 08:00 to 22:00 IST on all days (proposal, D-122). Order inside a queue: priority, then earliest SLA deadline, with a repeat contact ahead of a first contact at the same deadline (`routing-and-handoff.md` section 4.3).

## 3. Overflow

Because each trigger has its own queue, overflow borrows from another brief queue. No new queue is created. Overflow is used when the target queue is closed, unavailable, or forecast to miss the SLA. The last step is always a callback request, except for Crisis Response.

| Queue | Overflow chain (proposal, D-127) | Rule for the borrowed queue |
|---|---|---|
| Crisis Response | Senior Resolution Mgr, Security Operations, Next Available Agent | Any human with the crisis script is better than none; the crisis template stays on screen; no callback-only outcome |
| Security Operations | Fraud Investigation, Senior Resolution Mgr, callback | The two security queues back each other up |
| Fraud Investigation | Security Operations, Senior Resolution Mgr, callback | Protective actions already taken stay in place |
| AML Compliance | Enhanced Due Diligence, Compliance Helpdesk | Case queues only; no customer contact |
| Enhanced Due Diligence | AML Compliance, Compliance Helpdesk, callback | Only roles permitted to see the flag |
| Senior Resolution Mgr | Customer Retention, Supervisor Review, callback | Borrowed agent takes the conversation; the case stays owned by the Senior Resolution Mgr queue |
| Dispute Resolution | General Support, callback | General Support completes the intake only |
| Relationship Manager | Customer Retention, callback | Reason recorded; Relationship Manager follows up |
| Customer Retention | Senior Resolution Mgr, Next Available Agent, callback | |
| Compliance Helpdesk | callback | Nobody else may answer the regulatory question (GR-REG-18) |
| Wealth Advisory | callback | Nobody else may advise (GR-ADV-08; existing oracle GR-ADV-08-03) |
| Next Available Agent | General Support, Supervisor Review, callback | |
| Technical Support | General Support, callback | Honest status; the incident stays open |
| General Support | Next Available Agent, Supervisor Review, callback | |
| Supervisor Review | Senior Resolution Mgr, General Support, callback | |

Overflow rules:

1. A P0 escalation is never placed in a P2 pool while a P0 or P1 queue can take it, and a P0 customer is never left with only a callback while any human is available. If every step fails, the first available human in any queue takes it and an incident is opened.
2. A borrowed agent handles the conversation at the original priority and against the original SLA deadline. Overflow does not restart the clock.
3. The package states that the handoff was overflowed and from where, so the borrowed agent knows the specialist queue still owns the case.
4. A callback is a request, not a guarantee (D-09). The agent states no callback time unless the queue platform returns a slot.
5. Each overflow event is logged with its reason (closed, unavailable, forecast breach) and counted in EQ-07.

## 4. After-hours routing

The brief gives no hours. Proposal (D-122): the four P0 queues, Next Available Agent and General Support are staffed 24x7; the other nine queues are staffed in extended hours.

| Trigger class | Outside extended hours |
|---|---|
| P0 (ESC-001, ESC-009, ESC-011, ESC-012) | No change. 24x7 |
| P1 with a generalist intake: ESC-002, ESC-004, ESC-005, ESC-007 | Live handoff to Next Available Agent with the full package. The specialist case is opened in the target queue for the next opening. A callback request is offered. The 5-minute SLA is measured to the generalist's first message; the time to specialist contact is reported separately |
| P1 with no generalist substitute: ESC-008, ESC-013 | Callback request only. The agent keeps giving factual KB information |
| ESC-015 | Account-specific requests wait for the desk; callback offered; generic information is still served |
| P2: ESC-003, ESC-006 | No change. 24x7 |
| P2: ESC-010, ESC-014 | The overflow chain (General Support), then callback |
| Referrals: XTR-05, XTR-07 | Worked at the next opening |

After-hours honesty: the customer is told which team is and is not available now, in plain words, and is never told a specialist will join when none is on shift (A9.2 False Confidence). Persona Arjun (A13.2, Dubai time zone) makes this path routine rather than rare.

## 5. SLA-breach handling

SLA clock definitions are in `routing-and-handoff.md` section 3. Thresholds below are proposals (D-128); the warn level reuses the 70 percent convention of `monitoring-dashboard.md` section 6.

| Stage | When | P0 (120 s) | P1 (300 s or 600 s) | P2 (600 s or 900 s) |
|---|---|---|---|---|
| Warn | 70 percent of the SLA with no acceptance | 84 s: queue supervisor paged; overflow chain started in parallel | 210 s or 420 s: supervisor alerted; a cross-skilled agent is requested (section 7) | 420 s or 630 s: supervisor alerted |
| Customer choice | At the warn stage | None offered; the customer stays in the queue | Keep waiting or request a callback | Keep waiting or request a callback |
| Breach | 100 percent of the SLA | Next overflow step at once; any available human; incident opened (SEV2 for one breach, SEV1 if a customer loss or a crisis is involved; `incident-response-playbook.md` section 2) | Next overflow step; honest message; breach logged | Next overflow step; honest message; breach logged |
| Sustained breach | Attainment below the target for two consecutive 5-minute windows | Surge mode for the queue (section 7); Risk Committee informed through the incident | Rebalancing (section 7) | Callback mode for new P2 arrivals |
| ESC-011 | 60 s pickup target (proposal) | Any breach is reviewed individually, whatever the count | | |

Attainment targets (proposal): the share of escalations whose SLA is met should be at least 95 percent for P0, 90 percent for P1 and 85 percent for P2, measured per trigger per day. The brief states the SLAs but no attainment percentage. What the customer sees at a breach is the TPL-ESC-WAIT-UPDATE and TPL-ESC-HANDOFF-FAILED wording of `routing-and-handoff.md` sections 7 and 8: honest, no blame, no invented time.

A breach is a queue outcome, not an agent error, and is reported separately from the escalation-quality labels in section 8.

### 5.1 Resolution horizon for outcome classification

The A6 SLAs are response times, not resolution times. `docs/learning-pipeline/outcome-tracking.md` needs a "working SLA horizon" per queue to class an escalated conversation as unresolved-escalated. Proposal (D-128): 24 hours after the handoff for every live queue. A case still open then is classed unresolved-escalated provisionally and is reclassified resolved-with-escalation when the queue closes it as resolved. For the case queues (AML Compliance, Enhanced Due Diligence) the class follows the customer's own request, not the compliance case. The horizon is an internal classification cut-off; it is never stated to a customer as a promise (D-09).

## 6. Capacity model

### 6.1 What the brief gives

| Fact | Value | Source |
|---|---|---|
| Interactions per day | approximately 18,000 | A1.1 p.3 |
| Legacy staffing | 450 agents | A1.1 p.3 |
| Board aim | replace 60 percent of first-line support | A1.1 p.3 |
| Escalation rate target | below 30 percent | A8.3 p.20 |
| Containment target | at least 70 percent | A8.2 p.20; A1.4 p.5 |
| Category mix of the 500 transcripts | 85, 72, 58, 64, 45, 38, 42, 51, 28, 17 | A1.2 pp.3-4 |
| Advisor consultation | 30 minutes | Case Study 3 p.51 |

Derived by arithmetic from these: 30 percent of 18,000 is 5,400 escalations a day at the ceiling; the average arrival rate is 750 interactions an hour; 450 agents for 18,000 interactions is 40 interactions per agent per day; 40 percent of 450 is 180 agents remaining after a 60 percent replacement.

### 6.2 Assumptions (all proposals, D-130)

None of the following is in the brief. Each is a planning assumption to be replaced by measured values in the shadow period.

| Assumption | Value | Basis |
|---|---|---|
| Category mix of live traffic | the A1.2 shares | Assumption A2 (the table is the data) |
| Share of each category that escalates, by queue | table 6.3 | Judgement; fraud is 100 percent because rule 6 forbids containing it |
| Cross-category flows as a share of all interactions | Crisis 0.05 percent, AML 0.05 percent, PEP 0.1 percent, high-value closure 0.05 percent | Placeholders; no data exists |
| Arrival profile | 4 hours at 3.0 times the average hourly rate, 10 hours at 1.0, 10 hours at 0.2 (sums to 24) | The 3x peak-to-average ratio of `latency-scalability-cost.md` |
| Human handling time per escalation | Crisis 30 min; Fraud and Security 15; AML, Due Diligence and Senior Resolution 20; Relationship Manager 15; Disputes and Retention 12; Compliance, Technical and Supervisor 10; General and Next Available 8; Wealth Advisory 30 | Judgement, except Wealth Advisory (Case Study 3) |
| Service model | Erlang C per queue, no abandonment, no pooling across queues | Conservative: 15 separate queues are the least efficient arrangement |
| Attainment target used for sizing | 95, 90, 85 percent for P0, P1, P2 | Section 5 |
| Minimum seats | 2 for a P0 queue, 1 otherwise | A P0 queue is never single-staffed |
| Shrinkage, working week, occupancy cap | 30 percent, 40 hours, 80 percent | Common planning values, stated as assumptions |
| After-hours P1 volume | the night share (8.3 percent) of the extended-hours P1 queues is carried at night by Next Available Agent | Section 4 |

### 6.3 Assumed escalation share by category and queue

| Category (A1.2) | Share of volume | Per day | Assumed share escalated | To queues (share of the category) |
|---|---|---|---|---|
| Account Balance & Statement | 17.0% | 3,060 | 3% | General Support 1, Next Available Agent 1, Technical Support 1 |
| Transaction Dispute & Chargeback | 14.4% | 2,592 | 28% | Dispute Resolution 12, Fraud Investigation 8, Customer Retention 3, Next Available Agent 3, Supervisor Review 2 |
| Product Recommendation | 11.6% | 2,088 | 16% | Wealth Advisory 10, Compliance Helpdesk 4, General Support 2 |
| Complaint Resolution & Escalation | 12.8% | 2,304 | 39% | Customer Retention 14, Next Available Agent 10, Supervisor Review 8, Senior Resolution Mgr 5, General Support 2 |
| KYC Update & Documents | 9.0% | 1,620 | 10% | Compliance Helpdesk 4, Next Available Agent 3, General Support 2, Enhanced Due Diligence 1 |
| Card Blocking & Replacement | 7.6% | 1,368 | 4% | Fraud Investigation 2, Next Available Agent 1, Technical Support 1 |
| Loan Enquiry & EMI Restructuring | 8.4% | 1,512 | 21% | Next Available Agent 8, Compliance Helpdesk 6, Wealth Advisory 4, General Support 3 |
| UPI / NEFT / RTGS Payment Issues | 10.2% | 1,836 | 15% | Technical Support 5, Customer Retention 3, Next Available Agent 3, Dispute Resolution 2, General Support 2 |
| Fixed Deposit & Investment | 5.6% | 1,008 | 12% | Wealth Advisory 8, Compliance Helpdesk 3, Relationship Manager 1 |
| Fraud Alert & Account Security | 3.4% | 612 | 100% | Fraud Investigation 65, Security Operations 33, AML Compliance 2 |

### 6.4 Method

For each queue: daily volume from table 6.3; peak-hour arrivals at 3.0 times the average; offered load in Erlangs = arrivals per hour times handling time in hours; the smallest number of seats `N` for which the Erlang C probability of waiting no longer than the SLA reaches the attainment target, `1 - C(N, a) * exp(-(N - a) * T / AHT)`, with `T` the SLA in seconds (60 for Crisis Response). Two headcount views are reported, because they answer different questions:

- **FTE by workload** = handling hours a day times 7, divided by (40 hours times 0.70 times 0.80). This is the pooled lower bound: it assumes work can be shared perfectly.
- **FTE by seat cover** = seat-hours a day (peak seats for 4 hours, day seats for 10 hours, night seats for 10 hours on 24x7 queues) times 7, divided by (40 hours times 0.70). This is the cost of keeping 15 separate queues staffed to their SLAs.

The script is a scratch file outside the repository; its inputs are the tables above and `config/escalation_rules.yaml`. All figures below were produced by it and are reproduced unedited.

### 6.5 Scenario A: design mix

Result of the model run: design mix (assumption): escalations/day 3638 = 20.2 percent of 18000.

| Queue | Trigger | Pri | SLA s | Hours | Esc/day | Peak/h | AHT min | Peak load (Erl) | Peak seats | Attainment at peak | Day seats | Night seats | Workload h/day | FTE by workload | FTE by seat cover |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Crisis Response | ESC-011 | P0 | 60 | 24x7 | 9 | 1.1 | 30 | 0.56 | 3 | 98.1% | 2 | 2 | 4.5 | 1.4 | 13.0 |
| Security Operations | ESC-009 | P0 | 120 | 24x7 | 202 | 25.2 | 15 | 6.31 | 11 | 96.4% | 5 | 3 | 50.5 | 15.8 | 31.0 |
| Fraud Investigation | ESC-001 | P0 | 120 | 24x7 | 633 | 79.1 | 15 | 19.77 | 27 | 96.7% | 11 | 4 | 158.1 | 49.4 | 64.5 |
| AML Compliance | ESC-012 | P0 | 120 | 24x7 | 21 | 2.7 | 20 | 0.89 | 4 | 99.0% | 2 | 2 | 7.1 | 2.2 | 14.0 |
| Enhanced Due Diligence | ESC-015 | P1 | 300 | extended | 34 | 4.3 | 20 | 1.43 | 4 | 96.7% | 2 | 0 | 11.4 | 3.6 | 9.0 |
| Senior Resolution Mgr | ESC-002 | P1 | 300 | extended | 115 | 14.4 | 20 | 4.80 | 8 | 93.7% | 4 | 0 | 38.4 | 12.0 | 18.0 |
| Dispute Resolution | ESC-005 | P1 | 300 | extended | 348 | 43.5 | 12 | 8.69 | 12 | 94.4% | 5 | 0 | 69.6 | 21.7 | 24.5 |
| Relationship Manager | ESC-007 | P1 | 300 | extended | 19 | 2.4 | 15 | 0.60 | 2 | 91.4% | 2 | 0 | 4.8 | 1.5 | 7.0 |
| Customer Retention | ESC-004 | P1 | 300 | extended | 455 | 56.9 | 12 | 11.38 | 15 | 94.8% | 6 | 0 | 91.1 | 28.5 | 30.0 |
| Compliance Helpdesk | ESC-008 | P1 | 600 | extended | 269 | 33.7 | 10 | 5.61 | 8 | 97.5% | 4 | 0 | 44.9 | 14.0 | 18.0 |
| Wealth Advisory | ESC-013 | P1 | 600 | extended | 350 | 43.7 | 30 | 21.87 | 26 | 92.4% | 11 | 0 | 175.0 | 54.7 | 53.5 |
| Next Available Agent | ESC-006 | P2 | 600 | 24x7 | 577 | 72.1 | 8 | 9.62 | 11 | 89.7% | 5 | 4 | 76.9 | 24.0 | 33.5 |
| Technical Support | ESC-014 | P2 | 600 | extended | 136 | 17.0 | 10 | 2.84 | 4 | 86.2% | 2 | 0 | 22.7 | 7.1 | 9.0 |
| General Support | ESC-003 | P2 | 600 | 24x7 | 233 | 29.1 | 8 | 3.88 | 5 | 87.4% | 3 | 1 | 31.1 | 9.7 | 15.0 |
| Supervisor Review | ESC-010 | P2 | 900 | extended | 236 | 29.5 | 10 | 4.92 | 6 | 88.9% | 3 | 0 | 39.4 | 12.3 | 13.5 |
| **Total** | | | | | **3638** | | | | **146** | | | | **825.3** | **257.9** | **353.5** |

- after-hours P1 volume carried by Next Available Agent at night: 133/day (night share 8.3 percent)
- by priority/day: P0 865, P1 1591, P2 1182
- mean human handling time per escalation: 13.6 min
- containment (no escalation record): 79.8 percent (target >= 70 percent)
- FTE by workload: 258 = 57 percent of the legacy 450; 143 percent of 180 (the 40 percent left after a 60 percent replacement)
- FTE by seat cover: 354 = 79 percent of the legacy 450; 196 percent of 180 (the 40 percent left after a 60 percent replacement)

### 6.6 Scenario B: every flow scaled to the 30 percent ceiling

Result of the model run: every flow scaled to the 30 percent ceiling (factor 1.484): escalations/day 5400 = 30.0 percent of 18000.

| Queue | Trigger | Pri | SLA s | Hours | Esc/day | Peak/h | AHT min | Peak load (Erl) | Peak seats | Attainment at peak | Day seats | Night seats | Workload h/day | FTE by workload | FTE by seat cover |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Crisis Response | ESC-011 | P0 | 60 | 24x7 | 13 | 1.7 | 30 | 0.83 | 4 | 99.0% | 2 | 2 | 6.7 | 2.1 | 14.0 |
| Security Operations | ESC-009 | P0 | 120 | 24x7 | 300 | 37.5 | 15 | 9.37 | 15 | 96.9% | 7 | 3 | 74.9 | 23.4 | 40.0 |
| Fraud Investigation | ESC-001 | P0 | 120 | 24x7 | 939 | 117.4 | 15 | 29.34 | 37 | 95.6% | 15 | 5 | 234.7 | 73.4 | 87.0 |
| AML Compliance | ESC-012 | P0 | 120 | 24x7 | 32 | 3.9 | 20 | 1.31 | 4 | 96.2% | 3 | 2 | 10.5 | 3.3 | 16.5 |
| Enhanced Due Diligence | ESC-015 | P1 | 300 | extended | 51 | 6.3 | 20 | 2.12 | 5 | 96.4% | 3 | 0 | 16.9 | 5.3 | 12.5 |
| Senior Resolution Mgr | ESC-002 | P1 | 300 | extended | 171 | 21.4 | 20 | 7.13 | 11 | 94.9% | 5 | 0 | 57.0 | 17.8 | 23.5 |
| Dispute Resolution | ESC-005 | P1 | 300 | extended | 516 | 64.5 | 12 | 12.91 | 16 | 91.2% | 7 | 0 | 103.2 | 32.3 | 33.5 |
| Relationship Manager | ESC-007 | P1 | 300 | extended | 28 | 3.5 | 15 | 0.89 | 3 | 96.7% | 2 | 0 | 7.1 | 2.2 | 8.0 |
| Customer Retention | ESC-004 | P1 | 300 | extended | 676 | 84.5 | 12 | 16.90 | 21 | 95.4% | 9 | 0 | 135.2 | 42.3 | 43.5 |
| Compliance Helpdesk | ESC-008 | P1 | 600 | extended | 400 | 50.0 | 10 | 8.33 | 10 | 90.9% | 5 | 0 | 66.6 | 20.8 | 22.5 |
| Wealth Advisory | ESC-013 | P1 | 600 | extended | 519 | 64.9 | 30 | 32.46 | 37 | 92.5% | 14 | 0 | 259.7 | 81.2 | 72.0 |
| Next Available Agent | ESC-006 | P2 | 600 | 24x7 | 857 | 107.1 | 8 | 14.28 | 16 | 93.4% | 6 | 5 | 114.2 | 35.7 | 43.5 |
| Technical Support | ESC-014 | P2 | 600 | extended | 202 | 25.2 | 10 | 4.21 | 6 | 94.4% | 3 | 0 | 33.7 | 10.5 | 13.5 |
| General Support | ESC-003 | P2 | 600 | 24x7 | 346 | 43.2 | 8 | 5.76 | 7 | 88.6% | 3 | 2 | 46.1 | 14.4 | 19.5 |
| Supervisor Review | ESC-010 | P2 | 900 | extended | 351 | 43.8 | 10 | 7.30 | 9 | 96.4% | 4 | 0 | 58.4 | 18.3 | 19.0 |
| **Total** | | | | | **5400** | | | | **201** | | | | **1225.1** | **382.8** | **468.5** |

- after-hours P1 volume carried by Next Available Agent at night: 197/day (night share 8.3 percent)
- by priority/day: P0 1284, P1 2361, P2 1755
- mean human handling time per escalation: 13.6 min
- containment (no escalation record): 70.0 percent (target >= 70 percent)
- FTE by workload: 383 = 85 percent of the legacy 450; 213 percent of 180 (the 40 percent left after a 60 percent replacement)
- FTE by seat cover: 468 = 104 percent of the legacy 450; 260 percent of 180 (the 40 percent left after a 60 percent replacement)

### 6.7 Reading the results

1. **The escalation ceiling and the containment target are one constraint; first contact resolution is the binding one.** Containment is the share of conversations with no escalation record (`docs/metrics/kpi-framework.md` section 1.1), so 30 percent escalation is exactly 70 percent containment. The first contact resolution target of at least 70 percent (A8.2) is stricter: at 30 percent escalation it is met only if no contained conversation is dropped or returns within 7 days. The working aim therefore has to sit below the ceiling. The design mix gives 20.2 percent, which leaves about 10 points for dropped and returning conversations.
2. **P0 volume is set by the mix, not by tuning.** Fraud and security conversations are 3.4 percent of volume (612 a day) and all of them escalate, by rule. In scenario A the P0 queues take 865 escalations a day. This cannot be reduced by improving the agent; only the handling time and the split between Fraud Investigation and Security Operations can change.
3. **Meeting the 30 percent ceiling does not by itself deliver the 60 percent staffing reduction.** Under these assumptions the pooled workload view needs about 258 FTE in scenario A and 383 FTE in scenario B, against 180 agents remaining after a 60 percent replacement of 450. The seat-cover view (15 separately staffed queues) is higher: about 354 and 468. The model's break-even points: 180 FTE carry 2,541 escalations a day (14.1 percent) at the model's mean handling time of 13.6 minutes, 3,456 a day (19.2 percent) at 10 minutes, and 4,320 a day (24.0 percent) at 8 minutes. The staffing aim therefore depends on three levers, in this order of effect: the escalation rate, the human handling time (which the handoff package is designed to cut), and pooling of queues.
4. **Small 24x7 queues are expensive per conversation.** Crisis Response needs about 13 FTE by seat cover for about 9 conversations a day, because it must never be single-staffed at any hour. That is the price of the IMMEDIATE SLA and is not a candidate for saving; sharing trained crisis handlers with Security Operations at night is the realistic economy (section 3).
5. **Wealth Advisory is the largest P1 workload** (175 handling hours a day in scenario A) because each consultation is 30 minutes. Its volume depends directly on how many customers accept the ESC-013 offer, which the offer wording controls. A scheduled consultation instead of a live 10-minute pickup would remove most of the peak seats, but A6 sets the SLA at under 10 minutes; this is raised as an open question, not changed.
6. **The implied legacy handling time is short.** With the same productivity assumptions, 450 agents handling 18,000 interactions implies 4.8 minutes each. The model's 13.6-minute mean for escalated work assumes that what reaches a human is the hard residue. If measured handling times are closer to the legacy figure, the staffing gap in point 3 closes.

Sensitivity lines from the script, for reference: productive handling hours per FTE per calendar day: 3.20; legacy implied handling time: 450 FTE x 3.20 h / 18000 = 4.80 min per interaction; break-even: 180 FTE carry 2541 escalations/day at 13.6 min each = 14.1 percent escalation rate; break-even: 180 FTE carry 3456 escalations/day at 10.0 min each = 19.2 percent escalation rate; break-even: 180 FTE carry 4320 escalations/day at 8.0 min each = 24.0 percent escalation rate.

Limits of the model: the shares in 6.3 and the handling times are judgement, not data; Erlang C ignores abandonment (which lowers real load) and assumes steady arrivals inside each period (real peaks are sharper); 15 unpooled queues is the worst case and cross-skilling (section 7) recovers part of the gap between the two FTE views; AML is a case queue, so the live-queue formula overstates its seats. The model's purpose is to show orders of magnitude and sensitivities, and to give the dashboards a planned baseline to compare against.

## 7. Priority rebalancing

Rebalancing moves people or reorders work when a queue is at risk of missing its SLA. It never changes a trigger's priority, queue or SLA, and never applies a different rule to a customer because of who they are (A11.3). Proposals (D-127).

| Mechanism | Trigger for it | Effect | Limits |
|---|---|---|---|
| Ordering inside a queue | Always on | Priority, then earliest SLA deadline; a repeat contact ahead of a first contact at the same deadline | Never across priorities: a P2 item cannot pass a P1 item |
| Ageing boost | A P1 or P2 item reaches 80 percent of its SLA (480 s for a 600 s SLA, 720 s for 900 s) | The item moves to the head of its own priority band in its queue | It does not jump ahead of a higher priority |
| Cross-skill lending | A queue's forecast attainment falls below its target | Agents with the needed skill are lent from a queue that is above its target: General Support and Next Available Agent lend to each other; Customer Retention, Senior Resolution Mgr and Supervisor Review lend to each other; Fraud Investigation and Security Operations lend to each other | A P0 queue never lends below its minimum seats; Compliance Helpdesk, Wealth Advisory, Enhanced Due Diligence and AML Compliance never borrow from unqualified pools |
| P2 callback mode | P0 or P1 attainment is below target for two consecutive 5-minute windows | New P2 arrivals are offered a callback first, which frees generalists for the P1 after-hours and overflow intake | The right to a human (A11.3) holds: a customer who declines the callback is queued |
| Surge mode | A spike alert on a trigger (for example fraud reports at 3 times the same-hour baseline for 15 minutes) | Queue supervisor declares surge: all cross-skilled agents recalled to the queue, P2 callback mode on, incident opened, Real-time dashboard shows the surge banner | Declared and ended by a named supervisor; logged; reviewed afterwards |
| Pre-emption | ESC-011 arrives | The next free Crisis Response agent takes it ahead of everything; if none is free within the pickup target, the overflow chain is used at once | Crisis only |

Rebalancing decisions are logged (who, when, from which queue to which) and shown on the Real-time Operations dashboard (`docs/metrics/dashboards.md` section 2).

## 8. Escalation quality metrics

The brief asks to "define escalation quality metrics" (Part D p.60), penalises Premature Escalation (A9.2) and lists "false positive escalation" as a supervisor correction type (A5.1). The SLA shows whether a queue was fast; these metrics show whether the decision to escalate was right. Definitions and targets are proposals (D-131); the two hard zeros follow from the brief's safety position.

### 8.1 Labels

Every escalation and a sample of non-escalated conversations receive labels from three sources.

| Source | Who | What is labelled | Coverage |
|---|---|---|---|
| Wrap-up code | The human who took the handoff | One of: correct; premature; wrong queue; late. Plus: did the customer have to repeat anything (yes or no) | Every live handoff |
| Supervisor review | Supervisors (A5.1; 50 reviews per supervisor per day) | The `escalation_verdict` field of the correction record (`correct`, `missed` with the ESC ID, `unnecessary` with the ESC ID) and the escalation error types (missed, unnecessary, wrong queue, poor handoff summary) of `docs/learning-pipeline/supervisor-corrections.md` sections 3.1 and 4.2. This is the reference label when it disagrees with the wrap-up code | The Day 11 sampling streams, with no extra stream: E (escalation-triggered, 2 percent, at least 5 per ESC ID per day) for premature, late and wrong-queue labels; R (random, 1 percent, 180 a day) for an unbiased missed-escalation rate; C and P as enriched sources |
| Rule replay | Automated job | For the deterministic triggers (ESC-003, ESC-004, ESC-005, ESC-006, ESC-007, ESC-010, ESC-014, ESC-015), the rule is recomputed from the logged state for every conversation and compared with the escalation records | 100 percent of conversations, daily |

Label definitions:

| Label | Definition |
|---|---|
| Correct | A trigger condition was true and the conversation went to the right queue at the right time |
| Premature, detection error | An escalation was created although no trigger condition was actually true (for example sarcasm misread, an idiom taken as a crisis, an amount misread) |
| Premature, low value | The condition was true by the rule, but the human judges the agent could have completed the request. This is evidence about the rule or threshold, not an agent error, and goes to the rule's owner |
| Not premature by definition | Customer-requested handoffs (ESC-006, XTR-01), accepted offers (ESC-013) and P0 reports that turn out to be mistaken. A fraud report that proves to be a family member's purchase was still rightly escalated; it is counted as a false alarm, separately |
| Missed | A trigger condition was true and no escalation record exists |
| Late | An escalation was created, but the condition was true at an earlier turn |
| Wrong queue | The owner trigger was wrong (precedence or detection), so the customer was transferred again |

Mapping to the Day 11 labels: "premature" here is `escalation_verdict: unnecessary` (severity S4, "false positive escalation" in A5.1); "missed" is `escalation_verdict: missed` (S1 for a P0 trigger, S2 otherwise). Two refinements are proposed as sub-reasons of the Day 11 record rather than new labels: the split of "unnecessary" into detection error and low value, and "late". No supervisor capacity is added by this document: the labels come from the streams already sized in `supervisor-corrections.md` section 7.

Where missed escalations are looked for beyond the random stream (all are biased samples, used to find cases, not to estimate a rate): proximity score of 0.6 or more without an escalation; de-escalated records; CSAT of 1 or 2 (stream P); low-confidence conversations (stream C); repeat contact on the same issue within 7 days; conversations with a safety-critical intent. Proposal: every de-escalated record whose customer returns within 7 days is added to the always-reviewed set.

### 8.2 Metrics

`E` = escalation records in the period that reached a human or a case queue. `Er` = reviewed escalations. Weighted estimates use the sampling weights of each stratum.

| ID | Metric | Formula | Target (proposal unless stated) | Owner |
|---|---|---|---|---|
| EQ-01 | Premature escalation rate | (a) detection error: reviewed escalations with verdict unnecessary and sub-reason detection error, divided by `Er` minus those not premature by definition. (b) low value: the same with the low-value sub-reason. Reported per trigger and overall, from stream E | (a) at most 10 percent overall; ESC-004 at most 15 percent, which is the precision of 0.85 already proposed in `sentiment.md` section 9. (b) no target; trend only | CX Team |
| EQ-02 | Missed escalation rate | Estimated conversations with a true trigger and no record, divided by estimated conversations with a true trigger (correct escalations plus missed). Estimated from the random stream R (verdict missed among non-escalated conversations, scaled to volume). Also the rule-replay miss count, which is exact | Rule-replay misses: 0 (any miss is a defect). Missed P0: 0. Overall at most 2 percent; ESC-004 at most 10 percent (recall 0.90 in `sentiment.md` section 9) | Risk Committee for P0; CX Team otherwise |
| EQ-03 | Wrong-queue rate | Handoffs transferred again by the first human, divided by live handoffs | at most 3 percent | CX Team |
| EQ-04 | Late escalation rate | Reviewed escalations labelled late, divided by `Er`; with the mean number of turns late | at most 5 percent | CX Team |
| EQ-05 | Repeat-information rate | Live handoffs where the wrap-up says the customer had to repeat something, divided by live handoffs | at most 2 percent (the package exists to make this zero) | CX Team |
| EQ-06 | Failed-handoff rate | Handoffs with a failure of `routing-and-handoff.md` section 8, divided by handoffs attempted; by failure type | at most 1 percent; 0 for P0 | Platform on-call |
| EQ-07 | SLA attainment | Escalations whose SLA was met, divided by `E`; per trigger, with overflow and after-hours share shown | P0 at least 95 percent, P1 at least 90, P2 at least 85 (section 5). The SLA values are the brief's | Queue owners |
| EQ-08 | Package completeness | Packages with all 8 elements filled, divided by packages sent | at least 99 percent | NLU Team with platform |
| EQ-09 | De-escalation rate | Pending escalations cancelled under `routing-and-handoff.md` section 9.2, divided by escalations fired; with the share followed by a repeat contact within 7 days | No target (a target would invite gaming); the repeat-contact share at most 5 percent | CX Team |
| EQ-10 | Queue abandonment rate | Customers who left before a human accepted, divided by live handoffs queued; by priority | P0 at most 1 percent; P1 and P2 at most 5 percent | Queue owners |
| EQ-11 | Time to protective action | For ESC-001 and ESC-009: time from the trigger to the first confirmed protective step (card block, reset link), median and 95th percentile | Reported; no target until measured | Information Security Officer |
| EQ-12 | Post-escalation CSAT | Mean CSAT of escalated conversations, beside the CSAT of contained ones | Not below the contained CSAT by more than 0.3 points | CEB |

Notes on interpretation:

1. EQ-01 and EQ-02 pull in opposite directions and are always shown together. Lowering premature escalations by suppressing triggers shows up at once as missed ones. The asymmetry is deliberate: a premature escalation costs 10 points in the brief's scoring and one human conversation; a missed P0 is a safety failure.
2. Because the rule-replay job covers every conversation for eight triggers, their missed count is exact, not estimated. A non-zero value means the router did not apply the rule and is handled as a defect, not as a rate to be tuned.
3. The random stream reviews 180 conversations a day, of which about 144 are non-escalated at the scenario A rate. With zero misses found, the 95 percent upper bound on the share of non-escalated conversations that should have been escalated is about 2.6 percent for one day and about 0.38 percent for a week (about 1,005 reviews). A daily "zero" is therefore weak evidence; the sampled figure is reported weekly, and the claim of zero missed P0 rests on the rule replay, the hard-zero counter for an unescalated security-critical intent (DM-12) and the fixed suite, not on sampling.
4. Fairness: EQ-01 and EQ-02 are reported by language and by channel. A gap of more than 2 percentage points between languages opens a review (the same bound as `sentiment.md` section 9).
5. Inputs to the learning pipeline: premature and missed labels are supervisor corrections (A5.1) and follow the Day 11 propagation rules; this document defines the labels, not the training use.

## 9. Alerts for queue operations

Evaluated on 5-minute windows and shown on the Real-time Operations dashboard. Thresholds are proposals (D-128).

| Signal | Warn | Critical |
|---|---|---|
| Any P0 escalation unaccepted | 84 s | 120 s (breach; incident) |
| ESC-011 unaccepted | 30 s | 60 s |
| SLA attainment per queue (rolling 1 hour) | below target for 2 windows | below target minus 10 points for 2 windows |
| Escalation rate (rolling 1 hour) | 27 percent or more (90 percent of the 30 percent limit) | 30 percent or more for 2 windows |
| Escalation volume of one trigger | 2 times its same-hour baseline for 15 minutes | 3 times for 15 minutes (surge) |
| Fraud reports (ESC-001 plus ESC-009) | 2 times baseline for 15 minutes | 3 times for 15 minutes, or 20 in 5 minutes |
| Rule-replay miss | not applicable | any |
| Queue unavailable | any queue closed inside its hours | any P0 queue unavailable |
| Package completeness (rolling 1 hour) | below 99 percent | below 95 percent |
| Abandonment in queue | P1 or P2 above 5 percent in 1 hour | any P0 abandonment |

## 10. Decisions and open items

Decisions: D-122 (hours and after-hours), D-127 (overflow chains and rebalancing), D-128 (breach handling, warn fraction, attainment targets, alerts), D-130 (capacity assumptions and method), D-131 (escalation quality metrics and labelling).

Open items:

1. Every staffing figure rests on judgement inputs. The shadow period must replace the category shares and handling times with measured values before any staffing decision.
2. The queue platform must support skills, deadlines, pre-emption, lending, callback slots and wrap-up codes. None is specified by the brief.
3. The two sub-reasons (detection error or low value; late) and the wrap-up codes need adding to the Day 11 correction record and the human agent desktop.
4. The attainment targets and alert thresholds need Risk Committee and CEB sign-off.
5. The Crisis Response team's own protocol and its pickup target.
