# conv-16: Arjun: forex timing and tax-planning questions, and an after-hours advisor callback

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | An NRI in Dubai, signed in to the app late at night India time, asks whether to convert dollars now or wait, what the transfer charges and limits are, and then how much to put in fixed deposits to save tax. The assistant declines the forex and tax advice, states the knowledge gap on charges, and, because the advisory desk is closed, requests a callback. |
| Persona | Arjun (NRI) |
| Channel | app |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | TXN-006, PRD-005, GEN-006 |
| Guardrails exercised | GR-ADV-02, GR-ADV-04, GR-ADV-05, GR-ADV-06, GR-ADV-08, GR-OUT-01, GR-OUT-05, GR-REG-16, GR-SEC-R3 |
| Escalation outcome | ESC-013 accepted at T3 (P1, Wealth Advisory); the queue was closed, so the after-hours rule applied: callback only, case opened for the next opening; callback request placed at T6 |
| Escalation IDs | ESC-013 |
| Priority | P1 |
| Adversarial vectors | none |
| Security rules exercised | R3 |
| Patterns shown | P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP7, AP8 |
| Coverage tags | persona Arjun, information-vs-advice boundary: forex (A4.1) and tax planning (A4.1), TXN-006 charges and limits KB gap (KB-ESC-016), ESC-013 accepted then after-hours callback only (D-122), schedule_callback |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-ADV-FOREX, TPL-ADV-ADVISOR-OFFER, TPL-ADV-ADVISOR-UNAVAILABLE, TPL-ESC-CALLBACK-OFFER, TPL-ADV-TAX, TPL-GEN-CLOSING |
| KB entries cited | KB-ESC-016, KB-POL-001, KB-POL-004, KB-ESC-003, KB-POL-007, KB-REG-011, KB-FAQ-008 |
| Tools called | schedule_callback |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | Currency timing and tax-planning questions are declined with facts only, the charges and limits are stated as unknown with no figure, a transfer is not started, and an accepted advisor request outside hours becomes a callback request with an honest 'request, not a guarantee'. |

Setup: Arjun, Dubai, in the app, signed in (otp_verified). Session time is 23:10 IST on 12 Oct 2026. Wealth Advisory runs 08:00 to 22:00 IST (config/escalation_rules.yaml queue_hours), so it is closed.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Hi. I am an NRI in Dubai. I think the rupee will fall soon, so should I convert my dollars now or wait? Also what are the charges and limits for sending money to my account in India?

| Field | Value |
|---|---|
| NLU | segment 1 `TXN-006` 0.84 (tertiary charges_and_limits_info), segment 2 `PRD-005` 0.88 (tertiary forex_timing_advice); multi_intent set (second intent 0.88 is at or above multi_intent_second_min 0.60); order by mi_rank: TXN-006 (5) before PRD-005 (6), but the advice boundary reply carries both; entities: currency=USD; language: en 0.98 |
| Sentiment | raw 0.00, smoothed 0.00, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-02 (advice classifier 0.86), GR-ADV-04 (market-timing, forex and return-prediction guard), GR-SEC-R3 (no transfer can be started) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > RESPOND; auth otp_verified; turn_count 1; topic_stack [PRD-005 (forex_timing_advice): active, TXN-006 (charges_and_limits_info): queued]; slots {currency=USD (filled)}; pending_confirmation none; counters: multi_intent 1, advice_deflections 1; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. I can't predict where a currency will go or suggest when to buy or sell. I don't have transfer charges or limits to quote, and I can't start a transfer for you. A team member can give you the details. I also can't start a transfer from this chat. For a personal recommendation, a SEBI-registered advisor at NexBank can help. Shall I arrange that for you?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-ADV-04 (no direction or timing), GR-ADV-06, GR-ADV-08 (advisor offered once), GR-SEC-R3 (a transfer is not started), GR-OUT-01 (no charge, limit or rate stated) |
| KB / tools | KB: KB-ESC-016@1.0.0 (0.88), KB-POL-001@1.0.0 (0.86), KB-POL-004@1.0.0 (0.70); retrieval confidence 0.88; decision gap |
| Action | recommend: forex boundary reply with the knowledge-gap statement for charges and limits (nothing quoted), then the advisor offer |
| Generation | template `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-ADV-FOREX/default@1.0.0` + `TPL-ADV-ADVISOR-OFFER/default@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 2; topic_stack [PRD-005 (forex_timing_advice): active, TXN-006 (charges_and_limits_info): queued]; slots {currency=USD (filled)}; pending_confirmation none; counters: multi_intent 1, advice_deflections 1, advisor_offers 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | KB-POL-001, forex: the prohibited form is 'You should buy dollars now as rupee will depreciate'. KB-ESC-016 lists charges, limits, corridors, processing time and any rate as unknown, so none is given and no rate is read out from memory. |

### T3 | Customer

> Yes, connect me with an advisor.

| Field | Value |
|---|---|
| NLU | dialogue act accept_offer 0.96 (advisor offer); active intent `PRD-005` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw 0.00, smoothed 0.00, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-08 (offer accepted: the ESC-013 record is created now) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > ESCALATING; auth otp_verified; turn_count 3; topic_stack [PRD-005 (forex_timing_advice): active, TXN-006 (charges_and_limits_info): queued]; slots {currency=USD (filled)}; pending_confirmation none; counters: multi_intent 1, advice_deflections 1, advisor_offers 1; turns_since_resolution 3; escalation_proximity 0.60 |
| Decision point | ESC-013.a fires on acceptance. The router finds Wealth Advisory closed (08:00 to 22:00 IST; it is 23:10 IST). The after-hours rule for ESC-013 is callback only: no generalist answers an advice question (D-122). |

### T4 | Agent

> Our advisors aren't available right now, and I don't want to give you advice in their place. I can request a callback for you: the next advisory slot after the desk opens at 08:00 IST on 13 Oct 2026. A callback time is a request and may change. Would you like me to request one?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-ADV-08, GR-OUT-05 (a callback time is a request, not a guarantee) |
| KB / tools | KB: KB-ESC-003@1.0.0 (0.70), KB-POL-007@1.0.0 (0.78); retrieval confidence 0.78; decision answer<br>router: queue=Wealth Advisory (closed; hours 08:00-22:00 IST); after_hours rule=callback_only; callback_option=next slot after 08:00 IST on 13 Oct 2026 |
| Action | escalate: ESC-013 record created, case opened for the next opening, callback offered; no advice given by anyone in the meantime |
| Generation | template `TPL-ADV-ADVISOR-UNAVAILABLE/default@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 4; topic_stack [PRD-005 (forex_timing_advice): active, TXN-006 (charges_and_limits_info): queued]; slots {currency=USD (filled)}; pending_confirmation none; counters: multi_intent 1, advice_deflections 1, advisor_offers 1; turns_since_resolution 4; escalation_proximity 0.60 |

### T5 | Customer

> Okay, request a callback.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.94; active intent `CMP-005` (schedule_callback, implied); runner-up: n/a; entities: none |
| Sentiment | raw 0.00, smoothed 0.00, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth otp_verified; turn_count 5; topic_stack [PRD-005 (forex_timing_advice): active, TXN-006 (charges_and_limits_info): queued]; slots {currency=USD (filled)}; pending_confirmation schedule_callback, confirmed; counters: multi_intent 1, advice_deflections 1, advisor_offers 1; turns_since_resolution 5; escalation_proximity 0.60 |

### T6 | Agent

> Your callback request is placed. Reference: CBK-SYN-1601. Requested time: 13 Oct 2026, 08:00 to 10:00 IST. This is a request and the actual time may differ; the full details of our chat go with it.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the window is the tool's, stated as a request) |
| KB / tools | KB: KB-ESC-003@1.0.0 (0.72), KB-POL-007@1.0.0 (0.80); retrieval confidence 0.80; decision answer<br>tool: `schedule_callback`(team=Wealth Advisory, channel=registered contact (masked), idempotency_key=set) -> ok: {callback_reference: CBK-SYN-1601, requested_window: 13 Oct 2026, 08:00 to 10:00 IST} |
| Action | respond: callback request placed; the full conversation goes with it |
| Generation | template `TPL-ESC-CALLBACK-OFFER/placed@1.0.0` (language en); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING > RESPOND; auth otp_verified; turn_count 6; topic_stack [PRD-005 (forex_timing_advice): active, TXN-006 (charges_and_limits_info): queued]; slots {currency=USD (filled)}; pending_confirmation none; counters: multi_intent 1, advice_deflections 1, advisor_offers 1; turns_since_resolution 0; escalation_proximity 0.60 |

### T7 | Customer

> One more thing. How much should I put in tax-saving FDs to reduce my tax?

| Field | Value |
|---|---|
| NLU | intent `PRD-005` 0.92 (tertiary tax_planning_advice); runner-up `PRD-003` 0.44; entities: product=NexFD |
| Sentiment | raw 0.05, smoothed 0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-05 (tax-planning recommendation guard), GR-ADV-02 |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth otp_verified; turn_count 7; topic_stack [PRD-005 (tax_planning_advice): active]; slots {currency=USD (filled)}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (accepted); turns_since_resolution 1; escalation_proximity 0.60 |

### T8 | Agent

> NexFD carries Section 80C benefits, which the product catalogue example puts at up to 1.5L, and TDS is applicable. These are general facts. I can't suggest how much to invest or how to plan your taxes.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-ADV-05 (facts only; no amount, no plan), GR-ADV-08 (no second offer: a callback with the advisory team is already requested) |
| KB / tools | KB: KB-REG-011@1.0.0 (0.88), KB-FAQ-008@1.0.0 (0.80), KB-POL-001@1.0.0 (0.78); retrieval confidence 0.88; decision answer |
| Action | recommend: tax boundary reply; the permitted example fact (KB-POL-001, tax_planning) and no recommendation of how much to invest |
| Generation | template `TPL-ADV-TAX/default@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 8; topic_stack [PRD-005 (tax_planning_advice): active]; slots {currency=USD (filled)}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (accepted); turns_since_resolution 2; escalation_proximity 0.60 |
| Decision point | The caller is an NRI, and tax treatment can differ by residency. No residency-based statement is made, because the KB holds none (KB-REG-011 lists TDS rate and thresholds as not in the brief). |

### T9 | Customer

> Ok, thanks.

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.90 (tertiary thanks); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.20, smoothed 0.11, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth otp_verified; turn_count 9; topic_stack [PRD-005 (tax_planning_advice): active]; slots {currency=USD (filled)}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (accepted); turns_since_resolution 3; escalation_proximity 0.60 |

### T10 | Agent

> You're welcome. Thank you for banking with NexBank. Take care.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.11 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 10; topic_stack [PRD-005 (tax_planning_advice): active]; slots {currency=USD (filled)}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (accepted); turns_since_resolution 4; escalation_proximity 0.60 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation: the advisory case is open for the next opening and a callback is requested; resolution_status escalated (A10.1) |
| Messages | 10 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.00, 0.00, 0.00, 0.05, 0.20]; final smoothed 0.11 |
| Escalation record | ESC-013, sub-rule ESC-013.a, fired at T3 when the customer accepted the advisor offer; priority P1, queue Wealth Advisory, SLA under 10 min (not counted: queue closed, after-hours rule), handoff mode warm (case opened; live handoff impossible), cancellable customer_only; secondary triggers: none; result: callback request placed (reference in T6); no generalist gave advice (D-122) |
| CSAT / check-in | Not asked now: the escalated conversation is surveyed after the advisor closes it. |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_16 |
| 2 | Auth level | level otp_verified; level_at_trigger otp_verified |
| 3 | Intent history | PRD-005 > tax_planning_advice 0.92 first at T7; GEN-006 > thanks 0.90 first at T9 |
| 4 | Entities collected (masked) | currency=USD (filled) |
| 5 | Conversation summary | NRI customer asked whether to convert dollars now or wait, and for transfer charges and limits. Both were declined or stated as unknown; no figure was given. He accepted the advisor offer. The advisory queue was closed, so a callback was requested. He then asked how much to put in tax-saving FDs and was given only the catalogue facts. |
| 6 | Sentiment trajectory | raw [0.00, 0.00, 0.00, 0.05, 0.20]; current 0.11; emotions: none; sarcasm_suspected false |
| 7 | Actions already taken | schedule_callback at T6: ok, reference CBK-SYN-1601 |
| 8 | Escalation trigger and reason | trigger_id ESC-013; rule_id ESC-013.a; priority P1; source customer_request; secondary []; reason_text: Customer accepted the offer of a SEBI-registered advisor for a currency-timing and tax-planning question.; evidence_turns [T3] |

Envelope: priority P1; queue Wealth Advisory; handoff_mode warm; language en; channel app; complete true; missing_fields []; versions.prompt_version sp-1.0.0+518d5a1e.n000000. after-hours rule: case opened for the next opening, callback requested (D-122).  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no occasion for it in this scenario |
| P2 | Progressive Disclosure | shown at T2, T8 |
| P3 | Confirmation-Before-Action | not applicable: no occasion for it in this scenario |
| P4 | Graceful Degradation | shown at T2, T4, T6, T8 |
| P5 | Context Carry-Over | shown at T4, T6, T10 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 5 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 71 words (cap `atk_output_max_words`); one concept per message | T2, T6 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T4, T6 |
| AP4 | Premature Escalation | absent: ESC-013 was created only after the customer accepted the offer (offer-then-escalate, D-55) | none at risk |
| AP5 | Empathy Bypass | not at risk: no customer message carried a problem or a negative emotion | none |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); the session started at otp_verified and the callback to the registered contact needs otp_verified | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 6 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T4, T6, T8 |
