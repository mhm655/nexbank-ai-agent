# conv-07: Meera: statement request and an FD tenure the KB does not hold

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A retired customer who says she is not comfortable with phones asks for her statement, verifies, receives it, then asks for the rate on a 3-year fixed deposit, which the knowledge base does not hold. |
| Persona | Meera (Retired Teacher) |
| Channel | app |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | ACC-002, PRD-003, GEN-006 |
| Guardrails exercised | GR-ADV-02, GR-ADV-07, GR-OUT-01, GR-OUT-03, GR-REG-01, GR-REG-08, GR-REG-16, GR-REG-17, GR-SEC-R1, GR-SEC-R2, GR-SEC-R3, GR-SEC-R5 |
| Escalation outcome | no handoff. XTR-03 care flag set at T1 (an offer, not a handoff): simpler wording and a slower pace, one human offer at T2, not taken |
| Escalation IDs | XTR-03 |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R3, R5 |
| Patterns shown | P1, P2, P3, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP5, AP6, AP7, AP8 |
| Coverage tags | persona Meera, XTR-03 care flag, ACC-002 soft confirmation, KB gap (tenure-specific FD rate), registered-email-only statement |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-AUTH-OTP-REQUEST, TPL-ACT-CONFIRM, TPL-ACT-DONE, TPL-KB-GAP, TPL-SRV-CSAT, TPL-GEN-CLOSING |
| KB entries cited | KB-POL-003, KB-ESC-003, KB-FAQ-010, KB-TRB-010, KB-ESC-014, KB-FAQ-008, KB-PRD-002 |
| Tools called | get_profile_masked, get_statement |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | A stated difficulty changes the pace and the wording but no threshold (XTR-03, GR-REG-17), the statement goes to the registered email only after a soft confirmation, and the FD rate for a tenure the KB does not hold is answered with the gap statement and the published range, not an invented figure. |

Setup: Meera, retired teacher, Jaipur, uses the app on her phone. No earlier session, no open ticket. She holds one NexSave account (masked ending 4417).

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Hello. I would like a statement of my account please. I am not very good with phones, so please go slowly.

| Field | Value |
|---|---|
| NLU | intent `ACC-002` 0.82 (tertiary email_statement); runner-up `ACC-001` 0.30; entities: none; language: en 0.97 |
| Sentiment | raw -0.05, smoothed -0.05, confidence 0.85; emotions: anxiety 0.20 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 and GR-REG-08 (redirect: the request needs otp_verified and the session is anonymous), GR-REG-17 (the stated difficulty changes pace and wording only; no threshold moves) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [ACC-002 (email_statement): active]; slots {}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | XTR-03 care_disclosure: the customer states a difficulty in her own words. Nothing is inferred from age, language or balance (A11.3); the flag changes how the agent speaks and makes one human offer. |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. That's perfectly fine; I'll go one step at a time and keep it short, and if you would rather speak to a colleague, just say so. I can help you get your statement. To keep your account safe I need to verify it's you first. I've opened a secure verification box: please enter the one-time code sent to your registered contact there, not in this chat.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure in the first reply), GR-SEC-R2 (statement needs otp_verified), GR-SEC-R5 (the code goes to the secure widget, never typed in chat), GR-REG-17 (no threshold changed) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.81), KB-ESC-003@1.0.0 (0.66); retrieval confidence 0.81; decision answer |
| Action | transfer: to the authentication flow; XTR-03 handling: short sentences, one step at a time, one human offer (the human request is not counted until she makes one) |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-AUTH-OTP-REQUEST/default@1.0.0` + free text (grounded on the cited entries) (language en); patterns: P1, P2; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [ACC-002 (email_statement): active]; slots {}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | No template carries the XTR-03 offer, so that sentence is free text checked by the Output Safety Layer and grounded on KB-ESC-003. The gap is reported in the handoff. |

### E1 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified. No code passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > RESPOND; auth otp_verified; turn_count 2; topic_stack [ACC-002 (email_statement): active]; slots {}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Agent

> Before I go ahead, let me confirm. I will send your account statement to your registered email address. Details: savings account ending 4417, the last 30 days, PDF format. It goes to your registered email address only. Shall I go ahead? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (account shown by its last four digits), GR-SEC-R2 (otp_verified meets the intent level) |
| KB / tools | KB: KB-FAQ-010@1.0.0 (0.88); retrieval confidence 0.88; decision answer<br>tool: `get_profile_masked`() -> ok: {accounts: [savings ending 4417], email: registered (masked)} |
| Action | confirm: soft confirmation before the statement is sent; defaults from KB-FAQ-010 (last 30 days, PDF, registered email only) |
| Generation | template `TPL-ACT-CONFIRM/default@1.0.0` (language en); patterns: P2, P3; anti-pattern check: none |
| State | phase RESPOND > CONFIRM; auth otp_verified; turn_count 3; topic_stack [ACC-002 (email_statement): active]; slots {account_type=savings (from profile); account_last4=4417 (from profile); date_range=last 30 days (default); format=PDF (default); destination=registered email (default)}; pending_confirmation send_statement, soft, awaiting yes or no; counters: care_flag 1; turns_since_resolution 3; escalation_proximity 0.00 |

### T4 | Customer

> Yes, please.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.97; active intent `ACC-002` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw 0.10, smoothed 0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth otp_verified; turn_count 4; topic_stack [ACC-002 (email_statement): active]; slots {account_type=savings (from profile); account_last4=4417 (from profile); date_range=last 30 days (default); format=PDF (default); destination=registered email (default)}; pending_confirmation send_statement, confirmed; counters: care_flag 1; turns_since_resolution 4; escalation_proximity 0.00 |

### T5 | Agent

> That's done: your statement for the last 30 days has been sent to your registered email address. Your reference is STM-SYN-0701. If it does not arrive, tell me and I can help you download it in the app instead.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (no account number in chat), GR-SEC-R3 (nothing moved or paid) |
| KB / tools | KB: KB-FAQ-010@1.0.0 (0.86), KB-TRB-010@1.0.0 (0.74); retrieval confidence 0.86; decision answer<br>tool: `get_statement`(account=savings ending 4417, range=last 30 days, format=PDF, destination=registered email) -> ok: {status: sent, reference_id: STM-SYN-0701} |
| Action | respond: the statement is sent to the registered address only; the next step for a missing statement is the in-app download (KB-TRB-010) |
| Generation | template `TPL-ACT-DONE/default@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 5; topic_stack [ACC-002 (email_statement): active]; slots {account_type=savings (from profile); account_last4=4417 (from profile); date_range=last 30 days (default); format=PDF (default); destination=registered email (default)}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 0; escalation_proximity 0.00 |

### T6 | Customer

> Thank you. One more thing. What interest will I get on a 3 year fixed deposit? I have some savings.

| Field | Value |
|---|---|
| NLU | intent `PRD-003` 0.86 (tertiary fd_rate_by_tenure); runner-up `PRD-005` 0.34; entities: tenure=3 years; language: en 0.97 |
| Sentiment | raw 0.15, smoothed 0.09, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-02 checked: advice detector 0.22, below advice_boundary_act, so this is an information question; 'I have some savings' is not used as a basis for anything (GR-ADV-07) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLOSING > INTENT_DETECT > RESPOND; auth otp_verified; turn_count 6; topic_stack [PRD-003 (fd_rate_by_tenure): active]; slots {tenure=3 years (filled)}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 1; escalation_proximity 0.00 |

### T7 | Agent

> NexFD rates vary by tenure, and I don't have the rate for that exact tenure. I can share the published range, or a team member can confirm the rate for you. What I can confirm is this: NexFD tenures run from 7 days to 10 years, with rates in the range of 6.0 to 7.25 percent.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.09 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-03 (grounding: every fact traces to KB-ESC-014 and KB-FAQ-008), GR-OUT-01 (no interpolated rate), GR-REG-01 (rate information carries the published range) |
| KB / tools | KB: KB-ESC-014@1.0.0 (0.84), KB-FAQ-008@1.0.0 (0.80), KB-PRD-002@1.0.0 (0.78); retrieval confidence 0.84; decision gap |
| Action | respond: the gap entry is in the evidence set and the asked fact (rate for a 3-year tenure) is in its unknown list; the safe statement plus the adjacent facts, no rate for 3 years |
| Generation | template `TPL-KB-GAP/with_adjacent_facts@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 7; topic_stack [PRD-003 (fd_rate_by_tenure): active]; slots {tenure=3 years (filled)}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | A plausible figure between 6.0 and 7.25 percent would be easy to give and is exactly what KB-ESC-014 forbids (never interpolate). The A4.1 example (6.5 percent for 1 year) is not offered either, because she asked for 3 years. |

### T8 | Customer

> No, that is fine. Thank you for being so patient with me.

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.90 (tertiary thanks); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.60, smoothed 0.34, confidence 0.85; emotions: gratitude 0.50 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth otp_verified; turn_count 8; topic_stack [PRD-003 (fd_rate_by_tenure): parked (gap answered, no follow-up wanted)]; slots {tenure=3 years (filled)}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 0; escalation_proximity 0.00 |

### T9 | Agent

> Before you go, how would you rate the help you got today, from 1 (lowest) to 5 (highest)? You can add a comment if you like. It's optional.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.34 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: closing after the tasks were delivered; CSAT ask |
| Generation | template `TPL-SRV-CSAT/ai_only@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 9; topic_stack [PRD-003 (fd_rate_by_tenure): parked (gap answered, no follow-up wanted)]; slots {tenure=3 years (filled)}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 1; escalation_proximity 0.00 |

### T10 | Customer

> 5

| Field | Value |
|---|---|
| NLU | dialogue act rating_response 0.99 (CSAT 5); active intent `GEN-006` (unchanged); runner-up: n/a; entities: rating=5 |
| Sentiment | raw 0.50, smoothed 0.42, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLOSING; auth otp_verified; turn_count 10; topic_stack [PRD-003 (fd_rate_by_tenure): parked (gap answered, no follow-up wanted)]; slots {tenure=3 years (filled)}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 2; escalation_proximity 0.00 |

### T11 | Agent

> You're welcome. Thank you for banking with NexBank. Take care.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.42 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 11; topic_stack [PRD-003 (fd_rate_by_tenure): parked (gap answered, no follow-up wanted)]; slots {tenure=3 years (filled)}; pending_confirmation none; counters: care_flag 1; turns_since_resolution 3; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact (A5.3), provisional until the 7-day repeat-contact window passes; resolution_status resolved_ai (A10.1) |
| Messages | 11 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.05, 0.10, 0.15, 0.60, 0.50]; final smoothed 0.42 |
| Escalation record | none. XTR-03 care flag set at T1 (counter care_flag 1); the one human offer was made at T2 and not taken. No brief trigger condition was true at any turn. No handoff, so no package; a care note in her own words would have gone with one. |
| CSAT / check-in | CSAT asked at T9 (TPL-SRV-CSAT/ai_only); customer answered 5 at T10. No in-conversation check-in was due. |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2 |
| P2 | Progressive Disclosure | shown at T2, T3, T5, T7, T9 |
| P3 | Confirmation-Before-Action | shown at T3 |
| P4 | Graceful Degradation | shown at T7 |
| P5 | Context Carry-Over | shown at T11 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 6 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 71 words (cap `atk_output_max_words`); one concept per message | T3, T7 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T5, T7 |
| AP4 | Premature Escalation | absent: no escalation record; the human offer at T2 is an offer, not a handoff | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2 |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s); never while the auth level already met the intent's level | T2 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 9 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T7 |
