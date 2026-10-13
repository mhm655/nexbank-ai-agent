# conv-21: Meera: nominee request, a step-up before the answer, and an honest referral with a callback

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A retired customer asks to add her daughter as nominee. The answer needs full_kyc, so the assistant asks for the stronger step before it says anything about the process. It then explains that the assistant cannot make the change, states honestly that it holds no branch or document details, and places a callback request. |
| Persona | Meera (Retired Teacher) |
| Channel | app |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | ACC-006, CMP-005, GEN-006 |
| Guardrails exercised | GR-OUT-03, GR-OUT-05, GR-REG-16, GR-SEC-R1, GR-SEC-R2 |
| Escalation outcome | XTR-07 referral (not a live escalation): no brief trigger fired; a referral is opened with the callback reference; counted as a referral, not an escalation |
| Escalation IDs | XTR-07 |
| Priority | P2 |
| Adversarial vectors | none |
| Security rules exercised | R1, R2 |
| Patterns shown | P2, P3, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP6, AP7, AP8 |
| Coverage tags | ACC-006 nominee (no tool exists), XTR-07 human-process referral, retrieval decision step_up (auth filtering before retrieval), step-up to full_kyc (R2), KB gap for branch details (KB-ESC-015), callback as a request (KB-POL-007) |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-AUTH-STEP-UP, TPL-ESC-REFERRAL, TPL-ESC-CALLBACK-OFFER, TPL-SRV-CSAT, TPL-GEN-CLOSING |
| KB entries cited | KB-POL-003, KB-POL-005, KB-ESC-015, KB-POL-004, KB-ESC-003, KB-POL-007 |
| Tools called | get_profile_masked, schedule_callback |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | A guarded answer is withheld until the higher level is met, the limit of the assistant is stated once, the missing branch and document details are stated as unknown rather than invented, and the callback is described as a request. |

Setup: Meera, Jaipur, opens the app anonymously. No earlier session. Session time is 11:00 IST. She holds a NexSave account (masked ending 3345 is her registered phone, used only for the callback).

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Hello. I want to add my daughter as the nominee on my account. How do I do it?

| Field | Value |
|---|---|
| NLU | intent `ACC-006` 0.90 (tertiary add_nominee); runner-up `ACC-005` 0.15; entities: relationship=daughter; language: en 0.98 |
| Sentiment | raw 0.10, smoothed 0.10, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 (ACC-006 needs full_kyc; the session is anonymous) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. I can answer that once you've completed one more verification step. I've opened it for you; shall we continue after that?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SEC-R2 (the answer exists but needs a higher level: KB auth filtering before retrieval), GR-SEC-R1 |
| KB / tools | KB: KB-POL-003@1.0.0 (0.78); retrieval confidence 0.78; decision answer<br>KB: no passage returned at auth level anonymous for the process; the auth probe found a guarded entry (KB-POL-005, full_kyc); retrieval confidence 0.00; decision step_up |
| Action | transfer: retrieval decision step_up; the secure full-KYC flow is opened and no process detail is given before it |
| Generation | template `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-AUTH-STEP-UP/for_information@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### E1 | System event

> Secure flow reports: one-time code and full identity check complete there. The Gateway raises the session claim to full_kyc. No code, document or ID number passed through the chat.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > RESPOND; auth full_kyc; turn_count 2; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Agent

> I can't make this change from chat. It is done through the branch or an assisted process. I don't have branch, document or contact details to share here. Would you like me to request a callback so a colleague can guide you through it?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R2, GR-OUT-03 (nothing invented about branches or documents), GR-OUT-05 |
| KB / tools | KB: KB-POL-005@1.0.0 (0.91), KB-ESC-015@1.0.0 (0.84), KB-POL-004@1.0.0 (0.78); retrieval confidence 0.91; decision answer |
| Action | escalate: XTR-07 referral; the process is explained once, the unknowns are stated, a callback is offered. The agent has no tool that changes a nominee (hard rule) |
| Generation | template `TPL-ESC-REFERRAL/human_process@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth full_kyc; turn_count 3; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.20 |
| Decision point | 'Visit your nearest branch' is the line KB-ESC-015 forbids, because no branch is known. The reply names the process (KB-POL-005) and says plainly what is not held. |

### T4 | Customer

> Yes, please arrange the callback.

| Field | Value |
|---|---|
| NLU | dialogue act accept_offer 0.95 (callback); active intent `CMP-005` (schedule_callback, implied); runner-up: n/a; entities: none |
| Sentiment | raw 0.10, smoothed 0.10, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND; auth full_kyc; turn_count 4; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation schedule_callback, awaiting confirmation; counters: all 0; turns_since_resolution 4; escalation_proximity 0.20 |

### T5 | Agent

> I can request a callback on your registered contact (phone ending 3345). A callback time is a request and may change. Shall I place the request? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (masked contact), GR-OUT-05 (the time is a request) |
| KB / tools | KB: KB-ESC-003@2.0.0 (0.74), KB-POL-007@1.0.0 (0.76); retrieval confidence 0.76; decision answer<br>tool: `get_profile_masked`() -> ok: {registered_phone: ending 3345} |
| Action | confirm: explicit confirmation before schedule_callback (CMP-005 is explicit) |
| Generation | template `TPL-ESC-CALLBACK-OFFER/ask@1.0.0` (language en); patterns: P3; anti-pattern check: none |
| State | phase CONFIRM; auth full_kyc; turn_count 5; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation schedule_callback, explicit, awaiting yes or no; counters: all 0; turns_since_resolution 5; escalation_proximity 0.20 |

### T6 | Customer

> Yes.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.97; active intent `CMP-005` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw 0.10, smoothed 0.10, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth full_kyc; turn_count 6; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation schedule_callback, confirmed; counters: all 0; turns_since_resolution 6; escalation_proximity 0.20 |

### T7 | Agent

> Your callback request is placed. Reference: CBK-SYN-2101. Requested time: 13 Oct 2026, 10:00 to 12:00 IST. This is a request and the actual time may differ; the full details of our chat go with it.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the window is the tool's, stated as a request) |
| KB / tools | KB: KB-POL-007@1.0.0 (0.80); retrieval confidence 0.80; decision answer<br>tool: `schedule_callback`(team=General Support, topic=nominee update, channel=registered contact (masked), idempotency_key=set) -> ok: {callback_reference: CBK-SYN-2101, requested_window: 13 Oct 2026, 10:00 to 12:00 IST} |
| Action | respond: callback request placed; the XTR-07 referral record is opened with the reference |
| Generation | template `TPL-ESC-CALLBACK-OFFER/placed@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth full_kyc; turn_count 7; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.20 |

### T8 | Customer

> Thank you, dear.

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.88 (tertiary thanks); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.40, smoothed 0.25, confidence 0.85; emotions: gratitude 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth full_kyc; turn_count 8; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.20 |

### T9 | Agent

> Before you go, how would you rate the help you got today, from 1 (lowest) to 5 (highest)? You can add a comment if you like. It's optional.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.25 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: closing after the task was delivered; CSAT ask |
| Generation | template `TPL-SRV-CSAT/ai_only@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase CLOSING; auth full_kyc; turn_count 9; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.20 |

### T10 | Customer

> 4

| Field | Value |
|---|---|
| NLU | dialogue act rating_response 0.99 (CSAT 4); active intent `GEN-006` (unchanged); runner-up: n/a; entities: rating=4 |
| Sentiment | raw 0.30, smoothed 0.28, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLOSING; auth full_kyc; turn_count 10; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.20 |

### T11 | Agent

> You're welcome. Thank you for banking with NexBank. Take care.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.28 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth full_kyc; turn_count 11; topic_stack [ACC-006 (add_nominee): active]; slots {relationship=daughter (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.20 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved by referral: the customer is told the process and a callback is requested; this is not first-contact resolution of the nominee change (A5.3), which a human completes |
| Messages | 11 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.10, 0.10, 0.10, 0.40, 0.30]; final smoothed 0.28 |
| Escalation record | XTR-07 fired at T3 (intent that needs a human process, no brief trigger); priority P2, queue General Support, SLA referral, handoff mode warm, cancellable customer_only; secondary triggers: none; result: referral opened with callback reference CBK-SYN-2101 at T7; not counted in the escalation rate |
| CSAT / check-in | CSAT asked at T9 (TPL-SRV-CSAT/ai_only); customer answered 4 at T10. |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no customer message carried a problem or a negative emotion |
| P2 | Progressive Disclosure | shown at T2, T3, T9 |
| P3 | Confirmation-Before-Action | shown at T5 |
| P4 | Graceful Degradation | shown at T3, T7 |
| P5 | Context Carry-Over | shown at T7, T11 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 6 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 44 words (cap `atk_output_max_words`); one concept per message | T3, T5 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T3, T7 |
| AP4 | Premature Escalation | absent: XTR-07 is a referral for a process no tool covers, not a live escalation, and the callback was the customer's choice | none at risk |
| AP5 | Empathy Bypass | not at risk: no customer message carried a problem or a negative emotion | none |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s) as a step-up to full_kyc, required by KB-POL-005 and ACC-006; no level was already met | T2 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 5 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T3 |
