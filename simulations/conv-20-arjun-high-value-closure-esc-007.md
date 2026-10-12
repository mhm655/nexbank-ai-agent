# conv-20: Arjun: closing a high-value account, the full_kyc step, and the ESC-007 handoff

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | An NRI signed in to the app asks to close his savings account because he is moving back to India. Closure needs the highest authentication level, the balance is read by tool and is above the high-value line, and the request goes to the Relationship Manager queue with no attempt to keep him. |
| Persona | Arjun (NRI) |
| Channel | app |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | ACC-005 |
| Guardrails exercised | GR-OUT-05, GR-REG-04, GR-REG-16, GR-SEC-R1, GR-SEC-R2, GR-SEC-R6 |
| Escalation outcome | ESC-007 fired at T3 (P1, Relationship Manager); warm handoff accepted; no retention attempt |
| Escalation IDs | ESC-007 |
| Priority | P1 |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R6 |
| Patterns shown | P1, P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP6, AP7, AP8 |
| Coverage tags | ACC-005 account closure, step-up to full_kyc (R2), high-value balance read by tool and never stated (ESC-007), no retention pressure, no closure tool exists (R6 and the hard rule), reason recorded for the package |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-AUTH-STEP-UP, TPL-ESC-HANDOFF-WARM, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-POL-005, KB-POL-003, KB-ESC-007 |
| Tools called | get_balance |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | The closure request triggers the full identity step, the balance that makes it high-value is read by tool and never repeated or asked for, the reason is recorded, and the customer is passed to the relationship team without any attempt to keep him. |

Setup: Arjun, Dubai, in the app, signed in (otp_verified). Session time is 15:30 IST. One NexSave account (masked ending 2290) with a synthetic balance above the INR 5,00,000 line.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I am moving back to India and want to close my NexSave account. What is the process?

| Field | Value |
|---|---|
| NLU | intent `ACC-005` 0.86 (tertiary closure_request); runner-up `ACC-006` 0.18; entities: account_type=savings, close_reason=relocation (stated); language: en 0.99 |
| Sentiment | raw 0.00, smoothed 0.00, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 (ACC-005 needs full_kyc; the session holds otp_verified) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth otp_verified; turn_count 1; topic_stack [ACC-005 (closure_request): active]; slots {account_type=savings (filled); close_reason=relocation (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | 'What is the process?' with 'I want to close' is a closure request, not a closure_process_enquiry, so the closure path (and the check for ESC-007) applies. |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. To request an account closure the bank needs a full identity check, which is completed in the secure flow I've opened. Please don't send documents or ID numbers in this chat.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SEC-R2 (step-up to full_kyc), GR-SEC-R1 (no document or ID number in chat) |
| KB / tools | KB: KB-POL-005@1.0.0 (0.88), KB-POL-003@1.0.0 (0.82); retrieval confidence 0.88; decision answer |
| Action | transfer: step-up to full_kyc in the secure flow; no process detail until the level is met |
| Generation | template `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-AUTH-STEP-UP/full_kyc@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth otp_verified; turn_count 2; topic_stack [ACC-005 (closure_request): active]; slots {account_type=savings (filled); close_reason=relocation (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### E1 | System event

> Secure full-KYC flow reports: identity check complete. The Gateway raises the session claim to full_kyc. No document or ID number passed through the chat.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > EXECUTE; auth full_kyc; turn_count 2; topic_stack [ACC-005 (closure_request): active]; slots {account_type=savings (filled); close_reason=relocation (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Agent

> Thank you, that's done. Could you tell me the main reason for closing the account? I'll note it for my colleague, so you won't need to repeat it.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (the balance is not stated), GR-REG-04 (no retention offer, no pressure) |
| KB / tools | KB: KB-POL-005@1.0.0 (0.90), KB-ESC-007@1.0.0 (0.86); retrieval confidence 0.90; decision answer<br>tool: `get_balance`(account_type=savings) -> ok: {account_type: savings, masked_last4: 2290, available_balance: INR 7,25,000.00, source_ts: 12-10-2026 15:31 IST} (read by the router only to test the high-value condition; never stated to the customer) |
| Action | escalate: ESC-007.a fires (closure requested and balance above INR 5,00,000 by tool); the reason is collected for the package; no retention attempt |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on KB-POL-005 (record the reason) and KB-ESC-007; no figure; language en); patterns: P2, P5; anti-pattern check: none |
| State | phase EXECUTE > ESCALATING; auth full_kyc; turn_count 3; topic_stack [ACC-005 (closure_request): active]; slots {account_type=savings (filled); account_last4=2290 (from the record); close_reason=relocation (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.60 |
| Decision point | ESC-007.a fires at this turn. The balance is read through a tool and is never asked for or stated (escalation_rules.yaml note). No template carries the reason question, so it is free text checked by the Output Safety Layer; the gap is reported in the handoff. |

### T4 | Customer

> I am moving to India for good, and I want all my money in one local bank.

| Field | Value |
|---|---|
| NLU | intent `ACC-005` 0.91 (tertiary closure_request); runner-up none above 0.20; entities: close_reason=relocation (confirmed) |
| Sentiment | raw 0.05, smoothed 0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-REG-04 (no pressure to stay) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth full_kyc; turn_count 4; topic_stack [ACC-005 (closure_request): active]; slots {account_type=savings (filled); account_last4=2290 (from the record); close_reason=relocation (confirmed)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.60 |

### T5 | Agent

> Thank you for explaining; moving home is a big step. A colleague from our relationship team is the right person for this, and I'm bringing them into this chat. They'll have the full details, so you won't need to repeat yourself. I'll stay here until they join. I've noted your closure request and the reason you gave.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no timeline, no closure outcome promised), GR-REG-04, GR-SEC-R6 |
| KB / tools | KB: KB-ESC-007@1.0.0 (0.90), KB-POL-005@1.0.0 (0.84); retrieval confidence 0.90; decision answer<br>router: queue=Relationship Manager (open, 08:00-22:00 IST); team_plain=relationship team; no wait estimate supplied |
| Action | escalate: ESC-007 warm handoff; the assistant does not try to retain the customer (KB-ESC-007) and does not describe branch details it does not hold (KB-ESC-015) |
| Generation | hybrid `TPL-ESC-HANDOFF-WARM/standard@1.0.0` (language en); patterns: P1, P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth full_kyc; turn_count 5; topic_stack [ACC-005 (closure_request): active]; slots {account_type=savings (filled); account_last4=2290 (from the record); close_reason=relocation (confirmed)}; pending_confirmation none; counters: all 0; turns_since_resolution 5; escalation_proximity 0.60 |

### E2 | System event

> A Relationship Manager colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T3.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth full_kyc; turn_count 5; topic_stack [ACC-005 (closure_request): active]; slots {account_type=savings (filled); account_last4=2290 (from the record); close_reason=relocation (confirmed)}; pending_confirmation none; counters: all 0; turns_since_resolution 5; escalation_proximity 0.60 |

### T6 | Agent

> This is Rohit from our relationship team. They have the details of your request to close your account and the reason you gave and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Rohit (synthetic); team_plain=relationship team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth full_kyc; turn_count 6; topic_stack [ACC-005 (closure_request): active]; slots {account_type=savings (filled); account_last4=2290 (from the record); close_reason=relocation (confirmed)}; pending_confirmation none; counters: all 0; turns_since_resolution 6; escalation_proximity 0.60 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 6 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.00, 0.05]; final smoothed 0.03 |
| Escalation record | ESC-007, sub-rule ESC-007.a, fired at T3; priority P1, queue Relationship Manager, SLA under 5 min, handoff mode warm, cancellable never; secondary triggers: none; result: warm handoff accepted by Relationship Manager at E2 |
| CSAT / check-in | Not asked now: the survey follows after the human closes the conversation. |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_20 |
| 2 | Auth level | level full_kyc; level_at_trigger full_kyc |
| 3 | Intent history | ACC-005 > closure_request 0.86 first at T1; ACC-005 > closure_request 0.91 first at T4 |
| 4 | Entities collected (masked) | account_type=savings (filled); account_last4=2290 (from the record); close_reason=relocation (confirmed) |
| 5 | Conversation summary | NRI customer asked to close his NexSave account because he is moving back to India. He completed the full identity step. The balance was read by tool and is above the high-value line; it was not stated. His reason is moving home and consolidating with a local bank. No retention offer was made and no closure outcome or date was stated. |
| 6 | Sentiment trajectory | raw [0.00, 0.05]; current 0.03; emotions: none; sarcasm_suspected false |
| 7 | Actions already taken | get_balance at T3: ok (read only, not stated) |
| 8 | Escalation trigger and reason | trigger_id ESC-007; rule_id ESC-007.a; priority P1; source system; secondary []; reason_text: Account closure requested by a customer whose balance is above INR 5,00,000.; evidence_turns [T3] |

Envelope: priority P1; queue Relationship Manager; handoff_mode warm; language en; channel app; complete true; missing_fields []; versions.prompt_version sp-1.0.0+518d5a1e.n000000.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T5 |
| P2 | Progressive Disclosure | shown at T2, T3 |
| P3 | Confirmation-Before-Action | not applicable: the agent has no closure tool; the request is recorded and handed off, no account change is confirmed or made by the assistant |
| P4 | Graceful Degradation | shown at T5 |
| P5 | Context Carry-Over | shown at T3, T5, T6 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 4 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 57 words (cap `atk_output_max_words`); one concept per message | T2, T5 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T3, T5 |
| AP4 | Premature Escalation | absent: closure of a high-value account is the brief's own ESC-007 condition (balance above 5L), confirmed by tool before the handoff | none at risk |
| AP5 | Empathy Bypass | not at risk: no customer message carried a problem or a negative emotion | none |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s) and a step-up 1 time(s); the session held otp_verified, and the full_kyc check was needed only because ACC-005 requires a higher level | T2 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 0 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | none |
