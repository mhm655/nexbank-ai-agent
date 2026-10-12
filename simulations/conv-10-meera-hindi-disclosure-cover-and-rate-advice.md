# conv-10: Meera (Hindi): AI disclosure, deposit cover, and an FD-or-savings question declined

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

Non-English text in this file (customer lines, template wording, glosses) is not native-reviewed.

## Header

| Field | Value |
|---|---|
| Scenario | A retired customer writes in Hindi (Devanagari). She asks whether she is talking to a human, whether her pension money is insured, and then asks the assistant to say whether she should keep money in a fixed deposit or in savings. The assistant answers from the reviewed Hindi entries, declines the choice, and the advisor offer is declined. |
| Persona | Meera (Retired Teacher) |
| Channel | app |
| Language | hi |
| Starting auth level | anonymous |
| Intents covered | GEN-002, PRD-001, PRD-005, GEN-006 |
| Guardrails exercised | GR-ADV-01, GR-ADV-02, GR-ADV-03, GR-ADV-06, GR-ADV-07, GR-ADV-08, GR-OUT-01, GR-OUT-03, GR-REG-01, GR-REG-16, GR-REG-20 |
| Escalation outcome | ESC-013 offered at T6 and declined at T7; no record is created for a declined offer |
| Escalation IDs | ESC-013 (offered, declined) |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | none |
| Patterns shown | P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP7, AP8 |
| Coverage tags | Hindi (Devanagari), AI disclosure (GEN-002), reviewed Hindi KB entries only (KB-FAQ-009, KB-FAQ-001, KB-FAQ-008), information-vs-advice boundary: interest rates (A4.1), declined advisor offer |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-AI-DISCLOSURE, TPL-ADV-RATE, TPL-ADV-ADVISOR-OFFER, TPL-ADV-ADVISOR-DECLINED, TPL-GEN-CLOSING |
| KB entries cited | KB-FAQ-009, KB-POL-009, KB-FAQ-001, KB-REG-010, KB-PRD-001, KB-POL-001, KB-FAQ-008, KB-PRD-002, KB-REG-005 |
| Tools called | none |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | A Hindi-speaking customer gets the AI disclosure, the DICGC cover and the FD range from the reviewed Hindi KB bodies, the choice between a fixed deposit and savings is declined with the published range and one advisor offer, and the declined offer is acknowledged and not repeated. |

Setup: Meera, Jaipur, writes in Devanagari Hindi on the public site. Anonymous. No earlier session. Only four KB entries have reviewed Hindi bodies (KB-FAQ-001, KB-FAQ-002, KB-FAQ-008, KB-FAQ-009); this conversation stays inside them.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> नमस्ते। क्या मैं किसी इंसान से बात कर रही हूँ?

_English gloss (annotation only, not customer-facing; not native-reviewed): Hello. Am I speaking to a human being?_

| Field | Value |
|---|---|
| NLU | intent `GEN-002` 0.93 (tertiary are_you_human); runner-up none above 0.20; entities: none; language: hi 0.98 (script devanagari, code_switching false) |
| Sentiment | raw 0.00, smoothed 0.00, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > RESPOND; auth anonymous; turn_count 1; topic_stack [GEN-002 (are_you_human): active]; slots {}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> मैं एक AI सहायक हूँ, कोई व्यक्ति नहीं। मैं रोज़मर्रा के ज़्यादातर बैंकिंग सवालों में मदद कर सकता हूँ, और अगर आप हमारे किसी सहयोगी से बात करना चाहें तो बस बता दीजिए, मैं व्यवस्था कर दूँगा।

_English gloss (annotation only, not customer-facing; not native-reviewed): I'm an AI assistant, not a person. I can help with most everyday banking questions, and if you'd rather talk to a human colleague, just say so and I'll arrange it._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure when asked, and in the first reply), GR-OUT-03 (grounding) |
| KB / tools | KB: KB-FAQ-009@1.0.0 (0.95), KB-POL-009@1.0.0 (0.80); retrieval confidence 0.95; decision answer |
| Action | respond: plain AI disclosure with the human option, from the reviewed Hindi template |
| Generation | template `TPL-GEN-AI-DISCLOSURE/default@1.0.0` (language hi); patterns: P2; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 2; topic_stack [GEN-002 (are_you_human): active]; slots {}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.00 |

### T3 | Customer

> ठीक है। मेरी पेंशन के पैसे इस खाते में सुरक्षित हैं क्या? कितने तक का बीमा मिलता है?

_English gloss (annotation only, not customer-facing; not native-reviewed): All right. Is my pension money safe in this account? Up to how much is it insured?_

| Field | Value |
|---|---|
| NLU | intent `PRD-001` 0.85 (tertiary features); runner-up `PRD-003` 0.30; entities: product=NexSave Savings Account; language: hi 0.98 (script devanagari, code_switching false) |
| Sentiment | raw 0.05, smoothed 0.03, confidence 0.85; emotions: anxiety 0.20 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth anonymous; turn_count 3; topic_stack [PRD-001 (features): active]; slots {product=NexSave Savings Account (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T4 | Agent

> NexSave बचत खाते की जमा राशि पर DICGC कवर 5 लाख रुपये तक उपलब्ध है, जैसा कि NexBank की उत्पाद सूची में दिया गया है। इससे आगे की जानकारी के लिए आपको हमारी टीम से जोड़ा जा सकता है।

_English gloss (annotation only, not customer-facing; not native-reviewed): The deposits in your NexSave savings account have DICGC cover up to 5 lakh rupees, as given in NexBank's product list. For information beyond that, you can be connected to our team._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-03 (the reply is the reviewed Hindi body of KB-FAQ-001, word for word), GR-OUT-01 (the figure matches the entry), GR-REG-01 |
| KB / tools | KB: KB-FAQ-001@1.0.0 (0.93), KB-REG-010@1.0.0 (0.82), KB-PRD-001@1.0.0 (0.80); retrieval confidence 0.93; decision answer |
| Action | respond: the answer is the reviewed Hindi KB body; no machine translation of a financial fact (language-detection.md section 6) |
| Generation | llm (free text inside prompt layers 0 to 5; the reviewed Hindi body of KB-FAQ-001 used verbatim; no other fact added; language hi); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 4; topic_stack [PRD-001 (features): active]; slots {product=NexSave Savings Account (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.00 |
| Decision point | The Hindi text of this reply is the KB-FAQ-001 hi body. A translation of KB-PRD-001 or KB-REG-010 would be a machine translation of a financial fact, which is not allowed. |

### T5 | Customer

> अच्छा। मेरे पास कुछ पैसे हैं। FD में रखूँ या बचत खाते में ही रहने दूँ? आप बताइए कौन-सा बेहतर रहेगा।

_English gloss (annotation only, not customer-facing; not native-reviewed): I see. I have some money. Should I keep it in an FD or leave it in the savings account? Tell me which would be better._

| Field | Value |
|---|---|
| NLU | intent `PRD-005` 0.90 (tertiary interest_rate_advice); runner-up `PRD-003` 0.52; entities: product=NexFD, product=NexSave; language: hi 0.98 (script devanagari, code_switching false) |
| Sentiment | raw 0.00, smoothed 0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-01 (recommendation verb and product words), GR-ADV-02 (advice classifier 0.91), GR-ADV-03 (personal circumstance: money to place), GR-ADV-07 (no question about her amount, age or goals) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth anonymous; turn_count 5; topic_stack [PRD-005 (interest_rate_advice): active]; slots {}; pending_confirmation none; counters: advice_deflections 1; turns_since_resolution 1; escalation_proximity 0.00 |

### T6 | Agent

> NexFD की अवधि 7 दिन से 10 वर्ष तक है और दरें 6.0 से 7.25 प्रतिशत के दायरे में हैं। मैं ये तथ्य बता सकता हूँ, पर यह नहीं बता सकता कि आपको निवेश करना चाहिए या कहाँ। क्या आप अवधि या टैक्स के बारे में और जानना चाहेंगे? व्यक्तिगत सलाह के लिए नेक्सबैंक के SEBI-पंजीकृत सलाहकार आपकी मदद कर सकते हैं। क्या मैं इसकी व्यवस्था करूँ?

_English gloss (annotation only, not customer-facing; not native-reviewed): NexFD tenures run from 7 days to 10 years, and the rates are in the range of 6.0 to 7.25 percent. I can share these facts, but I can't tell you whether or where to invest. Would you like to know more about tenures or tax treatment? For a personal recommendation, a SEBI-registered advisor at NexBank can help. Shall I arrange that for you?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-ADV-06 (facts only, no choice between the two products), GR-ADV-08 (advisor offered once), GR-REG-20, GR-OUT-01 (range from the KB) |
| KB / tools | KB: KB-POL-001@1.0.0 (0.89), KB-FAQ-008@1.0.0 (0.86), KB-PRD-002@1.0.0 (0.80), KB-REG-005@1.0.0 (0.74); retrieval confidence 0.89; decision answer |
| Action | recommend: boundary reply in the reviewed Hindi template; the published range as the fact, no comparison with savings, offer of a SEBI-registered advisor (ESC-013) |
| Generation | template `TPL-ADV-RATE/range_only@1.0.0` + `TPL-ADV-ADVISOR-OFFER/default@1.0.0` (language hi); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 6; topic_stack [PRD-005 (interest_rate_advice): active]; slots {}; pending_confirmation none; counters: advice_deflections 1, advisor_offers 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | KB-POL-001, interest_rates: the permitted form is a published rate; the prohibited form is 'You should invest in FD as it gives better returns'. The question compares a product with her savings account, so no rate for the savings product is quoted next to the FD range either. |

### T7 | Customer

> नहीं, किसी सलाहकार की ज़रूरत नहीं है। मैं खुद सोच लूँगी।

_English gloss (annotation only, not customer-facing; not native-reviewed): No, I don't need an advisor. I will think about it myself._

| Field | Value |
|---|---|
| NLU | dialogue act decline 0.95 (advisor offer); active intent `PRD-005` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw -0.05, smoothed -0.02, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-ADV-08 (offer declined: no record, no repeat) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND; auth anonymous; turn_count 7; topic_stack [PRD-005 (interest_rate_advice): active]; slots {}; pending_confirmation none; counters: advice_deflections 1, advisor_offers 1 (declined); turns_since_resolution 3; escalation_proximity 0.00 |

### T8 | Agent

> ठीक है। मैं तथ्यों तक ही सीमित रहूँगा। आप क्या जानना चाहेंगे?

_English gloss (annotation only, not customer-facing; not native-reviewed): No problem. I'll keep to the facts. What would you like to know?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.02 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-ADV-08 (decline acknowledged, no second offer) |
| KB / tools | none |
| Action | respond: the decline is acknowledged; the topic stays parked |
| Generation | template `TPL-ADV-ADVISOR-DECLINED/default@1.0.0` (language hi); patterns: P4; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 8; topic_stack [PRD-005 (interest_rate_advice): parked (declined)]; slots {}; pending_confirmation none; counters: advice_deflections 1, advisor_offers 1 (declined); turns_since_resolution 0; escalation_proximity 0.00 |

### T9 | Customer

> ठीक है, धन्यवाद। आपने आराम से समझाया।

_English gloss (annotation only, not customer-facing; not native-reviewed): All right, thank you. You explained it calmly._

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.91 (tertiary thanks); runner-up none above 0.20; entities: none; language: hi 0.98 (script devanagari, code_switching false) |
| Sentiment | raw 0.40, smoothed 0.19, confidence 0.85; emotions: gratitude 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth anonymous; turn_count 9; topic_stack [PRD-005 (interest_rate_advice): parked (declined)]; slots {}; pending_confirmation none; counters: advice_deflections 1, advisor_offers 1 (declined); turns_since_resolution 1; escalation_proximity 0.00 |

### T10 | Agent

> आपका स्वागत है। नेक्सबैंक के साथ बैंकिंग करने के लिए धन्यवाद। अपना ध्यान रखिए।

_English gloss (annotation only, not customer-facing; not native-reviewed): You're welcome. Thank you for banking with NexBank. Take care._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.19 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language hi); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth anonymous; turn_count 10; topic_stack [PRD-005 (interest_rate_advice): parked (declined)]; slots {}; pending_confirmation none; counters: advice_deflections 1, advisor_offers 1 (declined); turns_since_resolution 2; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact (A5.3), provisional until the 7-day repeat-contact window passes; resolution_status resolved_ai (A10.1) |
| Messages | 10 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.00, 0.05, 0.00, -0.05, 0.40]; final smoothed 0.19 |
| Escalation record | none. ESC-013.a was never met: the offer at T6 was declined at T7, so no escalation record exists (D-55). |
| CSAT / check-in | Not asked in this conversation (the customer closed with thanks and left; csat_resurvey_gap_days applies to a later contact). |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no occasion for it in this scenario |
| P2 | Progressive Disclosure | shown at T2, T4, T6 |
| P3 | Confirmation-Before-Action | not applicable: no occasion for it in this scenario |
| P4 | Graceful Degradation | shown at T4, T6, T8 |
| P5 | Context Carry-Over | shown at T10 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 5 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 67 words (cap `atk_output_max_words`); one concept per message | T4, T6 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T4, T6 |
| AP4 | Premature Escalation | absent: no escalation record; the advisor was offered once and the decline was respected | none at risk |
| AP5 | Empathy Bypass | not at risk: no customer message carried a problem or a negative emotion | none at risk |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); never while the auth level already met the intent's level | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 4 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T4, T6 |
