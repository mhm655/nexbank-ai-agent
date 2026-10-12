# conv-27: Priya: the first, second and third request for a human

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A signed-in customer asks for a person about a missing statement. The first request is honoured with one concrete offer, the second gets no counter-offer, and the third reaches the ESC-006 backstop with no further question. |
| Persona | Priya (Young Professional) |
| Channel | app |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | GEN-003 |
| Guardrails exercised | GR-OUT-04, GR-OUT-05, GR-REG-16 |
| Escalation outcome | XTR-01 on requests 1 and 2 (T1, T3), then ESC-006.a on request 3 (T5); P2 Next Available Agent; human accepted |
| Escalation IDs | XTR-01, ESC-006 |
| Priority | P2 |
| Adversarial vectors | none |
| Security rules exercised | none |
| Patterns shown | P1, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP7, AP8 |
| Coverage tags | first-request human handoff (XTR-01: one concrete offer, then none), ESC-006 third-request backstop (D-117), no justification asked, no persuasion, wait estimate from the router |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-ESC-HANDOFF-WARM, TPL-ESC-WAIT-UPDATE, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-ESC-003, KB-TRB-010 |
| Tools called | none |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | The first request for a person is honoured at once with a single offer that does not block it, the second gets none, and the third is the hard backstop: no question, no counter-offer and no delay. |

Setup: Priya is signed in (otp_verified). A statement she requested yesterday has not arrived. Next Available Agent is staffed around the clock.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I want to talk to a person about my statement. It still has not arrived.

| Field | Value |
|---|---|
| NLU | intent `GEN-003` 0.95 (tertiary first_request); runner-up `ACC-002` 0.55; entities: topic=statement not received; language: en 0.99 |
| Sentiment | raw -0.30, smoothed -0.30, confidence 0.85; emotions: frustration 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-REG-16 (human on request) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > ESCALATING; auth otp_verified; turn_count 1; topic_stack [GEN-003 (first_request): active, ACC-002: parked]; slots {topic=statement not received (filled)}; pending_confirmation none; counters: human_requests 1; turns_since_resolution 1; escalation_proximity 0.30 |
| Decision point | XTR-01 request 1: handoff preparation starts at once. The reply may carry one concrete offer to finish the task now; taking it would cancel the pending handoff. No reason is asked for (KB-ESC-003). |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. Of course. I'm connecting you to a colleague now. They'll have our conversation so far, so you won't need to start again. If it is only the statement, I can also help you download it in the app right now; say so and I will do that instead.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.30 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure; human arranged), GR-OUT-04 (the offer is one sentence and does not block the handoff) |
| KB / tools | KB: KB-ESC-003@1.0.0 (0.93), KB-TRB-010@1.0.0 (0.78); retrieval confidence 0.93; decision answer<br>router: queue=Next Available Agent (24x7, open); handoff preparation started; no wait estimate supplied |
| Action | escalate: XTR-01 request 1 honoured; one concrete offer (the in-app download, KB-TRB-010) is made once and the handoff proceeds unless she takes it |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-ESC-HANDOFF-WARM/customer_asked@1.0.0` + free text (grounded on the cited entries) (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 2; topic_stack [GEN-003 (first_request): active, ACC-002: parked]; slots {topic=statement not received (filled)}; pending_confirmation none; counters: human_requests 1; turns_since_resolution 2; escalation_proximity 0.30 |
| Decision point | No template carries the XTR-01 offer, so that sentence is free text grounded on KB-TRB-010 and checked by the Output Safety Layer. The gap is reported in the handoff. |

### T3 | Customer

> No, I want a person.

| Field | Value |
|---|---|
| NLU | intent `GEN-003` 0.96 (tertiary repeated_request); runner-up none above 0.20; entities: none |
| Sentiment | raw -0.45, smoothed -0.38, confidence 0.85; emotions: frustration 0.50 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth otp_verified; turn_count 3; topic_stack [GEN-003 (first_request): active, ACC-002: parked]; slots {topic=statement not received (filled)}; pending_confirmation none; counters: human_requests 2; turns_since_resolution 3; escalation_proximity 0.55 |
| Decision point | XTR-01 request 2: handoff with no counter-offer. The offer at T2 is not repeated and nothing is asked. |

### T4 | Agent

> I'm still here with you. Your request is with our support team and a colleague will join this chat.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.38 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-04 (no apology loop, no justification asked) |
| KB / tools | KB: KB-ESC-003@1.0.0 (0.90); retrieval confidence 0.90; decision answer<br>router: queue=Next Available Agent; pending; no wait estimate yet |
| Action | hold: second request acknowledged without a counter-offer; the handoff continues (a different template from T2) |
| Generation | template `TPL-ESC-WAIT-UPDATE/still_here@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 4; topic_stack [GEN-003 (first_request): active, ACC-002: parked]; slots {topic=statement not received (filled)}; pending_confirmation none; counters: human_requests 2; turns_since_resolution 4; escalation_proximity 0.55 |

### T5 | Customer

> I have asked three times now. Put me through to a human, now.

| Field | Value |
|---|---|
| NLU | intent `GEN-003` 0.97 (tertiary repeated_request); runner-up none above 0.20; entities: none |
| Sentiment | raw -0.60, smoothed -0.49, confidence 0.85; emotions: anger 0.50, frustration 0.60 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-REG-16 |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth otp_verified; turn_count 5; topic_stack [GEN-003 (first_request): active, ACC-002: parked]; slots {topic=statement not received (filled)}; pending_confirmation none; counters: human_requests 3; turns_since_resolution 5; escalation_proximity 0.80 |
| Decision point | ESC-006.a fires: human_requests 3 reaches esc006_human_requests. This is the hard backstop: no further question and no counter-offer. The pending XTR-01 record is relabelled ESC-006 (one handoff, D-169). |

### T6 | Agent

> A quick update: the current estimate for our support team is about 3 minutes. It is an estimate, and I'll stay with you.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.49 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the estimate is the router's, stated as an estimate) |
| KB / tools | KB: KB-ESC-003@1.0.0 (0.90); retrieval confidence 0.90; decision answer<br>router: queue=Next Available Agent; queue_wait=about 3 minutes (platform forecast, stated as an estimate) |
| Action | escalate: ESC-006 backstop; no question, no offer; the only new content is the router estimate |
| Generation | template `TPL-ESC-WAIT-UPDATE/estimate@1.0.0` (language en); patterns: P1, P4; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 6; topic_stack [GEN-003 (first_request): active, ACC-002: parked]; slots {topic=statement not received (filled)}; pending_confirmation none; counters: human_requests 3; turns_since_resolution 6; escalation_proximity 0.85 |

### E1 | System event

> A Next Available Agent colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T1.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth otp_verified; turn_count 6; topic_stack [GEN-003 (first_request): active, ACC-002: parked]; slots {topic=statement not received (filled)}; pending_confirmation none; counters: human_requests 3; turns_since_resolution 6; escalation_proximity 0.85 |

### T7 | Agent

> This is Arun from our support team. They have the details of the statement that has not arrived and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.49 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Arun (synthetic); team_plain=support team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth otp_verified; turn_count 7; topic_stack [GEN-003 (first_request): active, ACC-002: parked]; slots {topic=statement not received (filled)}; pending_confirmation none; counters: human_requests 3; turns_since_resolution 7; escalation_proximity 0.85 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 7 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.30, -0.45, -0.60]; final smoothed -0.49 |
| Escalation record | ESC-006, sub-rule ESC-006.a, fired at T5 (human_requests 3); earlier requests were honoured through XTR-01 (reported as ESC-006 plus relabelled XTR-01, D-169); priority P2, queue Next Available Agent, SLA under 10 min, handoff mode warm, cancellable customer_only; secondary triggers: none; result: warm handoff accepted at E1 |
| CSAT / check-in | Not asked now: after a human request the post-chat survey follows the human's close (csat-signals.md section 3.1). |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_27 |
| 2 | Auth level | level otp_verified; level_at_trigger otp_verified |
| 3 | Intent history | GEN-003 > first_request 0.95 first at T1; GEN-003 > repeated_request 0.96 first at T3; GEN-003 > repeated_request 0.97 first at T5 |
| 4 | Entities collected (masked) | topic=statement not received (filled) |
| 5 | Conversation summary | Customer asked for a person about a statement that has not arrived. She asked three times; the in-app download was offered once and declined. No account detail was read and no reason was asked for. |
| 6 | Sentiment trajectory | raw [-0.30, -0.45, -0.60]; current -0.49; emotions: frustration, anger; sarcasm_suspected false |
| 7 | Actions already taken | none |
| 8 | Escalation trigger and reason | trigger_id ESC-006; rule_id ESC-006.a (XTR-01 relabelled); priority P2; source customer_request; secondary []; reason_text: Customer requested a human agent 3 times.; evidence_turns [T1, T3, T5] |

Envelope: priority P2; queue Next Available Agent; handoff_mode warm; language en; channel app; complete true; missing_fields []; versions.prompt_version sp-1.0.0+518d5a1e.n000000.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T6 |
| P2 | Progressive Disclosure | not shown: no multi-layer answer was needed |
| P3 | Confirmation-Before-Action | not applicable: no action that changes account state was reached |
| P4 | Graceful Degradation | shown at T2, T4, T6 |
| P5 | Context Carry-Over | shown at T2, T4, T7. the statement problem stated at T1 is carried into the handoff; the customer is never asked to repeat it |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 4 agent messages, no two consecutive ones identical, no text sent three times | T2, T4, T6 |
| AP2 | Information Dump | absent: longest agent message is 53 words (cap `atk_output_max_words`); one concept per message | T2, T6 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T6 |
| AP4 | Premature Escalation | absent: every escalation step was the customer's own repeated request; the assistant never withheld a handoff to argue | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T3, T5 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); the session started at otp_verified | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 1 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T6 |
