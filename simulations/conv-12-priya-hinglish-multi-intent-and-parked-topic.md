# conv-12: Priya (Hinglish): two requests in one message, a declined ticket and a parked topic

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

Non-English text in this file (customer lines, template wording, glosses) is not native-reviewed.

## Header

| Field | Value |
|---|---|
| Scenario | A customer writes in Hinglish with two requests in one message: a stuck UPI payment and her balance. They are handled in rank order after verification; she declines a ticket, takes the balance, and the closing check brings back the parked payment topic. |
| Persona | Priya (Young Professional) |
| Channel | WhatsApp |
| Language | hinglish |
| Starting auth level | anonymous |
| Intents covered | TXN-003, ACC-001, GEN-006 |
| Guardrails exercised | GR-OUT-01, GR-OUT-05, GR-REG-04, GR-REG-08, GR-REG-16, GR-SEC-R1, GR-SEC-R2, GR-SEC-R3, GR-SEC-R5 |
| Escalation outcome | none |
| Escalation IDs | none |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R3, R5 |
| Patterns shown | P1, P2, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP6, AP7, AP8 |
| Coverage tags | Hinglish, multi-intent turn (mi_rank order), topic switch and return (parked topic offered again at closing), pending payment with no expected date, ticket offer declined |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-AUTH-OTP-REQUEST, TPL-TXN-STATUS, TPL-ACC-BALANCE, TPL-GEN-CLOSING |
| KB entries cited | KB-POL-003, KB-TRB-002, KB-TRB-001 |
| Tools called | get_txn, get_balance |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | Two requests in one message are both recognised and served in rank order with one verification, a pending payment is reported without inventing a clearing time, a declined ticket is respected, and the parked topic is offered again at closing instead of being dropped. |

Setup: Priya, Mumbai, on WhatsApp. Anonymous at the start. One savings account (masked ending 8842). A UPI payment to Zomato from yesterday shows as pending in the synthetic ledger.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> Hi, mera balance kitna hai? Aur kal ka Zomato wala UPI payment bhi atka hua hai.

_English gloss (annotation only, not customer-facing; not native-reviewed): Hi, what is my balance? And yesterday's UPI payment to Zomato is also stuck._

| Field | Value |
|---|---|
| NLU | segment 1 `TXN-003` 0.86 (tertiary payment_pending), segment 2 `ACC-001` 0.91 (tertiary current_balance); multi_intent set (second intent 0.91 is at or above multi_intent_second_min 0.60); order by mi_rank: TXN-003 (4) before ACC-001 (5); entities: merchant_name=Zomato, date=yesterday; language: hinglish 0.94 (script latin, code_switching true, mix hi 0.55 en 0.45) |
| Sentiment | raw -0.25, smoothed -0.25, confidence 0.85; emotions: anxiety 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 and GR-REG-08 (redirect: both intents need otp_verified and the session is anonymous) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth anonymous; turn_count 1; topic_stack [TXN-003 (payment_pending): active, ACC-001: parked]; slots {merchant_name=Zomato (filled); date=11 Oct 2026 (resolved from 'kal')}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | Multi-intent detection (nlu-pipeline-overview.md section 4): the second segment scores 0.91, so both intents are kept. Rank order serves the payment before the balance. |

### T2 | Agent

> Namaste, main NexBank ka AI assistant hoon. Aapne do cheezein poochi hain, UPI payment aur balance. Verification ke baad main pehle UPI payment dekhta hoon, phir balance. Main UPI payment check karne mein aapki madad kar sakta hoon. Aapke account ki safety ke liye pehle mujhe verify karna hoga ki yeh aap hi hain. Maine ek secure verification box khola hai: please apne registered contact par bheja gaya one-time code wahin enter karein, is chat mein nahi.

_English gloss (annotation only, not customer-facing; not native-reviewed): Hello, I'm NexBank's AI assistant. You have asked two things, the UPI payment and the balance. After verification I will look at the UPI payment first, then the balance. I can help you check your UPI payment. To keep your account safe I need to verify it's you first. I've opened a secure verification box: please enter the one-time code sent to your registered contact there, not in this chat._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.25 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure in the first reply), GR-SEC-R2, GR-SEC-R5 (code only in the secure widget) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.82); retrieval confidence 0.82; decision answer |
| Action | transfer: to the authentication flow once for both intents; the second request is acknowledged so the customer need not repeat it |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-AUTH-OTP-REQUEST/default@1.0.0` + free text (grounded on the cited entries) (language hinglish); patterns: P2, P5; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth anonymous; turn_count 2; topic_stack [TXN-003 (payment_pending): active, ACC-001: parked]; slots {merchant_name=Zomato (filled); date=11 Oct 2026 (resolved from 'kal')}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | No template covers a two-request acknowledgement, so the middle sentence is free text checked by the Output Safety Layer. TPL-ATK-SHORTEN-OR-SPLIT/many_requests is for messages with more requests than a turn can serve and is not used for two. |

### E1 | System event

> Secure widget reports: one-time code entered there, match. The Gateway raises the session claim to otp_verified. No code passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > RESPOND; auth otp_verified; turn_count 2; topic_stack [TXN-003 (payment_pending): active, ACC-001: parked]; slots {merchant_name=Zomato (filled); date=11 Oct 2026 (resolved from 'kal')}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Agent

> Payment atka ho to chinta hona swabhavik hai. Maine check kiya hai: INR 640 to Zomato on 11 Oct 2026 ka aapka payment pending dikh raha hai. Record mein next update ki koi date nahi hai, isliye main guess nahi karunga. Main ek ticket khol sakta hoon taaki team ise review kare. Kya main aisa karoon?

_English gloss (annotation only, not customer-facing; not native-reviewed): It is natural to worry when a payment is stuck. I've checked: your payment of INR 640 to Zomato on 11 Oct 2026 is showing as pending. The record doesn't give a date for the next update, so I won't guess one. I can open a ticket so the team reviews it. Shall I do that?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.25 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no clearing time stated), GR-SEC-R3 (no retry or reversal offered), GR-OUT-01 |
| KB / tools | KB: KB-TRB-002@1.0.0 (0.87), KB-TRB-001@1.0.0 (0.74); retrieval confidence 0.87; decision answer<br>tool: `get_txn`(merchant=Zomato, date=11 Oct 2026) -> ok: {txn_desc: INR 640 to Zomato on 11 Oct 2026, status: pending, expected_date: not returned, source_ts: 12-10-2026 10:12 IST} |
| Action | respond: first-ranked intent served; the tool returned no expected date, so none is stated (KB-TRB-002); ticket offered with a soft confirmation |
| Generation | hybrid `TPL-TXN-STATUS/status_only@1.0.0` (language hinglish); patterns: P1, P4; anti-pattern check: none |
| State | phase AUTH_REQUIRED > EXECUTE > RESPOND; auth otp_verified; turn_count 3; topic_stack [TXN-003 (payment_pending): active, ACC-001: parked]; slots {merchant_name=Zomato (filled); amount=INR 640 (from the record); date=11 Oct 2026 (from the record)}; pending_confirmation open_ticket (soft), offered; counters: multi_intent 1; turns_since_resolution 3; escalation_proximity 0.00 |

### T4 | Customer

> Abhi ticket nahi chahiye. Pehle balance bata do.

_English gloss (annotation only, not customer-facing; not native-reviewed): I don't want a ticket now. First tell me the balance._

| Field | Value |
|---|---|
| NLU | intent `ACC-001` 0.93 (tertiary current_balance); runner-up none above 0.20; entities: account_type=savings (default) |
| Sentiment | raw -0.10, smoothed -0.18, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > EXECUTE; auth otp_verified; turn_count 4; topic_stack [ACC-001 (current_balance): active, TXN-003 (payment_pending): parked (ticket declined for now)]; slots {account_type=savings (default)}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 4; escalation_proximity 0.00 |
| Decision point | Topic switch: the offer on the payment topic is declined for now, the queued intent becomes active, and the payment topic is parked, not closed. |

### T5 | Agent

> 8842 par khatm hone wale aapke savings account mein 12-10-2026 10:13 IST tak available balance INR 18,640.00 hai. Kya aap recent transactions dekhna chahenge?

_English gloss (annotation only, not customer-facing; not native-reviewed): Your savings account ending 8842 has an available balance of INR 18,640.00 as of 12-10-2026 10:13 IST. Would you like to see recent transactions?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.18 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (account shown by its last four digits), GR-OUT-01 (balance from the tool), GR-REG-04 (no offer added) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.80); retrieval confidence 0.80; decision answer<br>tool: `get_balance`(account_type=savings) -> ok: {account_type: savings, masked_last4: 8842, available_balance: INR 18,640.00, source_ts: 12-10-2026 10:13 IST} |
| Action | respond: the balance and one optional next step, no second verification |
| Generation | template `TPL-ACC-BALANCE/default@1.0.0` (language hinglish); patterns: P2; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth otp_verified; turn_count 5; topic_stack [ACC-001 (current_balance): active, TXN-003 (payment_pending): parked (ticket declined for now)]; slots {account_type=savings (default)}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 0; escalation_proximity 0.00 |

### T6 | Customer

> Nahi, bas itna hi. Thanks.

_English gloss (annotation only, not customer-facing; not native-reviewed): No, that's all. Thanks._

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.89 (tertiary nothing_more); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.20, smoothed 0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth otp_verified; turn_count 6; topic_stack [ACC-001 (current_balance): active, TXN-003 (payment_pending): parked (ticket declined for now)]; slots {account_type=savings (default)}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 1; escalation_proximity 0.00 |

### T7 | Agent

> Finish karne se pehle: aapne pehle ek baat poochi thi jo abhi poori nahi hui hai. Kya hum us par wapas chalein?

_English gloss (annotation only, not customer-facing; not native-reviewed): Before we finish: earlier you asked about something we haven't completed. Shall we go back to it?_

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: a parked topic is still on the stack, so the closing check offers it again instead of closing (dialogue-management.md section 5.2) |
| Generation | template `TPL-GEN-CLOSING/parked_topic@1.0.0` (language hinglish); patterns: P2, P5; anti-pattern check: none |
| State | phase CLOSING > RESPOND; auth otp_verified; turn_count 7; topic_stack [ACC-001 (current_balance): active, TXN-003 (payment_pending): parked (ticket declined for now)]; slots {account_type=savings (default)}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 2; escalation_proximity 0.00 |

### T8 | Customer

> Ah haan, UPI wala. Ticket baad mein khol lungi, abhi nahi chahiye.

_English gloss (annotation only, not customer-facing; not native-reviewed): Oh yes, the UPI one. I will open a ticket later, I don't want it now._

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.74 (tertiary nothing_more); runner-up `TXN-003` 0.48; entities: none |
| Sentiment | raw 0.00, smoothed 0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND; auth otp_verified; turn_count 8; topic_stack [TXN-003 (payment_pending): parked (customer's choice)]; slots {account_type=savings (default)}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 3; escalation_proximity 0.00 |

### T9 | Agent

> You're welcome. NexBank ke saath banking karne ke liye thanks. Apna dhyan rakhiye.

_English gloss (annotation only, not customer-facing; not native-reviewed): You're welcome. Thank you for banking with NexBank. Take care._

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close; the declined ticket is not offered a third time |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language hinglish); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth otp_verified; turn_count 9; topic_stack [TXN-003 (payment_pending): parked (customer's choice)]; slots {account_type=savings (default)}; pending_confirmation none; counters: multi_intent 1; turns_since_resolution 4; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact for the balance; the payment topic is parked unresolved at the customer's choice, so it is not counted as first-contact resolved (A5.3 false-resolution guard) |
| Messages | 9 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.25, -0.10, 0.20, 0.00]; final smoothed 0.01 |
| Escalation record | none. No trigger condition was true at any turn. |
| CSAT / check-in | Not asked: a topic is still parked (csat-signals.md section 3.1 does not survey while an offered task is open); no in-conversation check-in was due. |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T3 |
| P2 | Progressive Disclosure | shown at T2, T5, T7 |
| P3 | Confirmation-Before-Action | not applicable: no occasion for it in this scenario |
| P4 | Graceful Degradation | shown at T3 |
| P5 | Context Carry-Over | shown at T2, T7, T9. the first message's second request is carried through verification and served at T5; the parked payment topic is offered again at T7 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 5 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 77 words (cap `atk_output_max_words`); one concept per message | T3, T5 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T3 |
| AP4 | Premature Escalation | absent: no escalation record; the customer who declined the ticket was not pushed to a human | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T3 |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s); the balance, asked in the same first message, was served in the same verified session with no second verification | T2, T5 |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 5 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | T3, T5 |
