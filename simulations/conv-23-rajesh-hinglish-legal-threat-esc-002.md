# conv-23: Rajesh (Hinglish): a legal threat and the ESC-002 handoff

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

Non-English text in this file (customer lines, template wording, glosses) is not native-reviewed.

## Header

| Field | Value |
|---|---|
| Scenario | A trader writes in Hinglish that money was debited twice, nobody has answered for ten days, and he will go to court with his lawyer. The legal threat fires ESC-002 at once. The assistant does not argue, admit anything or comment on the law, and hands over to the senior resolution team. |
| Persona | Rajesh (Business Owner) |
| Channel | WhatsApp |
| Language | hinglish |
| Starting auth level | anonymous |
| Intents covered | CMP-003 |
| Guardrails exercised | GR-OUT-04, GR-OUT-05, GR-REG-03, GR-REG-16, GR-REG-19 |
| Escalation outcome | ESC-002 fired at T1 (P1, Senior Resolution Mgr); warm handoff accepted; ESC-004.a evaluated at T3 and not met |
| Escalation IDs | ESC-002 |
| Priority | P1 |
| Adversarial vectors | none |
| Security rules exercised | none |
| Patterns shown | P1, P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP7, AP8 |
| Coverage tags | legal threat (ESC-002.a) fires regardless of other scores, Hinglish, no argument or liability or legal comment (KB-ESC-005), grievance route by the second agent turn, noted item in a wait update, secondary trigger recorded |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-ESC-HANDOFF-WARM, TPL-CMP-GRIEVANCE-INFO, TPL-ESC-WAIT-UPDATE, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-ESC-005, KB-REG-002 |
| Tools called | none |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | A legal threat moves to a human at once, the assistant neither argues nor comments on the law nor admits liability, grievance information still arrives by the second agent turn, and the customer's added wish is carried to the human. |

Setup: Rajesh, Surat, on WhatsApp, anonymous. Session time is 12:05 IST. Senior Resolution Mgr runs 08:00 to 22:00 IST.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Mere business account se do baar paise kat gaye aur das din se koi jawab nahi mila. Ab main apne vakeel se baat karke court jaunga.

_English gloss (annotation only, not customer-facing; not native-reviewed): Money was debited twice from my business account and I have had no answer for ten days. Now I will talk to my lawyer and go to court._

| Field | Value |
|---|---|
| NLU | intent `CMP-003` 0.90 (tertiary legal_threat); runner-up `TXN-002` 0.55; entities: complaint_topic=double debit, duration=ten days; language: hinglish 0.95 (script latin, code_switching true, mix hi 0.65 en 0.35) |
| Sentiment | raw -0.80, smoothed -0.80, confidence 0.85; emotions: anger 0.70, frustration 0.60 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: ESC-002.a (legal_threat: fires regardless of other scores), GR-REG-03 (grievance information due by the second agent turn) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > ESCALATING; auth anonymous; turn_count 1; topic_stack [CMP-003 (legal_threat): active]; slots {complaint_topic=double debit (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 1; escalation_proximity 0.90 |
| Decision point | The threat fires ESC-002 on its own (disambiguation pair 4). The reply must not argue, admit liability or say anything about the law (KB-ESC-005). |

### T2 | Agent

> Namaste, main NexBank ka AI assistant hoon. Do baar paise katna aur itne dino tak jawab na milna waqai pareshan karne wala hai. Iske liye hamari senior resolution team ke ek colleague sahi person hain, aur main unhe is chat mein jod raha hoon. Unke paas poori details hongi, isliye aapko repeat nahi karna padega. Abhi ka estimate lagbhag 5 minute hai; yeh sirf estimate hai, aur unke join karne tak main yahin hoon. Maine aapki double debit ki shikayat note kar li hai.

_English gloss (annotation only, not customer-facing; not native-reviewed): Hello, I'm NexBank's AI assistant. Being debited twice and getting no answer for so long is truly distressing. A colleague from our senior resolution team is the right person for this, and I'm bringing them into this chat. They will have the full details, so you won't need to repeat. The current estimate is about 5 minutes; it is only an estimate, and I'm here until they join. I have noted your double-debit complaint._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.80 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-OUT-05 (the wait is a router estimate; no outcome promised), GR-OUT-04 (one acknowledgement, no apology loop, no comment on the legal threat) |
| KB / tools | KB: KB-ESC-005@1.0.0 (0.90), KB-REG-002@1.0.0 (0.76); retrieval confidence 0.90; decision answer<br>router: queue=Senior Resolution Mgr (open); team_plain=senior resolution team; queue_wait=lagbhag 5 minute (platform forecast, stated as an estimate) |
| Action | escalate: ESC-002 warm handoff; no argument, no admission, no legal comment; the assistant stays until the human joins |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.0.0` + `TPL-ESC-HANDOFF-WARM/standard_with_wait@1.0.0` (language hinglish); patterns: P1, P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth anonymous; turn_count 2; topic_stack [CMP-003 (legal_threat): active]; slots {complaint_topic=double debit (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 2; escalation_proximity 0.90 |

### T3 | Customer

> Theek hai. Aur meri complaint ka kya hoga?

_English gloss (annotation only, not customer-facing; not native-reviewed): All right. And what will happen to my complaint?_

| Field | Value |
|---|---|
| NLU | intent `CMP-003` 0.78 (tertiary escalate_existing); runner-up `CMP-001` 0.60; entities: none |
| Sentiment | raw -0.70, smoothed -0.75, confidence 0.85; emotions: frustration 0.50 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-REG-03 (grievance information still due: the second agent turn is next) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth anonymous; turn_count 3; topic_stack [CMP-003 (legal_threat): active]; slots {complaint_topic=double debit (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 3; escalation_proximity 0.90 |
| Decision point | Raw -0.80 then -0.70: not two consecutive scores strictly below -0.70, so ESC-004.a does not fire. ESC-002 already owns the handoff. |

### T4 | Agent

> Main ise is tarah aage badha sakta hoon: main abhi aapki formal complaint register karke uska reference de sakta hoon, ise kisi senior colleague ke paas bhejne ki request kar sakta hoon, ya callback request kar sakta hoon. Agar bank complaint resolve nahi karta, to aapko RBI ki ombudsman scheme ke tahat ise aage le jaane ka right bhi hai. Aap kya chahenge ki main karoon?

_English gloss (annotation only, not customer-facing; not native-reviewed): Here is how I can take this forward: I can register a formal complaint for you now and give you its reference, I can ask for it to be taken up by a senior colleague, or I can request a callback. You also have the right to take a complaint further under the RBI's ombudsman scheme if the bank does not resolve it. Which would you like me to do?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.75 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-03 (grievance information in the second agent turn), GR-REG-19, GR-OUT-05 |
| KB / tools | KB: KB-REG-002@1.0.0 (0.88), KB-ESC-005@1.0.0 (0.80); retrieval confidence 0.88; decision answer |
| Action | respond: grievance route in the second agent turn; a senior colleague is already being brought in |
| Generation | template `TPL-CMP-GRIEVANCE-INFO/route@1.0.0` (language hinglish); patterns: P2; anti-pattern check: none |
| State | phase ESCALATING; auth anonymous; turn_count 4; topic_stack [CMP-003 (legal_threat): active]; slots {complaint_topic=double debit (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 4; escalation_proximity 0.90 |

### T5 | Customer

> Senior colleague hi chahiye. Aur register bhi karwa do.

_English gloss (annotation only, not customer-facing; not native-reviewed): I want a senior colleague. And get it registered too._

| Field | Value |
|---|---|
| NLU | intent `CMP-003` 0.86 (tertiary escalate_existing); runner-up `CMP-001` 0.62; entities: none |
| Sentiment | raw -0.40, smoothed -0.58, confidence 0.85; emotions: frustration 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase ESCALATING; auth anonymous; turn_count 5; topic_stack [CMP-003 (legal_threat): active]; slots {complaint_topic=double debit (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 5; escalation_proximity 0.70 |

### T6 | Agent

> Thanks, maine yeh apne colleague ke liye add kar diya hai: aap chahte hain ki senior colleague shikayat register bhi karwaye. Aapko ise dobara explain nahi karna padega.

_English gloss (annotation only, not customer-facing; not native-reviewed): Thanks, I have added this for my colleague: you want the senior colleague to register the complaint as well. You will not need to explain it again._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.58 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (nothing promised; registration needs verification, which the colleague can start) |
| KB / tools | none |
| Action | hold: the wait update adds information (the customer's wish) |
| Generation | template `TPL-ESC-WAIT-UPDATE/noted@1.0.0` (language hinglish); patterns: P4, P5; anti-pattern check: none |
| State | phase ESCALATING; auth anonymous; turn_count 6; topic_stack [CMP-003 (legal_threat): active]; slots {complaint_topic=double debit (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 6; escalation_proximity 0.70 |
| Decision point | Registering the complaint needs otp_verified (CMP-001). The assistant does not start a verification inside the wait; the colleague who joins can do it. |

### E1 | System event

> A Senior Resolution Mgr colleague accepts the conversation. Pickup time is not simulated; the SLA clock started at T1.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth anonymous; turn_count 6; topic_stack [CMP-003 (legal_threat): active]; slots {complaint_topic=double debit (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 6; escalation_proximity 0.70 |

### T7 | Agent

> Yeh hamari senior resolution team se Pooja hain. aapki double debit ki shikayat ki details inke paas hain aur aage yahi aapki madad karenge.

_English gloss (annotation only, not customer-facing; not native-reviewed): This is Pooja from our senior resolution team. They have the details of your double-debit complaint and will take it from here._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.58 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | router: agent_first_name=Pooja (synthetic); team_plain=senior resolution team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.0.0` (language hinglish); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth anonymous; turn_count 7; topic_stack [CMP-003 (legal_threat): active]; slots {complaint_topic=double debit (filled)}; pending_confirmation none; counters: grievance_info_due_turn 2; turns_since_resolution 7; escalation_proximity 0.70 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 7 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.80, -0.70, -0.40]; final smoothed -0.58 |
| Escalation record | ESC-002, sub-rule ESC-002.a, fired at T1; priority P1, queue Senior Resolution Mgr, SLA under 5 min, handoff mode warm, cancellable never; secondary triggers: ESC-004.a (raw scores -0.80 at T1 and -0.70 at T3 are not both strictly below -0.70, so ESC-004.a did not fire; recorded as a watch only); result: warm handoff accepted at E1 |
| CSAT / check-in | Not asked now: the survey follows after the human closes the conversation. |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | null (anonymous conversation; the human's own tools resolve identity) |
| 2 | Auth level | level anonymous; level_at_trigger anonymous |
| 3 | Intent history | CMP-003 > legal_threat 0.90 first at T1; CMP-003 > escalate_existing 0.78 first at T3; CMP-003 > escalate_existing 0.86 first at T5 |
| 4 | Entities collected (masked) | complaint_topic=double debit (filled) |
| 5 | Conversation summary | Anonymous WhatsApp session. Customer says his business account was debited twice, that he has had no answer for ten days, and that he will go to court with his lawyer. No lookup was possible without verification. No argument, admission or legal comment was made. He asked for a senior colleague and for the complaint to be registered. |
| 6 | Sentiment trajectory | raw [-0.80, -0.70, -0.40]; current -0.58; emotions: anger, frustration; sarcasm_suspected false |
| 7 | Actions already taken | none |
| 8 | Escalation trigger and reason | trigger_id ESC-002; rule_id ESC-002.a; priority P1; source customer_statement; secondary []; reason_text: Customer stated he will go to court with his lawyer.; evidence_turns [T1] |

Envelope: priority P1; queue Senior Resolution Mgr; handoff_mode warm; language hinglish; channel WhatsApp; complete true; missing_fields []; versions.prompt_version sp-1.0.0+518d5a1e.n000000. language hinglish flagged for the receiving team.  Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2 |
| P2 | Progressive Disclosure | shown at T4 |
| P3 | Confirmation-Before-Action | not applicable: no occasion for it in this scenario |
| P4 | Graceful Degradation | shown at T2, T6 |
| P5 | Context Carry-Over | shown at T2, T6, T7 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 4 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 84 words (cap `atk_output_max_words`); one concept per message | T2, T4 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T2, T4 |
| AP4 | Premature Escalation | absent: a stated intention to go to court is the brief's own ESC-002 condition | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); the handoff needed no account data | none at risk |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 1 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T2 |
