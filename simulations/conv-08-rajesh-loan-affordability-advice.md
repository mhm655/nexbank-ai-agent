# conv-08: Rajesh: loan facts and illustration, affordability declined

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A textile trader asks what a personal loan needs and for an instalment illustration, then asks the assistant to say whether he can afford it and which amount to take. The assistant gives facts and an illustration, declines the judgement, and the advisor offer is declined. |
| Persona | Rajesh (Business Owner) |
| Channel | chat |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | PRD-002, PRD-005, GEN-006 |
| Guardrails exercised | GR-ADV-02, GR-ADV-03, GR-ADV-06, GR-ADV-07, GR-ADV-08, GR-OUT-01, GR-OUT-03, GR-OUT-04, GR-REG-01, GR-REG-15, GR-REG-16, GR-REG-20 |
| Escalation outcome | ESC-013 offered at T5 and declined at T6; no record is created for a declined offer |
| Escalation IDs | ESC-013 (offered, declined) |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | none |
| Patterns shown | P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP7, AP8 |
| Coverage tags | information-vs-advice boundary: loan products (A4.1), emi_calculator illustration, loan fees KB gap (KB-ESC-018), no automated credit decision, declined advisor offer not repeated |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-GEN-DISCLOSE-MORE, TPL-ADV-LOAN, TPL-ADV-ADVISOR-OFFER, TPL-ADV-BOUNDARY, TPL-GEN-CLOSING |
| KB entries cited | KB-PRD-006, KB-FAQ-005, KB-ESC-018, KB-POL-008, KB-PRD-012, KB-POL-001, KB-REG-009 |
| Tools called | emi_calculator |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | The published criteria and a deterministic instalment illustration are given as facts, affordability and amount choice are declined without using the income he volunteered, the advisor is offered once, and the declined offer is not repeated. |

Setup: Rajesh, textile trader, Surat. Anonymous web chat on the public site. No earlier session.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I run a textile shop in Surat. What do I need for a NexPersonal loan? I would also like to know the EMI for 5 lakh over 3 years.

| Field | Value |
|---|---|
| NLU | intent `PRD-002` 0.87 (tertiary personal_loan_criteria); runner-up `PRD-005` 0.31; entities: loan_type=personal, amount=INR 5,00,000, tenure=3 years; language: en 0.97 |
| Sentiment | raw 0.05, smoothed 0.05, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none (generic information at anonymous level, generic_info_auth) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > RESPOND; auth anonymous; turn_count 1; topic_stack [PRD-002 (personal_loan_criteria): active]; slots {loan_type=personal (filled); amount=INR 5,00,000 (filled); tenure=3 years (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | Two asks in one message, both PRD-002 (criteria and emi_calculation): two tertiaries of one intent, so no multi-intent split. The EMI needs a rate that the customer did not give. |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. The NexPersonal Loan needs CIBIL above 650 and income verification. It starts at 10.5%, runs up to 5 years and has instant disbursal. I don't have the fees or terms for your case; those are in the loan offer documents, and a loan specialist can walk you through them. Would you like more detail on an instalment illustration or the loan specialist?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-REG-01 (rate stated with the pointer to fees and terms), GR-OUT-03 (grounding), GR-OUT-01 (figures match KB-PRD-006) |
| KB / tools | KB: KB-PRD-006@1.0.0 (0.89), KB-FAQ-005@1.0.0 (0.84), KB-ESC-018@1.0.0 (0.78), KB-POL-008@1.0.0 (0.70); retrieval confidence 0.89; decision answer |
| Action | respond: criteria and the disclosure pointer first; the illustration needs a rate, so it is offered as the next layer instead of guessing a rate |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-GEN-DISCLOSE-MORE/layer_1_2@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 2; topic_stack [PRD-002 (personal_loan_criteria): active]; slots {loan_type=personal (filled); amount=INR 5,00,000 (filled); tenure=3 years (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | Fees, prepayment terms and the maximum amount are in the KB-ESC-018 unknown list, so none is stated; the offer documents and a person are named instead (KB-POL-008). |

### T3 | Customer

> Use the starting rate. EMI for 5 lakh, 3 years?

| Field | Value |
|---|---|
| NLU | intent `PRD-002` 0.90 (tertiary emi_calculation); runner-up `PRD-005` 0.25; entities: amount=INR 5,00,000, tenure=3 years, rate=10.5% (customer chose the starting rate) |
| Sentiment | raw 0.10, smoothed 0.08, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > EXECUTE; auth anonymous; turn_count 3; topic_stack [PRD-002 (personal_loan_criteria): active]; slots {loan_type=personal (filled); amount=INR 5,00,000 (filled); tenure=3 years (filled); rate=10.5% (customer-chosen, illustrative)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |

### T4 | Agent

> Here are the details: For INR 5,00,000 at 10.5% over 3 years, the illustrative EMI is about INR 16,251 a month. This is an illustration only, using the starting rate you chose; the actual rate and fees depend on the offer documents. Is there anything else you'd like to know about this?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.08 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-01 (the figure is the emi_calculator result, not model arithmetic), GR-REG-15 (illustration, not a decision), GR-ADV-03 (no judgement on the customer's means) |
| KB / tools | KB: KB-PRD-012@1.0.0 (0.86), KB-PRD-006@1.0.0 (0.80), KB-ESC-018@1.0.0 (0.72); retrieval confidence 0.86; decision answer<br>tool: `emi_calculator`(principal=INR 5,00,000, annual_rate=10.5%, tenure=3 years; rate chosen by the customer) -> ok: {emi_approx: INR 16,251, method: reducing balance} |
| Action | respond: deterministic illustration with the KB-PRD-012 must-say lines (illustration only; actual rate and fees depend on the offer documents) |
| Generation | hybrid `TPL-GEN-DISCLOSE-MORE/layer_3@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth anonymous; turn_count 4; topic_stack [PRD-002 (personal_loan_criteria): active]; slots {loan_type=personal (filled); amount=INR 5,00,000 (filled); tenure=3 years (filled); rate=10.5% (customer-chosen, illustrative)}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.00 |

### T5 | Customer

> Good. So can I afford this? My shop makes about 80 thousand a month and I already pay two other loans. Tell me whether I should take 5 lakh or 10 lakh.

| Field | Value |
|---|---|
| NLU | intent `PRD-005` 0.91 (tertiary loan_affordability_advice); runner-up `PRD-002` 0.55; entities: income=stated (not used), existing_loans=2 (not used) |
| Sentiment | raw -0.05, smoothed 0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-02 (advice classifier 0.93), GR-ADV-03 (personal-circumstance suitability and affordability), GR-ADV-07 (income and loans are not used as inputs and are not stored as eligibility data), GR-REG-15 (no automated credit decision) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth anonymous; turn_count 5; topic_stack [PRD-005 (loan_affordability_advice): active, PRD-002: parked]; slots {}; pending_confirmation none; counters: advice_deflections 1; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | The customer volunteers income and other loans. The reply neither thanks him for the context nor uses it; asking for more of it would breach GR-ADV-07. |

### T6 | Agent

> The published criteria are: CIBIL above 650 and income verification. I can't judge affordability or whether you would be approved; a loan decision is made on a full application. Would you like an illustration of the monthly instalment for an amount and tenure you choose? For a personal recommendation, a SEBI-registered advisor at NexBank can help. Shall I arrange that for you?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-ADV-03 (affordability declined), GR-ADV-06 (output boundary check), GR-ADV-08 (advisor offered once), GR-REG-20 (information-only perimeter), GR-REG-15 (the bank, not the assistant, decides) |
| KB / tools | KB: KB-POL-001@1.0.0 (0.90), KB-FAQ-005@1.0.0 (0.83), KB-PRD-006@1.0.0 (0.80), KB-REG-009@1.0.0 (0.66); retrieval confidence 0.90; decision answer |
| Action | recommend: boundary reply; criteria as facts, no judgement, offer of a SEBI-registered advisor (ESC-013) because the customer asked for a personal recommendation |
| Generation | template `TPL-ADV-LOAN/criteria_only@1.0.0` + `TPL-ADV-ADVISOR-OFFER/default@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 6; topic_stack [PRD-005 (loan_affordability_advice): active, PRD-002: parked]; slots {}; pending_confirmation none; counters: advice_deflections 1, advisor_offers 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | KB-POL-001, loan_products: the prohibited form is 'Based on your salary, you can afford a 20L home loan'. The permitted form is the published criteria and an illustration. The brief's own example amount (20L) is not used here. |

### T7 | Customer

> No advisor, thanks. Just tell me, 5 lakh or 10 lakh? One word.

| Field | Value |
|---|---|
| NLU | intent `PRD-005` 0.88 (tertiary loan_affordability_advice); runner-up none above 0.20; entities: none |
| Sentiment | raw -0.10, smoothed -0.04, confidence 0.85; emotions: impatience 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-02 (second advice request on the topic), GR-ADV-08 (offer declined: not repeated, advisor_offer_max_per_topic) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth anonymous; turn_count 7; topic_stack [PRD-005 (loan_affordability_advice): active, PRD-002: parked]; slots {}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (declined); turns_since_resolution 3; escalation_proximity 0.00 |

### T8 | Agent

> Here is what I can tell you: I can show a monthly instalment illustration for any amount and tenure you name, using the starting rate of 10.5%, and the loan decision is made by the bank on a full application. I can share the facts, but I can't tell you which option to choose. Would you like more detail on any of these?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.04 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-ADV-06 (facts only), GR-ADV-08 (no second offer), GR-OUT-04 (no apology loop, no pressure) |
| KB / tools | KB: KB-POL-001@1.0.0 (0.88), KB-FAQ-005@1.0.0 (0.81), KB-PRD-006@1.0.0 (0.79); retrieval confidence 0.88; decision answer |
| Action | recommend: second advice request, same boundary in different words; the declined offer is respected by not repeating it |
| Generation | template `TPL-ADV-BOUNDARY/default@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 8; topic_stack [PRD-005 (loan_affordability_advice): active, PRD-002: parked]; slots {}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (declined); turns_since_resolution 4; escalation_proximity 0.00 |
| Decision point | TPL-ADV-ADVISOR-DECLINED is the acknowledgement of a decline. Here the decline and a repeated request arrive together, so the boundary reply carries the substance and no new offer is made. |

### T9 | Customer

> Ok. Show it for 10 lakh over 5 years as well.

| Field | Value |
|---|---|
| NLU | intent `PRD-002` 0.86 (tertiary emi_calculation); runner-up `PRD-005` 0.33; entities: amount=INR 10,00,000, tenure=5 years, rate=10.5% (same as before) |
| Sentiment | raw 0.00, smoothed -0.02, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > EXECUTE; auth anonymous; turn_count 9; topic_stack [PRD-002 (emi_calculation): active]; slots {loan_type=personal (filled); amount=INR 10,00,000 (filled); tenure=5 years (filled); rate=10.5% (customer-chosen, illustrative)}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (declined); turns_since_resolution 5; escalation_proximity 0.00 |

### T10 | Agent

> Here are the details: For INR 10,00,000 at 10.5% over 5 years, the illustrative EMI is about INR 21,494 a month. I don't have a maximum loan amount, so this is only an illustration and does not mean that amount is available. Is there anything else you'd like to know about this?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.02 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-01 (tool figure), GR-REG-15 (no decision implied), GR-OUT-03 (the unknown maximum amount is stated as unknown, KB-ESC-018) |
| KB / tools | KB: KB-PRD-012@1.0.0 (0.85), KB-ESC-018@1.0.0 (0.80), KB-PRD-006@1.0.0 (0.78); retrieval confidence 0.85; decision answer<br>tool: `emi_calculator`(principal=INR 10,00,000, annual_rate=10.5%, tenure=5 years; rate chosen by the customer) -> ok: {emi_approx: INR 21,494, method: reducing balance} |
| Action | respond: the calculation is allowed because it is deterministic; the answer says plainly that availability of the amount is not known |
| Generation | hybrid `TPL-GEN-DISCLOSE-MORE/layer_3@1.0.0` (language en); patterns: P2, P4; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth anonymous; turn_count 10; topic_stack [PRD-002 (emi_calculation): active]; slots {loan_type=personal (filled); amount=INR 10,00,000 (filled); tenure=5 years (filled); rate=10.5% (customer-chosen, illustrative)}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (declined); turns_since_resolution 0; escalation_proximity 0.00 |

### T11 | Customer

> Okay, thanks. I will think about it.

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.88 (tertiary thanks); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.30, smoothed 0.14, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth anonymous; turn_count 11; topic_stack [PRD-005 (loan_affordability_advice): parked (declined)]; slots {loan_type=personal (filled); amount=INR 10,00,000 (filled); tenure=5 years (filled); rate=10.5% (customer-chosen, illustrative)}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (declined); turns_since_resolution 1; escalation_proximity 0.00 |

### T12 | Agent

> You're welcome. Thank you for banking with NexBank. Take care.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.14 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close; the parked topic is a declined advice request, so TPL-GEN-CLOSING/parked_topic is not used |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth anonymous; turn_count 12; topic_stack [PRD-005 (loan_affordability_advice): parked (declined)]; slots {loan_type=personal (filled); amount=INR 10,00,000 (filled); tenure=5 years (filled); rate=10.5% (customer-chosen, illustrative)}; pending_confirmation none; counters: advice_deflections 2, advisor_offers 1 (declined); turns_since_resolution 2; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact (A5.3), provisional until the 7-day repeat-contact window passes; resolution_status resolved_ai (A10.1) |
| Messages | 12 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.05, 0.10, -0.05, -0.10, 0.00, 0.30]; final smoothed 0.14 |
| Escalation record | none. ESC-013.a was never met: the offer at T5 was declined at T6, so no escalation record exists (D-55). |
| CSAT / check-in | Not asked in this conversation (the customer closed with thanks and left; csat_resurvey_gap_days applies to a later contact). |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no occasion for it in this scenario |
| P2 | Progressive Disclosure | shown at T2, T4, T6, T8, T10 |
| P3 | Confirmation-Before-Action | not applicable: no occasion for it in this scenario |
| P4 | Graceful Degradation | shown at T2, T6, T8, T10 |
| P5 | Context Carry-Over | shown at T12 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 6 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 67 words (cap `atk_output_max_words`); one concept per message | T2, T5 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T4, T9 |
| AP4 | Premature Escalation | absent: no escalation record; the advisor was offered once, as the boundary requires, and the decline was respected | none at risk |
| AP5 | Empathy Bypass | not at risk: no customer message carried a problem or a negative emotion | none at risk |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); never while the auth level already met the intent's level | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 13 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T2, T4, T9 |
