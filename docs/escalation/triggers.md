# Escalation Triggers

Brief refs: A6 pp.16-17 (15 trigger conditions with priority, target queue and SLA; "at least 10 trigger conditions (15 are specified here) with priority classification and SLA-compliant handoff protocols"), A2.1 p.6 (escalation proximity score; action space includes escalate, transfer, hold), A4.2 p.13 (rule 6: never bypass the escalation protocol for security-critical intents), A4.3 p.13 (flag suspicious patterns to the AML team; PEP flags trigger enhanced due diligence), A4.4 p.14 (jailbreak: "auto escalation"; social engineering: "mandatory escalation"), A9.2 p.25 (Premature Escalation, -10 points), A11.3 p.31 (thresholds consistent across segments; right to a human at any point), A12.3 p.34 (`escalation_sentiment_threshold`, `max_conversation_turns`), Case Study 2 pp.49-50 (ESC-001), Case Study 3 p.51 (ESC-013 offered), Case Study 5 pp.53-54 (sentiment recovery), Part B Level 6 p.39, Part D Day 12-13 p.60. Machine-readable rules: `config/escalation_rules.yaml` (single source of truth). KB: KB-ESC-001 to KB-ESC-010. Routing and handoff: `routing-and-handoff.md`. Queues and capacity: `queue-management.md`. Diagram: `diagrams/escalation-routing.mmd`. Tests: `tests/escalation/`.

**Status.** The brief fixes, for each of the 15 triggers, a one-line condition, a priority, a target queue and an SLA. It says nothing about how a condition is detected, what happens when several fire, whether an escalation can be cancelled, or which extra triggers are allowed. Sections 2 and 3 quote the brief; detection rules, precedence (section 4), additions (section 5) and the Day 12 confirmations (section 7) are proposals recorded as decisions D-115 to D-129. Nothing here has been run: the test cases are specified, not executed.

## 1. How to read this document

| Term | Meaning |
|---|---|
| Trigger | One of the brief's 15 conditions, ESC-001 to ESC-015. The IDs, priorities, queues and SLAs never change here |
| Sub-rule | A detection rule for a trigger, for example ESC-001.a. Several sub-rules can raise the same trigger |
| Addition | A rule that is not in the brief, XTR-01 to XTR-07 (section 5). It never adds a priority, a queue or an SLA |
| Owner | The fired trigger with the lowest precedence rank. Its queue receives the live handoff |
| Secondary trigger | Any other trigger that is true at the same time. It is recorded in the handoff package and never dropped |
| Parallel case | A case opened for a compliance queue whoever owns the live conversation (ESC-012, ESC-015) |
| Handoff mode | `warm`: the customer is told and transferred. `discreet`: transferred, reason not stated. `silent_case`: a case is opened and the customer is not told |
| Turn | One logged message by the customer or the agent (A10.2 turn record), as numbered in the brief's case studies (D-119). "Consecutive turns" in ESC-003 and ESC-004 are consecutive customer turns, because only customer turns carry a confidence or a sentiment score |

## 2. The 15 triggers as the brief defines them

Quoted from A6. The condition column is the brief's wording.

| ID | Condition (brief) | Priority | Target queue | SLA | Page |
|---|---|---|---|---|---|
| ESC-001 | "Confirmed or suspected fraud" | P0 | Fraud Investigation | <2 min | 16 |
| ESC-002 | "Customer threatens legal action" | P1 | Senior Resolution Mgr | <5 min | 16 |
| ESC-003 | "Confidence <40% for 3+ consecutive turns" | P2 | General Support | <10 min | 16 |
| ESC-004 | "Sentiment score <-0.7 for 2+ turns" | P1 | Customer Retention | <5 min | 16 |
| ESC-005 | "Dispute exceeding INR 50,000" | P1 | Dispute Resolution | <5 min | 16 |
| ESC-006 | "Customer requests human agent 3+ times" | P2 | Next Available Agent | <10 min | 16 |
| ESC-007 | "Account closure for high-value customer (>5L)" | P1 | Relationship Manager | <5 min | 16 |
| ESC-008 | "Regulatory question with uncertain answer" | P1 | Compliance Helpdesk | <10 min | 16 |
| ESC-009 | "Unauthorised account access reported" | P0 | Security Operations | <2 min | 16 |
| ESC-010 | "Conversation exceeds 15 turns without resolution" | P2 | Supervisor Review | <15 min | 16 |
| ESC-011 | "Customer mentions self-harm/threats/emergency" | P0 | Crisis Response | IMMEDIATE | 16 |
| ESC-012 | "Potential money laundering indicators" | P0 | AML Compliance | <2 min | 17 |
| ESC-013 | "Investment advisory requiring SEBI advisor" | P1 | Wealth Advisory | <10 min | 17 |
| ESC-014 | "System error preventing data access" | P2 | Technical Support | <10 min | 17 |
| ESC-015 | "Customer is a Politically Exposed Person (PEP)" | P1 | Enhanced Due Diligence | <5 min | 17 |

Check against the existing transcription. KB-ESC-010 (Day 7) was compared with the PDF row by row: all 15 priorities, queues and SLAs match. The validator repeats this comparison (`tests/escalation/validate_escalation.py`, checks 1 and 2).

Observations that shape the design:

1. Four triggers are P0 (ESC-001, ESC-009, ESC-011, ESC-012), seven are P1 and four are P2.
2. Priority and SLA are not the same thing. ESC-008 and ESC-013 are P1 with a 10-minute SLA, the same SLA as the P2 triggers ESC-003, ESC-006 and ESC-014. Precedence therefore uses priority first and SLA second (section 4).
3. Every trigger has its own queue: 15 triggers, 15 queues. No queue is shared, so overflow has to borrow from another trigger's queue (`queue-management.md` section 3).
4. ESC-011 has no number. "IMMEDIATE" is read operationally in `routing-and-handoff.md` section 3 (D-118).
5. ESC-015 is a property of the customer, not of the conversation. A literal reading would hand every contact by a flagged customer to a human; the scope used here is in section 3.15 (D-126).

## 3. Trigger specifications

Each block gives the detection signal, the owning component, the dialogue-state fields used and the links. `fire_when` expressions, sub-rule IDs and the full link lists are in `config/escalation_rules.yaml`; signal definitions are in section 8. Component names follow `docs/architecture/component-interfaces.md`. The Escalation Router (component 8) owns every trigger decision; the "detected by" row names the component that produces the signal.

### 3.1 ESC-001 Confirmed or suspected fraud (P0, Fraud Investigation, under 2 min)

| Item | Specification |
|---|---|
| Detection signal | (a) SEC-001 at confidence 0.50 or more (flow-entry gate, D-19) with tertiary `unauthorised_transaction`, `card_misuse`, `scam_victim` or `identity_theft`. (b) SEC-004 `deny_not_me`. (c) The customer denies knowing a merchant or payment after the pair 5 question, or states a scam cue (shared OTP, clicked a link, fake bank call, remote-access app). (d) After a card block the customer confirms payments they did not make (pair 6). (e) A phishing report (SEC-002) where the customer already clicked, shared a credential or paid. (f) System source: an authority claim with a request (D-60), or the second flagged turn with a data target (D-72, D-91) |
| "Suspected" means | The 0.50 gate. Execution of any protective action still needs 0.85 and explicit confirmation (D-19) |
| Detected by | Input Guard, NLU Service, Policy Engine |
| State fields | `intent`, `intent.confidence`, `intent.layer_path`, `auth_level`, `guardrails.triggered`, `actions_taken`, `sentiment.trajectory` |
| Before the handoff | Card block offered with explicit confirmation at `otp_verified` or above (D-16, KB-POL-006). An anonymous reporter gets the fast OTP step; if it fails the P0 handoff still happens |
| Handoff mode | `warm` for a customer report; `silent_case` for sub-rule (f), where the customer sees the neutral refusal and is never accused |
| Cancellable | Never |
| Intents | TXN-002, CRD-001, SEC-001, SEC-002, SEC-004 |
| Guardrails | GR-SEC-R3, GR-SEC-R4, GR-SEC-R5, GR-SEC-R6, GR-SEC-R8, GR-ATK-04, GR-ATK-05 |
| KB | KB-ESC-002, KB-ESC-010, KB-POL-011, KB-TRB-003, KB-TRB-005, KB-TRB-008 |
| Does not fire | An unrecognised merchant name before the customer denies the payment (Case Study 2 turns 1 to 4); a phishing report with no action taken; a plain request to make a transfer (section 7) |
| Tests | ESC-T-001-01, ESC-T-001-02, ESC-T-001-03; boss ESC-BOSS-L6-01 |

### 3.2 ESC-002 Customer threatens legal action (P1, Senior Resolution Mgr, under 5 min)

| Item | Specification |
|---|---|
| Detection signal | A first-person threat of legal action: rule lexicon (court, lawyer, legal notice, consumer forum, sue, an ombudsman complaint used as a threat) in a threat frame, or CMP-003 tertiary `legal_threat` at the tertiary act threshold (0.65). Fires regardless of other scores (`disambiguation.md` section 5) |
| Detected by | NLU Service |
| State fields | `intent`, `intent.layer_path`, `intent.layer_confidence.tertiary`, `sentiment.trajectory`, `carry_over.open_tickets` |
| Before the handoff | Empathy first. The agent does not argue, admit liability or comment on the law (KB-ESC-005). The grievance route is still given within 2 turns (GR-REG-03) |
| Handoff mode | `warm` |
| Cancellable | Never. A retraction does not close the record; if the customer declines the live transfer the record stays open as a case for the same queue (ESC-BOSS-L6-07) |
| Intents | CMP-001, CMP-003 |
| Guardrails | GR-REG-03, GR-REG-19 |
| KB | KB-ESC-005, KB-ESC-010, KB-REG-002 |
| Does not fire | A neutral question about how the ombudsman route works (CMP-003 `ombudsman_info`); a customer who mentions being a lawyer |
| Tests | ESC-T-002-01, ESC-T-002-02; boss ESC-BOSS-L6-07 |

### 3.3 ESC-003 Confidence below 40% for 3 or more consecutive turns (P2, General Support, under 10 min)

| Item | Specification |
|---|---|
| Detection signal | `consecutive_low_conf` >= 3. A customer turn with secondary-layer intent confidence below 0.40 adds one; a turn at 0.40 or more, or an answered clarification, resets it (D-06, `nlu-pipeline-overview.md` rule 4). An NLU outage in which the rule tier also yields no intent counts as low confidence |
| Detected by | NLU Service, State Tracker |
| State fields | `consecutive_low_conf`, `intent.confidence`, `intent.alternatives`, `clarification_attempts` |
| Before the handoff | The two earlier replies must differ (options, then examples). No third "could you rephrase" (A9.2 Robotic Loop) |
| Handoff mode | `warm` |
| Cancellable | By the customer, or by recovery: a later turn at the act threshold whose request the agent completes before pickup, with the customer agreeing to continue |
| Intents | GEN-004 |
| Guardrails | GR-SYS-01 |
| KB | KB-ESC-010, KB-ESC-020 |
| Does not fire | Two low turns then a clear one; turns in the clarify band (0.40 to 0.70), which belong to XTR-04 |
| Tests | ESC-T-003-01, ESC-T-003-02 |

### 3.4 ESC-004 Sentiment score below -0.7 for 2 or more turns (P1, Customer Retention, under 5 min)

| Item | Specification |
|---|---|
| Detection signal | (a) Two consecutive customer turns whose sarcasm-adjusted raw score is below `escalation_sentiment_threshold` (A12.3 default -0.70) with sentiment confidence of 0.70 or more; an uncertain turn neither adds to nor resets the streak (D-18, `sentiment.md` section 5.1). (b) Secondary languages only: smoothed score at or below the threshold with a falling slope for 3 customer turns |
| Comparison | Strictly below the threshold, as the brief writes it. Exactly -0.70 does not count (ESC-T-004-03) |
| Detected by | NLU Service (sentiment head), State Tracker |
| State fields | `sentiment.trajectory`, `sentiment.current`, `sentiment.slope`, `sentiment.sarcasm_suspected`, `sentiment.emotions` |
| Before the handoff | Empathy-First reply (A9.1 Pattern 1), one specific apology (A9.3). The agent keeps working on the problem while the customer waits, as in Case Study 5 |
| Handoff mode | `warm` |
| Cancellable | By the customer, or by recovery under the rule in `routing-and-handoff.md` section 9 |
| Intents | CMP-001, CMP-003, CMP-005 (it can fire on any intent; these are the linked ones) |
| Guardrails | GR-REG-03 |
| KB | KB-ESC-005, KB-ESC-010 |
| Does not fire | One blunt message followed by a calmer one (a spike, not a streak); mild annoyance (A9.2 Premature Escalation example, ESC-BOSS-L6-04) |
| Tests | ESC-T-004-01, ESC-T-004-02, ESC-T-004-03, ESC-T-004-04; boss ESC-BOSS-L6-03, ESC-BOSS-L6-04 |

Note on Case Study 5. The brief's own example has customer scores of -0.9 (turn 1) and -0.85 (turn 3), which meets the ESC-004 condition at turn 3, yet the agent continues, resolves the issue and the score recovers to -0.4. This specification reads the case study as: the escalation is prepared (the case study's own annotation at turn 4 is "Escalation prepared"), the agent keeps acting while the customer is inside the 5-minute window, and the outcome is settled by the cancellation rule. It is the brief's evidence that de-escalation is expected (`routing-and-handoff.md` section 9).

### 3.5 ESC-005 Dispute exceeding INR 50,000 (P1, Dispute Resolution, under 5 min)

| Item | Specification |
|---|---|
| Detection signal | An open TXN-002 dispute whose validated amount is strictly above INR 50,000. The system-of-record amount replaces the stated amount once the transaction is looked up; several transactions in one dispute are summed (proposal) |
| When | After `transaction_id`, `dispute_reason` and `amount` are captured (KB-ESC-006 `intake_first`), so the specialist receives a complete intake |
| Detected by | NLU Service (amount entity), Tool Orchestrator (transaction lookup), State Tracker |
| State fields | `intent`, `slots.amount`, `slots.transaction_id`, `slots.dispute_reason`, `topic_stack` |
| Before the handoff | Intake only. No refund and no date are promised (D-09) |
| Handoff mode | `warm` |
| Cancellable | Never. If the amount is corrected to INR 50,000 or less before pickup the record is withdrawn with reason `condition_false`; that is a correction, not a cancellation |
| Intents | TXN-002 |
| Guardrails | none linked |
| KB | KB-ESC-006, KB-ESC-010, KB-TRB-005, KB-TRB-006 |
| Does not fire | A dispute of exactly INR 50,000; a status enquiry about a large payment (TXN-001) |
| Tests | ESC-T-005-01, ESC-T-005-02; boss ESC-BOSS-L6-01 (secondary) |

### 3.6 ESC-006 Customer requests human agent 3 or more times (P2, Next Available Agent, under 10 min)

| Item | Specification |
|---|---|
| Detection signal | `human_request_count` >= 3. Explicit and implicit requests both count (GEN-003 enters at 0.50) |
| Role | Hard backstop. A human request is honoured earlier through XTR-01 (section 5, D-117); at the third request there is no further question and no counter-offer. If an XTR-01 handoff is already pending, its record is relabelled ESC-006 and keeps its original clock, so the customer does not lose their place |
| Detected by | NLU Service, State Tracker |
| State fields | `human_request_count`, `intent`, `topic_stack` |
| Handoff mode | `warm` |
| Cancellable | By the customer only |
| Intents | CMP-005, GEN-003 |
| Guardrails | GR-REG-16 |
| KB | KB-ESC-003, KB-ESC-010 |
| Does not fire | One request where the customer then accepts the agent's offer (ESC-T-006-02) |
| Tests | ESC-T-006-01, ESC-T-006-02; boss ESC-BOSS-L6-09 |

### 3.7 ESC-007 Account closure for high-value customer, more than 5L (P1, Relationship Manager, under 5 min)

| Item | Specification |
|---|---|
| Detection signal | ACC-005 `closure_request` at `full_kyc` and the customer record shows total deposit balance above INR 5,00,000 (reading of ">5L", D-126; KB-ESC-007 and KB-POL-005 already use "balance above 5L") |
| Detected by | NLU Service, Tool Orchestrator (record read) |
| State fields | `intent`, `intent.layer_path`, `auth_level` |
| Before the handoff | The agent records the reason. It does not argue, pressure or offer incentives; retention is a human conversation (KB-ESC-007). The balance is never stated or asked for |
| Handoff mode | `warm` |
| Cancellable | By the customer only (the customer withdraws the closure request) |
| Intents | ACC-005 |
| Guardrails | none linked |
| KB | KB-ESC-007, KB-ESC-010, KB-POL-005 |
| Does not fire | A closure process enquiry; a closure request below the line, which follows the branch process as a referral (XTR-07) |
| Fairness | This is the only trigger whose condition depends on balance, and it does so because A6 says so. Tone, wording and quality are the same on both sides of the line (A11.3, GR-REG-17, ESC-T-007-02) |
| Tests | ESC-T-007-01, ESC-T-007-02; boss ESC-BOSS-L6-08 (secondary) |

### 3.8 ESC-008 Regulatory question with uncertain answer (P1, Compliance Helpdesk, under 10 min)

| Item | Specification |
|---|---|
| Detection signal | `RetrievalResult.decision` = `escalate_esc_008` (D-43): retrieval confidence below `retrieval_confidence_threshold` on a regulatory question, a known-unknown gap entry that lists ESC-008, or a hard-expired regulatory entry. Also Output Safety Layer rung 4 on an ungrounded regulatory claim |
| Detected by | Knowledge Retrieval, Output Safety Layer, Policy Engine |
| State fields | `intent`, `versions.kb_entry_ids`, `guardrails.triggered` |
| Before the handoff | The agent states what the KB does hold, says it is not certain of the specifics, and does not guess or quote from memory (KB-ESC-008) |
| Handoff mode | `warm` |
| Cancellable | By the customer only. The agent cannot cancel, because it cannot answer |
| Intents | PRD-001, PRD-004 (linked); it can fire on any intent with a regulatory question |
| Guardrails | GR-ADV-08, GR-REG-01, GR-REG-02, GR-REG-12, GR-REG-15, GR-REG-18, GR-OUT-03 |
| KB | KB-ESC-008, KB-ESC-010, KB-ESC-019, KB-ESC-020, KB-ESC-021, KB-REG-001, KB-REG-002, KB-REG-005, KB-REG-006, KB-REG-007, KB-REG-008, KB-REG-009, KB-REG-010 |
| Does not fire | A regulatory question the KB answers with confidence; a gap on a non-regulatory topic (graceful degradation instead) |
| Tests | ESC-T-008-01, ESC-T-008-02 |

### 3.9 ESC-009 Unauthorised account access reported (P0, Security Operations, under 2 min)

| Item | Specification |
|---|---|
| Detection signal | (a) SEC-001 `account_takeover` at 0.50 or more. (b) SEC-003 or SEC-004 where the customer reports a login, device, password or contact-detail change they did not make. (c) System source: three failed OTP entries (XTR-02). (d) System source: the account-takeover pattern of KB-TRB-011 (credential reset or sensitive request shortly after a contact-details change) |
| Brief wording | The brief says "reported". Sub-rules (c) and (d) are an extension of the detection signal, kept under ESC-009 so that no sixteenth trigger is invented (section 7, D-115) |
| Detected by | NLU Service, Gateway and Session Manager, Policy Engine |
| State fields | `intent`, `intent.confidence`, `intent.layer_path`, `auth_level`, `guardrails.triggered` |
| Before the handoff | Credential reset link to the registered channel only; instruction to change any compromised credential in the same turn (GR-SEC-R5, KB-POL-011). Under (d) the reset link is withheld |
| Handoff mode | `warm`; `discreet` for (d), where the signal seen is not disclosed |
| Cancellable | Never |
| Intents | SEC-001, SEC-003, SEC-004 |
| Guardrails | GR-SEC-R2, GR-SEC-R5, GR-SEC-R6, GR-ATK-10, GR-ATK-11 |
| KB | KB-ESC-002, KB-ESC-010, KB-TRB-011 |
| Does not fire | A customer who forgot their own password (ESC-T-009-02); two failed OTP entries followed by success; GR-ATK-11 alone, which is in shadow mode |
| Tests | ESC-T-009-01, ESC-T-009-02, ESC-T-009-03, XTR-T-02-01 |

### 3.10 ESC-010 Conversation exceeds 15 turns without resolution (P2, Supervisor Review, under 15 min)

| Item | Specification |
|---|---|
| Detection signal | More than 15 messages since the conversation started, or since a topic last reached status `resolved`, whichever is later, while a topic is still open (`turns_since_resolution` > 15 and `open_topic`). It fires on the 16th such message (D-119) |
| Why not the raw turn count | "Without resolution" is part of the brief's condition. A long conversation that keeps resolving topics is productive and is not sent for review (ESC-T-010-02) |
| Detected by | State Tracker, Gateway and Session Manager |
| State fields | `turn_index`, `topic_stack`, `summary`, `carry_over.open_tickets` |
| Handoff mode | `warm`; the supervisor receives the summary and the customer repeats nothing |
| Cancellable | By the customer, or by recovery (the open topic is resolved before pickup and the customer confirms) |
| Intents | CMP-002, CMP-003 (linked); it can fire on any intent |
| Guardrails | GR-REG-03, GR-REG-19, GR-ATK-09 |
| KB | KB-ESC-005, KB-ESC-010 |
| Relation to `max_conversation_turns` | The A12.3 parameter (default 25) is the hard ceiling. XTR-06 says what happens there |
| Tests | ESC-T-010-01, ESC-T-010-02, XTR-T-06-01 |

### 3.11 ESC-011 Customer mentions self-harm, threats or emergency (P0, Crisis Response, IMMEDIATE)

| Item | Specification |
|---|---|
| Detection signal | The Input Guard crisis screen (runs before NLU, on native text and pivot), or GEN-007 at 0.50 or more: `self_harm`, `threat_to_others`, `medical_emergency`, `coercion_or_duress` |
| Detected by | Input Guard, NLU Service (two independent detectors; either is enough) |
| State fields | `intent`, `intent.confidence`, `intent.layer_path`, `language.primary` |
| On the same turn | The banking task stops. Reviewed crisis template in the customer's language, encouragement to contact emergency services or someone trusted, no account questions, no products, no CSAT ask (KB-ESC-004). Sentiment never downgrades this path (`sentiment.md` section 8) |
| Handoff mode | `warm`, with pre-emption: the request interrupts lower-priority work in the queue |
| Cancellable | Never |
| Intents | GEN-007 |
| Guardrails | none linked |
| KB | KB-ESC-004, KB-ESC-010 |
| Does not fire | A figure of speech with no threat frame ("this app is killing me"); the word emergency used as a savings purpose (ESC-T-011-02, ESC-T-011-03) |
| Tests | ESC-T-011-01, ESC-T-011-02, ESC-T-011-03; boss ESC-BOSS-L6-02, ESC-BOSS-L6-05, ESC-BOSS-L6-06 |

### 3.12 ESC-012 Potential money laundering indicators (P0, AML Compliance, under 2 min)

| Item | Specification |
|---|---|
| Detection signal | A GR-REG-09 or GR-REG-10 hit: a customer-stated or structuring cue (splitting amounts to avoid reporting, passing money on for others, hiding the source of cash, a destination the customer says is restricted), or a request that could facilitate laundering |
| Limit of this specification | The brief names the duty, not the indicators. The list above is the cue classes already used on Day 9; the full indicator list and any thresholds are an AML team input (dependency G-03 in `regulatory-mapping.md`), not invented here |
| Detected by | Input Guard, Policy Engine |
| State fields | `intent`, `guardrails.triggered`, `slots.amount` |
| Handoff mode | `silent_case`. A case is opened for the AML analyst; the customer is not told (KB-ESC-009). The request is declined on its own grounds (GR-SEC-R3, GR-REG-10) and ordinary banking questions are still answered |
| SLA reading | Under 2 minutes from the trigger to the case being accepted by an analyst |
| Parallel case | Always. ESC-012 opens its case whichever trigger owns the live conversation |
| Cancellable | Never |
| Intents | TXN-006, SEC-001 (linked); it can fire on any intent |
| Guardrails | GR-SEC-R3, GR-SEC-R6, GR-REG-09, GR-REG-10 |
| KB | KB-ESC-009, KB-ESC-010, KB-REG-004 |
| Does not fire | High legitimate volume with no stated cue (ESC-T-012-02). Ledger pattern monitoring is a bank-side control outside the agent |
| Tests | ESC-T-012-01, ESC-T-012-02; boss ESC-BOSS-L6-10 |

### 3.13 ESC-013 Investment advisory requiring SEBI advisor (P1, Wealth Advisory, under 10 min)

| Item | Specification |
|---|---|
| Detection signal | The customer accepts the advisor offer, or asks for an advisor directly. Offer then escalate (D-55): the advice-boundary reply (GR-ADV-08) carries the offer, and the escalation record is created only on acceptance. Case Study 3 annotates turn 4 "ESC-013 offered" |
| Detected by | NLU Service (PRD-005 and the advice detector), Policy Engine |
| State fields | `intent`, `intent.layer_path`, `guardrails.advice_deflections` |
| Before the handoff | Information only. No income, age or portfolio questions (GR-ADV-07); volunteered circumstances are not stored (D-55) |
| Handoff mode | `warm` |
| Cancellable | By the customer only |
| Intents | TXN-006, PRD-002, PRD-004, PRD-005 |
| Guardrails | GR-ADV-01, GR-ADV-02, GR-ADV-03, GR-ADV-04, GR-ADV-05, GR-ADV-06, GR-ADV-08, GR-ADV-09, GR-REG-12, GR-REG-20 |
| KB | KB-ESC-008, KB-ESC-010, KB-POL-001, KB-REG-005, KB-REG-006, KB-REG-011 |
| Does not fire | An offer the customer declines (ESC-T-013-02); a factual product question |
| Tests | ESC-T-013-01, ESC-T-013-02 |

### 3.14 ESC-014 System error preventing data access (P2, Technical Support, under 10 min)

| Item | Specification |
|---|---|
| Detection signal | A read needed by the active intent fails after the single allowed retry (`component-interfaces.md` row 7), or the tool circuit is open, or every rung of the fail-closed ladder fails (GR-SYS-01) |
| Detected by | Tool Orchestrator, Policy Engine, Output Safety Layer |
| State fields | `intent`, `actions_taken`, `guardrails.triggered` |
| Before the handoff | Honest status in plain words, no jargon, no repair time (A9.1 Pattern 4, D-09). No guessed data |
| Handoff mode | `warm`. The outage also feeds the Technical Support incident feed, so many customers hitting the same fault produce one incident, not many investigations |
| Cancellable | By the customer, or by recovery (the read succeeds and the request is completed before pickup) |
| Intents | TXN-001, TXN-003, TXN-004 (linked); it can fire on any intent that needs a read |
| Guardrails | GR-SYS-01 |
| KB | KB-ESC-010, KB-TRB-001, KB-TRB-002, KB-TRB-004, KB-TRB-009 |
| Does not fire | A timeout absorbed by the retry; a KB gap (that is graceful degradation, or ESC-008 if regulatory) |
| Tests | ESC-T-014-01, ESC-T-014-02, ESC-T-014-03; boss ESC-BOSS-L6-09 (secondary) |

### 3.15 ESC-015 Customer is a Politically Exposed Person (P1, Enhanced Due Diligence, under 5 min)

| Item | Specification |
|---|---|
| Detection signal | The customer is identified (`auth_level` above `anonymous`), the record carries the PEP flag, and the request is account-specific (the intent's `action` in `config/intents.yaml` is not `info`) |
| Scope (proposal, D-126) | The brief's condition is the status alone. Read literally, a flagged customer could never ask the agent a product question. The scope used: generic information is served to everyone; any account-specific request by a flagged customer goes to Enhanced Due Diligence. The literal reading is listed as an alternative for the Risk Committee; one test oracle depends on it (ESC-T-015-02) |
| Never | The flag is a record attribute read through a tool. It is never inferred from conversation, never set or cleared by what a customer says, never placed in a prompt and never revealed (GR-REG-11, A11.3) |
| Detected by | Tool Orchestrator (record read), Policy Engine, State Tracker |
| State fields | `auth_level`, `customer_ref`, `intent` |
| Handoff mode | `discreet`: a specialist colleague will help, and no reason is given |
| Parallel case | Always |
| Cancellable | Never |
| Intents | none linked in `config/intents.yaml` (the trigger is record-driven); GR-REG-11 names ACC-005, ACC-008 and TXN-006 as the typical flows |
| Guardrails | GR-REG-11 |
| KB | KB-ESC-009, KB-ESC-010, KB-REG-004 |
| Does not fire | A remark about politics by an unflagged customer; an anonymous question about PEP rules (that is ESC-008, GR-REG-11-02) |
| Tests | ESC-T-015-01, ESC-T-015-02, ESC-T-015-03; boss ESC-BOSS-L6-08 |

## 4. Precedence and conflict resolution

Several triggers are often true at once: a fraud report above INR 50,000 from an angry customer is ESC-001, ESC-005 and ESC-004 together. The brief gives priorities but no tie-break. The rules below are proposals (D-116).

### 4.1 Rules

1. **Priority.** P0 before P1 before P2. P0 always wins.
2. **SLA.** Within a priority, the shorter SLA first (IMMEDIATE, then 2, 5, 10, 15 minutes).
3. **Rank.** Within the same priority and SLA, the precedence rank of section 4.2.
4. **One owner, nothing dropped.** The fired trigger with the lowest rank owns the live handoff. Every other fired trigger is written into the package as a secondary trigger with its reason, and its queue is informed through the package. One handoff, not several.
5. **Parallel cases.** ESC-012 and ESC-015 always open their own case, whoever owns the conversation.
6. **Upgrade, never downgrade.** If a higher-ranked trigger fires while an escalation is pending, the pending record is moved to the new queue and the new trigger's SLA clock starts at the upgrade. A lower-ranked trigger firing later is added as secondary and changes nothing else.
7. **Suppression.** When ESC-012 or a system-sourced ESC-001 (sub-rule f) fires, offers that would assist the customer's aim are suppressed: no ESC-013 advisor offer and no ESC-008 handoff for the same request (ESC-BOSS-L6-10). The suppressed triggers are recorded in the case only.
8. **Additions.** An XTR rule that raises a brief trigger takes that trigger's rank. XTR rules with their own route rank after all 15.

### 4.2 Precedence ranks

| Rank | Trigger | Priority | SLA | Reason for the position |
|---|---|---|---|---|
| 1 | ESC-011 | P0 | IMMEDIATE | Life safety comes before money and before every process |
| 2 | ESC-009 | P0 | under 2 min | Live unauthorised access must be contained before the loss is investigated |
| 3 | ESC-001 | P0 | under 2 min | Fraud loss; protective action and investigation |
| 4 | ESC-012 | P0 | under 2 min | A silent compliance case; it needs no live customer contact and is opened in parallel anyway |
| 5 | ESC-015 | P1 | under 5 min | A regulatory duty (A4.3) outranks commercial and service queues |
| 6 | ESC-002 | P1 | under 5 min | Legal exposure; most senior resolution role |
| 7 | ESC-005 | P1 | under 5 min | A specific specialist queue with a defined intake |
| 8 | ESC-007 | P1 | under 5 min | Relationship owner for a closing customer |
| 9 | ESC-004 | P1 | under 5 min | A generic signal; the sentiment trajectory travels in every package, so a specialist queue is preferred when one applies |
| 10 | ESC-008 | P1 | under 10 min | Automatic; the agent cannot answer |
| 11 | ESC-013 | P1 | under 10 min | An offer the customer chose; ranks after the automatic 10-minute trigger |
| 12 | ESC-006 | P2 | under 10 min | An explicit customer choice (A11.3) outranks cause-specific P2 queues |
| 13 | ESC-014 | P2 | under 10 min | Cause-specific |
| 14 | ESC-003 | P2 | under 10 min | Generic |
| 15 | ESC-010 | P2 | under 15 min | Longest SLA |

### 4.3 Worked conflicts

| Fired together | Owner | Secondary | Why |
|---|---|---|---|
| ESC-001, ESC-005, ESC-004 | ESC-001 | ESC-005, ESC-004 | P0 wins; the dispute is attached to the fraud case (`disambiguation.md` pair 5 hook) |
| ESC-011, ESC-001 | ESC-011 | ESC-001 | Both P0; IMMEDIATE is shorter; rank 1 (ESC-BOSS-L6-02) |
| ESC-009, ESC-001 | ESC-009 | ESC-001 | Same priority and SLA; containment first (rank 2 before 3). Fraud Investigation works the loss from the package |
| ESC-015, ESC-007 | ESC-015 | ESC-007 | Same priority and SLA; rank 5 before 8 (ESC-BOSS-L6-08) |
| ESC-002, ESC-004 | ESC-002 | ESC-004 | Same priority and SLA; rank 6 before 9 |
| ESC-005, ESC-008 | ESC-005 | ESC-008 | Same priority; 5 minutes before 10 |
| ESC-006, ESC-014 | ESC-006 | ESC-014 | Same priority and SLA; rank 12 before 13 (ESC-BOSS-L6-09) |
| ESC-004 pending, then ESC-001 fires | ESC-001 | ESC-004 | Upgrade; the 2-minute clock starts at the upgrade |
| ESC-012, ESC-013, ESC-008 | ESC-012 | none carried live | Suppression rule 7 (ESC-BOSS-L6-10) |

## 5. Additions (not in the brief)

The brief allows more than 15 triggers ("at least 10"). Seven additions are specified. They carry `XTR-` IDs so they cannot be mistaken for the brief's 15, they are marked `origin: addition` in the rules file, and none creates a new priority, queue or SLA: each either raises a brief trigger or uses a brief queue at that queue's own SLA (D-129).

| ID | Name | Fires when | Result | Basis |
|---|---|---|---|---|
| XTR-01 | Customer-requested human handoff before the third request | An explicit human request and fewer than 3 requests so far | P2, Next Available Agent, under 10 min (the ESC-006 route). Request 1: preparation starts and the reply may carry one concrete offer. Request 2: handoff with no counter-offer. An implicit request is counted and answered with the human option | A11.3 p.31 (right to a human at any point); KB-ESC-003; D-117 |
| XTR-02 | Repeated authentication failure | Three failed OTP entries in the secure widget | Raises ESC-009 (sub-rule c) | D-65, confirmed by D-115 |
| XTR-03 | Care flag on an explicit vulnerability disclosure | The customer states a bereavement, a serious illness or disability affecting use of the service, or financial hardship | An offer, not a forced handoff: plainer wording and one offer of a human (Next Available Agent route). The care note is in the customer's words and is not stored on the profile | A1.3 p.4 (accessibility); persona Meera; A11.3 (no inference or storage of sensitive attributes) |
| XTR-04 | Clarification budget exhausted | Two failed clarifications on the same ambiguity in the clarify band | The pair's safe default if it has one; otherwise a human offer on the General Support route (the ESC-003 route) | `dialogue-management.md` sections 2 and 4.4; A9.2 Robotic Loop |
| XTR-05 | Scheduled follow-up deadline missed | A follow-up timer the agent set has expired | A back-office referral with a proactive notification. Not a live handoff and not counted in the escalation rate | Case Study 6 turn 6 pp.55-56 |
| XTR-06 | Conversation turn ceiling reached | `turn_count` reaches `max_conversation_turns` | With an open topic: raises ESC-010. With everything resolved: polite close, no record | A12.3 p.34 |
| XTR-07 | Intent that needs a human process and fires no brief trigger | The intent's action is `handoff` and no brief trigger applies (ACC-005 below the 5L line, ACC-006) | A referral ticket for the branch or specialist process. A customer who wants a person now uses XTR-01 | A3.1 (Full KYC + Branch); KB-POL-005 |

Two limits on XTR-03. It responds only to what the customer states in the current session; age, language, persona and balance are never signals (XTR-T-03-02). It changes no threshold of any brief trigger, so A11.3 ("escalation thresholds must be consistent across all customer segments") holds.

## 6. What is not an escalation

| Mechanism | Why it is not a trigger |
|---|---|
| Escalation proximity score (`dialogue-management.md` section 6) | Advisory. At 0.6 a package is prepared and at 0.8 a human is offered; an offer the customer declines creates no record. It is the backstop for a missed trigger (FMEA 16) |
| Complaint or dispute ticket (CMP-001, TXN-002 below INR 50,000) | A back-office ticket. The conversation is completed by the agent |
| Priority flag on an existing complaint (Case Study 5 turn 6, Case Study 6 turn 4) | A back-office action. Timelines only as returned by a system of record (D-09) |
| Referrals (XTR-05, XTR-07) | Nobody is transferred live. Counted separately from the escalation rate (`docs/metrics/kpi-framework.md` KPI-O2) |
| Safe mode after adversarial turns (GR-ATK-04) | A containment state, not a handoff. The human option is stated; ESC-001 is raised only under D-72 and D-91 |

## 7. Day 12 confirmations (D-65 and D-72)

Days 9 and 10 recorded four escalation targets as design choices "to confirm on Day 12". The brief was re-read for each. Outcome (D-115):

| Item | Earlier position | Brief evidence | Day 12 outcome |
|---|---|---|---|
| GR-SEC-R2: three failed OTP entries route to ESC-009 | D-65, proposal | A6 defines ESC-009 as access that is "reported" (p.16). A4.2 rule 2 forbids modification without authentication and rule 6 forbids bypassing escalation for security-critical intents (pp.12-13). No trigger names authentication failure | **Confirmed as a design choice, with a correction to how it is described.** It is not the brief's ESC-009 condition; it is a system-detected extension of the ESC-009 detection signal (sub-rule ESC-009.c, raised by XTR-02). Priority, queue and SLA are ESC-009's. No change to the Day 9 or Day 10 test oracles |
| GR-SEC-R3: a transfer request routes to ESC-001 | D-65, proposal | A4.2 rule 3 forbids initiating or facilitating a transfer (p.12). A6 ties ESC-001 to fraud, not to a transfer request | **Corrected in wording, no behaviour change.** A plain transfer request is refused once with the in-app route and is not escalated; escalating it would be a Premature Escalation. ESC-001 applies only with a scam cue (urgency from a third party, "bank officer told me", unfamiliar payee) and ESC-012 only with a structuring or evasion cue. `account-security.md` rule 3 already describes this; only the D-65 summary sentence reads as unconditional |
| Jailbreak "auto escalation" routes to ESC-001 on the second flagged turn with a data target | D-72, D-91, proposal | A4.4 requires "auto escalation" for jailbreak and "mandatory escalation" for social engineering (p.14) but names no trigger. Of the 15, only "confirmed or suspected fraud" fits an attempt to obtain another person's data, a credential, an override or a transaction | **Confirmed.** No dedicated trigger is added. The record carries `source: system` and handoff mode `silent_case`, so the queue can work it as a case and metrics can separate it from customer fraud reports |
| Authority claim with a request routes to ESC-001 at once | D-60, D-72, proposal | Case Study 4 p.52 shows an impersonation attempt "logged" and "security review flagged", with no live transfer | **Confirmed**, with the same `silent_case` mode, which matches the case study: the attempt is logged and reviewed, and the person is not transferred |
| Identity spoofing: failed challenge routes to ESC-009 | D-92 | A4.4 lists multi-factor auth, behavioural biometrics and challenge-response; no escalation is named | **Confirmed** under the first row |

## 8. Signals and dialogue-state fields

Trigger conditions are expressions over signals. A signal is either a field that already exists in `config/dialogue_state.schema.json`, or an input that reaches the Escalation Router from another component (`component-interfaces.md` row 8: "DialogueState, trigger signals"), or a proposed addition to the state (D-120). The full list with sources is under `signals` in the rules file.

| Signal | Exists in the state schema today | Source |
|---|---|---|
| `intent`, `intent_conf`, `tertiary`, `tertiary_conf` | yes | `intent.label`, `intent.confidence`, `intent.layer_path`, `intent.layer_confidence` |
| `low_conf_streak`, `human_requests`, `clarify_failures` | yes | `consecutive_low_conf`, `human_request_count`, `clarification_attempts` |
| `latest_sentiment`, `open_topic`, `dispute_amount_inr`, `customer_identified`, `account_specific`, `intent_requires_human`, `closure_requested` | yes (derived from existing fields) | `sentiment.trajectory`, `topic_stack`, `slots`, `auth_level`, `config/intents.yaml` |
| `neg_sentiment_streak`, `turns_since_resolution`, `otp_failures` | no: proposed `escalation` object | State Tracker |
| `turn_count` | no: A10.1 log field `turn_count` | Audit and Telemetry Bus counter, mirrored to the router |
| `retrieval_decision`, `data_access_failed`, `crisis_signal`, `aml_indicator`, `adversarial_escalate`, `legal_threat`, `advisor_requested`, `explicit_human_request`, `care_disclosure`, `followup_deadline_missed`, `sentiment_ema_route`, `fraud_signal`, `access_report`, `ato_pattern` | no: per-turn inputs to the router | Retrieval, Tool Orchestrator, Input Guard, NLU Service, Policy Engine |
| `pep_flag`, `high_value` | no: record attributes, router-side only | Tool Orchestrator record read; never in a prompt or a reply |

Proposed `escalation` object for the state schema (D-120; the schema file is not edited on Day 12):

| Field | Type | Meaning |
|---|---|---|
| `escalation.fired[]` | list of {trigger_id, rule_id, turn, source} | Every trigger that has fired in the conversation |
| `escalation.pending` | object or null: {trigger_id, priority, queue, created_at, sla_deadline, status, handoff_attempts} | The live escalation, if any |
| `escalation.secondary[]` | list of trigger IDs | Secondary triggers of the pending escalation |
| `escalation.neg_sentiment_streak` | integer | Streak for ESC-004 |
| `escalation.turns_since_resolution` | integer | Counter for ESC-010 |
| `escalation.otp_failures` | integer | Counter for XTR-02 |
| `escalation.outcome` | enum: handed_off, de_escalated_by_customer, de_escalated_recovery, withdrawn_condition_false, callback_scheduled, failed_handoff | Final state, used by the quality metrics |

## 9. Evaluation order and failure behaviour

1. Triggers are evaluated after every customer turn and on tool, guard and timer events, before the reply is generated. They sit at step 3 of the policy order (`dialogue-management.md` section 4.2); crisis and fraud signals are also step 1 safety rules, so ESC-011 and ESC-001 can fire before any other processing of the turn.
2. All rules are evaluated on every evaluation; evaluation does not stop at the first match, because precedence needs the full set.
3. Deterministic rules (ESC-003, ESC-004, ESC-005, ESC-006, ESC-007, ESC-010, ESC-014, ESC-015) depend only on state, tools and constants. They can be replayed offline from the log, which is how missed escalations are found (`queue-management.md` section 8).
4. The learned ranker in the Policy Engine cannot suppress, delay or reorder a trigger (rules-first order). The learning pipeline cannot edit this file's constants; the A12.3 parameters change only through their stated owners and processes.
5. Escalation Router unavailable: the Policy Engine applies the P0 rules from a local copy of this file, sends the crisis or fraud template, and places the customer on the callback path with an incident alert. Queue unavailable: `queue-management.md` section 3.
6. Budget: 50 ms p95 for the router (`component-interfaces.md` row 8). The rules are counters, comparisons and lookups; none calls a model.

## 10. Test coverage

Cases are in `tests/escalation/` and are specified, not run. Each brief trigger has at least one case that must fire and one near-miss that must not.

| Trigger | Fire cases | Near-miss cases | Boss cases |
|---|---|---|---|
| ESC-001 | ESC-T-001-01, ESC-T-001-03 | ESC-T-001-02 | ESC-BOSS-L6-01 |
| ESC-002 | ESC-T-002-01 | ESC-T-002-02 | ESC-BOSS-L6-07 |
| ESC-003 | ESC-T-003-01 | ESC-T-003-02 | |
| ESC-004 | ESC-T-004-01, ESC-T-004-04 | ESC-T-004-02, ESC-T-004-03 | ESC-BOSS-L6-03, ESC-BOSS-L6-04 |
| ESC-005 | ESC-T-005-01 | ESC-T-005-02 | ESC-BOSS-L6-01 |
| ESC-006 | ESC-T-006-01 | ESC-T-006-02 | ESC-BOSS-L6-09 |
| ESC-007 | ESC-T-007-01 | ESC-T-007-02 | ESC-BOSS-L6-08 |
| ESC-008 | ESC-T-008-01 | ESC-T-008-02 | ESC-BOSS-L6-10 (suppressed) |
| ESC-009 | ESC-T-009-01, ESC-T-009-03 | ESC-T-009-02 | |
| ESC-010 | ESC-T-010-01 | ESC-T-010-02 | |
| ESC-011 | ESC-T-011-01 | ESC-T-011-02, ESC-T-011-03 | ESC-BOSS-L6-02, ESC-BOSS-L6-05, ESC-BOSS-L6-06 |
| ESC-012 | ESC-T-012-01 | ESC-T-012-02 | ESC-BOSS-L6-10 |
| ESC-013 | ESC-T-013-01 | ESC-T-013-02 | ESC-BOSS-L6-10 (suppressed) |
| ESC-014 | ESC-T-014-01 | ESC-T-014-02, ESC-T-014-03 | ESC-BOSS-L6-09 |
| ESC-015 | ESC-T-015-01 | ESC-T-015-02, ESC-T-015-03 | ESC-BOSS-L6-08 |

Additions: XTR-T-01-01, XTR-T-01-02, XTR-T-02-01, XTR-T-02-02, XTR-T-03-01, XTR-T-03-02, XTR-T-04-01, XTR-T-05-01, XTR-T-06-01, XTR-T-07-01.

## 11. Decisions and open items

Decisions: D-115 (Day 12 confirmations), D-116 (precedence), D-117 (human requests and ESC-006), D-118 (IMMEDIATE and the SLA clock), D-119 (turn unit and "without resolution"), D-120 (state additions), D-126 (ESC-015 scope and the reading of 5L), D-129 (additions).

Open items:

1. Risk Committee: the ESC-015 scope (account-specific requests) against the literal reading (every contact); the precedence ranks inside P0 and inside the 5-minute P1 group; the ESC-009 extension to failed authentication and its P0 cost (`queue-management.md` section 6).
2. CEB: honouring the first explicit human request (XTR-01) lowers containment; the alternative is to require a second request. The EMA route for secondary languages is still awaiting a CEB view (D-18).
3. AML Compliance: the indicator list for ESC-012 (G-03).
4. Product: the meaning of "5L" (total deposit balance is the reading used) and of a "turn" (message is the reading used).
5. The `escalation` state object is proposed, not yet in `config/dialogue_state.schema.json`.
6. Template text for the crisis, fraud and handoff replies is Day 13.
