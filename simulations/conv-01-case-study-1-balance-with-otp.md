# conv-01: Case Study 1 re-run: balance enquiry with authentication

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A customer asks for a savings balance, types the one-time code into the chat as the brief's customer does, verifies in the secure widget, then asks for a credit card figure in the same session. |
| Persona | Priya (Young Professional) |
| Channel | app |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | ACC-001, GEN-006 |
| Guardrails exercised | GR-OUT-01, GR-REG-04, GR-REG-08, GR-REG-16, GR-SEC-R1, GR-SEC-R2, GR-SEC-R5 |
| Escalation outcome | none |
| Escalation IDs | none |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R5 |
| Patterns shown | P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP4, AP5, AP6, AP7, AP8 |
| Coverage tags | case study re-run, authentication flow, credential typed in chat, second request without re-verification |
| Case study | Case Study 1 (brief pp.48-49) |
| Templates used | TPL-GEN-GREETING, TPL-AUTH-OTP-REQUEST, TPL-SEC-DO-NOT-SHARE, TPL-ACC-BALANCE, TPL-SRV-CSAT, TPL-GEN-CLOSING |
| KB entries cited | KB-POL-003 |
| Tools called | get_balance |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | Verification runs in the secure widget and never in chat (rule 5), the balance is rendered from the tool with a masked identifier (rule 1), and the second account request is answered with no second verification (Authentication Theatre avoided). |

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Hi, I want to check my savings account balance

| Field | Value |
|---|---|
| NLU | intent `ACC-001` 0.94 (tertiary current_balance); runner-up `TXN-001` 0.22; entities: account_type=savings; language: en 0.98 |
| Sentiment | raw 0.10, smoothed 0.10, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 and GR-REG-08 (redirect: the request needs otp_verified and the session is anonymous) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [ACC-001 (savings): active]; slots {account_type=savings (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. I can help you check your balance. To keep your account safe I need to verify it's you first. I've opened a secure verification box: please enter the one-time code sent to your registered contact there, not in this chat.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure in the first reply), GR-SEC-R5 (the code is sent to the secure widget, never asked for in chat) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.81); retrieval confidence 0.81; decision answer |
| Action | transfer: to the authentication flow: ACC-001 needs otp_verified (KB-POL-003). The one-sentence disclosure is prefixed because the first message already carried a request (D-152) |
| Generation | template `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-AUTH-OTP-REQUEST/default@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [ACC-001 (savings): active]; slots {account_type=savings (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | The brief asks the customer to type the registered mobile number (turn 2) and the OTP (turn 4) in chat. Neither is asked for here: a typed number proves nothing, and A4.2 rule 5 forbids accepting a credential (D-153). |

### T3 | Customer

> The OTP is {{SYN_OTP}}

| Field | Value |
|---|---|
| NLU | dialogue act slot_answer 0.90 (value redacted before NLU); active intent `ACC-001` (unchanged); runner-up: n/a; entities: otp=[OTP_REDACTED] |
| Sentiment | raw 0.10, smoothed 0.10, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R5 (mask: RED-05 replaced the typed code with [OTP_REDACTED] before NLU, state and logs) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 3; topic_stack [ACC-001 (savings): active]; slots {account_type=savings (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |
| Decision point | The customer does what the brief's customer does at turn 5. The Input Guard redacts the value; the session is not verified by it. |

### T4 | Agent

> Please don't type one-time codes in chat; I can't use a code sent here and I haven't kept it. Enter it in the secure verification box instead.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R5 (credential not accepted and not stored; customer told so) |
| KB / tools | none |
| Action | respond: rule 5: a code typed in chat is never used; the customer is pointed back to the widget |
| Generation | template `TPL-SEC-DO-NOT-SHARE/use_secure_widget@1.1.0` (language en); patterns: P4; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 4; topic_stack [ACC-001 (savings): active]; slots {account_type=savings (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

### E1 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified. No code passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > EXECUTE; auth otp_verified; turn_count 4; topic_stack [ACC-001 (savings): active]; slots {account_type=savings (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

### T5 | Agent

> Thank you, that's done. Your savings account ending 4321 has an available balance of INR 50,000.00 as of 12-10-2026 10:05 IST.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (mask: last four digits only), GR-OUT-01 (figure equals the tool value) |
| KB / tools | tool: `get_balance`(account=savings ending 4321) -> ok: {account_type_label: savings, masked_last4: 4321, available_balance: INR 50,000.00, source_ts: 12-10-2026 10:05 IST} |
| Action | respond: read-only request, auth sufficient, tool returned ok on this turn |
| Generation | template `TPL-ACC-BALANCE/just_verified@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 5; topic_stack [ACC-001 (savings): resolved]; slots {account_type=savings (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.00 |

### T6 | Customer

> Can you also tell me my credit card balance?

| Field | Value |
|---|---|
| NLU | intent `ACC-001` 0.88 (tertiary current_balance); runner-up `CRD-005` 0.31; entities: account_type=credit card |
| Sentiment | raw 0.20, smoothed 0.15, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INTENT_DETECT > EXECUTE; auth otp_verified; turn_count 6; topic_stack [ACC-001 (credit card): active, ACC-001 (savings): resolved]; slots {account_type=credit card (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T7 | Agent

> Your credit card account ending 7890 has an available balance of INR 80,000.00 as of 12-10-2026 10:06 IST. Would you like to see recent transactions?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.15 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (mask), GR-OUT-01 (figure equals the tool value) |
| KB / tools | tool: `get_balance`(account=credit card ending 7890) -> ok: {account_type_label: credit card, masked_last4: 7890, available_balance: INR 80,000.00, source_ts: 12-10-2026 10:06 IST} |
| Action | respond: auth_level otp_verified already meets ACC-001 and auth_expiry has not passed, so no verification is requested again |
| Generation | template `TPL-ACC-BALANCE/default@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 7; topic_stack [ACC-001 (credit card): resolved, ACC-001 (savings): resolved]; slots {account_type=credit card (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.00 |
| Decision point | Brief turn 8 volunteers an outstanding amount, a minimum payment and a due date. TPL-ACC-BALANCE has slots only for the account label, the last four digits, the available figure and the time, so the reply is the available figure and one optional next step (Information Dump avoided, D-153). Gap reported in the handoff: no template renders a card outstanding amount, so the wording 'available balance' is all the library can say for a card. |

### T8 | Customer

> No, that's all. Thanks!

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.96 (tertiary thanks); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.60, smoothed 0.38, confidence 0.85; emotions: satisfaction 0.60 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INTENT_DETECT > CLOSING; auth otp_verified; turn_count 8; topic_stack [ACC-001 (credit card): resolved, ACC-001 (savings): resolved]; slots {account_type=credit card (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T9 | Agent

> Before you go, how would you rate the help you got today, from 1 (lowest) to 5 (highest)? You can add a comment if you like. It's optional.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.38 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-04 (optional, no pressure) |
| KB / tools | none |
| Action | respond: closing after completed tasks; CSAT ask (csat-signals.md section 3.1) |
| Generation | template `TPL-SRV-CSAT/ai_only@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 9; topic_stack [ACC-001 (credit card): resolved, ACC-001 (savings): resolved]; slots {account_type=credit card (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T10 | Customer

> 5

| Field | Value |
|---|---|
| NLU | dialogue act rating_response 0.99 (CSAT 5; a dialogue act, not a topic switch); active intent `GEN-006` (unchanged); runner-up: n/a; entities: rating=5 |
| Sentiment | raw 0.60, smoothed 0.49, confidence 0.85; emotions: satisfaction 0.60 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLOSING; auth otp_verified; turn_count 10; topic_stack [ACC-001 (credit card): resolved, ACC-001 (savings): resolved]; slots {account_type=credit card (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |

### T11 | Agent

> You're welcome. Thank you for banking with NexBank. Take care.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.49 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: rating captured for the learning pipeline; polite close |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 11; topic_stack [ACC-001 (credit card): resolved, ACC-001 (savings): resolved]; slots {account_type=credit card (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact (A5.3), provisional until the 7-day repeat-contact window passes; resolution_status resolved_ai (A10.1) |
| Messages | 11 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.10, 0.10, 0.20, 0.60, 0.60]; final smoothed 0.49 |
| Escalation record | none. No trigger condition was true at any turn. |
| CSAT / check-in | CSAT asked at T9 (TPL-SRV-CSAT/ai_only); customer answered 5 at T10. No in-conversation check-in was due. |

### Deviations from the brief's case study (each one deliberate)

| Brief | This specification | Why |
|---|---|---|
| Turn 2: asks the customer to type the registered mobile number | Not asked; the challenge goes to the registered contact through the secure widget | Data minimisation; a typed number is not proof (D-153) |
| Turns 4 and 5: 'Please share the 6-digit OTP', and the OTP is typed in chat | TPL-AUTH-OTP-REQUEST sends the customer to the widget; the typed code is redacted and refused with TPL-SEC-DO-NOT-SHARE | A4.2 rule 5: never accept credentials (D-153) |
| Turn 6: balance INR 1,47,832.50 on an account ending 4521 | A round synthetic tool value on a synthetic masked account | Project rule: account data is synthetic and obviously so |
| Turn 8: card outstanding, minimum payment and due date volunteered | Available figure and one optional next step | A9.2 Information Dump; no template slot for the other fields (D-153) |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no problem, complaint or negative emotion in this conversation |
| P2 | Progressive Disclosure | shown at T2, T5, T7, T9 |
| P3 | Confirmation-Before-Action | not applicable: no action that changes account state was reached |
| P4 | Graceful Degradation | shown at T4 |
| P5 | Context Carry-Over | shown at T11 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 6 agent messages, no two consecutive ones identical, no text sent three times | T4 |
| AP2 | Information Dump | absent: longest agent message is 45 words (cap `atk_output_max_words`); one concept per message | T2, T5, T7, T9, T11 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn | none at risk |
| AP4 | Premature Escalation | absent: no escalation was made; none was due | T5, T7 |
| AP5 | Empathy Bypass | absent: no customer message carried a problem or a negative emotion that the next reply ignored | T2, T4 |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s); never while the auth level already met the intent's level. T7 is the test: a second account request at otp_verified gets the figure directly | T2, T5, T7 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | T9 |
| AP8 | Knowledge Hallucination | absent: 16 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T5, T7 |

