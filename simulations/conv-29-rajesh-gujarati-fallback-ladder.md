# conv-29: Rajesh (Gujarati): the secondary-language fallback ladder

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

Non-English text in this file (customer lines, template wording, glosses) is not native-reviewed.

## Header

| Field | Value |
|---|---|
| Scenario | A trader writes in Gujarati, a secondary language with no reviewed templates, first in Roman script and then in Gujarati script. The assistant walks the secondary-language fallback ladder: language choice, one clarification, a second clarification with a human offer, a Gujarati-speaking colleague who is not free, and a callback in Gujarati at his choice. |
| Persona | Rajesh (Business Owner) |
| Channel | app |
| Language | gu (secondary), replies in hi |
| Starting auth level | otp_verified |
| Intents covered | ACC-001, TXN-003, CMP-005, GEN-003, GEN-006 |
| Guardrails exercised | GR-OUT-03, GR-OUT-05, GR-REG-16, GR-SEC-R1, GR-SYS-01 |
| Escalation outcome | XTR-01 request 1 at T7 (language gu): no Gujarati-speaking colleague free, so the customer chose a callback in Gujarati at T9; callback request placed at T12; no live handoff |
| Escalation IDs | XTR-01 |
| Priority | P2 |
| Adversarial vectors | none |
| Security rules exercised | R1 |
| Patterns shown | P2, P3, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP7, AP8 |
| Coverage tags | secondary language Gujarati with the fallback ladder of language-detection.md section 7 (language ID below the floor, clarification, second clarification and human offer, language-matched human unavailable, callback in the language), reply language stored by customer choice (Hindi), Hindi templates, XTR-01 with a language flag |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-GEN-LANGUAGE-SWITCH, TPL-GEN-CLARIFY, TPL-ESC-LANGUAGE-CHOICE, TPL-ESC-CALLBACK-OFFER, TPL-GEN-CLOSING |
| KB entries cited | KB-ESC-020, KB-ESC-003, KB-POL-007 |
| Tools called | get_profile_masked, schedule_callback |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | Reviewed wording is used for everything the assistant says, the switch to Hindi is the customer's choice and never automatic, the budget of two clarifications is respected with a different reply each time, and when no colleague who speaks Gujarati is free the customer chooses between Hindi or English now and a Gujarati callback. |

Setup: Rajesh is signed in (otp_verified). Reviewed templates exist for English, Hindi and Hinglish only; Gujarati is a secondary language (language-detection.md section 7). The router has no Gujarati-speaking colleague free. Gujarati text in this file is not native-reviewed. A balance question and a payment question are in his first message.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Maru balance ketlu chhe? Ane kal no payment kem nathi aavyo?

_English gloss (annotation only, not customer-facing; not native-reviewed): What is my balance? And why did yesterday's payment not come through?_

| Field | Value |
|---|---|
| NLU | intent `ACC-001` 0.49 (tertiary current_balance); runner-up `TXN-003` 0.46; entities: date=yesterday; language: gu 0.44 (script latin; hinglish 0.38; below lang_id_floor 0.50; Roman-script secondary below 0.80) |
| Sentiment | raw -0.10, smoothed -0.10, confidence 0.55; emotions: worry 0.20 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: ladder rung 1: language ID below lang_id_floor, so the language-choice reply is used |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > CLARIFY; auth otp_verified; turn_count 1; topic_stack [ACC-001 (current_balance): active (candidate, not yet confirmed), TXN-003 (payment): parked (candidate)]; slots {date=11 Oct 2026 (resolved from 'kal')}; pending_confirmation none; counters: clarify_attempts 0, lang_choice_offered 1; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | Neither the language nor the intent is certain enough to act. The Input Guard still screens native text and the English pivot, and the flow-entry gates for fraud, distress and human requests stay at 0.50. Sentiment confidence is 0.55, below sentiment_turn_confidence_min (0.70), because the Roman-script Gujarati language ID is uncertain (D-18: in a secondary language the confidence is the gap, so ESC-004.b, not .a, is the route that applies if the scores fall). |

### T2 | Agent

> नमस्ते, मैं नेक्सबैंक का AI सहायक हूँ। मैं आपकी बात सही समझना चाहता हूँ। क्या आप हिंदी या अंग्रेज़ी में बात जारी रखना चाहेंगे, या मैं आपकी भाषा बोलने वाले किसी सहयोगी को जोड़ूँ? I want to be sure I understand you correctly. Would you like to continue in Hindi or English, or shall I bring in a colleague who speaks your language?

_English gloss (annotation only, not customer-facing; not native-reviewed): Hello, I'm NexBank's AI assistant. I want to understand you correctly. Would you like to continue in Hindi or English, or shall I bring in a colleague who speaks your language? [The same question follows in English.]_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.10 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-OUT-03 |
| KB / tools | none |
| Action | clarify: language-choice reply in Hindi and English together; the switch is the customer's choice and never automatic |
| Generation | template `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-GEN-LANGUAGE-SWITCH/offer_choice@1.0.0` + `TPL-GEN-LANGUAGE-SWITCH/offer_choice@1.0.0` [en] (language hi); patterns: P4; anti-pattern check: none |
| State | phase CLARIFY; auth otp_verified; turn_count 2; topic_stack [ACC-001 (current_balance): active (candidate, not yet confirmed), TXN-003 (payment): parked (candidate)]; slots {date=11 Oct 2026 (resolved from 'kal')}; pending_confirmation none; counters: clarify_attempts 0, lang_choice_offered 1; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Customer

> Hindi chalse. Balance ketlu chhe e batavo.

_English gloss (annotation only, not customer-facing; not native-reviewed): Hindi will do. Tell me what the balance is._

| Field | Value |
|---|---|
| NLU | intent `ACC-001` 0.62 (tertiary current_balance); runner-up `TXN-003` 0.35; entities: none; language: gu 0.52 (script latin, code_switching true); customer chose Hindi for replies |
| Sentiment | raw 0.00, smoothed -0.05, confidence 0.60; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLARIFY; auth otp_verified; turn_count 3; topic_stack [ACC-001 (current_balance): active (candidate, not yet confirmed)]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: clarify_attempts 0, lang_choice_offered 1; turns_since_resolution 3; escalation_proximity 0.00 |
| Decision point | reply_language is stored as hi by the customer's choice. The NLU keeps reading what he types, which is still Roman-script Gujarati. |

### T4 | Agent

> ज़रूर, अब हम हिंदी में बात करेंगे। मैं मदद करूँगा। सही समझने के लिए पूछ रहा हूँ: क्या यह बैलेंस देखने के बारे में है, या किसी भुगतान की स्थिति देखने के बारे में?

_English gloss (annotation only, not customer-facing; not native-reviewed): Sure, from now we will talk in Hindi. To be sure I understand: is this about checking the balance, or about checking the status of a payment?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SYS-01 (ladder rung 2: ordinary clarification from a reviewed template) |
| KB / tools | KB: KB-ESC-020@1.0.0 (0.60); retrieval confidence 0.60; decision answer |
| Action | clarify: first clarification, in the chosen language, from a reviewed Hindi template |
| Generation | template `TPL-GEN-LANGUAGE-SWITCH/confirm_switch@1.0.0` + `TPL-GEN-CLARIFY/two_options@1.1.0` (language hi); patterns: P2, P4; anti-pattern check: none |
| State | phase CLARIFY; auth otp_verified; turn_count 4; topic_stack [ACC-001 (current_balance): active (candidate, not yet confirmed)]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: clarify_attempts 1; turns_since_resolution 4; escalation_proximity 0.00 |

### T5 | Customer

> Balance j. Pan mane Gujarati ma j samjavo ne.

_English gloss (annotation only, not customer-facing; not native-reviewed): Just the balance. But please explain it to me in Gujarati only._

| Field | Value |
|---|---|
| NLU | intent `ACC-001` 0.61 (tertiary current_balance); runner-up none above 0.20; entities: none; language: gu 0.55 (script latin, code_switching true) |
| Sentiment | raw -0.05, smoothed -0.05, confidence 0.60; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLARIFY; auth otp_verified; turn_count 5; topic_stack [ACC-001 (current_balance): active (candidate, not yet confirmed)]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: clarify_attempts 1; turns_since_resolution 5; escalation_proximity 0.10 |
| Decision point | Still below intent_confidence_threshold (0.70) after one clarification. Secondary-language accuracy is lower, so the fallback does not act on 0.61. |

### T6 | Agent

> साथ बने रहने के लिए धन्यवाद। मैं यह समझ पाया कि बात बैलेंस की है, पर यह स्पष्ट नहीं है कि आप मुझसे क्या करवाना चाहते हैं। क्या यह बैलेंस देखना है या गुजराती बोलने वाले सहयोगी से बात करना? अगर दोनों में से कोई नहीं, तो मैं एक सहयोगी को जोड़ सकता हूँ।

_English gloss (annotation only, not customer-facing; not native-reviewed): Thank you for staying with me. I understood that this is about the balance, but it is not clear what you want me to do. Is it checking the balance, or talking to a colleague who speaks Gujarati? If neither fits, I can bring in a colleague._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SYS-01 (ladder rung 3: second clarification, with the offer of a person who speaks the language) |
| KB / tools | KB: KB-ESC-020@1.0.0 (0.60); retrieval confidence 0.60; decision answer |
| Action | clarify: second and last clarification (max_clarification_turns 2), different wording from T4, with the human offer |
| Generation | template `TPL-GEN-CLARIFY/second_attempt@1.1.0` (language hi); patterns: P4; anti-pattern check: none |
| State | phase CLARIFY; auth otp_verified; turn_count 6; topic_stack [ACC-001 (current_balance): active (candidate, not yet confirmed)]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: clarify_attempts 2; turns_since_resolution 6; escalation_proximity 0.10 |

### T7 | Customer

> મને ગુજરાતી બોલતા કોઈ સહયોગી સાથે વાત કરવી છે.

_English gloss (annotation only, not customer-facing; not native-reviewed): I want to talk to a colleague who speaks Gujarati._

| Field | Value |
|---|---|
| NLU | intent `GEN-003` 0.88 (tertiary first_request); runner-up none above 0.20; entities: language=gu; language: gu 0.93 (script gujarati) |
| Sentiment | raw 0.00, smoothed -0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: XTR-01 (request 1) with a language flag; the Input Guard screened native text and the English pivot |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLARIFY > ESCALATING; auth otp_verified; turn_count 7; topic_stack [GEN-003 (first_request): active, ACC-001: parked]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: human_requests 1; turns_since_resolution 7; escalation_proximity 0.30 |
| Decision point | XTR-01 request 1. The balance question stays parked in state and travels with the request. |

### T8 | Agent

> अभी गुजराती बोलने वाले कोई सहयोगी उपलब्ध नहीं हैं। मैं आपको अभी हिंदी या अंग्रेज़ी में जोड़ सकता हूँ, या गुजराती में कॉलबैक का अनुरोध कर सकता हूँ। आप क्या पसंद करेंगे?

_English gloss (annotation only, not customer-facing; not native-reviewed): No colleague who speaks Gujarati is available right now. I can connect you now in Hindi or English, or request a callback in Gujarati. What would you prefer?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no availability promised) |
| KB / tools | KB: KB-ESC-003@2.0.0 (0.70); retrieval confidence 0.70; decision answer<br>router: queue=Next Available Agent (24x7, open); skills available now: hi, en; no gu-speaking agent free; wanted_language=गुजराती |
| Action | escalate: XTR-01 handoff paused for the language choice (P2 never waits for a language match longer than the choice, and P0 never waits at all, D-121) |
| Generation | template `TPL-ESC-LANGUAGE-CHOICE/default@1.0.0` (language hi); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth otp_verified; turn_count 8; topic_stack [GEN-003 (first_request): active, ACC-001: parked]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: human_requests 1; turns_since_resolution 8; escalation_proximity 0.30 |

### T9 | Customer

> કૉલબૅક ગુજરાતીમાં જ કરો.

_English gloss (annotation only, not customer-facing; not native-reviewed): Do the callback in Gujarati only._

| Field | Value |
|---|---|
| NLU | dialogue act choose_option 0.90 (callback in Gujarati); active intent `CMP-005` (schedule_callback, implied); runner-up: n/a; entities: language=gu; language: gu 0.92 (script gujarati) |
| Sentiment | raw 0.05, smoothed 0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth otp_verified; turn_count 9; topic_stack [GEN-003 (first_request): active, ACC-001: parked]; slots {reply_language=hi (customer choice)}; pending_confirmation schedule_callback, awaiting confirmation; counters: human_requests 1; turns_since_resolution 9; escalation_proximity 0.30 |

### T10 | Agent

> मैं आपके पंजीकृत संपर्क (फ़ोन 4471 पर समाप्त) पर कॉलबैक का अनुरोध कर सकता हूँ। कॉलबैक का समय एक अनुरोध है और बदल सकता है। क्या मैं अनुरोध दर्ज करूँ? कृपया हाँ या नहीं में जवाब दें।

_English gloss (annotation only, not customer-facing; not native-reviewed): I can request a callback on your registered contact (phone ending 4471). A callback time is a request and may change. Shall I place the request? Please reply yes or no._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (masked contact), GR-OUT-05 |
| KB / tools | KB: KB-ESC-003@2.0.0 (0.72), KB-POL-007@1.0.0 (0.76); retrieval confidence 0.76; decision answer<br>tool: `get_profile_masked`() -> ok: {registered_phone: ending 4471} |
| Action | confirm: explicit confirmation before schedule_callback; the callback language is carried in the request |
| Generation | template `TPL-ESC-CALLBACK-OFFER/ask@1.0.0` (language hi); patterns: P3; anti-pattern check: none |
| State | phase CONFIRM; auth otp_verified; turn_count 10; topic_stack [GEN-003 (first_request): active, ACC-001: parked]; slots {reply_language=hi (customer choice)}; pending_confirmation schedule_callback, explicit, awaiting yes or no; counters: human_requests 1; turns_since_resolution 10; escalation_proximity 0.30 |

### T11 | Customer

> હા.

_English gloss (annotation only, not customer-facing; not native-reviewed): Yes._

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.93; active intent `CMP-005` (unchanged); runner-up: n/a; entities: none; language: gu 0.90 |
| Sentiment | raw 0.00, smoothed 0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth otp_verified; turn_count 11; topic_stack [GEN-003 (first_request): active, ACC-001: parked]; slots {reply_language=hi (customer choice)}; pending_confirmation schedule_callback, confirmed; counters: human_requests 1; turns_since_resolution 11; escalation_proximity 0.30 |

### T12 | Agent

> आपका कॉलबैक अनुरोध दर्ज हो गया है। संदर्भ: CBK-SYN-2901। अनुरोधित समय: 13 Oct 2026, 10:00 to 12:00 IST। यह एक अनुरोध है और वास्तविक समय अलग हो सकता है; हमारी बातचीत की पूरी जानकारी इसके साथ जाएगी।

_English gloss (annotation only, not customer-facing; not native-reviewed): Your callback request is placed. Reference: CBK-SYN-2901. Requested time: 13 Oct 2026, 10:00 to 12:00 IST. This is a request and the actual time may differ; the full details of our chat go with it._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the window is the tool's, stated as a request) |
| KB / tools | KB: KB-POL-007@1.0.0 (0.80); retrieval confidence 0.80; decision answer<br>tool: `schedule_callback`(team=Next Available Agent, language=gu, channel=registered contact (masked), idempotency_key=set) -> ok: {callback_reference: CBK-SYN-2901, requested_window: 13 Oct 2026, 10:00 to 12:00 IST} |
| Action | respond: callback request placed with the language flag; the parked balance question is in the attached summary |
| Generation | template `TPL-ESC-CALLBACK-OFFER/placed@1.0.0` (language hi); patterns: P4, P5; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 12; topic_stack [GEN-003 (first_request): active, ACC-001: parked]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: human_requests 1; turns_since_resolution 0; escalation_proximity 0.30 |

### T13 | Customer

> આભાર.

_English gloss (annotation only, not customer-facing; not native-reviewed): Thank you._

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.85 (tertiary thanks); runner-up none above 0.20; entities: none; language: gu 0.94 (script gujarati) |
| Sentiment | raw 0.30, smoothed 0.15, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth otp_verified; turn_count 13; topic_stack [GEN-003 (first_request): active, ACC-001: parked]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: human_requests 1; turns_since_resolution 1; escalation_proximity 0.30 |

### T14 | Agent

> आपका स्वागत है। नेक्सबैंक के साथ बैंकिंग करने के लिए धन्यवाद। अपना ध्यान रखिए।

_English gloss (annotation only, not customer-facing; not native-reviewed): You're welcome. Thank you for banking with NexBank. Take care._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.15 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close in the chosen reply language |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language hi); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 14; topic_stack [GEN-003 (first_request): active, ACC-001: parked]; slots {reply_language=hi (customer choice)}; pending_confirmation none; counters: human_requests 1; turns_since_resolution 2; escalation_proximity 0.30 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved by callback request at the customer's choice; the balance request was never served (A5.3 false-resolution guard: not counted as resolved) |
| Messages | 14 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.10, 0.00, -0.05, 0.00, 0.05, 0.00, 0.30]; final smoothed 0.15 |
| Escalation record | XTR-01, basis explicit_human_request with human_requests 1 and language gu, fired at T7; priority P2, queue Next Available Agent, SLA under 10 min, handoff mode warm, cancellable customer_only; secondary triggers: none; result: no Gujarati-speaking colleague free, the customer chose a callback in Gujarati (cancellation by the customer), callback request placed at T12 with the full conversation attached. ESC-003 and XTR-04 were not met. |
| CSAT / check-in | Not asked now: the callback is pending; the survey follows the callback (csat-signals.md section 3.1). |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | not applicable: no customer message carried a problem or a negative emotion |
| P2 | Progressive Disclosure | shown at T4 |
| P3 | Confirmation-Before-Action | shown at T10 |
| P4 | Graceful Degradation | shown at T2, T4, T6, T8, T12 |
| P5 | Context Carry-Over | shown at T8, T12, T14. the original request for the balance is held in state across the whole ladder and carried to the callback |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 7 agent messages, no two consecutive ones identical, no text sent three times | T2, T4, T6 |
| AP2 | Information Dump | absent: longest agent message is 63 words (cap `atk_output_max_words`); one concept per message | T2, T4 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T8, T12 |
| AP4 | Premature Escalation | absent: the human request at T7 was the customer's own; the language offer at T2 and T6 were the specified ladder steps, not escalations | none at risk |
| AP5 | Empathy Bypass | not at risk: no customer message carried a problem or a negative emotion | none |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); the session started at otp_verified | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 3 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T10, T12 |
