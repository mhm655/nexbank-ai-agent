# conv-03: Case Study 3 re-run: product question that asks for advice

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A customer asks whether to put idle money in a fixed deposit or mutual funds, then volunteers his age and a retirement goal and asks which is better for him. |
| Persona | Arjun (NRI) |
| Channel | chat |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | PRD-005 |
| Guardrails exercised | GR-ADV-01, GR-ADV-02, GR-ADV-03, GR-ADV-06, GR-ADV-07, GR-ADV-08, GR-OUT-05, GR-REG-01, GR-REG-16, GR-REG-20 |
| Escalation outcome | ESC-013 offered at T2 and T4; record created on acceptance at T5 (P1, Wealth Advisory); advisor accepted |
| Escalation IDs | ESC-013 |
| Priority | P1 |
| Adversarial vectors | none |
| Security rules exercised | none |
| Patterns shown | P2, P4, P5 |
| Anti-patterns designed against | AP2, AP3, AP4, AP5, AP6, AP8 |
| Coverage tags | case study re-run, advice boundary: investment (A4.1), ESC-013 offered then accepted |
| Case study | Case Study 3 (brief pp.51-52) |
| Templates used | TPL-GEN-GREETING, TPL-ADV-INVEST, TPL-ADV-ADVISOR-OFFER, TPL-ADV-BOUNDARY, TPL-ADV-ADVISOR-CONFIRM, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-PRD-002, KB-PRD-008, KB-POL-001, KB-REG-005 |
| Tools called | none |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | Facts are given from the KB, the recommendation is declined twice in different words, volunteered age and goals are neither stored nor echoed, and the advisor record is created only when the customer accepts. |

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I have 5 lakhs sitting idle. Should I put it in FD or mutual funds?

| Field | Value |
|---|---|
| NLU | intent `PRD-005` 0.88 (tertiary investment_product_advice); runner-up `PRD-003` 0.41; entities: product_name=NexFD Fixed Deposit, product_name=NexInvest Mutual Funds; the amount is read and not stored (D-55); language: en 0.98 |
| Sentiment | raw 0.10, smoothed 0.10, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-01 (rule hit: recommendation verb with product words), GR-ADV-02 (advice classifier 0.91, above advice_boundary_act) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > RESPOND; auth anonymous; turn_count 1; topic_stack [PRD-005: active]; slots {}; pending_confirmation none; counters: advice_deflections 1; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. NexFD is a fixed deposit with rates of 6.0 to 7.25 percent and tenures from 7 days to 10 years; Section 80C benefits and TDS apply. NexInvest is a direct mutual fund platform with SIP from INR 100; it is SEBI regulated and KYC is mandatory. A risk disclosure applies to mutual fund investments. I can't pick an investment for you or say how it will perform. Would you like more detail on how any of these work? For a personal recommendation, a SEBI-registered advisor at NexBank can help. Shall I arrange that for you?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure in the first reply), GR-ADV-06 (output boundary check: facts only), GR-ADV-08 (advisor offer), GR-REG-01 (disclosures in the first layer), GR-REG-20 (no claim to be an advisor) |
| KB / tools | KB: KB-PRD-002@1.0.0 (0.90), KB-PRD-008@1.0.0 (0.88), KB-POL-001@1.0.0 (0.83), KB-REG-005@1.0.0 (0.80); retrieval confidence 0.90; decision answer |
| Action | recommend: information-only product facts from the catalogue, recommendation declined, advisor offer made once for this topic |
| Generation | template `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-ADV-INVEST/default@1.0.0` + `TPL-ADV-ADVISOR-OFFER/default@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 2; topic_stack [PRD-005: active]; slots {}; pending_confirmation none; counters: advice_deflections 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | The brief's reply says NexBank partners with AMCs 'offering equity, debt, and hybrid funds'. KB-PRD-008 holds no fund list, so no fund types are named. It also opens with praise for the question; this reply goes straight to the facts. |

### T3 | Customer

> Just tell me which one is better for me. I'm 35 and want to retire at 50.

| Field | Value |
|---|---|
| NLU | intent `PRD-005` 0.93 (tertiary investment_product_advice); runner-up `PRD-001` 0.22; entities: none stored: age and retirement goal are read transiently by the advice detector and never written to slots, pinned facts or the summary (D-55) |
| Sentiment | raw -0.20, smoothed -0.05, confidence 0.85; emotions: frustration 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-03 (personal-circumstance suitability request), GR-ADV-07 (block on eliciting: nothing about income, age or goals is asked or echoed) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INTENT_DETECT > RESPOND; auth anonymous; turn_count 3; topic_stack [PRD-005: active]; slots {}; pending_confirmation none; counters: advice_deflections 2; turns_since_resolution 3; escalation_proximity 0.00 |

### T4 | Agent

> Here is what I can tell you: NexFD has a published rate range and tenure span, with Section 80C benefits and TDS; NexInvest is a direct mutual fund platform, and a risk disclosure applies to it. I can share the facts, but I can't tell you which option to choose. Would you like more detail on any of these? For a personal recommendation, a SEBI-registered advisor at NexBank can help. Shall I arrange that for you?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-ADV-06 (facts only), GR-ADV-07 (age and goal not used as a basis), GR-ADV-08 (offer) |
| KB / tools | KB: KB-POL-001@1.0.0 (0.88), KB-PRD-002@1.0.0 (0.82), KB-PRD-008@1.0.0 (0.80), KB-REG-005@1.0.0 (0.79); retrieval confidence 0.88; decision answer |
| Action | recommend: second advice request on the same topic: different wording, same boundary; the offer is repeated only because the customer asked for advice again (financial-advice.md section 7) |
| Generation | template `TPL-ADV-BOUNDARY/default@1.0.0` + `TPL-ADV-ADVISOR-OFFER/default@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 4; topic_stack [PRD-005: active]; slots {}; pending_confirmation none; counters: advice_deflections 2; turns_since_resolution 4; escalation_proximity 0.00 |
| Decision point | Brief turn 4 offers 'a free 30-minute consultation'. Neither a duration nor a price is in the KB, so neither is stated (D-55, D-153). The reply does not thank the customer for 'sharing that context', because the context is not used. |

### T5 | Customer

> Fine, set that up.

| Field | Value |
|---|---|
| NLU | dialogue act accept_offer 0.95 (advisor); active intent `PRD-005` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw 0.00, smoothed -0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > ESCALATING; auth anonymous; turn_count 5; topic_stack [PRD-005: active]; slots {}; pending_confirmation none; counters: advice_deflections 2; turns_since_resolution 5; escalation_proximity 0.30 |
| Decision point | advisor_requested is now true: ESC-013.a creates the record (P1, Wealth Advisory, under 10 min). A declined offer would have created none. |

### T6 | Agent

> I'm connecting you to one of our SEBI-registered advisors. I've passed on your question about fixed deposits and mutual funds, so you won't need to repeat it. The current estimate is about 6 minutes; it is an estimate, and I'll stay here until they join.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the wait is a router estimate, worded as one) |
| KB / tools | router: queue=Wealth Advisory (open, extended hours); queue_wait=about 6 minutes (platform forecast, stated as an estimate) |
| Action | escalate: offer accepted; the package carries the topic and the customer's own question, not the volunteered circumstances |
| Generation | template `TPL-ADV-ADVISOR-CONFIRM/with_wait@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase ESCALATING; auth anonymous; turn_count 6; topic_stack [PRD-005: active]; slots {}; pending_confirmation none; counters: advice_deflections 2; turns_since_resolution 6; escalation_proximity 0.30 |

### E1 | System event

> A Wealth Advisory colleague accepts the conversation.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth anonymous; turn_count 6; topic_stack [PRD-005: active]; slots {}; pending_confirmation none; counters: advice_deflections 2; turns_since_resolution 6; escalation_proximity 0.30 |

### T7 | Agent

> This is Kabir from our advisory team. They have the details of your question about fixed deposits and mutual funds and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Kabir (synthetic); team_plain=advisory team |
| Action | escalate: handoff complete; the agent stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.1.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth anonymous; turn_count 7; topic_stack [PRD-005: active]; slots {}; pending_confirmation none; counters: advice_deflections 2; turns_since_resolution 7; escalation_proximity 0.30 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the advisor closes (A5.3); resolution_status escalated (A10.1). A correct escalation: the request needs a SEBI-registered advisor. |
| Messages | 7 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.10, -0.20, 0.00]; final smoothed -0.03 |
| Escalation record | ESC-013, sub-rule or basis ESC-013.a, fired at T5; priority P1, queue Wealth Advisory, SLA under 10 min, handoff mode warm, cancellable customer_only; secondary triggers: none; result: warm handoff accepted by Wealth Advisory at E1 |
| CSAT / check-in | Asked after the human conversation ends, in two parts (TPL-SRV-CSAT/after_human_ai_part, then after_human_human_part); not shown. |

### Deviations from the brief's case study (each one deliberate)

| Brief | This specification | Why |
|---|---|---|
| Turn 2: 'equity, debt, and hybrid funds' through partner AMCs | Only what KB-PRD-008 holds: direct platform, SIP minimum, regulator, KYC, risk disclosure | No fund list in A13.1 |
| Turn 4: 'I appreciate you sharing that context' | The age and goal are not acknowledged as inputs | GR-ADV-07, D-55: volunteered circumstances are not used |
| Turn 4: 'a free 30-minute consultation' | Offer with no duration and no price | Not in the KB (D-55, D-153) |
| Advisor 'schedule' wording | Live connection with a router estimate, because the queue is open | ESC-013 SLA under 10 min; after-hours behaviour is shown in conv-10 |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_03 |
| 2 | Auth level | level anonymous; level_at_trigger anonymous |
| 3 | Intent history | PRD-005 > investment_product_advice 0.88 first at T1; PRD-005 > investment_product_advice 0.93 first at T3 |
| 4 | Entities collected (masked) | none collected |
| 5 | Conversation summary | Customer asked whether to place idle funds in NexFD or mutual funds and then asked which is better for him. Product facts were given from the catalogue; no recommendation was made. He accepted the advisor offer. His question in his own words is at T1 and T3 of the transcript. |
| 6 | Sentiment trajectory | raw [0.10, -0.20, 0.00]; current -0.03; emotions: frustration; sarcasm_suspected false |
| 7 | Actions already taken | none |
| 8 | Escalation trigger and reason | trigger_id ESC-013; rule_id ESC-013.a; priority P1; source customer_request; secondary []; reason_text: Customer accepted the offer of a SEBI-registered advisor for a personal recommendation.; evidence_turns [T5] |

Envelope: priority P1; queue Wealth Advisory; handoff_mode warm; language en; channel chat; complete true; missing_fields []; versions.prompt_version sp-1.1.0+1527a050.n000000. The summary does not restate the age or the goal he volunteered; the advisor can open the transcript (D-55). Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no problem, complaint or negative emotion in this conversation |
| P2 | Progressive Disclosure | shown at T2, T4 |
| P3 | Confirmation-Before-Action | not applicable: no action that changes account state was reached |
| P4 | Graceful Degradation | shown at T2, T4 |
| P5 | Context Carry-Over | shown at T6, T7 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 4 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 100 words (cap `atk_output_max_words`); one concept per message | T2, T4, T7 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn | T2, T4, T6 |
| AP4 | Premature Escalation | absent: escalation only on ESC-013 at T5 | T2, T4 |
| AP5 | Empathy Bypass | absent: no customer message carried a problem or a negative emotion that the next reply ignored | T2 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); never while the auth level already met the intent's level | T6, T7 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 8 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T2, T4 |

