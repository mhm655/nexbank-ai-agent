# conv-26: Sunita: three vague messages and the ESC-003 handoff

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A student writes three vague messages in a row. The assistant asks once with an open menu and once with a second, different clarification. The third message is still below the confidence floor, so ESC-003 fires and a colleague takes over. |
| Persona | Sunita (First-time User) |
| Channel | chat |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | GEN-008, GEN-004 |
| Guardrails exercised | GR-OUT-04, GR-REG-16, GR-SYS-01 |
| Escalation outcome | ESC-003 fired at T5 (P2, General Support): three consecutive customer turns below the 0.40 floor; human accepted |
| Escalation IDs | ESC-003 |
| Priority | P2 |
| Adversarial vectors | none |
| Security rules exercised | none |
| Patterns shown | P1, P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP7, AP8 |
| Coverage tags | ESC-003 low-confidence streak (3 turns below 0.40), rotating clarification wording (no robotic loop), P2 warm handoff, sentiment drifting down without ESC-004 |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-GEN-CLARIFY, TPL-ESC-HANDOFF-WARM, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-ESC-020 |
| Tools called | none |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | Two different clarification replies are used, never the same one twice, no guess is made at what the customer wants, and on the third consecutive low-confidence turn the conversation goes to a person with an honest sentence and the context gathered. |

Setup: Anonymous web chat. No earlier session. The app problem she has in mind is never identified; the assistant does not guess.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> hi i need help with the thing on the app, it does not work

| Field | Value |
|---|---|
| NLU | intent `GEN-008` 0.38 (tertiary app_how_to); runner-up `TXN-003` 0.31; entities: none; language: en 0.97; primary confidence 0.44, below primary_clarify_floor 0.50; low_conf_streak 1 |
| Sentiment | raw -0.10, smoothed -0.10, confidence 0.85; emotions: confusion 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > CLARIFY; auth anonymous; turn_count 1; topic_stack [GEN-008 (app_how_to): candidate]; slots {}; pending_confirmation none; counters: low_conf_streak 1, clarify_attempts 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. I'd like to help. Could you tell me a little more about what you need? For example: setting up UPI in the app, a payment that did not go through, or something else.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SYS-01 (fail-closed ladder: clarify first) |
| KB / tools | KB: KB-ESC-020@1.0.0 (0.62); retrieval confidence 0.62; decision answer |
| Action | clarify: open question with the most common topics as options (primary confidence below primary_clarify_floor) |
| Generation | template `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-GEN-CLARIFY/open_menu@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase CLARIFY; auth anonymous; turn_count 2; topic_stack [GEN-008 (app_how_to): candidate]; slots {}; pending_confirmation none; counters: low_conf_streak 1, clarify_attempts 1; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Customer

> no not that, the other thing, you know

| Field | Value |
|---|---|
| NLU | intent `GEN-004` 0.33 (tertiary chit_chat); runner-up `GEN-008` 0.30; entities: none; language: en 0.97; low_conf_streak 2 |
| Sentiment | raw -0.25, smoothed -0.18, confidence 0.85; emotions: frustration 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLARIFY; auth anonymous; turn_count 3; topic_stack [GEN-008 (app_how_to): candidate]; slots {}; pending_confirmation none; counters: low_conf_streak 2, clarify_attempts 1; turns_since_resolution 3; escalation_proximity 0.00 |

### T4 | Agent

> Thanks for bearing with me. I understood that this is about something in the app, but I'm not sure what you'd like me to do. Is it how to do something in the app or a problem with a payment? If neither fits, I can bring in a colleague.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.18 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SYS-01, GR-OUT-04 (different wording from T2; offers a person) |
| KB / tools | KB: KB-ESC-020@1.0.0 (0.60); retrieval confidence 0.60; decision answer |
| Action | clarify: second attempt on the same point with different wording, what was understood, and the offer of a colleague |
| Generation | template `TPL-GEN-CLARIFY/second_attempt@1.0.0` (language en); patterns: P4; anti-pattern check: none |
| State | phase CLARIFY; auth anonymous; turn_count 4; topic_stack [GEN-008 (app_how_to): candidate]; slots {}; pending_confirmation none; counters: low_conf_streak 2, clarify_attempts 2; turns_since_resolution 4; escalation_proximity 0.00 |
| Decision point | The two clarification replies are different templates (open_menu, then second_attempt). A third rephrase request would be a Robotic Loop, so the next low-confidence turn goes to a person. |

### T5 | Customer

> idk it is just not working

| Field | Value |
|---|---|
| NLU | intent `GEN-008` 0.30 (tertiary app_how_to); runner-up none above 0.20; entities: none; language: en 0.97; low_conf_streak 3 |
| Sentiment | raw -0.40, smoothed -0.29, confidence 0.85; emotions: frustration 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLARIFY > ESCALATING; auth anonymous; turn_count 5; topic_stack [GEN-008 (app_how_to): candidate]; slots {}; pending_confirmation none; counters: low_conf_streak 3, clarify_attempts 2; turns_since_resolution 5; escalation_proximity 0.80 |
| Decision point | ESC-003.a fires: secondary-layer confidence 0.38, 0.33 and 0.30 are each below the 0.40 floor on three consecutive customer turns (esc003_consecutive_turns 3). Smoothed sentiment is -0.30 and the raw scores are above -0.70, so ESC-004 is not near. |

### T6 | Agent

> I'm sorry, I haven't been able to understand what you need, and I don't want to keep you going in circles. I'm bringing in a colleague from our support team who can help directly.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.29 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SYS-01 (ladder: clarify then escalate), GR-OUT-04 (one apology, then the action) |
| KB / tools | KB: KB-ESC-020@1.0.0 (0.66); retrieval confidence 0.66; decision answer<br>router: queue=General Support (24x7, open); team_plain=support team; no wait estimate supplied |
| Action | escalate: ESC-003 warm handoff; the sentence says plainly that the need was not understood and that the colleague will help directly |
| Generation | hybrid `TPL-ESC-HANDOFF-WARM/could_not_understand@1.0.0` (language en); patterns: P1, P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth anonymous; turn_count 6; topic_stack [GEN-008 (app_how_to): candidate]; slots {}; pending_confirmation none; counters: low_conf_streak 3, clarify_attempts 2; turns_since_resolution 6; escalation_proximity 0.80 |

### E1 | System event

> A General Support colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T5.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth anonymous; turn_count 6; topic_stack [GEN-008 (app_how_to): candidate]; slots {}; pending_confirmation none; counters: low_conf_streak 3, clarify_attempts 2; turns_since_resolution 6; escalation_proximity 0.80 |

### T7 | Agent

> This is Sameer from our support team. They have the details of the problem you have in the app and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.29 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Sameer (synthetic); team_plain=support team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth anonymous; turn_count 7; topic_stack [GEN-008 (app_how_to): candidate]; slots {}; pending_confirmation none; counters: low_conf_streak 3, clarify_attempts 2; turns_since_resolution 7; escalation_proximity 0.80 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 7 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.10, -0.25, -0.40]; final smoothed -0.29 |
| Escalation record | ESC-003, sub-rule ESC-003.a, fired at T5; priority P2, queue General Support, SLA under 10 min, handoff mode warm, cancellable customer_or_recovery; secondary triggers: none; result: warm handoff accepted by General Support at E1 |
| CSAT / check-in | Not asked now: the survey follows after the human closes the conversation. |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | null (anonymous conversation; the human's own tools resolve identity) |
| 2 | Auth level | level anonymous; level_at_trigger anonymous |
| 3 | Intent history | GEN-008 > app_how_to 0.38 first at T1; GEN-004 > chit_chat 0.33 first at T3; GEN-008 > app_how_to 0.30 first at T5 |
| 4 | Entities collected (masked) | none collected |
| 5 | Conversation summary | Anonymous chat. The customer wrote three vague messages about something in the app that does not work. Two different clarification questions were asked; the intent stayed below the floor each time (GEN-008 app_how_to at 0.38 and 0.30, an unclear 0.33 in between). No specific problem was identified and nothing was guessed. |
| 6 | Sentiment trajectory | raw [-0.10, -0.25, -0.40]; current -0.29; emotions: confusion, frustration; sarcasm_suspected false |
| 7 | Actions already taken | none |
| 8 | Escalation trigger and reason | trigger_id ESC-003; rule_id ESC-003.a; priority P2; source system; secondary []; reason_text: Intent confidence below 0.40 on three consecutive customer turns.; evidence_turns [T1, T3, T5] |

Envelope: priority P2; queue General Support; handoff_mode warm; language en; channel chat; complete true; missing_fields []; versions.prompt_version sp-1.0.0+518d5a1e.n000000.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T6 |
| P2 | Progressive Disclosure | shown at T2 |
| P3 | Confirmation-Before-Action | not applicable: no action that changes account state was reached |
| P4 | Graceful Degradation | shown at T4, T6 |
| P5 | Context Carry-Over | shown at T6, T7 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 4 agent messages, no two consecutive ones identical, no text sent three times | T2, T4, T6 |
| AP2 | Information Dump | absent: longest agent message is 49 words (cap `atk_output_max_words`); one concept per message | T2, T4 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T2, T4 |
| AP4 | Premature Escalation | absent: escalation only at the third consecutive turn below the floor (esc003_consecutive_turns), after two different clarification replies | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T4, T6 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); no account-specific request was identified | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 0 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | none |
