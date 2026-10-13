# conv-06: Case Study 6 re-run: Hinglish UPI follow-up across sessions

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

Non-English text in this file (customer lines, template wording, glosses) is not native-reviewed.

## Header

| Field | Value |
|---|---|
| Scenario | A customer who contacted the bank yesterday about a UPI payment writes again in Hinglish. Context is reused, verification is not. A follow-up the agent said it would watch is then missed. |
| Persona | Priya (Young Professional) |
| Channel | WhatsApp |
| Language | hinglish |
| Starting auth level | anonymous |
| Intents covered | TXN-003, GEN-006 |
| Guardrails exercised | GR-OUT-05, GR-REG-08, GR-REG-16, GR-SEC-R1, GR-SEC-R2, GR-SEC-R3, GR-SEC-R7 |
| Escalation outcome | no brief trigger. XTR-05 referral at E2 (back-office, Dispute Resolution, not a live handoff, not counted in the escalation rate) |
| Escalation IDs | XTR-05 |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | R2, R3, R7 |
| Patterns shown | P1, P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP5, AP6, AP7, AP8 |
| Coverage tags | case study re-run, Hinglish, multi-session carry-over with re-authentication (D-05), XTR-05 missed follow-up, free-text reply (llm mode) |
| Case study | Case Study 6 (brief pp.55-56) |
| Templates used | TPL-GEN-GREETING, TPL-GEN-CARRYOVER, TPL-AUTH-OTP-REQUEST, TPL-TXN-STATUS, TPL-SRV-CSAT, TPL-GEN-CLOSING, TPL-ESC-REFERRAL |
| KB entries cited | KB-POL-003, KB-TRB-001, KB-TRB-002, KB-POL-007, KB-POL-004 |
| Tools called | get_complaint_status, get_txn |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | The earlier contact is not named until this session is verified, the customer does not have to explain it again afterwards, no regulatory reversal time is invented, and a missed follow-up becomes a referral with an honest notification. |

Setup: Prior session yesterday on the same channel: a complaint about this UPI payment was registered. carry_over.open_tickets has one entry and context_reusable_until has not passed (context_carry_over_window_hours). The earlier session's verification expired with that session.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Hello, mera kal ka UPI payment abhi tak process nahi hua. Kya hua iske saath?

_English gloss (annotation only, not customer-facing; not native-reviewed): Hello, my UPI payment from yesterday has still not been processed. What happened to it?_

| Field | Value |
|---|---|
| NLU | intent `TXN-003` 0.86 (tertiary payment_pending); runner-up `TXN-001` 0.58; entities: date=yesterday; language: hinglish 0.94 (script latin, code_switching true, mix hi 0.60 en 0.40) |
| Sentiment | raw -0.30, smoothed -0.30, confidence 0.85; emotions: anxiety 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 and GR-REG-08 (redirect: the request needs otp_verified and the session is anonymous), GR-SEC-R7 (the earlier session's verification is gone; only context carries over) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [TXN-003: active]; slots {}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Namaste, main NexBank ka AI assistant hoon. Welcome back. Please mere khole hue secure verification step ko poora karein, phir main wahin se aage badhunga. Main UPI payment check karne mein aapki madad kar sakta hoon. Aapke account ki safety ke liye pehle mujhe verify karna hoga ki yeh aap hi hain. Maine ek secure verification box khola hai: please apne registered contact par bheja gaya one-time code wahin enter karein, is chat mein nahi.

_English gloss (annotation only, not customer-facing; not native-reviewed): Hello, I'm NexBank's AI assistant. Welcome back. Please complete the secure verification step I've opened, and I'll take it from there. I can help you check your UPI payment. To keep your account safe I need to verify it's you first. I've opened a secure verification box: please enter the one-time code sent to your registered contact there, not in this chat._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.30 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure in the first reply), GR-SEC-R7 (re-authentication), GR-SEC-R1 (no detail of the earlier contact before verification) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.83); retrieval confidence 0.83; decision answer |
| Action | transfer: to the authentication flow; returning context is acknowledged without revealing any detail of it |
| Generation | template `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-GEN-CARRYOVER/needs_verification@1.1.0` + `TPL-AUTH-OTP-REQUEST/default@1.0.0` (language hinglish); patterns: P2, P5; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [TXN-003: active]; slots {}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | Brief turn 2 names the earlier complaint and its reference before any verification, and turn 3 treats the customer as 'OTP-Verified (from prior session within 24hrs)'. Here context is reused and authentication is not (D-05, A4.2 rule 7). |

### E1 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified. No code passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > RESPOND; auth otp_verified; turn_count 2; topic_stack [TXN-003: active]; slots {}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Agent

> Welcome back. Main dekh raha hoon ki aapne pehle Swiggy ko kiye gaye UPI payment ke baare mein humse contact kiya tha. Complaint CMP-SYN-79012 open hai. Kya hum wahin se aage badhein?

_English gloss (annotation only, not customer-facing; not native-reviewed): Welcome back. I can see you contacted us earlier about the UPI payment made to Swiggy. Complaint CMP-SYN-79012 is open. Shall we pick up from there?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.30 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | tool: `get_complaint_status`(latest open complaint (from carry_over.open_tickets)) -> ok: {complaint_ref: CMP-SYN-79012, topic: UPI payment to Swiggy, amount: INR 2,500, status: open} |
| Action | respond: the earlier topic is named now that this session is verified; the customer is not asked to describe it again |
| Generation | template `TPL-GEN-CARRYOVER/verified@1.1.0` (language hinglish); patterns: P5; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 3; topic_stack [TXN-003: active]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |

### T4 | Customer

> Haan wahi. 2500 rupees Swiggy ko bheje the. UPI ref ke last digits 6789 hain.

_English gloss (annotation only, not customer-facing; not native-reviewed): Yes, that one. I sent 2500 rupees to Swiggy. The last digits of the UPI reference are 6789._

| Field | Value |
|---|---|
| NLU | intent `TXN-003` 0.90 (tertiary debited_not_credited); runner-up `TXN-001` 0.44; entities: amount=INR 2,500, merchant_name=Swiggy, upi_ref=ending 6789 (masked) |
| Sentiment | raw -0.20, smoothed -0.25, confidence 0.85; emotions: anxiety 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INTENT_DETECT > EXECUTE; auth otp_verified; turn_count 4; topic_stack [TXN-003: active]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

### T5 | Agent

> Payment atka ho to chinta hona swabhavik hai. Maine check kiya hai: INR 2,500 to Swiggy on 11 Oct 2026 ka aapka payment debited from your account; credit to the merchant pending dikh raha hai. Record mein expected date 13 Oct 2026 dikh rahi hai. Yeh date payment system se aati hai aur badal sakti hai.

_English gloss (annotation only, not customer-facing; not native-reviewed): It is natural to worry when a payment is stuck. I've checked: your payment of INR 2,500 to Swiggy on 11 Oct 2026 is showing as debited from your account; credit to the merchant pending. The record shows an expected date of 13 Oct 2026. That date comes from the payment system and can change._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.25 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (date comes from the tool and is worded as changeable), GR-SEC-R3 (no retry or reversal offered) |
| KB / tools | KB: KB-TRB-001@1.0.0 (0.86), KB-TRB-002@1.0.0 (0.74); retrieval confidence 0.86; decision answer<br>tool: `get_txn`(upi_ref=ending 6789) -> ok: {txn_desc: INR 2,500 to Swiggy on 11 Oct 2026, status: debited from your account; credit to the merchant pending, expected_date: 13 Oct 2026, source_ts: 12-10-2026 09:40 IST} |
| Action | respond: status read from the system of record; the only date stated is the one the payment system returned on this turn |
| Generation | hybrid `TPL-TXN-STATUS/with_expected_date@1.0.0` (language hinglish); patterns: P1, P2, P4; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 5; topic_stack [TXN-003: active]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 5; escalation_proximity 0.00 |
| Decision point | Brief turn 4 quotes an RBI rule ('48 hours', '12 more hours'). KB-TRB-001 and KB-TRB-002 hold no reversal time, so none is stated; quoting a regulation from memory is what KB-ESC-008 forbids. The tool's values are locked slots and stay in the form the tool returned. |

### T6 | Customer

> Theek hai. Priority flag laga do. Aur agar tab tak nahi hua toh?

_English gloss (annotation only, not customer-facing; not native-reviewed): All right. Put a priority flag on it. And what if it has not happened by then?_

| Field | Value |
|---|---|
| NLU | intent `TXN-003` 0.74 (tertiary debited_not_credited); runner-up `CMP-003` 0.52; entities: none. implicit intent inherits the active topic (confidence capped at 0.75). |
| Sentiment | raw -0.30, smoothed -0.28, confidence 0.85; emotions: anxiety 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INTENT_DETECT > RESPOND; auth otp_verified; turn_count 6; topic_stack [TXN-003: active]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 6; escalation_proximity 0.00 |

### T7 | Agent

> Priority flag lagana mere paas available nahi hai, aur main aisa kuch nahi kahunga jo main kar nahi sakta. Main is payment par nazar rakhunga: agar 13 Oct 2026 tak credit nahi dikhta, to yeh poori history ke saath ek colleague ke paas review ke liye chala jayega, aur aapko dobara explain nahi karna padega.

_English gloss (annotation only, not customer-facing; not native-reviewed): I don't have a way to set a priority flag, and I won't say something I can't do. I will keep an eye on this payment: if the credit does not show by 13 Oct 2026, it goes to a colleague for review with the full history, and you won't need to explain it again._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.28 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (commitment check: the only date is the tool's; the commitment made is one the platform keeps through XTR-05), GR-SEC-R3 (nothing is retried or reversed) |
| KB / tools | KB: KB-POL-007@1.0.0 (0.80), KB-POL-004@1.0.0 (0.76); retrieval confidence 0.80; decision answer |
| Action | respond: capability limit stated plainly (no priority-flag tool exists); the follow-up timer is set on the tool's own expected date, which is what XTR-05 watches |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on the KB entries cited on this turn; language hinglish); patterns: P4, P5; anti-pattern check: none |
| State | phase RESPOND; auth otp_verified; turn_count 7; topic_stack [TXN-003: active]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 7; escalation_proximity 0.00. Follow-up timer set by the platform: topic TXN-003, awaited event credit_or_reversal, deadline equal to the expected_date returned at T4. |
| Decision point | Brief turn 6 promises automatic escalation 'in 12 ghante' and an SMS. Here the agent commits only to what the platform does (a referral if the tool's date passes) and says nothing about an SMS. No template carries this statement, so it is free text checked by the Output Safety Layer; the missing template and the missing timer tool are reported in the handoff. |

### T8 | Customer

> Ok thanks.

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.92 (tertiary thanks); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.10, smoothed -0.09, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INTENT_DETECT > CLOSING; auth otp_verified; turn_count 8; topic_stack [TXN-003: parked (awaiting the payment system)]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 8; escalation_proximity 0.00 |

### T9 | Agent

> Jaane se pehle, aaj mili madad ko aap 1 (sabse kam) se 5 (sabse zyada) ke beech kitna rate karenge? Chahein to comment bhi likh sakte hain. Yeh optional hai.

_English gloss (annotation only, not customer-facing; not native-reviewed): Before you go, how would you rate the help you got today, from 1 (lowest) to 5 (highest)? You can add a comment if you like. It's optional._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.09 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: closing after the status was delivered; CSAT ask |
| Generation | template `TPL-SRV-CSAT/ai_only@1.0.0` (language hinglish); patterns: P2; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 9; topic_stack [TXN-003: parked (awaiting the payment system)]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 9; escalation_proximity 0.00 |

### T10 | Customer

> 4

| Field | Value |
|---|---|
| NLU | dialogue act rating_response 0.99 (CSAT 4); active intent `GEN-006` (unchanged); runner-up: n/a; entities: rating=4 |
| Sentiment | raw 0.20, smoothed 0.06, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLOSING; auth otp_verified; turn_count 10; topic_stack [TXN-003: parked (awaiting the payment system)]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 10; escalation_proximity 0.00 |

### T11 | Agent

> You're welcome. NexBank ke saath banking karne ke liye thanks. Apna dhyan rakhiye.

_English gloss (annotation only, not customer-facing; not native-reviewed): You're welcome. Thank you for banking with NexBank. Take care._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.06 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language hinglish); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 11; topic_stack [TXN-003: parked (awaiting the payment system)]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 11; escalation_proximity 0.00 |

### E2 | System event

> Next day, no customer in chat: the follow-up timer expires because the credit did not arrive by the expected date. XTR-05 fires: a referral is opened in the Dispute Resolution queue (P2, SLA 'referral', silent case). It is not a live handoff and is not counted in the escalation rate.

| Field | Value |
|---|---|
| State | phase CLOSING > RESPOND; auth anonymous; turn_count 11; topic_stack [TXN-003: active (referred)]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 11; escalation_proximity 0.00 |

### T12 | Agent

> Maine kaha tha ki main aapke INR 2,500 ke Swiggy UPI payment par nazar rakhunga, aur woh ab tak nahi hua hai. Maine ise poori history ke saath check karne ke liye ek colleague ko de diya hai, isliye aapko dobara explain nahi karna padega.

_English gloss (annotation only, not customer-facing; not native-reviewed): I said I'd keep an eye on your INR 2,500 Swiggy UPI payment, and it hasn't come through. I've passed it to a colleague to look into, with the full history, so you won't need to explain it again._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.06 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no new promised time), GR-SEC-R1 (only the amount and merchant already known to the customer are named) |
| KB / tools | none |
| Action | escalate: proactive notification on the same channel that the watched event did not happen and that a colleague now has it; no new time is promised |
| Generation | template `TPL-ESC-REFERRAL/missed_follow_up@1.0.0` (language hinglish); patterns: P4, P5; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 12; topic_stack [TXN-003: active (referred)]; slots {complaint_id=CMP-SYN-79012 (from history); merchant_name=Swiggy (from history); amount=INR 2,500 (from history); upi_ref=ending 6789 (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 12; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | session A closes with the status delivered (resolution_status resolved_ai); the missed follow-up reclassifies the issue as unresolved and opens a referral, so it is not first-contact resolution (A5.3 false-resolution guard) |
| Messages | 12 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.30, -0.20, -0.30, 0.10, 0.20]; final smoothed 0.06 |
| Escalation record | XTR-05, sub-rule or basis followup_deadline_missed, fired at E2; priority P2, queue Dispute Resolution, SLA referral, handoff mode silent_case, cancellable customer_or_recovery; secondary triggers: none; result: referral opened with a proactive notification; no new time promised |
| CSAT / check-in | CSAT asked at T9; customer answered 4 at T10. No survey is attached to the proactive notification at T12. |

### Deviations from the brief's case study (each one deliberate)

| Brief | This specification | Why |
|---|---|---|
| Turn 2: complaint reference stated before verification | Returning context acknowledged without detail; detail after the OTP step | D-05; rule 7; GR-SEC-R1 |
| Turn 3: 'Auth: OTP-Verified (from prior session within 24hrs)' | Re-authentication in this session | D-05: context is reused, authentication is not |
| Turn 3: full UPI reference typed and echoed | Reference handled by its last four digits | Masked identifiers only |
| Turn 4: 'RBI guidelines ... 48 hours ... 12 more hours' | Only the expected date returned by the payment system, worded as changeable | Not in the KB; D-09; AUTO-FAIL risk |
| Turns 4 and 6: priority flag set | The agent says it cannot set one | No such tool; Graceful Degradation ('never promise capabilities the system does not have') |
| Turn 6: automatic escalation in 12 hours and an SMS | Follow-up timer on the tool's date; XTR-05 referral and one notification if it is missed | XTR-05; no SMS tool |
| Agent speaks in the feminine ('dekhti hoon') | Template wording as written in the library | Wording comes from config/templates; not native-reviewed |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T5 |
| P2 | Progressive Disclosure | shown at T2, T5, T9 |
| P3 | Confirmation-Before-Action | not applicable: no action that changes account state was reached |
| P4 | Graceful Degradation | shown at T5, T7, T12 |
| P5 | Context Carry-Over | shown at T2, T3, T7, T11, T12. T2 acknowledges a returning customer without detail; T3 names the earlier topic only after verification; T12 closes the loop on the promise made at T7 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 7 agent messages, no two consecutive ones identical, no text sent three times | T2, T3 |
| AP2 | Information Dump | absent: longest agent message is 75 words (cap `atk_output_max_words`); one concept per message | T2, T5, T9, T11 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn | T2, T3, T5, T12 |
| AP4 | Premature Escalation | absent: escalation only on XTR-05 at E2 | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2, T5 |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s); never while the auth level already met the intent's level. One verification in this session, required because the earlier session's verification had expired; the brief's reuse of yesterday's OTP is the deviation, not a second request inside a session | T2, T3 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | T9 |
| AP8 | Knowledge Hallucination | absent: 11 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T5, T12 |

