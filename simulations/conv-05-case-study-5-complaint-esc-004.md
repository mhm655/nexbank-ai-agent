# conv-05: Case Study 5 re-run: long-running complaint and the ESC-004 decision

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A customer arrives angry about a reversal that was approved and never credited. The brief's own sentiment scores are kept, and they meet the ESC-004 condition. |
| Persona | Rajesh (Business Owner) |
| Channel | app |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | CMP-003 |
| Guardrails exercised | GR-OUT-01, GR-OUT-04, GR-OUT-05, GR-REG-03, GR-REG-08, GR-REG-16, GR-REG-19, GR-SEC-R2 |
| Escalation outcome | ESC-004 fired at T4 (P1, Customer Retention); the recovery score is checked at T6 (exactly -0.40, recovering) but the customer asks for the escalation, so it stays; human accepted |
| Escalation IDs | ESC-004 |
| Priority | P1 |
| Adversarial vectors | none |
| Security rules exercised | R2 |
| Patterns shown | P1, P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP5, AP6, AP7, AP8 |
| Coverage tags | case study re-run, ESC-004 fired on the brief's own scores, grievance route within 2 agent turns, recovery score checked at the -0.40 boundary (recovering) and the customer keeps the handoff |
| Case study | Case Study 5 (brief pp.53-54) |
| Templates used | TPL-GEN-GREETING, TPL-CMP-EMPATHY-FIRST, TPL-CMP-GRIEVANCE-INFO, TPL-ESC-HANDOFF-WARM, TPL-ESC-WAIT-UPDATE, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-ESC-005, KB-REG-002, KB-POL-007 |
| Tools called | get_complaint_status |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | Empathy comes before verification, the open complaint is found without asking for its reference, the grievance route is given by the second agent turn, no credit time is promised, and two consecutive scores below -0.70 escalate to a human even though the customer starts to calm down. |

Setup: carry_over.open_tickets holds one open complaint for this customer (an incorrect debit, reversal approved, credit pending).

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Your bank is terrible. I've been trying to get my issue resolved for 3 weeks!

| Field | Value |
|---|---|
| NLU | intent `CMP-003` 0.79 (tertiary repeat_unresolved); runner-up `CMP-001` 0.66; entities: none; language: en 0.98 |
| Sentiment | raw -0.90, smoothed -0.90, confidence 0.88; emotions: anger 0.80, frustration 0.90 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 and GR-REG-08 (redirect: the request needs otp_verified and the session is anonymous), GR-REG-03 (grievance information due within grievance_info_max_turns agent turns) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [CMP-003: active]; slots {}; pending_confirmation none; counters: neg_sentiment_streak 1; turns_since_resolution 1; escalation_proximity 0.60 |
| Decision point | Pair 4: CMP-003 against CMP-001 with a gap of 0.13. The repeat cue ('3 weeks') together with an open complaint in carry_over decides CMP-003 without a question. First score below -0.70: streak 1, no trigger yet. |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. I'm sorry you've been chasing this for three weeks; that is not the experience we want for you. I want to look into this for you straight away. So that I can open your records, please complete the secure verification step I've opened.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.90 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure in the first reply), GR-OUT-04 (acknowledgement before the verification request) |
| KB / tools | KB: KB-ESC-005@1.0.0 (0.82), KB-REG-002@1.0.0 (0.80); retrieval confidence 0.82; decision answer |
| Action | apologise: one specific apology, then the next step (verification so the complaint can be opened) |
| Generation | hybrid (llm-guided structure: Acknowledge slot written by the model, the rest locked) `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-CMP-EMPATHY-FIRST/needs_verification_first@1.0.0` (language en); patterns: P1, P2; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [CMP-003: active]; slots {}; pending_confirmation none; counters: neg_sentiment_streak 1; turns_since_resolution 2; escalation_proximity 0.60 |

### E1 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified. No code passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > RESPOND; auth otp_verified; turn_count 2; topic_stack [CMP-003: active]; slots {}; pending_confirmation none; counters: neg_sentiment_streak 1; turns_since_resolution 2; escalation_proximity 0.60 |

### T3 | Agent

> Thank you for verifying; I have your open complaint in front of me now. Let me help put this right. I've found complaint CMP-SYN-78901 about an incorrect debit of INR 8,500: the reversal was approved on 27 Sep 2026 and the credit is still showing as pending. The record gives no date for the credit, so I won't guess one. Here is how I can take this forward: I can register a formal complaint for you now and give you its reference, I can ask for it to be taken up by a senior colleague, or I can request a callback. You also have the right to take a complaint further under the RBI's ombudsman scheme if the bank does not resolve it. Which would you like me to do?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.90 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-03 (grievance route given in time), GR-OUT-05 (no date: the tool returned none), GR-OUT-01 (amount and date equal the tool values) |
| KB / tools | KB: KB-REG-002@1.0.0 (0.87), KB-ESC-005@1.0.0 (0.84), KB-POL-007@1.0.0 (0.78); retrieval confidence 0.87; decision answer<br>tool: `get_complaint_status`(latest open complaint (defaulted from history)) -> ok: {complaint_ref: CMP-SYN-78901, issue: incorrect debit, amount: INR 8,500, raised_on: 20 Sep 2026, status: reversal approved on 27 Sep 2026; credit pending, expected_date: none} |
| Action | respond: complaint read from the system of record without asking for its reference; grievance route given on the second agent turn after the complaint |
| Generation | hybrid (llm-guided structure: Acknowledge slot written by the model, the rest locked) `TPL-CMP-EMPATHY-FIRST/four_steps@1.0.0` + `TPL-CMP-GRIEVANCE-INFO/route@1.0.0` (language en); patterns: P1, P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 3; topic_stack [CMP-003: active]; slots {complaint_id=CMP-SYN-78901 (defaulted from history); amount=INR 8,500 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 1; turns_since_resolution 3; escalation_proximity 0.60 |
| Decision point | The brief's agent asks for the complaint reference (turn 2). The customer has exactly one open complaint, so it is defaulted from history (CMP-002 note, Context Carry-Over). The message is long because the grievance route is due on this turn (GR-REG-03); it still carries one topic. |

### T4 | Customer

> That's the one. A wrong debit of 8500 that your people promised to reverse two weeks ago! Escalate it.

| Field | Value |
|---|---|
| NLU | intent `CMP-003` 0.90 (tertiary escalate_existing); runner-up `CMP-002` 0.40; entities: amount=INR 8,500, complaint_id=CMP-SYN-78901 |
| Sentiment | raw -0.85, smoothed -0.88, confidence 0.90; emotions: anger 0.80, frustration 0.80 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-REG-19 (complaint record kept for quarterly reporting) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INTENT_DETECT > ESCALATING; auth otp_verified; turn_count 4; topic_stack [CMP-003: active]; slots {complaint_id=CMP-SYN-78901 (defaulted from history); amount=INR 8,500 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 2; turns_since_resolution 4; escalation_proximity 0.85 |
| Decision point | ESC-004.a fires: raw scores -0.90 and -0.85 on two consecutive customer turns, both strictly below escalation_sentiment_threshold, both with sentiment confidence at or above sentiment_turn_confidence_min. These are the brief's own scores (triggers.md section 3.4 note). The customer also asks for the escalation, which is what CMP-003 escalate_existing does. |

### T5 | Agent

> A reversal approved two weeks ago that still has not reached you is a delay you should not have had. A colleague from our customer care team is the right person for this, and I'm bringing them into this chat. They'll have the full details, so you won't need to repeat yourself. The current estimate is about 3 minutes; it is an estimate, and I'll stay here until they join. I've noted complaint CMP-SYN-78901, the approved reversal and the pending credit for them.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.88 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no credit time or outcome promised; the wait is a router estimate), GR-OUT-04 (one acknowledgement, no second apology) |
| KB / tools | router: queue=Customer Retention (open); team_plain=customer care team; queue_wait=about 3 minutes (platform forecast, stated as an estimate) |
| Action | escalate: ESC-004 handoff to Customer Retention; the agent stays and keeps the package current |
| Generation | hybrid `TPL-ESC-HANDOFF-WARM/standard_with_wait@1.0.0` (language en); patterns: P1, P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 5; topic_stack [CMP-003: active]; slots {complaint_id=CMP-SYN-78901 (defaulted from history); amount=INR 8,500 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 2; turns_since_resolution 5; escalation_proximity 0.85 |
| Decision point | Brief turn 6 says the amount will be credited 'within 24 hours' and that an SMS will follow. No tool returned a date or a notification, so neither is said (D-09, False Confidence). |

### T6 | Customer

> Finally someone who actually reads the complaint! Yes please escalate this.

| Field | Value |
|---|---|
| NLU | intent `CMP-003` 0.86 (tertiary escalate_existing); runner-up none above 0.20; entities: none |
| Sentiment | raw -0.40, smoothed -0.64, confidence 0.85; emotions: frustration 0.40; sarcasm probability 0.30 (below 0.40: literal score used) |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth otp_verified; turn_count 6; topic_stack [CMP-003: active]; slots {complaint_id=CMP-SYN-78901 (defaulted from history); amount=INR 8,500 (from the record)}; pending_confirmation none; counters: all 0; turns_since_resolution 6; escalation_proximity 0.70 |
| Decision point | Recovery check (routing-and-handoff.md section 9.2): the score part of the ESC-004 recovery condition is non-strict (D-200): the latest raw score is at or above esc004_cancel_sentiment_min (-0.40). The score is exactly -0.40, so it counts as recovering, which is the brief's own "-0.4 (recovering)" reading (Case Study 5, brief p.53, turn 5). But the credit has not arrived (no concrete resolution yet) and, above all, the customer is asking for the escalation, so the customer does not agree to withdraw it. TPL-ESC-DEESCALATION-CHECK is not sent to a customer who has just asked for the handoff, and the handoff stays. |

### T7 | Agent

> Thanks, I've added that for my colleague: you want the pending reversal taken up as a priority. You won't need to explain it again.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.64 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | hold: the wait update adds information (the customer's wish) and is the first one in this wait |
| Generation | template `TPL-ESC-WAIT-UPDATE/noted@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 7; topic_stack [CMP-003: active]; slots {complaint_id=CMP-SYN-78901 (defaulted from history); amount=INR 8,500 (from the record)}; pending_confirmation none; counters: all 0; turns_since_resolution 7; escalation_proximity 0.70 |

### E2 | System event

> A Customer Retention colleague accepts the conversation.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth otp_verified; turn_count 7; topic_stack [CMP-003: active]; slots {complaint_id=CMP-SYN-78901 (defaulted from history); amount=INR 8,500 (from the record)}; pending_confirmation none; counters: all 0; turns_since_resolution 7; escalation_proximity 0.70 |

### T8 | Agent

> This is Farhan from our customer care team. They have the details of your complaint about the incorrect debit and its pending reversal and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.64 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Farhan (synthetic); team_plain=customer care team |
| Action | escalate: handoff complete; the agent stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.1.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth otp_verified; turn_count 8; topic_stack [CMP-003: active]; slots {complaint_id=CMP-SYN-78901 (defaulted from history); amount=INR 8,500 (from the record)}; pending_confirmation none; counters: all 0; turns_since_resolution 8; escalation_proximity 0.70 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated (A10.1). Sentiment moved from -0.90 to -0.40 before the human joined. |
| Messages | 8 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.90, -0.85, -0.40]; final smoothed -0.64 |
| Escalation record | ESC-004, sub-rule or basis ESC-004.a, fired at T4; priority P1, queue Customer Retention, SLA under 5 min, handoff mode warm, cancellable customer_or_recovery; secondary triggers: none; result: warm handoff accepted by Customer Retention at E2; the de-escalation check was not sent |
| CSAT / check-in | Asked after the human conversation ends (two-part CSAT). No in-conversation check-in: none is sent after an escalation has fired. |

### Deviations from the brief's case study (each one deliberate)

| Brief | This specification | Why |
|---|---|---|
| Turn 2: asks for the complaint reference | The single open complaint is defaulted from history after verification | CMP-002 note; Context Carry-Over |
| No verification shown | OTP step in the widget, after the acknowledgement | Complaint details are account-specific (rule 2, GR-REG-08) |
| Turn 4: the agent 'escalates to our operations team' itself and carries on | ESC-004 fires on the brief's scores and a Customer Retention colleague takes over | A6: two turns below -0.7; the agent has no tool that prioritises a reversal |
| Turn 6: 'credited ... within 24 hours' and an SMS confirmation | No date and no notification promised | D-09; no tool returned either |
| Turn 4: 'a 2-week delay after approval is unacceptable' | One acknowledgement of the delay without a verdict on fault | Tone guide: own the delay, do not debate fault |
| Outcome: resolved by the AI at -0.4 | Handed to a human at -0.40 | The score -0.40 counts as recovering (condition at or above -0.40, D-200), as in the brief; the customer said "Yes please escalate this", so there is nothing to withdraw, and the agent has no tool that credits the reversal or sets a timeline |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_05 |
| 2 | Auth level | level otp_verified; level_at_trigger otp_verified |
| 3 | Intent history | CMP-003 > repeat_unresolved 0.79 first at T1; CMP-003 > escalate_existing 0.90 first at T4; CMP-003 > escalate_existing 0.86 first at T6 |
| 4 | Entities collected (masked) | complaint_id=CMP-SYN-78901 (defaulted from history); amount=INR 8,500 (from the record) |
| 5 | Conversation summary | Customer has an open complaint CMP-SYN-78901 about an incorrect debit of INR 8,500. The record shows the reversal approved on 27 Sep 2026 and the credit still pending, with no expected date. He has been chasing it for about three weeks and asked for it to be escalated. He was given the grievance route and told a colleague is joining. No credit date was promised. |
| 6 | Sentiment trajectory | raw [-0.90, -0.85, -0.40]; current -0.64; emotions: anger, frustration; sarcasm_suspected false |
| 7 | Actions already taken | none |
| 8 | Escalation trigger and reason | trigger_id ESC-004; rule_id ESC-004.a; priority P1; source system; secondary []; reason_text: Two consecutive customer turns scored below the sentiment threshold (-0.90, -0.85) on an unresolved complaint.; evidence_turns [T4] |

Envelope: priority P1; queue Customer Retention; handoff_mode warm; language en; channel app; complete true; missing_fields []; versions.prompt_version sp-1.1.0+1527a050.n000000.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2, T3, T5 |
| P2 | Progressive Disclosure | shown at T2, T3 |
| P3 | Confirmation-Before-Action | not applicable: no action that changes account state was reached |
| P4 | Graceful Degradation | shown at T3, T5, T7 |
| P5 | Context Carry-Over | shown at T5, T7, T8 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 5 agent messages, no two consecutive ones identical, no text sent three times | T5, T7 |
| AP2 | Information Dump | absent: longest agent message is 130 words (cap `atk_output_max_words`); one concept per message | T2, T3, T5, T8 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn | T2, T3, T5, T7 |
| AP4 | Premature Escalation | absent: escalation only on ESC-004 at T4 | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2, T3, T5 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); never while the auth level already met the intent's level | T5, T8 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | T2, T3, T5, T7 |
| AP8 | Knowledge Hallucination | absent: 6 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T3 |

