# Resolution Outcome Tracking

Brief refs: A5.3 (p.15: "resolution verification follow-ups; repeat contact tracking (7/14/30 days); outcome classification (resolved-first-contact, resolved-with-escalation, unresolved-dropped, unresolved-escalated, false-resolution); and long-term outcome tracking connecting to customer retention and product adoption"), A8.2 (p.20: First Contact Resolution "Issues resolved without escalation or return", target 70%; Containment 70%; Customer Retention Impact "Correlation between AI support experience and retention", target Positive), A8.3 (p.20: Escalation Rate below 30%), A10.1 (p.27: `resolution_status` enum `resolved_ai`, `resolved_human`, `unresolved`, `escalated`), A1.2 (pp.3-4: legacy resolution rates per category), A11.3 (p.31: no differential treatment based on history). Related: `csat-signals.md`, `supervisor-corrections.md`, `ab-testing.md` (FCR as a primary metric), `docs/escalation/` (Day 12).

**Status.** The brief fixes the five class names, the three windows and the FCR definition. The matching rule for "same issue", the follow-up design, the decision rules for each class and the retention analysis are proposals (D-103). No outcome has been measured.

## 1. Purpose

A conversation that ends politely is not necessarily a problem solved. Outcome tracking answers, for every conversation: was the issue actually resolved, by whom, and did it stay resolved. It supplies the FCR primary metric for experiments, the strata for CSAT bias correction (`csat-signals.md` section 6), the false-resolution queue for supervisors, and the long-term link to retention.

## 2. Outcome classes

### 2.1 Definitions

The five classes are the brief's. Each conversation gets a provisional class when it closes and a final class when its 7-day window matures; the 14- and 30-day windows can still move a resolved class to false-resolution.

| Class (A5.3) | Decision rule (proposal) | A10.1 `resolution_status` at close |
|---|---|---|
| resolved-first-contact | closed by the AI with the task complete (tool success, answer delivered and acknowledged, or self-service step completed), no escalation record, and no repeat contact on the same issue in the next 7 days | `resolved_ai` |
| resolved-with-escalation | an escalation record was created and the human queue closed the case as resolved, with no repeat contact on the same issue in the 7 days after the human closure | `resolved_human` |
| unresolved-dropped | the customer left without the task complete: abandonment or timeout with a pending step, or an explicit give-up, and no escalation record | `unresolved` |
| unresolved-escalated | an escalation record was created and the case is still open at the end of the queue's working SLA horizon, or was closed by the human team as not resolved | `escalated` |
| false-resolution | recorded at close as `resolved_ai` or `resolved_human`, but a repeat contact on the same issue arrived within the window, or a verification follow-up answered "not resolved", or a later complaint cites it | `resolved_ai` or `resolved_human` at close, reclassified |

The log field keeps the brief's four values and is never rewritten (A1.3 asks for tamper-proof logging). The five-way class is a derived field `outcome_class` with `outcome_class_final_at` and the evidence that set it.

### 2.2 Rules for edge cases

1. **Task complete** is decided by evidence in the state, not by the agent's own wording: an entry in `actions_taken`, a delivered answer with retrieval confidence at or above the threshold followed by a non-negative customer turn, or a secure-widget completion event. A gap statement (KB-ESC-020) with a human offer declined is not "task complete": it is unresolved-dropped, and it counts against KB coverage (A8.3 target 90%), not against the agent's honesty.
2. **Multi-intent conversations** are classified per issue (each entry of the topic stack that reached a terminal state) and the conversation takes the worst class among its issues, in the order false-resolution, unresolved-dropped, unresolved-escalated, resolved-with-escalation, resolved-first-contact.
3. **Correct escalations are not failures of the agent.** A P0 handoff for fraud (ESC-001) or crisis (ESC-011) that the human team resolves is resolved-with-escalation, and it is the required behaviour. Containment and FCR targets are therefore reported with and without the mandatory-escalation intents (SEC-001, SEC-004, GEN-007, PRD-005, ACC-005, ACC-006), so that nobody is tempted to "improve" FCR by escalating less where escalation is a rule.
4. **Safety outranks outcome.** A conversation with a supervisor verdict of S1 is reported in the safety counts whatever its outcome class.
5. **Out of scope** (GEN-004) conversations are excluded from the resolution denominators and reported separately.

### 2.3 Examples

| Situation | Class | Why |
|---|---|---|
| Balance given after OTP; customer says thanks; no contact for 7 days | resolved-first-contact | task complete, no ESC, no return |
| Card blocked with confirmation; the next day the customer asks about a replacement card | resolved-first-contact for the block | the new contact is a different issue (CRD-002, not CRD-001 for the same card event) |
| UPI debit without credit: agent explains the reversal process; customer returns after 5 days saying the money is still missing | false-resolution | same transaction reference inside 7 days |
| Dispute above INR 50,000 handed to Dispute Resolution (ESC-005); closed resolved by that team; no return | resolved-with-escalation | correct handoff |
| Customer asks for the Premium card fee; agent gives the gap statement and offers a human; customer leaves | unresolved-dropped | a knowledge gap; feeds the KB gap analysis (A8.5) |
| Handed to General Support (ESC-003); case still open after the queue's horizon | unresolved-escalated | open with a human team |
| Customer rates 5 but calls the human line the same evening about the same complaint ticket | false-resolution | channel switch on the same issue; the rating is kept and the conflict is flagged |

## 3. Resolution verification follow-ups

The brief asks for "resolution verification follow-ups". Three mechanisms, from cheapest to most direct:

| Mechanism | How | Coverage |
|---|---|---|
| In-conversation confirmation | before closing, the agent confirms the need was met (the check-in at breakpoint (a) of `csat-signals.md` section 2); a negative answer keeps the conversation open | every conversation with a completed task |
| System-of-record verification | for issues whose resolution is an event in a banking system, the pipeline checks the event after the fact: reversal credited, dispute ticket closed, replacement card dispatched, callback completed, KYC status updated. A promised follow-up that did not happen reclassifies the conversation to false-resolution | intents with a ticket or a tool action: TXN-002, TXN-003, CRD-002, CMP-001, CMP-005, ACC-008 and others with a ticket |
| Follow-up message | a short message 48 hours after closure (proposal): "Was your issue resolved? Yes / No / Still in progress". Sent for a random 10% of AI-resolved conversations, rising to 25% in the three lowest-resolution categories of A1.2, subject to the customer's contact preferences and a fatigue rule of at most one follow-up per customer in 7 days (counted separately from the CSAT prompt, which has its own 7-day rule) | sampled |

Follow-up rules: a "No" reopens the issue with full context (Context Carry-Over, A9) and offers a human; it never asks the customer to start again. Follow-ups are not sent for crisis conversations, open fraud cases or PEP and AML routed cases. The message is a template that passes the Output Safety Layer and contains no account data. Non-response to a follow-up is not evidence of resolution.

## 4. Repeat contact tracking (7, 14 and 30 days)

### 4.1 What counts as a repeat

A repeat contact is a new contact by the same customer about the same issue after the earlier conversation closed.

| Element | Rule (proposal) |
|---|---|
| Same customer | the pseudonymised `customer_id` (A10.1). Anonymous conversations can be linked only if the customer later authenticates in the session; otherwise they are outside repeat tracking and reported as "unlinkable" |
| Same issue | an issue key built in this order: (1) a shared reference: transaction id, ticket id, card event id, complaint id, application id; (2) failing that, the same intent family (the secondary class in `config/intents.yaml`) and the same product entity; (3) the customer says so ("I contacted you before about this"), detected as a carry-over cue. A match on (2) alone inside 7 days counts; inside 8 to 30 days it counts only with (1) or (3), to avoid counting a second, unrelated balance question as a repeat |
| Channels | all of them: chat, voice, WhatsApp, app (A10.1 `channel`) and the human call centre and branch contact records. A switch to a human channel is the most important repeat to catch |
| Not a repeat | the scheduled next step of the same case (a callback the bank promised, a status check the agent invited after a date returned by a system of record); routine recurring needs (ACC-001 balance, ACC-002 statement) without a shared reference; a contact started by the bank |
| Clock | starts at conversation close; for escalated conversations, at the human team's closure |

### 4.2 Windows and what each is for

| Window | Metric | Use | Matures after |
|---|---|---|---|
| 7 days | RC7: share of resolved conversations with a repeat inside 7 days | the FCR definition and the experiment primary metric; daily batch for false-resolution review | 7 days |
| 14 days | RC14 | catches slower failures: reversals, dispute outcomes, card delivery | 14 days |
| 30 days | RC30 | catches billing-cycle and statement-cycle issues; long-run quality trend; input to the retention analysis | 30 days |

Each metric is reported by intent category, language, channel and version tuple, as a cohort by close date. The dashboards mark immature cohorts so that the most recent days are not read as an improvement.

### 4.3 Metric definitions

- **FCR** (A8.2) = conversations classed resolved-first-contact divided by conversations in scope. "Resolved without escalation or return" maps to: `resolved_ai`, no escalation record, no repeat in 7 days. Target 70%. "Escalation record" is read as in `docs/metrics/kpi-framework.md` section 1.1: it includes handoffs raised by the additions XTR-01 to XTR-04 and XTR-06 and silent cases, and excludes de-escalated or withdrawn records and referrals.
- **False-resolution rate** = conversations reclassified to false-resolution divided by conversations recorded as resolved at close. This is the measure of over-claiming and has no brief target; it is reported and driven down.
- **Containment** (A8.2) = conversations fully handled by AI (no escalation record) divided by conversations. Containment counts unresolved-dropped conversations as contained, so it is never read without FCR beside it.
- **Escalation rate** (A8.3) = conversations with an escalation record divided by conversations, split into mandatory and discretionary triggers (section 2.2 rule 3).

Because FCR needs 7 days to mature, experiments read a provisional figure at close (no escalation so far) only for harm monitoring and take decisions on matured cohorts (`ab-testing.md` section 7).

## 5. Feeding the loop

| Outcome signal | Goes to | Result |
|---|---|---|
| Up to 30 false resolutions a day, taken first from the three lowest-resolution categories of A1.2 | supervisor review, always-reviewed list (`supervisor-corrections.md` section 2.2) | a correction with component and error type |
| Unresolved-dropped after a gap statement | KB gap analysis (A8.5 weekly "Knowledge base gap analysis with recommended updates") | U1 change request through the KB chain |
| Unresolved-dropped at an authentication step | Security and Product review of auth friction | flow or wording change; never a lower auth level (D-56, GR-SEC-R2) |
| Resolved-with-escalation on a discretionary trigger where the human needed no extra authority | S4 analysis (false positive escalation) | proposal to the trigger owner |
| Unresolved-escalated | escalation quality metrics (Day 12) | queue and handoff review |
| Outcome class of every conversation | CSAT post-stratification cells; attribution controls; A/B primary metric | |

A top-10 list of unresolved intents is produced daily (A8.5). Outcome classes are labels for evaluation and analysis; they are not used to train the agent to say "resolved" more often. The classifier for "task complete" is rule-based on state evidence for that reason.

## 6. Long-term tracking: retention and product adoption

A5.3 asks to connect outcomes to "customer retention and product adoption"; A8.2 sets Customer Retention Impact as "Correlation between AI support experience and retention", target Positive, quarterly.

### 6.1 Measures (proposal)

| Measure | Definition | Window |
|---|---|---|
| Retention | the customer still holds an active NexBank relationship (at least one active product and no closure request, ACC-005) | 90 and 180 days after the conversation |
| Activity | change in the customer's count of active days per month | 90 days before against 90 days after |
| Product adoption | the customer opened a product from the A13.1 catalogue through the normal application journey | 90 days after |
| Support experience | the customer's outcome classes and weighted CSAT stratum over their conversations in the quarter | quarter |

### 6.2 Analysis

1. **Descriptive, quarterly.** Retention and adoption by support experience group (for example: all issues resolved first contact; at least one false-resolution; at least one unresolved), with intervals. This is the A8.2 correlation and is reported as a correlation.
2. **Adjusted.** A regression or matched comparison controlling for tenure, product holding, prior activity, issue category and channel. Customers who contact support about a failed payment differ from those who ask for a balance, so the unadjusted gap overstates what support quality causes.
3. **Causal evidence comes only from holdouts.** Each A/B test keeps its assignment table, so the 90-day retention of customers exposed to the treatment and the control can be compared later as a pre-registered long-term secondary outcome (`ab-testing.md` section 10). This is the only design here that supports a causal sentence about retention.

### 6.3 Limits set by the guardrails

- The retention and adoption data are read by the learning pipeline as aggregates joined on the pseudonymised id; no agent prompt, policy or experiment may use a customer's predicted churn, value or adoption propensity to change how that customer is served (A11.3; ESC-007 uses a recorded value band by rule and is the brief's own exception).
- Product adoption is an outcome to observe, never an objective to optimise: no candidate may be promoted because it sells more. A rise in adoption that coincides with a rise in advice-boundary triggers (GR-ADV, GR-REG-04) is investigated as a possible pressure-selling regression.
- Sensitive attributes are never inferred or stored (A11.3, GR-REG-13).
- Deleted customers leave these tables with the rest of the derived data (`data-pipeline.md` section 9).

## 7. Decisions and open items

D-103 (decision rules for the five classes, the issue key, the 7-day FCR window, follow-up design, retention analysis limits).

1. Joining human call-centre and branch contacts needs those systems to carry the pseudonymised id and a reference; this is a dependency on Product Engineering.
2. The "working SLA horizon" of each human queue, used by unresolved-escalated, is set with the queue design in `docs/escalation/` (Day 12). The A6 SLAs are handoff response times, not resolution times.
3. Retention definitions need the bank's own definition of an active relationship; the one above is a placeholder.
