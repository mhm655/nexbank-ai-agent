# conv-28: Priya: a status lookup that fails twice and the ESC-014 handoff

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A signed-in customer asks where her NEFT transfer is. The status lookup times out and fails again on its single retry, so the assistant says plainly that it cannot see the record, guesses nothing, and hands over to technical support. |
| Persona | Priya (Young Professional) |
| Channel | app |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | TXN-004, GEN-003 |
| Guardrails exercised | GR-OUT-03, GR-OUT-05, GR-REG-16, GR-SYS-01 |
| Escalation outcome | ESC-014 fired at T2 (P2, Technical Support) after the single read retry failed; human accepted |
| Escalation IDs | ESC-014 |
| Priority | P2 |
| Adversarial vectors | none |
| Security rules exercised | none |
| Patterns shown | P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP7, AP8 |
| Coverage tags | tool failure (ESC-014 path): one retry on a read, no guessed value, no cached figure, honest handoff, wait estimate from the router |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-ACT-FAILED, TPL-ESC-HANDOFF-WARM, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-TRB-009, KB-TRB-004, KB-ESC-010 |
| Tools called | get_txn |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | A read that fails twice produces an honest 'I cannot see it', no status, date or amount is invented, and the handoff goes to the right queue with the details already gathered. |

Setup: Priya is signed in (otp_verified). Session time is 14:10 IST; Technical Support runs 08:00 to 22:00 IST. The synthetic NEFT status service times out on both attempts.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Where is my NEFT transfer to my landlord? The reference ends 5532 and it went to Synthetic Bank.

| Field | Value |
|---|---|
| NLU | intent `TXN-004` 0.89 (tertiary neft); runner-up `TXN-001` 0.35; entities: neft_ref=ending 5532 (masked), beneficiary_bank=Synthetic Bank; language: en 0.99 |
| Sentiment | raw -0.10, smoothed -0.10, confidence 0.85; emotions: worry 0.20 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > EXECUTE; auth otp_verified; turn_count 1; topic_stack [TXN-004 (neft): active]; slots {neft_ref=ending 5532 (filled); beneficiary_bank=Synthetic Bank (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. I'm not able to see the status of that payment right now, and I don't want to guess. I can bring in a colleague who can check another way. Shall I?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-OUT-03 (no guessed status), GR-OUT-05 (no timeline), GR-SYS-01 (fail-closed ladder: safe wording, then escalate) |
| KB / tools | KB: KB-TRB-009@1.0.0 (0.90), KB-TRB-004@1.0.0 (0.80); retrieval confidence 0.90; decision answer<br>tool: `get_txn`(neft_ref=ending 5532, beneficiary_bank=Synthetic Bank) -> error: timeout (attempt 1)<br>tool: `get_txn`(neft_ref=ending 5532, beneficiary_bank=Synthetic Bank) -> error: timeout (attempt 2, the single allowed retry) |
| Action | escalate: ESC-014.a after the single retry; the failure is stated plainly, a colleague is offered, and no value is guessed or taken from a cache |
| Generation | template `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-ACT-FAILED/read_failed@1.1.0` (language en); patterns: P4; anti-pattern check: none |
| State | phase EXECUTE > ESCALATING; auth otp_verified; turn_count 2; topic_stack [TXN-004 (neft): active]; slots {neft_ref=ending 5532 (filled); beneficiary_bank=Synthetic Bank (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.50 |
| Decision point | TPL-ACT-FAILED/read_failed states the failure and offers a colleague. ESC-014.a has already fired, so the handoff is prepared in parallel and the customer can still decline it (cancellable customer_or_recovery). The 'Ok' at T3 accepts the offer; its question about the wait is answered at T4 by TPL-ESC-HANDOFF-WARM/system_error. |

### T3 | Customer

> Ok. How long will that take?

| Field | Value |
|---|---|
| NLU | intent `GEN-003` 0.58 (tertiary implicit_request); runner-up `TXN-004` 0.50; entities: none |
| Sentiment | raw -0.15, smoothed -0.13, confidence 0.85; emotions: impatience 0.20 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth otp_verified; turn_count 3; topic_stack [TXN-004 (neft): active]; slots {neft_ref=ending 5532 (filled); beneficiary_bank=Synthetic Bank (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.50 |
| Decision point | A question about the wait, not a request for a different human: no human_request_count increment. |

### T4 | Agent

> I can't reach those records right now, and I don't want to guess. I'm connecting you to a colleague from our support team who can check another way. They'll have what you've told me.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.13 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no timeline: no wait estimate was supplied, so none is given) |
| KB / tools | KB: KB-TRB-009@1.0.0 (0.88), KB-ESC-010@1.0.0 (0.70); retrieval confidence 0.88; decision answer<br>router: queue=Technical Support (open, 08:00-22:00 IST); team_plain=support team; no wait estimate supplied |
| Action | escalate: ESC-014 warm handoff to Technical Support |
| Generation | hybrid `TPL-ESC-HANDOFF-WARM/system_error@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 4; topic_stack [TXN-004 (neft): active]; slots {neft_ref=ending 5532 (filled); beneficiary_bank=Synthetic Bank (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.50 |

### E1 | System event

> A Technical Support colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T2.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth otp_verified; turn_count 4; topic_stack [TXN-004 (neft): active]; slots {neft_ref=ending 5532 (filled); beneficiary_bank=Synthetic Bank (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.50 |

### T5 | Agent

> This is Lata from our support team. They have the details of the NEFT transfer whose status could not be read and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.13 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Lata (synthetic); team_plain=support team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.1.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth otp_verified; turn_count 5; topic_stack [TXN-004 (neft): active]; slots {neft_ref=ending 5532 (filled); beneficiary_bank=Synthetic Bank (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 5; escalation_proximity 0.50 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 5 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.10, -0.15]; final smoothed -0.13 |
| Escalation record | ESC-014, sub-rule ESC-014.a, fired at T2; priority P2, queue Technical Support, SLA under 10 min, handoff mode warm, cancellable customer_or_recovery; secondary triggers: none; result: warm handoff accepted by Technical Support at E1 |
| CSAT / check-in | Not asked now: the survey follows after the human closes the conversation. |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_28 |
| 2 | Auth level | level otp_verified; level_at_trigger otp_verified |
| 3 | Intent history | TXN-004 > neft 0.89 first at T1; GEN-003 > implicit_request 0.58 first at T3 |
| 4 | Entities collected (masked) | neft_ref=ending 5532 (filled); beneficiary_bank=Synthetic Bank (filled) |
| 5 | Conversation summary | Customer asked for the status of an NEFT transfer to her landlord (reference ending 5532, beneficiary Synthetic Bank). The status lookup timed out twice (one attempt and the single allowed retry). No status was given or guessed. She was told a colleague would check another way. |
| 6 | Sentiment trajectory | raw [-0.10, -0.15]; current -0.13; emotions: worry; sarcasm_suspected false |
| 7 | Actions already taken | get_txn at T2: error timeout (2 attempts); no write attempted |
| 8 | Escalation trigger and reason | trigger_id ESC-014; rule_id ESC-014.a; priority P2; source system; secondary []; reason_text: Read tool failed after the single retry.; evidence_turns [T2] |

Envelope: priority P2; queue Technical Support; handoff_mode warm; language en; channel app; complete true; missing_fields []; versions.prompt_version sp-1.1.0+1527a050.n000000.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no customer message carried a problem or a negative emotion |
| P2 | Progressive Disclosure | not shown: no multi-layer answer was possible |
| P3 | Confirmation-Before-Action | not applicable: no action that changes account state was reached |
| P4 | Graceful Degradation | shown at T2, T4 |
| P5 | Context Carry-Over | shown at T4, T5 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 3 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 36 words (cap `atk_output_max_words`); one concept per message | T2 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T2, T4 |
| AP4 | Premature Escalation | absent: escalation only after the one allowed retry also failed (component-interfaces.md row 7); a slow but successful read would not have fired | none at risk |
| AP5 | Empathy Bypass | not at risk: no customer message carried a problem or a negative emotion | T2 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); the session started at otp_verified | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 0 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T4 |
