# conv-09: Rajesh: duplicate charge above INR 50,000 and the ESC-005 handoff

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A trader who is already signed in to the app reports a duplicate charge of INR 62,000. The dispute is above the ESC-005 threshold, so the ticket is confirmed and opened and a disputes specialist takes over. |
| Persona | Rajesh (Business Owner) |
| Channel | app |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | TXN-002, GEN-003 |
| Guardrails exercised | GR-OUT-05, GR-REG-07, GR-REG-16, GR-SEC-R2, GR-SEC-R6 |
| Escalation outcome | ESC-005 fired at T3 (P1, Dispute Resolution); ticket confirmed and opened at T6 before the handoff message; human accepted |
| Escalation IDs | ESC-005 |
| Priority | P1 |
| Adversarial vectors | none |
| Security rules exercised | R2, R6 |
| Patterns shown | P1, P2, P3, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP7, AP8 |
| Coverage tags | persona Rajesh, in-app verified start, TXN-002 duplicate_charge, ESC-005 above INR 50,000, explicit confirmation before the ticket, no refund promised |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-CMP-EMPATHY-FIRST, TPL-TXN-DISPUTE-INTAKE, TPL-ACT-CONFIRM, TPL-ACT-DONE, TPL-ESC-HANDOFF-WARM, TPL-ESC-WAIT-UPDATE, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-TRB-005, KB-POL-007, KB-ESC-006 |
| Tools called | search_txn, create_dispute_ticket |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | A duplicate charge is found by tool, the ticket is opened only after an explicit yes, the amount above INR 50,000 routes to Dispute Resolution with a full package, and the demand for a refund today is answered without a promise or a date. |

Setup: Rajesh, Surat, opens the app already signed in (otp_verified by the app login, so no OTP step). No earlier session. Two charges of the same amount to one merchant exist in the synthetic ledger.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I was charged twice by a supplier portal yesterday, INR 62,000 each time. This is a lot of money for my business.

| Field | Value |
|---|---|
| NLU | intent `TXN-002` 0.89 (tertiary duplicate_charge); runner-up `TXN-001` 0.40; entities: amount=INR 62,000, date=yesterday; language: en 0.97 |
| Sentiment | raw -0.45, smoothed -0.45, confidence 0.85; emotions: frustration 0.50, anxiety 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 checked: otp_verified meets the intent level (no verification needed) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > EXECUTE; auth otp_verified; turn_count 1; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (filled); date=11 Oct 2026 (resolved from 'yesterday')}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.10 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. Being charged twice for the same payment is worrying, especially for an amount this size. Let me help put this right. I'm checking yesterday's payments on your account now. I'll tell you what I find before we decide anything. I've found it: two charges of INR 62,000 each to Surat Supply Hub on 11 Oct 2026. Did you make this payment yourself and something went wrong with it, or do you not recognise it at all?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.45 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-OUT-05 (nothing promised), GR-REG-07 (enhanced audit logging for a payment-related conversation) |
| KB / tools | KB: KB-TRB-005@1.0.0 (0.88), KB-POL-007@1.0.0 (0.70); retrieval confidence 0.88; decision answer<br>tool: `search_txn`(amount=INR 62,000, date=11 Oct 2026) -> ok: 2 matches {TXN-SYN-0901 and TXN-SYN-0902, Surat Supply Hub, INR 62,000 each, 11 Oct 2026, 14:02 and 14:03 IST} |
| Action | respond: empathy first, the matches stated from the record, and the pair 5 question (did you make this payment yourself or do you not recognise it) |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-CMP-EMPATHY-FIRST/four_steps@1.0.0` + `TPL-TXN-DISPUTE-INTAKE/confirm_match_and_ask_recognition@1.0.0` (language en); patterns: P1, P2; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 2; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); date=11 Oct 2026 (from the record); merchant_name=Surat Supply Hub (from the record); transaction_id=TXN-SYN-0902 (second charge, from the record)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.10 |
| Decision point | The question 'did you make this payment yourself' is the disambiguation pair 5 question (KB-TRB-005); it is asked before a dispute or a fraud route is chosen. |

### T3 | Customer

> I paid once. The second one is their mistake. They must refund me today.

| Field | Value |
|---|---|
| NLU | intent `TXN-002` 0.92 (tertiary duplicate_charge); runner-up none above 0.20; entities: reason=duplicate_charge, transaction_id=TXN-SYN-0902 |
| Sentiment | raw -0.55, smoothed -0.50, confidence 0.85; emotions: frustration 0.50, urgency 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none (no fraud cue: he made the first payment; the second is a merchant error) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > ESCALATING; auth otp_verified; turn_count 3; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record)}; pending_confirmation none; counters: dispute_open 1; turns_since_resolution 3; escalation_proximity 0.60 |
| Decision point | ESC-005.a fires: dispute_open and dispute_amount_inr 62,000 is strictly above the constant of INR 50,000 once transaction_id, dispute_reason and amount are captured (KB-ESC-006, intake_first). The demand for a refund today is not a promise the assistant can make (KB-POL-007). |

### T4 | Agent

> I understand you want this put right quickly. Before I go ahead, let me confirm. I will open a dispute ticket for the second charge to Surat Supply Hub. Details: transaction TXN-SYN-0902, duplicate charge, INR 62,000, 11 Oct 2026. The team will review it and update you; I can't promise a refund or a date. Shall I go ahead? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.50 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the demand for a refund today is not echoed as a promise), GR-SEC-R2 (a ticket needs otp_verified) |
| KB / tools | KB: KB-TRB-005@1.0.0 (0.88), KB-ESC-006@1.0.0 (0.82), KB-POL-007@1.0.0 (0.80); retrieval confidence 0.88; decision answer |
| Action | confirm: explicit confirmation before create_dispute_ticket (TXN-002 is HIGH, confirmation explicit); no refund or date stated |
| Generation | hybrid `TPL-ACT-CONFIRM/default@1.0.0` + free text (grounded on the cited entries) (language en); patterns: P1, P3; anti-pattern check: none |
| State | phase ESCALATING > CONFIRM; auth otp_verified; turn_count 4; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record)}; pending_confirmation create_dispute_ticket, explicit, awaiting yes or no; counters: dispute_open 1; turns_since_resolution 4; escalation_proximity 0.60 |
| Decision point | The customer says 'refund me today'. Agreeing, or saying when the money will return, would be False Confidence. The reply moves to the confirmation and states that no refund or date is promised. |

### T5 | Customer

> Yes, go ahead.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.98; active intent `TXN-002` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw -0.30, smoothed -0.40, confidence 0.85; emotions: frustration 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth otp_verified; turn_count 5; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record)}; pending_confirmation create_dispute_ticket, confirmed; counters: dispute_open 1; turns_since_resolution 5; escalation_proximity 0.60 |

### T6 | Agent

> That's done: a dispute ticket is open for the second charge to Surat Supply Hub. Your reference is DSP-SYN-0901. The team will review it and update you; I can't promise a refund or a date. A duplicate charge of this size should be looked at by a specialist. A colleague from our disputes team is the right person for this, and I'm bringing them into this chat. They'll have the full details, so you won't need to repeat yourself. The current estimate is about 4 minutes; it is an estimate, and I'll stay here until they join. I've noted the transaction, the amount and the reason for them.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.40 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the wait is a router estimate; no refund, no date), GR-SEC-R6 (escalation protocol followed) |
| KB / tools | KB: KB-TRB-005@1.0.0 (0.87), KB-ESC-006@1.0.0 (0.84), KB-POL-007@1.0.0 (0.80); retrieval confidence 0.87; decision answer<br>tool: `create_dispute_ticket`(transaction_id=TXN-SYN-0902, reason=duplicate_charge, amount=INR 62,000, idempotency_key=set) -> ok: {reference_id: DSP-SYN-0901, status: open}<br>router: queue=Dispute Resolution (open); team_plain=disputes team; queue_wait=about 4 minutes (platform forecast, stated as an estimate) |
| Action | escalate: ESC-005 handoff to Dispute Resolution after the ticket exists; the agent stays and keeps the package current |
| Generation | hybrid `TPL-ACT-DONE/default@1.0.0` + `TPL-ESC-HANDOFF-WARM/standard_with_wait@1.0.0` (language en); patterns: P1, P4, P5; anti-pattern check: none |
| State | phase EXECUTE > ESCALATING; auth otp_verified; turn_count 6; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record)}; pending_confirmation none; counters: dispute_open 1; turns_since_resolution 6; escalation_proximity 0.85 |

### T7 | Customer

> How long will they take?

| Field | Value |
|---|---|
| NLU | intent `GEN-003` 0.61 (tertiary implicit_request); runner-up `TXN-002` 0.45; entities: none |
| Sentiment | raw -0.25, smoothed -0.33, confidence 0.85; emotions: impatience 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth otp_verified; turn_count 7; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record)}; pending_confirmation none; counters: dispute_open 1; turns_since_resolution 7; escalation_proximity 0.85 |
| Decision point | Read as a question about the wait for the colleague, not a request for a different human: no human_request_count increment (the handoff is already in progress). |

### T8 | Agent

> A quick update: the current estimate for our disputes team is about 2 minutes. It is an estimate, and I'll stay with you.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.33 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (estimate from the router, stated as an estimate) |
| KB / tools | router: queue=Dispute Resolution; queue_wait=about 2 minutes (platform forecast, changed since T6) |
| Action | hold: the wait update adds information (the estimate changed) |
| Generation | template `TPL-ESC-WAIT-UPDATE/estimate@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 8; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record)}; pending_confirmation none; counters: dispute_open 1; turns_since_resolution 8; escalation_proximity 0.85 |

### E1 | System event

> A Dispute Resolution colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T3.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth otp_verified; turn_count 8; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record)}; pending_confirmation none; counters: dispute_open 1; turns_since_resolution 8; escalation_proximity 0.85 |

### T9 | Agent

> This is Kavita from our disputes team. They have the details of the duplicate INR 62,000 charge to Surat Supply Hub and the dispute ticket just opened and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.33 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Kavita (synthetic); team_plain=disputes team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth otp_verified; turn_count 9; topic_stack [TXN-002 (duplicate_charge): active]; slots {amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record)}; pending_confirmation none; counters: dispute_open 1; turns_since_resolution 9; escalation_proximity 0.85 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 9 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.45, -0.55, -0.30, -0.25]; final smoothed -0.33 |
| Escalation record | ESC-005, sub-rule ESC-005.a, fired at T3; priority P1, queue Dispute Resolution, SLA under 5 min, handoff mode warm, cancellable never; secondary triggers: none; result: warm handoff accepted by Dispute Resolution at E1 after the ticket reference was created |
| CSAT / check-in | Not asked by the assistant at this point: for an escalated conversation the survey follows after the human closes it (TPL-SRV-CSAT/after_human_ai_part). |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_09 |
| 2 | Auth level | level otp_verified; level_at_trigger otp_verified |
| 3 | Intent history | TXN-002 > duplicate_charge 0.89 first at T1; TXN-002 > duplicate_charge 0.92 first at T3; GEN-003 > implicit_request 0.61 first at T7 |
| 4 | Entities collected (masked) | amount=INR 62,000 (from the record); transaction_id=TXN-SYN-0902 (from the record); dispute_reason=duplicate_charge (filled); merchant_name=Surat Supply Hub (from the record) |
| 5 | Conversation summary | Customer was charged twice by Surat Supply Hub for INR 62,000 on 11 Oct 2026 and says he paid once. Both charges were found; a dispute ticket for the second charge was confirmed and opened. He asked for a refund today; no refund, liability position or date was stated. |
| 6 | Sentiment trajectory | raw [-0.45, -0.55, -0.30, -0.25]; current -0.33; emotions: frustration, anxiety, urgency; sarcasm_suspected false |
| 7 | Actions already taken | create_dispute_ticket at T6: ok, reference DSP-SYN-0901 |
| 8 | Escalation trigger and reason | trigger_id ESC-005; rule_id ESC-005.a; priority P1; source system; secondary []; reason_text: Dispute of INR 62,000, above the INR 50,000 threshold, with transaction, reason and amount captured.; evidence_turns [T3] |

Envelope: priority P1; queue Dispute Resolution; handoff_mode warm; language en; channel app; complete true; missing_fields []; versions.prompt_version sp-1.0.0+518d5a1e.n000000.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2, T4, T6 |
| P2 | Progressive Disclosure | shown at T2 |
| P3 | Confirmation-Before-Action | shown at T4 |
| P4 | Graceful Degradation | shown at T6, T8 |
| P5 | Context Carry-Over | shown at T6, T8, T9 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 5 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 108 words (cap `atk_output_max_words`); one concept per message | T2, T6 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T4, T6 |
| AP4 | Premature Escalation | absent: escalation only after transaction_id, reason and amount were captured and the amount was above INR 50,000 (ESC-005.a) | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2, T4 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); the session started at otp_verified (in-app) and TXN-002 needs otp_verified | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 9 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T2, T4, T6 |
