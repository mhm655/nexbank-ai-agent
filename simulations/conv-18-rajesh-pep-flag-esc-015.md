# conv-18: Rajesh: a flagged customer, a generic answer, and a discreet handoff that never says why

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A signed-in customer whose profile carries an internal PEP flag asks a generic product question, which the assistant answers while a silent due-diligence record is opened. His next question is account-specific, so a discreet live handoff follows. The customer is never told. |
| Persona | Rajesh (Business Owner) |
| Channel | chat |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | PRD-002, TXN-001 |
| Guardrails exercised | GR-OUT-03, GR-REG-01, GR-REG-08, GR-REG-11, GR-REG-16, GR-REG-17, GR-SEC-R6 |
| Escalation outcome | ESC-015.a record created silently at T1 (every contact by an identified flagged customer); ESC-015.b live discreet handoff at T3 (account-specific request); human accepted |
| Escalation IDs | ESC-015 |
| Priority | P1 |
| Adversarial vectors | none |
| Security rules exercised | R6 |
| Patterns shown | P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP6, AP7, AP8 |
| Coverage tags | PEP flag (ESC-015): record on every identified flagged contact, live discreet handoff only when account-specific, never tip off (D-164), generic information still served, GR-REG-11 and GR-REG-17 |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-GEN-DISCLOSE-MORE, TPL-ESC-HANDOFF-DISCREET, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-PRD-005, KB-FAQ-005, KB-ESC-018, KB-POL-008, KB-ESC-009, KB-REG-004 |
| Tools called | get_profile_masked |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | A generic question from a flagged customer is answered normally while the record is opened, an account-specific request gets a neutral live handoff, nothing the customer sees mentions a flag, a review or a reason, and the flag is read from the customer record, not from anything he says. |

Setup: Rajesh is signed in (otp_verified) and identified. His customer record carries a PEP flag set by the bank's compliance process (a record attribute read through get_profile_masked; the flag is never shown or stated, and nothing he says sets or clears it, GR-REG-11). Session time is 11:20 IST.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Hello, what do I need for a NexHome Loan?

| Field | Value |
|---|---|
| NLU | intent `PRD-002` 0.88 (tertiary home_loan_criteria); runner-up `PRD-001` 0.30; entities: loan_type=home; language: en 0.99 |
| Sentiment | raw 0.10, smoothed 0.10, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-REG-11 (customer_identified and pep_flag, both read from the profile above: ESC-015.a opens the record and the parallel due-diligence case; no customer-visible effect), GR-REG-17 (thresholds, tone and wording are the same as for every customer) |
| KB / tools | tool: `get_profile_masked`() -> ok: {first_name: Rajesh, accounts: [savings ending 6318], pep_flag: true (internal attribute; never rendered, never stated)} (read once for the identified, signed-in session before any guardrail uses the flag; the flag comes from the record, never from the message) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > RESPOND; auth otp_verified; turn_count 1; topic_stack [PRD-002 (home_loan_criteria): active]; slots {loan_type=home (filled)}; pending_confirmation none; counters: pep_case_open 1; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | ESC-015.a is literal (D-164): the record is created because the customer is identified and the flag is true. It is a silent case, with no handoff message and no change to the reply. A generic information request is answered by the assistant. |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. The NexHome Loan starts at 8.25% and runs up to 30 years, with up to 90% LTV. It needs CIBIL above 700, property valuation and a legal check. Fees and terms are in the loan offer documents, and a loan specialist can walk you through them. Would you like more detail on an instalment illustration or the loan specialist?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-REG-01 (rate with the pointer to fees and terms), GR-REG-17 (identical treatment), GR-OUT-03 |
| KB / tools | KB: KB-PRD-005@1.0.0 (0.90), KB-FAQ-005@1.0.0 (0.84), KB-ESC-018@1.0.0 (0.76), KB-POL-008@1.0.0 (0.70); retrieval confidence 0.90; decision answer |
| Action | respond: generic product information, same wording as for any customer; the silent record exists in the background |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-GEN-DISCLOSE-MORE/layer_1_2@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 2; topic_stack [PRD-002 (home_loan_criteria): active]; slots {loan_type=home (filled)}; pending_confirmation none; counters: pep_case_open 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | The reply does not mention enhanced checks, a review, or a different process. KB-ESC-009: keep the tone neutral and do not reveal the flag. |

### T3 | Customer

> Good. Can you check where my last transfer to my supplier is? What is its status?

| Field | Value |
|---|---|
| NLU | intent `TXN-001` 0.85 (tertiary by_description); runner-up `TXN-004` 0.52; entities: description=last transfer to supplier |
| Sentiment | raw 0.05, smoothed 0.08, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-REG-11 (ESC-015.b: the request is account-specific, so a live discreet handoff is made), GR-REG-08 (identity already verified) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > ESCALATING; auth otp_verified; turn_count 3; topic_stack [TXN-001 (by_description): active, PRD-002: parked]; slots {description=last transfer to supplier (filled)}; pending_confirmation none; counters: pep_case_open 1; turns_since_resolution 3; escalation_proximity 0.70 |
| Decision point | ESC-015.b: the request reads an account (action read), so the live handoff to Enhanced Due Diligence is made. The transaction is not looked up by the assistant. This is the one place where the path differs from a non-flagged customer's: the brief's PEP trigger (A6 p.17, A4.3 p.13) requires it and it gives way to GR-REG-17's identical treatment only for routing, not for tone, thresholds or wording. The mitigation is the neutral wording of T4, the same as for any handoff that names no team. |

### T4 | Agent

> A colleague will help you with this request. I'm bringing them into this chat, and they'll have the details so far, so you won't need to repeat anything.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.08 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-11 (no mention of the flag, the queue name or the reason), GR-SEC-R6 (escalation protocol followed) |
| KB / tools | KB: KB-ESC-009@1.0.0 (0.80), KB-REG-004@1.0.0 (0.72); retrieval confidence 0.80; decision answer<br>router: queue=Enhanced Due Diligence (open, 08:00-22:00 IST); handoff_mode=discreet; customer_visible=false (no team name) |
| Action | escalate: ESC-015.b discreet live handoff; neutral wording only, no team name, no reason, no wait estimate |
| Generation | template `TPL-ESC-HANDOFF-DISCREET/default@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 4; topic_stack [TXN-001 (by_description): active, PRD-002: parked]; slots {description=last transfer to supplier (filled)}; pending_confirmation none; counters: pep_case_open 1; turns_since_resolution 4; escalation_proximity 0.70 |
| Decision point | The wording is the same as for any warm handoff that does not name a team. A message that said 'for compliance reasons' or 'a specialist for senior clients' would tip him off. |

### E1 | System event

> An Enhanced Due Diligence colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T3 (the due-diligence case itself has been open since T1).

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth otp_verified; turn_count 4; topic_stack [TXN-001 (by_description): active, PRD-002: parked]; slots {description=last transfer to supplier (filled)}; pending_confirmation none; counters: pep_case_open 1; turns_since_resolution 4; escalation_proximity 0.70 |

### T5 | Agent

> Mohan from our team has joined and will help you from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.08 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Mohan (synthetic); no team name and no topic line (discreet_or_crisis) |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/discreet_or_crisis@1.1.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth otp_verified; turn_count 5; topic_stack [TXN-001 (by_description): active, PRD-002: parked]; slots {description=last transfer to supplier (filled)}; pending_confirmation none; counters: pep_case_open 1; turns_since_resolution 5; escalation_proximity 0.70 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 5 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.10, 0.05]; final smoothed 0.08 |
| Escalation record | ESC-015, sub-rules ESC-015.a (T1, silent_case, record and parallel due-diligence case) and ESC-015.b (T3, discreet live handoff), priority P1, queue Enhanced Due Diligence, SLA under 5 min, handoff mode discreet, cancellable never; secondary triggers: none; result: discreet handoff accepted at E1; the record was open from T1 |
| CSAT / check-in | Not asked now: the survey follows after the human closes the conversation and only if no security or compliance case bars it (csat-signals.md section 3.1). |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_18 |
| 2 | Auth level | level otp_verified; level_at_trigger otp_verified |
| 3 | Intent history | PRD-002 > home_loan_criteria 0.88 first at T1; TXN-001 > by_description 0.85 first at T3 |
| 4 | Entities collected (masked) | description=last transfer to supplier (filled); loan_type=home (filled) |
| 5 | Conversation summary | Customer asked what a NexHome Loan needs and received the published criteria. He then asked for the status of his last transfer to a supplier, which is account-specific and was handed over without any lookup. Nothing was said to him about a flag or a review. |
| 6 | Sentiment trajectory | raw [0.10, 0.05]; current 0.08; emotions: none; sarcasm_suspected false |
| 7 | Actions already taken | none (profile read at T1 only) |
| 8 | Escalation trigger and reason | trigger_id ESC-015; rule_id ESC-015.a and ESC-015.b; priority P1; source system; secondary []; reason_text: Identified customer with an internal PEP flag; first contact generic (record opened), then an account-specific request (live discreet handoff).; evidence_turns [T1, T3] |

Envelope: priority P1; queue Enhanced Due Diligence; handoff_mode discreet; language en; channel chat; complete true; missing_fields []; versions.prompt_version sp-1.1.0+1527a050.n000000. restricted_notes carries the flag reason, visible to Enhanced Due Diligence only. The customer-facing text never names the flag.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no customer message carried a problem or a negative emotion |
| P2 | Progressive Disclosure | shown at T2 |
| P3 | Confirmation-Before-Action | not applicable: no action that changes account state was reached |
| P4 | Graceful Degradation | shown at T4 |
| P5 | Context Carry-Over | shown at T4, T5 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 3 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 64 words (cap `atk_output_max_words`); one concept per message | T2 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T2, T4 |
| AP4 | Premature Escalation | absent: the generic question at T1 was answered by the assistant with no live handoff; the live handoff came only with the account-specific request (ESC-015.b) | none at risk |
| AP5 | Empathy Bypass | not at risk: no customer message carried a problem or a negative emotion | none at risk |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); the session started at otp_verified and no level above it was needed for the handoff | none |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 4 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T2 |
