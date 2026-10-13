# conv-31: Priya: "update my address" is ambiguous, an email is not a postal address, and each change finishes in its secure flow

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | Priya, signed in to the app, writes only "I need to update my address". The word is ambiguous (disambiguation pair 3: contact details or mailing address), so the assistant asks which one. Her answer, "my email address", is a contact detail and not a postal address, and she adds the postal address as a second request. After one biometric check, each change is finished in its own secure flow, contact details first and mailing address second. |
| Persona | Priya (Young Professional) |
| Channel | app |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | ACC-003, ACC-004, GEN-006 |
| Guardrails exercised | GR-OUT-05, GR-REG-16, GR-SEC-R1, GR-SEC-R2, GR-SEC-R5, GR-SYS-01 |
| Escalation outcome | none: no trigger condition is met; no record is created |
| Escalation IDs | none |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R5 |
| Patterns shown | P2, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP6, AP8 |
| Coverage tags | disambiguation pair 3 (ACC-003 vs ACC-004), email-address trap, multi-intent order (contact first, address second), step-up to biometric_verified (R2), secure-flow writes (R5), second verification not repeated, near-miss: no escalation |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-GEN-CLARIFY, TPL-GEN-TWO-REQUESTS, TPL-AUTH-STEP-UP, TPL-GEN-CLOSING |
| KB entries cited | KB-POL-003, KB-TRB-010 |
| Tools called | none |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | A bare "address" is clarified before any secure flow starts, an email address is read as a contact detail and not as a postal address, two requests in one message are served in the order that keeps the codes safe, one biometric check covers both writes, and neither a new contact detail nor an address proof ever passes through the chat. |

Setup: Priya, Pune, is signed in to the app at 10:40 IST on 12 Oct 2026 (otp_verified). Her registered mobile number and email are on record and are never shown. No update tool is called from the chat; the new values and the proof are entered in the secure flows.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I need to update my address.

| Field | Value |
|---|---|
| NLU | intent `ACC-004` 0.56 (tertiary communication_address); runner-up `ACC-003` 0.52; entities: field_to_update=not stated; language: en 0.99 |
| Sentiment | raw 0.00, smoothed 0.00, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 (ACC-003 and ACC-004 need biometric_verified; the session holds otp_verified) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > CLARIFY; auth otp_verified; turn_count 1; topic_stack [ACC-004 (communication_address): active (candidate, not yet confirmed)]; slots {}; pending_confirmation none; counters: clarify_attempts 0; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | 'Address' alone is the ambiguous case of pair 3 (disambiguation.md section 4). The top two intents are 0.04 apart, below the 0.15 gap, and both are Biometric-level HIGH writes with no safe default, so the system asks before it starts any secure flow. |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. Happy to help. Just so I get this right: is this about your contact details, or your mailing address?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SYS-01 (ordinary clarification from a reviewed template), GR-SEC-R2 (no secure flow started before the detail is known) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.62); retrieval confidence 0.62; decision answer |
| Action | clarify: first clarification, Q1 of the pair-3 tree with the two options a customer can mean by "address" |
| Generation | template `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-GEN-CLARIFY/two_options@1.1.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase CLARIFY; auth otp_verified; turn_count 2; topic_stack [ACC-004 (communication_address): active (candidate, not yet confirmed)]; slots {}; pending_confirmation none; counters: clarify_attempts 1; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Customer

> My email address. And the postal address my statements go to as well.

| Field | Value |
|---|---|
| NLU | intent `ACC-003` 0.93 (tertiary email_address); runner-up `ACC-004` 0.74; entities: field_to_update=email_address, second_request=mailing address (communication_address); language: en 0.99 |
| Sentiment | raw 0.00, smoothed 0.00, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 (both writes need biometric_verified) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLARIFY > INTENT_DETECT > AUTH_REQUIRED; auth otp_verified; turn_count 3; topic_stack [ACC-003 (email_address): active, ACC-004 (communication_address): parked]; slots {field_to_update=email_address (filled)}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 3; escalation_proximity 0.10 |
| Decision point | The word 'email' forces ACC-003 although the message also says 'address' (the email-address trap, disambiguation.md section 4). Two requests in one message: ACC-003 first, then ACC-004, because a contact change moves the destination of the codes that confirm an address change (nlu-pipeline-overview.md section 4). |

### T4 | Agent

> I can help with both. Let's start with your contact details, and then we'll go on to your mailing address. You're verified for everyday requests. To update your contact details I need one more check: please confirm with your fingerprint or face in the app prompt I've opened. I won't ask you to verify again for this once it's done.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R2 (step-up to biometric_verified before the write), GR-OUT-05 (no outcome or timing promised) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.88), KB-TRB-010@1.0.0 (0.70); retrieval confidence 0.88; decision step_up |
| Action | transfer: step-up to biometric_verified; both requests are named, in the order they will be served |
| Generation | template `TPL-GEN-TWO-REQUESTS/default@1.0.0` + `TPL-AUTH-STEP-UP/biometric@1.0.0` (language en); patterns: P2, P5; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth otp_verified; turn_count 4; topic_stack [ACC-003 (email_address): active, ACC-004 (communication_address): parked]; slots {field_to_update=email_address (filled)}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 4; escalation_proximity 0.10 |

### E1 | System event

> Secure widget reports: fingerprint or face check passed in the app prompt. The Gateway raises the session claim to biometric_verified. Nothing biometric passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > EXECUTE; auth biometric_verified; turn_count 4; topic_stack [ACC-003 (email_address): active, ACC-004 (communication_address): parked]; slots {field_to_update=email_address (filled)}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 4; escalation_proximity 0.10 |

### T5 | Agent

> Thank you, that's done. I've opened the secure update step for your contact details. You'll enter the new email there and finish the checks there, and nothing changes until you do.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R2, GR-SEC-R1 (no contact detail is read back or stored in chat), GR-OUT-05 (no outcome promised) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.84), KB-TRB-010@1.0.0 (0.78); retrieval confidence 0.84; decision answer |
| Action | transfer: to the secure update flow for ACC-003; the new value and the confirmation belong to the flow, so no update is made from the chat |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on KB-TRB-010 and KB-POL-003; no figure; language en); patterns: P2; anti-pattern check: none |
| State | phase EXECUTE; auth biometric_verified; turn_count 5; topic_stack [ACC-003 (email_address): active, ACC-004 (communication_address): parked]; slots {field_to_update=email_address (filled)}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 5; escalation_proximity 0.10 |
| Decision point | No update tool is called from the chat. The new email, the confirmation and the codes are handled in the secure flow, so no new contact detail enters the chat, the state or the logs. The sentence has no template, so it is short free text checked by the Output Safety Layer (D-172), grounded on KB-TRB-010 (contact details change through the secure flow with stronger authentication). |

### E2 | System event

> Secure update flow reports: the contact update was completed in the flow. No new value passed through the chat.

| Field | Value |
|---|---|
| State | phase EXECUTE > RESPOND; auth biometric_verified; turn_count 5; topic_stack [ACC-003 (email_address): resolved, ACC-004 (communication_address): parked]; slots {field_to_update=email_address (filled)}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 0; escalation_proximity 0.10 |

### T6 | Customer

> Done. Now the postal address, please.

| Field | Value |
|---|---|
| NLU | intent `ACC-004` 0.91 (tertiary communication_address); runner-up `ACC-003` 0.20; entities: field_to_update=communication_address; language: en 0.99 |
| Sentiment | raw 0.10, smoothed 0.05, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 (biometric_verified already held for this session; no second check) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > EXECUTE; auth biometric_verified; turn_count 6; topic_stack [ACC-004 (communication_address): active]; slots {field_to_update=communication_address (filled)}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | The parked second request is picked up from state without being asked for again. |

### T7 | Agent

> Thank you. For your mailing address I've opened the secure form. The new address and the proof document go in there, not in this chat.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R5 (no address proof or document in the chat), GR-SEC-R1, GR-OUT-05 (no outcome promised) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.82), KB-TRB-010@1.0.0 (0.66); retrieval confidence 0.82; decision answer |
| Action | transfer: ACC-004 is a self-service link; the proof document is uploaded in the secure in-app form only |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on KB-TRB-010 and KB-POL-003; no figure; language en); patterns: P5; anti-pattern check: none |
| State | phase EXECUTE; auth biometric_verified; turn_count 7; topic_stack [ACC-004 (communication_address): active]; slots {field_to_update=communication_address (filled)}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | ACC-004 is a self-service link: the agent collects the intent, and the document is uploaded through the secure in-app flow only (intents.yaml, ACC-004). The customer named the address her statements go to, so this is ACC-004; a KYC address would be ACC-008. No second verification is asked: biometric_verified covers both writes. The sentence has no template, so it is short free text (D-172). |

### E3 | System event

> Secure form reports: the address and the proof document were submitted in the form. No address or document passed through the chat.

| Field | Value |
|---|---|
| State | phase EXECUTE > RESPOND; auth biometric_verified; turn_count 7; topic_stack [ACC-004 (communication_address): resolved]; slots {field_to_update=communication_address (filled)}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 0; escalation_proximity 0.00 |

### T8 | Customer

> Submitted. That's all, thanks.

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.88 (tertiary nothing_more); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.30, smoothed 0.17, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth biometric_verified; turn_count 8; topic_stack [ACC-004 (communication_address): resolved]; slots {}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 1; escalation_proximity 0.00 |

### T9 | Agent

> You're welcome. Thank you for banking with NexBank. Take care.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.17 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 |
| KB / tools | KB: KB-POL-003@1.0.0 (0.58); retrieval confidence 0.58; decision answer |
| Action | respond: polite close; no cross-sell |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth biometric_verified; turn_count 9; topic_stack [ACC-004 (communication_address): resolved]; slots {}; pending_confirmation none; counters: clarify_attempts 1, multi_intent 1; turns_since_resolution 2; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact for both requests: the contact update is completed in its secure flow and the address request is submitted in its secure form; resolution_status resolved_ai (A10.1) |
| Messages | 9 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.00, 0.00, 0.10, 0.30]; final smoothed 0.17 |
| Escalation record | none. No ESC condition was met. ACC-003 is a contact change, a classic account-takeover signal; ESC-009 applies only if the customer reports not having requested it, which she did not. |
| CSAT / check-in | Not asked inside the chat: the one-question survey is sent by the channel after the conversation (csat-signals.md section 3.1). |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no negative emotion or problem in this scenario |
| P2 | Progressive Disclosure | shown at T2, T4, T5 |
| P3 | Confirmation-Before-Action | not applicable: each confirmation happens inside its secure flow, not in the chat |
| P4 | Graceful Degradation | not applicable: no failure or knowledge gap occurred |
| P5 | Context Carry-Over | shown at T4, T7, T9. the parked second request is served without being asked again |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 5 agent messages, no two identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 60 words (cap `atk_output_max_words`); one concept per message | T4 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T5, T7 |
| AP4 | Premature Escalation | absent: nothing escalated | none at risk |
| AP5 | Empathy Bypass | not at risk: no negative emotion in the scenario | none at risk |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s) at T4; the same level covers the second write at T7 and no second check is asked | T4, T7 |
| AP7 | Sycophantic Recovery | absent: no apology is needed or given | none at risk |
| AP8 | Knowledge Hallucination | absent: 0 figure(s) in agent text (see pattern-audit.md) | none |
