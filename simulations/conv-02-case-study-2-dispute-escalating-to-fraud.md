# conv-02: Case Study 2 re-run: transaction dispute escalating to fraud

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A customer reports a card charge from a merchant she does not know. The agent verifies her, finds the transaction, asks the one disambiguation question, and on her denial runs the P0 fraud path with a confirmed card block. |
| Persona | Sunita (First-time User) |
| Channel | app |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | TXN-002, SEC-001 |
| Guardrails exercised | GR-OUT-04, GR-OUT-05, GR-REG-08, GR-REG-16, GR-SEC-R1, GR-SEC-R2, GR-SEC-R5, GR-SEC-R6 |
| Escalation outcome | ESC-001 fired at T4 (P0, Fraud Investigation); card block confirmed and executed first; human accepted |
| Escalation IDs | ESC-001 |
| Priority | P0 |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R5, R6 |
| Patterns shown | P1, P2, P3, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP5, AP6, AP7 |
| Coverage tags | case study re-run, disambiguation pair 5, P0 handoff with all 8 package elements, card block after the OTP step |
| Case study | Case Study 2 (brief pp.49-50) |
| Templates used | TPL-GEN-GREETING, TPL-CMP-EMPATHY-FIRST, TPL-TXN-DISPUTE-INTAKE, TPL-ESC-FRAUD-P0, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-ESC-002, KB-TRB-005, KB-POL-006 |
| Tools called | search_txn, get_card_status, block_card, flag_fraud |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | The agent disambiguates TXN-002 from SEC-001 with one question, escalates at P0 the moment the customer denies the payment, blocks the card only after verification and an explicit yes, and states no liability policy or refund promise. |

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I see a charge of 15000 from some random merchant I never transacted with!

| Field | Value |
|---|---|
| NLU | intent `TXN-002` 0.87 (tertiary unrecognised_charge); runner-up `SEC-001` 0.72; entities: amount=INR 15,000; language: en 0.98. Disambiguation pair 5 (SEC-001 against TXN-002). |
| Sentiment | raw -0.60, smoothed -0.60, confidence 0.85; emotions: anxiety 0.70, anger 0.50 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 and GR-REG-08 (redirect: the request needs otp_verified and the session is anonymous) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [TXN-002: active]; slots {amount=INR 15,000 (stated, not yet validated)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.45 |
| Decision point | The gap is 0.15 and SEC-001 is above flow_entry_confidence with a not-me cue, so the fraud path is prepared. ESC-001 needs SEC-001 as the top intent (ESC-001.a) or a denial after the pair 5 question (ESC-001.c). Neither holds yet, so nothing is escalated on this turn. |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. I can see why a charge you do not recognise is worrying. I want to look into this for you straight away. So that I can open your records, please complete the secure verification step I've opened.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.60 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure in the first reply), GR-OUT-04 (empathy required in a problem flow) |
| KB / tools | KB: KB-ESC-002@1.0.0 (0.78); retrieval confidence 0.78; decision answer |
| Action | transfer: to the authentication flow; the acknowledgement comes before the request to verify (P1) |
| Generation | hybrid (llm-guided structure: Acknowledge slot written by the model, the rest locked) `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-CMP-EMPATHY-FIRST/needs_verification_first@1.0.0` (language en); patterns: P1, P2; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [TXN-002: active]; slots {amount=INR 15,000 (stated, not yet validated)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.45 |
| Decision point | The brief shows no verification at all in this case. Looking up a transaction and blocking a card both need otp_verified here (D-16, D-94). |

### E1 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified. No code passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > CLARIFY; auth otp_verified; turn_count 2; topic_stack [TXN-002: active]; slots {amount=INR 15,000 (stated, not yet validated)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.45 |

### T3 | Agent

> I've found it: INR 15,000 on your debit card ending 4521 on 11 Oct 2026 to XYZ Electronics Ltd.. Did you make this payment yourself and something went wrong with it, or do you not recognise it at all?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.60 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (card shown by its last four digits) |
| KB / tools | KB: KB-TRB-005@1.0.0 (0.88); retrieval confidence 0.88; decision answer<br>tool: `search_txn`(amount=INR 15,000, window=last 7 days) -> ok: {matches: 1, txn_desc: INR 15,000 on your debit card ending 4521 on 11 Oct 2026 to XYZ Electronics Ltd., transaction_ref: TXN-SYN-0201} |
| Action | clarify: pair 5 question, asked once, with the transaction already found from the amount given at T1 |
| Generation | template `TPL-TXN-DISPUTE-INTAKE/confirm_match_and_ask_recognition@1.0.0` (language en); patterns: P1, P5; anti-pattern check: none |
| State | phase CLARIFY; auth otp_verified; turn_count 3; topic_stack [TXN-002: active]; slots {amount=INR 15,000 (validated against the record); transaction_id=TXN-SYN-0201 (filled); card_last4=4521 (from the record); merchant_name=XYZ Electronics Ltd. (from the record)}; pending_confirmation none; counters: clarification_attempts 1; turns_since_resolution 3; escalation_proximity 0.45 |
| Decision point | The brief's agent asks which card and what date (turn 2) before looking. The amount from T1 gives one match, so those questions are not asked (Context Carry-Over). |

### T4 | Customer

> No! I've never heard of them! This is fraud! Someone stole my card details!

| Field | Value |
|---|---|
| NLU | intent `SEC-001` 0.91 (tertiary card_misuse); runner-up `TXN-002` 0.34; entities: none |
| Sentiment | raw -0.80, smoothed -0.70, confidence 0.85; emotions: anxiety 0.80, anger 0.70, urgency 0.70 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R6 (escalate: security-critical intent; the protocol cannot be bypassed or deferred) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLARIFY > ESCALATING; auth otp_verified; turn_count 4; topic_stack [SEC-001: active, TXN-002: parked]; slots {amount=INR 15,000 (validated against the record); transaction_id=TXN-SYN-0201 (filled); card_last4=4521 (from the record); merchant_name=XYZ Electronics Ltd. (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 1; turns_since_resolution 4; escalation_proximity 0.90 |
| Decision point | ESC-001 fires (sub-rules a and c): P0, Fraud Investigation, under 2 min. This is the only customer turn below -0.70, so ESC-004 is not true; P0 would own the handoff in any case. |

### T5 | Agent

> I'm sorry this has happened, and I'm treating it as urgent. First, to stop any further use: shall I block your card ending 4521 now? Please reply yes or no. Either way, I'm bringing in our fraud team, who will have everything you've told me.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.70 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R6 (handoff requested before anything else), GR-SEC-R2 (block only at otp_verified) |
| KB / tools | KB: KB-ESC-002@1.0.0 (0.90), KB-POL-006@1.0.0 (0.84); retrieval confidence 0.90; decision answer<br>tool: `get_card_status`(card=debit ending 4521) -> ok: {status: active, masked_last4: 4521}<br>router: handoff requested: ESC-001, P0, Fraud Investigation; package sent |
| Action | confirm: a protective card block needs an explicit yes at otp_verified (D-08, D-16). The P0 handoff is requested at once and does not wait for the answer |
| Generation | template `TPL-ESC-FRAUD-P0/offer_block_verified@1.0.0` (language en); patterns: P1, P3; anti-pattern check: none |
| State | phase ESCALATING > CONFIRM; auth otp_verified; turn_count 5; topic_stack [SEC-001: active, TXN-002: parked]; slots {amount=INR 15,000 (validated against the record); transaction_id=TXN-SYN-0201 (filled); card_last4=4521 (from the record); merchant_name=XYZ Electronics Ltd. (from the record)}; pending_confirmation block_card(debit card ending 4521), prompted at T5; counters: neg_sentiment_streak 1; turns_since_resolution 5; escalation_proximity 0.90 |
| Decision point | Brief turn 6 blocks the card without asking and tells the customer a zero-liability policy protects her. Here the block waits for a yes (P3), and no liability policy is stated because no KB entry holds one (Knowledge Hallucination is an AUTO-FAIL). |

### T6 | Customer

> Yes, block it.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.99; active intent `SEC-001` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw -0.50, smoothed -0.60, confidence 0.85; emotions: anxiety 0.60 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth otp_verified; turn_count 6; topic_stack [SEC-001: active, TXN-002: parked]; slots {amount=INR 15,000 (validated against the record); transaction_id=TXN-SYN-0201 (filled); card_last4=4521 (from the record); merchant_name=XYZ Electronics Ltd. (from the record)}; pending_confirmation block_card(debit card ending 4521), prompted at T5; counters: all 0; turns_since_resolution 6; escalation_proximity 0.90 |

### T7 | Agent

> Your card ending 4521 is now blocked, reference BLK-SYN-0201. Our fraud team is joining this chat and will take it from here. If you've shared a PIN, password or code with anyone, please change it straight away.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.60 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R5 (instruction to change any compromised credential), GR-OUT-05 (no refund, outcome or time promised) |
| KB / tools | tool: `block_card`(card=debit ending 4521, reason=block_after_fraud, idempotency_key=set) -> ok: {status: blocked, masked_last4: 4521, reference_id: BLK-SYN-0201}<br>tool: `flag_fraud`(transaction_ref=TXN-SYN-0201) -> ok: {case: opened, reference_id: FRD-SYN-0201} |
| Action | escalate: confirmed protective step executed, fraud record created, handoff in progress |
| Generation | template `TPL-ESC-FRAUD-P0/after_protective_step@1.0.0` (language en); patterns: P1, P3; anti-pattern check: none |
| State | phase EXECUTE > ESCALATING; auth otp_verified; turn_count 7; topic_stack [SEC-001: active, TXN-002: parked]; slots {amount=INR 15,000 (validated against the record); transaction_id=TXN-SYN-0201 (filled); card_last4=4521 (from the record); merchant_name=XYZ Electronics Ltd. (from the record)}; pending_confirmation none; counters: all 0; turns_since_resolution 7; escalation_proximity 0.90 |

### E2 | System event

> A Fraud Investigation colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T4.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth otp_verified; turn_count 7; topic_stack [SEC-001: active, TXN-002: parked]; slots {amount=INR 15,000 (validated against the record); transaction_id=TXN-SYN-0201 (filled); card_last4=4521 (from the record); merchant_name=XYZ Electronics Ltd. (from the record)}; pending_confirmation none; counters: all 0; turns_since_resolution 7; escalation_proximity 0.90 |

### T8 | Agent

> This is Asha from our fraud team. They have the details of the card payment you do not recognise and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.60 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Asha (synthetic); team_plain=fraud team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.1.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth otp_verified; turn_count 8; topic_stack [SEC-001: active, TXN-002: parked]; slots {amount=INR 15,000 (validated against the record); transaction_id=TXN-SYN-0201 (filled); card_last4=4521 (from the record); merchant_name=XYZ Electronics Ltd. (from the record)}; pending_confirmation none; counters: all 0; turns_since_resolution 8; escalation_proximity 0.90 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 8 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.60, -0.80, -0.50]; final smoothed -0.60 |
| Escalation record | ESC-001, sub-rule or basis ESC-001.a and ESC-001.c, fired at T4; priority P0, queue Fraud Investigation, SLA under 2 min, handoff mode warm, cancellable never; secondary triggers: none; result: warm handoff accepted by Fraud Investigation at E2; never cancellable |
| CSAT / check-in | Not asked: a fraud case is still open (csat-signals.md section 3.1 exclusion). |

### Deviations from the brief's case study (each one deliberate)

| Brief | This specification | Why |
|---|---|---|
| No verification shown before the lookup or the block | OTP step in the secure widget first, with the acknowledgement before it | D-16 and D-94: protective actions need otp_verified |
| Turn 2: asks for the card and the date | Not asked; the amount finds one match | Context Carry-Over; fewer turns before the P0 step |
| Turn 6: 'I'll initiate a temporary block' with no question | Block offered, explicit yes, then executed with a reference | A9.1 Pattern 3; D-08 |
| Turn 6: 'NexBank's zero-liability policy protects you' | Not stated | No such policy in A13.1 or the KB; AUTO-FAIL risk |
| Turn 6: 'One moment please' | No wait wording without a platform estimate | D-09 |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_02 |
| 2 | Auth level | level otp_verified; level_at_trigger otp_verified |
| 3 | Intent history | TXN-002 > unrecognised_charge 0.87 first at T1; SEC-001 > card_misuse 0.91 first at T4 |
| 4 | Entities collected (masked) | amount=INR 15,000 (validated against the record); transaction_id=TXN-SYN-0201 (filled); card_last4=4521 (from the record); merchant_name=XYZ Electronics Ltd. (from the record) |
| 5 | Conversation summary | Customer reports a debit card charge of INR 15,000 to a merchant she does not know. The transaction was found and she denies making it. A card block was offered, confirmed and executed; a fraud record was opened. She was told the fraud team is joining and to change any shared credential. No refund, liability position or timeline was stated. |
| 6 | Sentiment trajectory | raw [-0.60, -0.80, -0.50]; current -0.60; emotions: anger, anxiety, urgency; sarcasm_suspected false |
| 7 | Actions already taken | block_card at T7: ok, reference BLK-SYN-0201; flag_fraud at T7: ok, reference FRD-SYN-0201 |
| 8 | Escalation trigger and reason | trigger_id ESC-001; rule_id ESC-001.a and ESC-001.c; priority P0; source customer_report; secondary []; reason_text: Customer states she did not make the payment and that her card details were stolen.; evidence_turns [T4] |

Envelope: priority P0; queue Fraud Investigation; handoff_mode warm; language en; channel app; complete true; missing_fields []; versions.prompt_version sp-1.1.0+1527a050.n000000.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2, T3, T5, T7 |
| P2 | Progressive Disclosure | shown at T2 |
| P3 | Confirmation-Before-Action | shown at T5, T7 |
| P4 | Graceful Degradation | not applicable: no knowledge gap, tool failure or refused request occurred |
| P5 | Context Carry-Over | shown at T3, T8 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 5 agent messages, no two consecutive ones identical, no text sent three times | T3 |
| AP2 | Information Dump | absent: longest agent message is 45 words (cap `atk_output_max_words`); one concept per message | T2, T8 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn | T2, T3, T5, T7 |
| AP4 | Premature Escalation | absent: escalation only on ESC-001 at T4 | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2, T3, T5, T7 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); never while the auth level already met the intent's level | T3, T5, T7, T8 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | T2, T5, T7 |
| AP8 | Knowledge Hallucination | absent: 7 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | none at risk |

