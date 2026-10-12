# conv-22: Priya: a fee complaint, an ombudsman question that is not a legal threat, and an ESC-008 handoff

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A customer complains about a fee nobody explained, verifies, registers the complaint, and then asks how to approach the ombudsman and by what date. The word ombudsman is not a legal threat, so ESC-002 does not fire; the filing deadline is a known unknown, so ESC-008 sends her to the Compliance Helpdesk. |
| Persona | Priya (Young Professional) |
| Channel | chat |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | CMP-001, CMP-003 |
| Guardrails exercised | GR-OUT-03, GR-OUT-05, GR-REG-03, GR-REG-08, GR-REG-16, GR-REG-18, GR-REG-19, GR-SEC-R2, GR-SEC-R5 |
| Escalation outcome | ESC-008 fired at T8 (P1, Compliance Helpdesk): regulatory question with an uncertain answer; human accepted. ESC-002 not fired (near-miss, checked at T8) |
| Escalation IDs | ESC-008 |
| Priority | P1 |
| Adversarial vectors | none |
| Security rules exercised | R2, R5 |
| Patterns shown | P1, P2, P3, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP6, AP7, AP8 |
| Coverage tags | CMP-001 complaint with grievance route by the second agent turn (GR-REG-03), correct non-escalation near-miss (ombudsman_info is not a legal threat), ESC-008 regulatory-uncertain handoff (D-43), KB gap KB-ESC-019, complaint registration after soft confirmation |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-CMP-EMPATHY-FIRST, TPL-CMP-GRIEVANCE-INFO, TPL-ACT-CONFIRM, TPL-ACT-DONE, TPL-ESC-HANDOFF-WARM, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-REG-002, KB-POL-003, KB-ESC-005, KB-POL-007, KB-ESC-019, KB-ESC-008 |
| Tools called | create_complaint |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | The grievance route is given by the second agent turn, a question about the ombudsman does not fire the legal-threat escalation, and an ombudsman deadline the KB does not hold is never guessed: the customer is told what is known and a compliance colleague confirms the rest. |

Setup: Priya, Mumbai, on the web chat, anonymous. Session time is 16:40 IST, inside the Compliance Helpdesk hours (08:00 to 22:00 IST).

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I was charged a fee on my account that nobody told me about. I want to complain.

| Field | Value |
|---|---|
| NLU | intent `CMP-001` 0.90 (tertiary charges_and_fees); runner-up `CMP-003` 0.30; entities: complaint_category=charges_and_fees; language: en 0.99 |
| Sentiment | raw -0.50, smoothed -0.50, confidence 0.85; emotions: frustration 0.50 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 and GR-REG-08 (CMP-001 needs otp_verified; anonymous), GR-REG-03 (grievance information is due by the second agent turn: complaint detected) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [CMP-001 (charges_and_fees): active]; slots {complaint_category=charges_and_fees (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. Being charged a fee that nobody explained is frustrating. I want to look into this for you straight away. So that I can open your records, please complete the secure verification step I've opened.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.50 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SEC-R2, GR-SEC-R5 (code only in the secure widget) |
| KB / tools | KB: KB-REG-002@1.0.0 (0.84), KB-POL-003@1.0.0 (0.78); retrieval confidence 0.84; decision answer |
| Action | transfer: to the authentication flow; acknowledgement comes before the request to verify (Empathy-First) |
| Generation | llm-guided `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-CMP-EMPATHY-FIRST/needs_verification_first@1.0.0` (language en); patterns: P1; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [CMP-001 (charges_and_fees): active]; slots {complaint_category=charges_and_fees (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 2; escalation_proximity 0.00 |

### E1 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified. No code passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > RESPOND; auth otp_verified; turn_count 2; topic_stack [CMP-001 (charges_and_fees): active]; slots {complaint_category=charges_and_fees (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Agent

> Here is how I can take this forward: I can register a formal complaint for you now and give you its reference, I can ask for it to be taken up by a senior colleague, or I can request a callback. You also have the right to take a complaint further under the RBI's ombudsman scheme if the bank does not resolve it. Which would you like me to do?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.50 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-03 (grievance information at the second agent turn), GR-REG-19 (complaint record-keeping), GR-OUT-05 (no outcome promised) |
| KB / tools | KB: KB-REG-002@1.0.0 (0.90), KB-ESC-005@1.0.0 (0.80); retrieval confidence 0.90; decision answer |
| Action | respond: the grievance route and the right to take it further, in the second agent turn |
| Generation | template `TPL-CMP-GRIEVANCE-INFO/route@1.0.0` (language en); patterns: P1, P2; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 3; topic_stack [CMP-001 (charges_and_fees): active]; slots {complaint_category=charges_and_fees (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 3; escalation_proximity 0.00 |
| Decision point | The ombudsman sentence in this template is the KB-REG-002 duty. It states the right and no time limit, contact or award limit. |

### T4 | Customer

> Register the complaint please.

| Field | Value |
|---|---|
| NLU | intent `CMP-001` 0.93 (tertiary charges_and_fees); runner-up none above 0.20; entities: none |
| Sentiment | raw -0.25, smoothed -0.38, confidence 0.85; emotions: frustration 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > EXECUTE; auth otp_verified; turn_count 4; topic_stack [CMP-001 (charges_and_fees): active]; slots {complaint_category=charges_and_fees (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 4; escalation_proximity 0.00 |

### T5 | Agent

> Before I go ahead, let me confirm. I will register a complaint about a fee that was not explained to you. Details: category charges and fees, fee not explained before it was charged. You will get a reference once it is registered. Shall I go ahead? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.38 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-19 |
| KB / tools | KB: KB-REG-002@1.0.0 (0.84); retrieval confidence 0.84; decision answer |
| Action | confirm: soft confirmation before create_complaint (CMP-001 confirmation is soft) |
| Generation | template `TPL-ACT-CONFIRM/default@1.0.0` (language en); patterns: P3; anti-pattern check: none |
| State | phase EXECUTE > CONFIRM; auth otp_verified; turn_count 5; topic_stack [CMP-001 (charges_and_fees): active]; slots {complaint_category=charges_and_fees (filled)}; pending_confirmation create_complaint (soft), awaiting yes or no; counters: grievance_info_due_turn 2; turns_since_resolution 5; escalation_proximity 0.00 |

### T6 | Customer

> Yes.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.97; active intent `CMP-001` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw -0.10, smoothed -0.24, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth otp_verified; turn_count 6; topic_stack [CMP-001 (charges_and_fees): active]; slots {complaint_category=charges_and_fees (filled)}; pending_confirmation create_complaint, confirmed; counters: grievance_info_due_turn 2; turns_since_resolution 6; escalation_proximity 0.00 |

### T7 | Agent

> That's done: your complaint about the unexplained fee is registered. Your reference is CMP-SYN-2201. The team will review it and update you; I can't promise an outcome or a date.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.24 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no outcome or date promised) |
| KB / tools | KB: KB-POL-007@1.0.0 (0.82), KB-REG-002@1.0.0 (0.80); retrieval confidence 0.82; decision answer<br>tool: `create_complaint`(category=charges_and_fees, description=fee not explained, idempotency_key=set) -> ok: {reference_id: CMP-SYN-2201, status: open} |
| Action | respond: complaint registered with a reference; nothing promised |
| Generation | template `TPL-ACT-DONE/default@1.0.0` (language en); patterns: P1, P2; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 7; topic_stack [CMP-001 (charges_and_fees): active]; slots {complaint_category=charges_and_fees (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 0; escalation_proximity 0.00 |

### T8 | Customer

> Thanks. And if you do not fix it, how do I go to the ombudsman, and by what date do I have to file?

| Field | Value |
|---|---|
| NLU | intent `CMP-003` 0.87 (tertiary ombudsman_info); runner-up `CMP-001` 0.30; entities: topic=ombudsman filing deadline |
| Sentiment | raw -0.15, smoothed -0.19, confidence 0.85; emotions: worry 0.20 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: ESC-002 evaluated: legal_threat false (a question about how the ombudsman route works is CMP-003 ombudsman_info and does not fire), GR-REG-03 |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > ESCALATING; auth otp_verified; turn_count 8; topic_stack [CMP-003 (ombudsman_info): active, CMP-001: resolved]; slots {complaint_id=CMP-SYN-2201 (from history)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 1; escalation_proximity 0.50 |
| Decision point | Near-miss: the word 'ombudsman' is not a legal threat and ESC-002 stays false. The filing deadline is a fact the KB does not hold (KB-ESC-019 lists it as unknown and lists ESC-008), so ESC-008.a fires. |

### T9 | Agent

> You do have the right to approach the ombudsman under the RBI's scheme. I can register your complaint and arrange a senior colleague or a callback. I don't have the ombudsman contact details or time limits to hand, so I will pass your request to a team member who can confirm them. I want to give you an accurate answer here, and I don't have the specifics confirmed. A colleague from our compliance helpdesk team can confirm them, and I'm bringing them into this chat with your question.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.19 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-18 (no guess and no quotation from memory), GR-OUT-03 (grounding on KB-ESC-019), GR-OUT-05 (no deadline stated), GR-REG-19 |
| KB / tools | KB: KB-ESC-019@1.0.0 (0.86), KB-REG-002@1.0.0 (0.82), KB-ESC-008@1.1.0 (0.78); retrieval confidence 0.86; decision escalate_esc_008<br>router: queue=Compliance Helpdesk (open, 08:00-22:00 IST); team_plain=compliance helpdesk team; no wait estimate supplied |
| Action | escalate: ESC-008 warm handoff to Compliance Helpdesk; the known fact (the right to approach the ombudsman) and the unknown (contact, deadline) are stated separately |
| Generation | hybrid `TPL-CMP-GRIEVANCE-INFO/ombudsman_detail_asked@1.0.0` + `TPL-ESC-HANDOFF-WARM/regulatory_uncertain@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 9; topic_stack [CMP-003 (ombudsman_info): active, CMP-001: resolved]; slots {complaint_id=CMP-SYN-2201 (from history)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 2; escalation_proximity 0.85 |
| Decision point | Quoting a filing period from memory is what KB-ESC-008 and GR-REG-18 forbid. The two templates are composed because the gap statement covers the unknown and the handoff template covers the route; the repeated 'pass to a colleague' idea is accepted as the price of verbatim wording. |

### E2 | System event

> A Compliance Helpdesk colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T8.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth otp_verified; turn_count 9; topic_stack [CMP-003 (ombudsman_info): active, CMP-001: resolved]; slots {complaint_id=CMP-SYN-2201 (from history)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 2; escalation_proximity 0.85 |

### T10 | Agent

> This is Divya from our compliance helpdesk team. They have the details of your question about taking the complaint to the ombudsman and the filing deadline and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.19 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Divya (synthetic); team_plain=compliance helpdesk team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth otp_verified; turn_count 10; topic_stack [CMP-003 (ombudsman_info): active, CMP-001: resolved]; slots {complaint_id=CMP-SYN-2201 (from history)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 3; escalation_proximity 0.85 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); the complaint is registered (resolution_status escalated at handoff, A10.1) |
| Messages | 10 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.50, -0.25, -0.10, -0.15]; final smoothed -0.19 |
| Escalation record | ESC-008, sub-rule ESC-008.a, fired at T8 (retrieval_decision escalate_esc_008: the best match is gap entry KB-ESC-019, which lists ESC-008, and the asked fact is in its unknown list); priority P1, queue Compliance Helpdesk, SLA under 10 min, handoff mode warm, cancellable never; secondary triggers: none; result: warm handoff accepted at E2. ESC-002 evaluated at T8 and false. |
| CSAT / check-in | Not asked now: the survey follows after the human closes the conversation (TPL-SRV-CSAT/after_human_ai_part). |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_22 |
| 2 | Auth level | level otp_verified; level_at_trigger otp_verified |
| 3 | Intent history | CMP-001 > charges_and_fees 0.90 first at T1; CMP-001 > charges_and_fees 0.93 first at T4; CMP-003 > ombudsman_info 0.87 first at T8 |
| 4 | Entities collected (masked) | complaint_id=CMP-SYN-2201 (from history) |
| 5 | Conversation summary | Customer complained about a fee she says was not explained to her; the complaint was registered as CMP-SYN-2201. She then asked how to approach the ombudsman and the deadline for filing. The right to approach the ombudsman was stated; the contact and time limit are not in the knowledge base and were not guessed. No outcome or date was promised. |
| 6 | Sentiment trajectory | raw [-0.50, -0.25, -0.10, -0.15]; current -0.19; emotions: frustration, worry; sarcasm_suspected false |
| 7 | Actions already taken | create_complaint at T7: ok, reference CMP-SYN-2201 |
| 8 | Escalation trigger and reason | trigger_id ESC-008; rule_id ESC-008.a; priority P1; source system; secondary []; reason_text: Regulatory question (ombudsman filing deadline) with no confirmed answer in the knowledge base.; evidence_turns [T8] |

Envelope: priority P1; queue Compliance Helpdesk; handoff_mode warm; language en; channel chat; complete true; missing_fields []; versions.prompt_version sp-1.0.0+518d5a1e.n000000.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2, T3, T7 |
| P2 | Progressive Disclosure | shown at T3, T7 |
| P3 | Confirmation-Before-Action | shown at T5 |
| P4 | Graceful Degradation | shown at T9 |
| P5 | Context Carry-Over | shown at T9, T10 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 6 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 88 words (cap `atk_output_max_words`); one concept per message | T3, T9 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T7, T9 |
| AP4 | Premature Escalation | absent: the first escalation came only when a regulatory fact was asked for that the KB cannot give; the complaint itself was handled by the assistant | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2 |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s); CMP-001 needs otp_verified and the session began anonymous | T2 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 1 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T9 |
