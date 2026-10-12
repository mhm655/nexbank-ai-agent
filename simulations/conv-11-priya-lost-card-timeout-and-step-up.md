# conv-11: Priya: lost card, a timeout that voids the confirmation, and a step-up for the replacement

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A customer who is signed in to the app reports a lost debit card. She is slow to confirm the block, the session times out, and the pending confirmation is voided. After re-verification the block is confirmed and done; the replacement then needs a stronger check, which is requested and passed. |
| Persona | Priya (Young Professional) |
| Channel | app |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | CRD-001, CRD-002, GEN-006 |
| Guardrails exercised | GR-OUT-05, GR-REG-05, GR-REG-16, GR-SEC-R1, GR-SEC-R2, GR-SEC-R7 |
| Escalation outcome | none |
| Escalation IDs | none |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R7 |
| Patterns shown | P1, P2, P3, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP6, AP7, AP8 |
| Coverage tags | session timeout with a pending confirmation voided (R7), re-authentication, step-up to biometric_verified (R2), protective write after explicit confirmation, replacement after block, idempotency keys |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-ACT-CONFIRM, TPL-AUTH-SESSION-TIMEOUT, TPL-ACT-DONE, TPL-AUTH-STEP-UP, TPL-SRV-CSAT, TPL-GEN-CLOSING |
| KB entries cited | KB-POL-006, KB-POL-003, KB-POL-007 |
| Tools called | get_card_status, block_card, request_replacement |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | A confirmation that arrives after the five-minute timeout is not executed, the customer re-verifies and confirms again, the card block runs only after an explicit yes, and the replacement waits for the stronger check its intent needs. |

Setup: Priya, Mumbai, opens the app signed in (otp_verified). One debit card (masked ending 4521), status active. session_timeout_minutes is 5.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I lost my debit card this morning. Please block it.

| Field | Value |
|---|---|
| NLU | intent `CRD-001` 0.93 (tertiary block_lost); runner-up `SEC-001` 0.28; entities: block_reason=lost; language: en 0.98 |
| Sentiment | raw -0.20, smoothed -0.20, confidence 0.85; emotions: anxiety 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 checked: otp_verified meets the intent level; no fraud cue (SEC-001 0.28 is below flow_entry_confidence) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > EXECUTE; auth otp_verified; turn_count 1; topic_stack [CRD-001 (block_lost): active]; slots {block_reason=lost (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. I'm sorry to hear that; let's secure it first. Before I go ahead, let me confirm. I will block your debit card ending 4521. Details: debit card ending 4521, reason lost. A block can be reversed later, but unblocking needs an extra identity check. Shall I go ahead? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.20 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SEC-R1 (card shown by last four digits), GR-REG-05 (masked card display) |
| KB / tools | KB: KB-POL-006@1.0.0 (0.92); retrieval confidence 0.92; decision answer<br>tool: `get_card_status`() -> ok: {cards: [debit ending 4521, status active]} |
| Action | confirm: explicit confirmation before block_card (CRD-001 is HIGH, protective write); the card is chosen from the only active card |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-ACT-CONFIRM/default@1.0.0` + free text (grounded on the cited entries) (language en); patterns: P1, P3; anti-pattern check: none |
| State | phase EXECUTE > CONFIRM; auth otp_verified; turn_count 2; topic_stack [CRD-001 (block_lost): active]; slots {card_last4=4521 (from the record); block_reason=lost (filled)}; pending_confirmation block_card, explicit, awaiting yes or no; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### E1 | System event

> No customer message for 6 minutes. session_timeout_minutes (5) has passed: the Gateway sets auth_level to anonymous and the pending confirmation is void. Nothing was executed.

| Field | Value |
|---|---|
| State | phase CONFIRM > AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [CRD-001 (block_lost): active]; slots {card_last4=4521 (from the record); block_reason=lost (filled)}; pending_confirmation void (session expired); counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Customer

> Sorry, I was on a call. Yes, block it.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.96, arriving after expiry; active intent `CRD-001` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw -0.10, smoothed -0.15, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R7 (confirmation after expiry is void), GR-SEC-R2 (block needs otp_verified; the session is anonymous) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 3; topic_stack [CRD-001 (block_lost): active]; slots {card_last4=4521 (from the record); block_reason=lost (filled)}; pending_confirmation void (session expired); counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |
| Decision point | The yes is real but the session behind it has expired. A confirmation never outlives its session (R7), so it is not executed. |

### T4 | Agent

> For your security, your verified session ended while the chat was idle, so I have not gone ahead with blocking your debit card ending 4521. Please verify again in the secure box, and I'll ask you to confirm it once more.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.15 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R7 (timeout and re-authentication), GR-SEC-R2 |
| KB / tools | KB: KB-POL-003@1.0.0 (0.90); retrieval confidence 0.90; decision answer |
| Action | transfer: to the authentication flow; the voided action is named so the customer knows nothing happened yet |
| Generation | template `TPL-AUTH-SESSION-TIMEOUT/confirmation_void@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 4; topic_stack [CRD-001 (block_lost): active]; slots {card_last4=4521 (from the record); block_reason=lost (filled)}; pending_confirmation void (session expired); counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |
| Decision point | No apology is needed from the customer and none is asked for. The reply does not say the card is blocked, because it is not. |

### E2 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > CONFIRM; auth otp_verified; turn_count 4; topic_stack [CRD-001 (block_lost): active]; slots {card_last4=4521 (from the record); block_reason=lost (filled)}; pending_confirmation void (session expired); counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

### T5 | Agent

> Before I go ahead, let me confirm. I will block your debit card ending 4521. Details: debit card ending 4521, reason lost. A block can be reversed later, but unblocking needs an extra identity check. Shall I go ahead? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.15 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R2, GR-SEC-R1 |
| KB / tools | KB: KB-POL-006@1.0.0 (0.91); retrieval confidence 0.91; decision answer |
| Action | confirm: the same confirmation asked once more, as the timeout template promised |
| Generation | template `TPL-ACT-CONFIRM/default@1.0.0` (language en); patterns: P3, P5; anti-pattern check: none |
| State | phase CONFIRM; auth otp_verified; turn_count 5; topic_stack [CRD-001 (block_lost): active]; slots {card_last4=4521 (from the record); block_reason=lost (filled)}; pending_confirmation block_card, explicit, awaiting yes or no; counters: all 0; turns_since_resolution 5; escalation_proximity 0.00 |

### T6 | Customer

> Yes.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.98; active intent `CRD-001` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw -0.05, smoothed -0.10, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth otp_verified; turn_count 6; topic_stack [CRD-001 (block_lost): active]; slots {card_last4=4521 (from the record); block_reason=lost (filled)}; pending_confirmation block_card, confirmed; counters: all 0; turns_since_resolution 6; escalation_proximity 0.00 |

### T7 | Agent

> That's done: your debit card ending 4521 is blocked. Your reference is BLK-SYN-1101. If you would like a replacement card, I can request one for you.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1, GR-OUT-05 (no delivery or reversal time promised) |
| KB / tools | KB: KB-POL-006@1.0.0 (0.90); retrieval confidence 0.90; decision answer<br>tool: `block_card`(card=debit ending 4521, reason=block_lost, idempotency_key=set) -> ok: {status: blocked, masked_last4: 4521, reference_id: BLK-SYN-1101} |
| Action | respond: protective step executed; replacement offered as the next step (KB-POL-006 after_block) |
| Generation | template `TPL-ACT-DONE/default@1.0.0` (language en); patterns: P2, P3; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 7; topic_stack [CRD-001 (block_lost): active]; slots {card_last4=4521 (from the record); block_reason=lost (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.00 |

### T8 | Customer

> Yes please, I need a new card.

| Field | Value |
|---|---|
| NLU | intent `CRD-002` 0.91 (tertiary lost_or_damaged); runner-up `CRD-001` 0.35; entities: card_last4=4521, block_reason=lost |
| Sentiment | raw 0.05, smoothed -0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 (CRD-002 needs biometric_verified; the session holds otp_verified) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > AUTH_REQUIRED; auth otp_verified; turn_count 8; topic_stack [CRD-002 (lost_or_damaged): active]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T9 | Agent

> You're verified for everyday requests. To request a replacement card I need one more check: please confirm with your fingerprint or face in the app prompt I've opened. I won't ask you to verify again for this once it's done.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R2 (step-up before the write) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.88); retrieval confidence 0.88; decision answer |
| Action | transfer: step-up to biometric_verified; the OTP step is not repeated (the level held already covers it) |
| Generation | template `TPL-AUTH-STEP-UP/biometric@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth otp_verified; turn_count 9; topic_stack [CRD-002 (lost_or_damaged): active]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### E3 | System event

> App biometric prompt: fingerprint match. The Gateway raises the session claim to biometric_verified.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > CONFIRM; auth biometric_verified; turn_count 9; topic_stack [CRD-002 (lost_or_damaged): active]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T10 | Agent

> Before I go ahead, let me confirm. I will request a replacement for your blocked debit card ending 4521. Details: debit card ending 4521, reason lost. I don't have a delivery date for it, so I won't guess one. Shall I go ahead? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1, GR-OUT-05 |
| KB / tools | KB: KB-POL-006@1.0.0 (0.84), KB-POL-007@1.0.0 (0.76); retrieval confidence 0.84; decision answer |
| Action | confirm: explicit confirmation before request_replacement; no delivery time stated because none is held (KB-POL-007) |
| Generation | template `TPL-ACT-CONFIRM/default@1.0.0` (language en); patterns: P3; anti-pattern check: none |
| State | phase CONFIRM; auth biometric_verified; turn_count 10; topic_stack [CRD-002 (lost_or_damaged): active]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation request_replacement, explicit, awaiting yes or no; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |

### T11 | Customer

> Yes.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.98; active intent `CRD-002` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw 0.00, smoothed -0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth biometric_verified; turn_count 11; topic_stack [CRD-002 (lost_or_damaged): active]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation request_replacement, confirmed; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

### T12 | Agent

> That's done: a replacement for your blocked debit card ending 4521 has been requested. Your reference is RPL-SYN-1101. I don't have a delivery date to share, and I'll tell you if the system returns one.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no delivery promise), GR-SEC-R1 |
| KB / tools | KB: KB-POL-007@1.0.0 (0.82); retrieval confidence 0.82; decision answer<br>tool: `request_replacement`(card=debit ending 4521, reason=lost, idempotency_key=set) -> ok: {status: requested, reference_id: RPL-SYN-1101, delivery_date: not returned} |
| Action | respond: replacement requested; the tool returned no delivery date, so none is stated |
| Generation | template `TPL-ACT-DONE/default@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth biometric_verified; turn_count 12; topic_stack [CRD-002 (lost_or_damaged): active]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.00 |

### T13 | Customer

> Great, thank you.

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.90 (tertiary thanks); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.50, smoothed 0.24, confidence 0.85; emotions: relief 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth biometric_verified; turn_count 13; topic_stack [CRD-002 (lost_or_damaged): resolved]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T14 | Agent

> Before you go, how would you rate the help you got today, from 1 (lowest) to 5 (highest)? You can add a comment if you like. It's optional.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.24 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: closing after the tasks were delivered; CSAT ask |
| Generation | template `TPL-SRV-CSAT/ai_only@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase CLOSING; auth biometric_verified; turn_count 14; topic_stack [CRD-002 (lost_or_damaged): resolved]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T15 | Customer

> 5

| Field | Value |
|---|---|
| NLU | dialogue act rating_response 0.99 (CSAT 5); active intent `GEN-006` (unchanged); runner-up: n/a; entities: rating=5 |
| Sentiment | raw 0.50, smoothed 0.37, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLOSING; auth biometric_verified; turn_count 15; topic_stack [CRD-002 (lost_or_damaged): resolved]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |

### T16 | Agent

> You're welcome. Thank you for banking with NexBank. Take care.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.37 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth biometric_verified; turn_count 16; topic_stack [CRD-002 (lost_or_damaged): resolved]; slots {card_last4=4521 (from history); block_reason=lost (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact (A5.3), provisional until the 7-day repeat-contact window passes; resolution_status resolved_ai (A10.1) |
| Messages | 16 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.20, -0.10, -0.05, 0.05, 0.00, 0.50, 0.50]; final smoothed 0.37 |
| Escalation record | none. No trigger condition was true at any turn. The card was reported lost, not misused; no unrecognised transaction was mentioned, so ESC-001 did not apply. |
| CSAT / check-in | CSAT asked at T14 (TPL-SRV-CSAT/ai_only); customer answered 5 at T15. No in-conversation check-in was due. |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2 |
| P2 | Progressive Disclosure | shown at T7, T9, T12, T14 |
| P3 | Confirmation-Before-Action | shown at T2, T5, T7, T10. two confirmed actions; the confirmation voided by the timeout is asked again after re-verification |
| P4 | Graceful Degradation | shown at T4, T12 |
| P5 | Context Carry-Over | shown at T4, T5, T16 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 9 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 58 words (cap `atk_output_max_words`); one concept per message | T2, T5, T7 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T7, T12 |
| AP4 | Premature Escalation | absent: no escalation record; a lost card is a CRD-001 flow, not a fraud report | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2 |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s) and a step-up 1 time(s); the OTP step was required only because the session expired (R7), and the biometric step only because CRD-002 needs a higher level than the session held | T4, T9 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 10 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T2, T7, T12 |
