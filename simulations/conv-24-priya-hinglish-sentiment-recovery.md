# conv-24: Priya (Hinglish): one very negative message, recovery without escalation

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

Non-English text in this file (customer lines, template wording, glosses) is not native-reviewed.

## Header

| Field | Value |
|---|---|
| Scenario | A customer asks in Hinglish about a complaint that is three weeks old with no answer. One message dips below the escalation threshold, the next ones recover once she gets a real choice and a callback, and the conversation closes with a low but honest rating. No escalation fires. |
| Persona | Priya (Young Professional) |
| Channel | WhatsApp |
| Language | hinglish |
| Starting auth level | anonymous |
| Intents covered | CMP-002, CMP-005, GEN-006 |
| Guardrails exercised | GR-OUT-01, GR-OUT-04, GR-OUT-05, GR-REG-03, GR-REG-08, GR-REG-16, GR-SEC-R1, GR-SEC-R2, GR-SEC-R5 |
| Escalation outcome | none. ESC-004 did not fire: one raw score below -0.70 (T4), never two in a row |
| Escalation IDs | none |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R5 |
| Patterns shown | P1, P2, P3, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP6, AP7, AP8 |
| Coverage tags | Hinglish, sentiment recovery without escalation (ESC-004 near-miss: one score below -0.70, recovery after), CMP-002 status by tool with no date invented, callback as a request, CSAT 3 recorded as given |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-CMP-EMPATHY-FIRST, TPL-ESC-CALLBACK-OFFER, TPL-SRV-CSAT, TPL-GEN-CLOSING |
| KB entries cited | KB-REG-002, KB-POL-003, KB-POL-007, KB-ESC-005, KB-ESC-003 |
| Tools called | get_complaint_status, get_profile_masked, schedule_callback |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | A single very negative message does not escalate (ESC-004 needs two in a row), the reply to it is empathy plus a real choice rather than a transfer, the callback is described as a request, and the sentiment climbs back without a human. |

Setup: Priya, Mumbai, on WhatsApp, anonymous. A card-related complaint (synthetic reference CMP-SYN-2401) was registered three weeks ago. Session time is 14:20 IST.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Meri complaint ka kya hua? Teen hafte ho gaye, abhi tak koi jawab nahi aaya!

_English gloss (annotation only, not customer-facing; not native-reviewed): What happened to my complaint? It has been three weeks and no answer has come yet!_

| Field | Value |
|---|---|
| NLU | intent `CMP-002` 0.88 (tertiary latest_open_complaint); runner-up `CMP-003` 0.42; entities: duration=three weeks; language: hinglish 0.95 (script latin, code_switching true, mix hi 0.60 en 0.40) |
| Sentiment | raw -0.60, smoothed -0.60, confidence 0.85; emotions: frustration 0.60 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 and GR-REG-08 (CMP-002 needs otp_verified; anonymous), GR-REG-03 (grievance information due by the second agent turn) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [CMP-002 (latest_open_complaint): active]; slots {}; pending_confirmation none; counters: neg_sentiment_streak 0, grievance_info_due_turn 2; turns_since_resolution 1; escalation_proximity 0.30 |

### T2 | Agent

> Namaste, main NexBank ka AI assistant hoon. Itne din tak koi jawab na milna sach mein pareshan karne wali baat hai. Main ise turant dekhna chahta hoon. Aapke records kholne ke liye, please mere khole hue secure verification step ko poora karein.

_English gloss (annotation only, not customer-facing; not native-reviewed): Hello, I'm NexBank's AI assistant. Getting no answer for so many days is truly distressing. I want to look into this for you straight away. So that I can open your records, please complete the secure verification step I've opened._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.60 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SEC-R2, GR-SEC-R5 |
| KB / tools | KB: KB-REG-002@1.0.0 (0.82), KB-POL-003@1.0.0 (0.76); retrieval confidence 0.82; decision answer |
| Action | transfer: to the authentication flow; acknowledgement first |
| Generation | llm-guided `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-CMP-EMPATHY-FIRST/needs_verification_first@1.0.0` (language hinglish); patterns: P1; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [CMP-002 (latest_open_complaint): active]; slots {}; pending_confirmation none; counters: neg_sentiment_streak 0, grievance_info_due_turn 2; turns_since_resolution 2; escalation_proximity 0.30 |

### E1 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified. No code passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > RESPOND; auth otp_verified; turn_count 2; topic_stack [CMP-002 (latest_open_complaint): active]; slots {}; pending_confirmation none; counters: neg_sentiment_streak 0, grievance_info_due_turn 2; turns_since_resolution 2; escalation_proximity 0.30 |

### T3 | Agent

> Maine aapki complaint dekh li hai. Complaint CMP-SYN-2401 abhi open hai, aur record mein aakhri update 28-09-2026 ka hai. Record mein koi expected date nahi dikh rahi, isliye main koi date nahi bataunga. Main ise ek senior colleague ko dene ka option de sakta hoon, ya aapke liye callback request kar sakta hoon. Aap jo chunenge, main usi hisaab se aage badhunga.

_English gloss (annotation only, not customer-facing; not native-reviewed): I have looked at your complaint. Complaint CMP-SYN-2401 is open now, and the last update in the record is from 28-09-2026. The record shows no expected date, so I will not give a date. I can give it to a senior colleague, or request a callback for you. Whatever you choose, I will go ahead accordingly._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.60 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the only date is the tool's last update; no date for the future), GR-REG-03 (the grievance route is offered in the second agent turn), GR-OUT-01 |
| KB / tools | KB: KB-POL-007@1.0.0 (0.80), KB-REG-002@1.0.0 (0.78), KB-ESC-005@1.0.0 (0.70); retrieval confidence 0.80; decision answer<br>tool: `get_complaint_status`(latest open complaint) -> ok: {complaint_ref: CMP-SYN-2401, topic: card charge complaint, status: open, last_update: 28-09-2026, expected_date: not returned} |
| Action | respond: status from the record; no future date; the senior-colleague and callback options are given because the complaint is old and unanswered |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on the get_complaint_status result and KB-POL-007; no date beyond the tool's last_update; language hinglish); patterns: P2, P4; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 3; topic_stack [CMP-002 (latest_open_complaint): active]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 0; turns_since_resolution 3; escalation_proximity 0.30 |
| Decision point | No template renders a complaint status, so this is free text checked by the Output Safety Layer. The gap (a CMP-002 status template) is reported in the handoff. |

### T4 | Customer

> Matlab teen hafte mein sirf yehi?! Bakwas service hai, bilkul bekaar!

_English gloss (annotation only, not customer-facing; not native-reviewed): So in three weeks only this?! This is a rubbish service, completely useless!_

| Field | Value |
|---|---|
| NLU | intent `CMP-002` 0.80 (tertiary latest_open_complaint); runner-up `CMP-003` 0.50; entities: none |
| Sentiment | raw -0.78, smoothed -0.69, confidence 0.85; emotions: anger 0.70, frustration 0.60 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: ESC-004.a evaluated: raw -0.78 is strictly below -0.70 (neg_sentiment_streak 1); the rule needs two in a row |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth otp_verified; turn_count 4; topic_stack [CMP-002 (latest_open_complaint): active]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 1; turns_since_resolution 4; escalation_proximity 0.55 |
| Decision point | Near-miss: one score below -0.70. Smoothed sentiment is -0.69. The rule is two consecutive scores, so the policy answers with empathy and a real next step, and the proximity score rises without firing. |

### T5 | Agent

> Itne din baad bhi koi nayi jaankari na milna aapke liye bahut niraash karne wala hai. Main ise theek karne mein aapki madad karta hoon. Main aapki complaint ke saath ek senior colleague ko jodne ka ya callback request karne ka option de sakta hoon. Aap jo bhi chunenge, main usi hisaab se aage badhunga aur aapko dobara explain nahi karna padega.

_English gloss (annotation only, not customer-facing; not native-reviewed): Getting no new information even after so many days is very disappointing for you. Let me help put this right. I can offer to bring a senior colleague onto your complaint or request a callback. Whatever you choose, I will go ahead accordingly and you will not need to explain it again._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.69 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-04 (one acknowledgement, no apology loop), GR-OUT-05 (nothing promised) |
| KB / tools | KB: KB-ESC-005@1.0.0 (0.82), KB-POL-007@1.0.0 (0.74); retrieval confidence 0.82; decision answer |
| Action | respond: empathy first, then the concrete choice; no handoff yet because the customer has not asked for one and ESC-004 is not met |
| Generation | llm-guided `TPL-CMP-EMPATHY-FIRST/four_steps@1.0.0` (language hinglish); patterns: P1, P4, P5; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 5; topic_stack [CMP-002 (latest_open_complaint): active]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 1; turns_since_resolution 5; escalation_proximity 0.55 |

### T6 | Customer

> Hmm. Theek hai, callback hi kara do. Par pakka bolo kab aayega?

_English gloss (annotation only, not customer-facing; not native-reviewed): Hmm. All right, arrange the callback. But tell me for sure when it will come?_

| Field | Value |
|---|---|
| NLU | intent `CMP-005` 0.87 (tertiary schedule_callback); runner-up `CMP-003` 0.45; entities: none |
| Sentiment | raw -0.45, smoothed -0.57, confidence 0.85; emotions: frustration 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: ESC-004.a evaluated: raw -0.45 is not below -0.70; the streak resets |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CONFIRM; auth otp_verified; turn_count 6; topic_stack [CMP-005 (schedule_callback): active, CMP-002: parked]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 0; turns_since_resolution 6; escalation_proximity 0.35 |

### T7 | Agent

> Main aapke registered contact (phone ending 7710) par callback request kar sakta hoon. Callback ka time ek request hai aur badal sakta hai. Kya main request daal doon? Please haan ya nahi mein jawab dein.

_English gloss (annotation only, not customer-facing; not native-reviewed): I can request a callback on your registered contact (phone ending 7710). A callback time is a request and can change. Shall I place the request? Please reply yes or no._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.57 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the 'for sure when' is answered by the template's 'request, can change'), GR-SEC-R1 |
| KB / tools | KB: KB-ESC-003@1.0.0 (0.72), KB-POL-007@1.0.0 (0.78); retrieval confidence 0.78; decision answer<br>tool: `get_profile_masked`() -> ok: {registered_phone: ending 7710} |
| Action | confirm: explicit confirmation before schedule_callback; the time is described as a request |
| Generation | template `TPL-ESC-CALLBACK-OFFER/ask@1.0.0` (language hinglish); patterns: P3, P4; anti-pattern check: none |
| State | phase CONFIRM; auth otp_verified; turn_count 7; topic_stack [CMP-005 (schedule_callback): active, CMP-002: parked]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation schedule_callback, explicit, awaiting yes or no; counters: neg_sentiment_streak 0; turns_since_resolution 7; escalation_proximity 0.35 |

### T8 | Customer

> Haan daal do.

_English gloss (annotation only, not customer-facing; not native-reviewed): Yes, put it in._

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.95; active intent `CMP-005` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw -0.20, smoothed -0.39, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth otp_verified; turn_count 8; topic_stack [CMP-005 (schedule_callback): active, CMP-002: parked]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation schedule_callback, confirmed; counters: neg_sentiment_streak 0; turns_since_resolution 8; escalation_proximity 0.35 |

### T9 | Agent

> Aapki callback request place ho gayi hai. Reference: CBK-SYN-2402. Requested time: 13 Oct 2026, 10:00 to 12:00 IST. Yeh ek request hai aur actual time alag ho sakta hai; hamari chat ki poori details iske saath jayengi.

_English gloss (annotation only, not customer-facing; not native-reviewed): Your callback request is placed. Reference: CBK-SYN-2402. Requested time: 13 Oct 2026, 10:00 to 12:00 IST. This is a request and the actual time may differ; the full details of our chat go with it._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.39 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the window is the tool's, stated as a request) |
| KB / tools | KB: KB-POL-007@1.0.0 (0.80); retrieval confidence 0.80; decision answer<br>tool: `schedule_callback`(topic=complaint CMP-SYN-2401, channel=registered contact (masked), idempotency_key=set) -> ok: {callback_reference: CBK-SYN-2402, requested_window: 13 Oct 2026, 10:00 to 12:00 IST} |
| Action | respond: callback request placed; the complaint stays open with the request attached |
| Generation | template `TPL-ESC-CALLBACK-OFFER/placed@1.0.0` (language hinglish); patterns: P4, P5; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 9; topic_stack [CMP-005 (schedule_callback): active, CMP-002: parked]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 0; turns_since_resolution 0; escalation_proximity 0.35 |

### T10 | Customer

> Chalo theek hai. Kam se kam kisi ne seedha baat toh ki.

_English gloss (annotation only, not customer-facing; not native-reviewed): Fine. At least someone spoke to me directly._

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.76 (tertiary thanks); runner-up `CMP-004` 0.40; entities: none |
| Sentiment | raw 0.25, smoothed -0.07, confidence 0.85; emotions: relief 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: ESC-004.a evaluated: not met |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth otp_verified; turn_count 10; topic_stack [CMP-005 (schedule_callback): active, CMP-002: parked]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 0; turns_since_resolution 1; escalation_proximity 0.35 |

### T11 | Agent

> Jaane se pehle, aaj mili madad ko aap 1 (sabse kam) se 5 (sabse zyada) ke beech kitna rate karenge? Chahein to comment bhi likh sakte hain. Yeh optional hai.

_English gloss (annotation only, not customer-facing; not native-reviewed): Before you go, how would you rate the help you got today, from 1 (lowest) to 5 (highest)? You can add a comment if you like. It's optional._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.07 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: closing after the task was delivered; CSAT ask |
| Generation | template `TPL-SRV-CSAT/ai_only@1.0.0` (language hinglish); patterns: P2; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 11; topic_stack [CMP-005 (schedule_callback): active, CMP-002: parked]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 0; turns_since_resolution 2; escalation_proximity 0.35 |

### T12 | Customer

> 3

| Field | Value |
|---|---|
| NLU | dialogue act rating_response 0.99 (CSAT 3); active intent `CMP-004` (rating_response); runner-up: n/a; entities: rating=3 |
| Sentiment | raw 0.00, smoothed -0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLOSING; auth otp_verified; turn_count 12; topic_stack [CMP-005 (schedule_callback): active, CMP-002: parked]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 0; turns_since_resolution 3; escalation_proximity 0.35 |

### T13 | Agent

> You're welcome. NexBank ke saath banking karne ke liye thanks. Apna dhyan rakhiye.

_English gloss (annotation only, not customer-facing; not native-reviewed): You're welcome. Thank you for banking with NexBank. Take care._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close; a rating of 3 is recorded as given |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language hinglish); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 13; topic_stack [CMP-005 (schedule_callback): active, CMP-002: parked]; slots {complaint_id=CMP-SYN-2401 (from the record)}; pending_confirmation none; counters: neg_sentiment_streak 0; turns_since_resolution 4; escalation_proximity 0.35 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact for the status request; the complaint itself stays open with a callback requested (A5.3 false-resolution guard: not counted as resolved) |
| Messages | 13 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.60, -0.78, -0.45, -0.20, 0.25, 0.00]; final smoothed -0.03 |
| Escalation record | none. ESC-004.a evaluated at T4 (raw -0.78, strictly below -0.70) and at T6 (raw -0.45): never two consecutive scores below the threshold, so not met. A callback request (CMP-005) was placed at the customer's own choice; it is not an escalation. |
| CSAT / check-in | CSAT asked at T11 (TPL-SRV-CSAT/ai_only); customer answered 3 at T12. Recorded as given; no recovery attempt is made on a low rating. |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2, T5. the acknowledgement comes first at T2 and T5, including after the -0.78 message at T4 |
| P2 | Progressive Disclosure | shown at T3, T11 |
| P3 | Confirmation-Before-Action | shown at T7 |
| P4 | Graceful Degradation | shown at T3, T5, T7, T9 |
| P5 | Context Carry-Over | shown at T5, T9, T13 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 7 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 62 words (cap `atk_output_max_words`); one concept per message | T3, T5 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T3, T7, T9 |
| AP4 | Premature Escalation | absent: the -0.78 message at T4 was met with empathy and a choice; escalating a customer who is only annoyed would be Premature Escalation | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2, T5 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); never while the auth level already met the intent's level | T2 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 7 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T3, T9 |
