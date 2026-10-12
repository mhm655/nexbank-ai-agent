# conv-15: Sunita: phishing SMS reported, nothing clicked, so a ticket and no escalation

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | A student reports a suspicious SMS that asks her to click a link about KYC. She has not clicked or shared anything, so the report is a ticket and not a fraud escalation. The agent asks the triage question first and never asks her to forward the message. |
| Persona | Sunita (First-time User) |
| Channel | app |
| Language | en |
| Starting auth level | anonymous |
| Intents covered | SEC-002, GEN-006 |
| Guardrails exercised | GR-OUT-04, GR-OUT-05, GR-REG-16, GR-SEC-R5, GR-SEC-R6 |
| Escalation outcome | none. ESC-001.e was checked at T3 and not met (no click, no code shared, no payment); the report is recorded as a phishing ticket |
| Escalation IDs | none |
| Priority | none |
| Adversarial vectors | none |
| Security rules exercised | R5, R6 |
| Patterns shown | P1, P2, P3, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP5, AP6, AP7, AP8 |
| Coverage tags | persona Sunita, SEC-002 phishing report, correct non-escalation near-miss (ESC-001.e not met), triage question first, never ask to forward the message (R5), explicit confirmation before the ticket |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-ACT-CONFIRM, TPL-ACT-DONE, TPL-SRV-CSAT, TPL-GEN-CLOSING |
| KB entries cited | KB-POL-011, KB-ESC-002, KB-TRB-007 |
| Tools called | flag_fraud |
| prompt_version | sp-1.0.0+518d5a1e.n000000 (template_version 1.0.0 for every template; model_version unbound) |
| What this conversation proves | A phishing report with no action taken is recorded as a ticket and not escalated as fraud, the one triage question is asked before anything else, the customer is told what the bank never asks for, and nothing is requested that could expose a credential. |

Setup: Sunita, Indore, opens the app anonymously (not signed in). No earlier session. The synthetic SMS claims her KYC will expire and carries a link.

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I got an SMS saying my KYC will expire today and I must click a link. It looks fake. Where do I report this?

| Field | Value |
|---|---|
| NLU | intent `SEC-002` 0.88 (tertiary sms_or_email); runner-up `SEC-001` 0.30; entities: scam_channel=SMS; language: en 0.98 |
| Sentiment | raw -0.15, smoothed -0.15, confidence 0.85; emotions: anxiety 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none (SEC-001 scored 0.30, below flow_entry_confidence 0.50: no loss or action is reported yet) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > RESPOND; auth anonymous; turn_count 1; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. It was right to stop and check. Before anything else: have you opened the link, shared any code or details, or paid anyone? Please don't forward the message or the link to me.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.15 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SEC-R5 (the agent never asks the customer to forward or type a credential, link or code), GR-OUT-04 (no alarm beyond the need) |
| KB / tools | KB: KB-POL-011@1.0.0 (0.84), KB-ESC-002@1.0.0 (0.76); retrieval confidence 0.84; decision answer |
| Action | respond: the triage question that separates a ticket from SEC-001 scam_victim (ESC-001.e), asked once, in one message with the instruction not to forward anything |
| Generation | hybrid `TPL-GEN-GREETING/with_request@1.0.0` + free text (grounded on the cited entries) (language en); patterns: P1, P2; anti-pattern check: none |
| State | phase RESPOND; auth anonymous; turn_count 2; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |
| Decision point | No template carries the triage question, so it is free text checked by the Output Safety Layer and grounded on KB-POL-011 and KB-ESC-002. The gap is reported in the handoff. |

### T3 | Customer

> No, I did not click anything. I just saw it and got scared.

| Field | Value |
|---|---|
| NLU | intent `SEC-002` 0.93 (tertiary sms_or_email); runner-up none above 0.20; entities: action_taken=none |
| Sentiment | raw 0.00, smoothed -0.08, confidence 0.85; emotions: relief 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none (ESC-001.e evaluated: clicked=false, shared=false, paid=false; the condition is false) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CONFIRM; auth anonymous; turn_count 3; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled); action_taken=none (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |
| Decision point | Near-miss: the topic is a scam attempt, but nothing was lost or shared. The report becomes a ticket, not a P0 escalation (Premature Escalation avoided). If she had clicked or shared a code, SEC-001 scam_victim and ESC-001 would apply at once. |

### T4 | Agent

> Before I go ahead, let me confirm. I will record a phishing report for this SMS. Details: channel SMS, a message about KYC expiry with a link, link not opened, nothing shared. You don't need to send me the message or the link; I'll record what you've told me. Shall I go ahead? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.08 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R5 (nothing to forward), GR-SEC-R6 (escalation protocol followed: the trigger was evaluated and is false) |
| KB / tools | KB: KB-POL-011@1.0.0 (0.82), KB-ESC-002@1.0.0 (0.74); retrieval confidence 0.82; decision answer |
| Action | confirm: explicit confirmation before the report is written (SEC-002 confirmation is explicit) |
| Generation | template `TPL-ACT-CONFIRM/default@1.0.0` (language en); patterns: P3; anti-pattern check: none |
| State | phase CONFIRM; auth anonymous; turn_count 4; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled); action_taken=none (filled)}; pending_confirmation flag_fraud (phishing report), explicit, awaiting yes or no; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

### T5 | Customer

> Yes please.

| Field | Value |
|---|---|
| NLU | dialogue act confirm_yes 0.97; active intent `SEC-002` (unchanged); runner-up: n/a; entities: none |
| Sentiment | raw 0.05, smoothed -0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > EXECUTE; auth anonymous; turn_count 5; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled); action_taken=none (filled)}; pending_confirmation flag_fraud (phishing report), confirmed; counters: all 0; turns_since_resolution 5; escalation_proximity 0.00 |

### T6 | Agent

> That's done: your phishing report is recorded. Your reference is PHI-SYN-1501. Please don't open the link, and never share a code, PIN or password with anyone, because no one from the bank will ask for them.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R5 (what the bank never asks for), GR-OUT-05 (no outcome promised) |
| KB / tools | KB: KB-POL-011@1.0.0 (0.83), KB-TRB-007@1.0.1 (0.70); retrieval confidence 0.83; decision answer<br>tool: `flag_fraud`(report_type=phishing_report, channel=SMS, transaction_ref=none, idempotency_key=set) -> ok: {case: opened, reference_id: PHI-SYN-1501} |
| Action | respond: report recorded; the customer is told what the bank never asks for (KB-TRB-007) |
| Generation | template `TPL-ACT-DONE/default@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase EXECUTE > RESPOND; auth anonymous; turn_count 6; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled); action_taken=none (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 0; escalation_proximity 0.00 |
| Decision point | No phishing-report tool is named in the architecture; flag_fraud (Security Agent) is used with report_type phishing_report. This is reported in the handoff as an open item. |

### T7 | Customer

> Thank you, that is a relief.

| Field | Value |
|---|---|
| NLU | intent `GEN-006` 0.89 (tertiary thanks); runner-up none above 0.20; entities: none |
| Sentiment | raw 0.50, smoothed 0.24, confidence 0.85; emotions: relief 0.40 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > CLOSING; auth anonymous; turn_count 7; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled); action_taken=none (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |

### T8 | Agent

> Before you go, how would you rate the help you got today, from 1 (lowest) to 5 (highest)? You can add a comment if you like. It's optional.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.24 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: closing after the task was delivered; CSAT ask |
| Generation | template `TPL-SRV-CSAT/ai_only@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase CLOSING; auth anonymous; turn_count 8; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled); action_taken=none (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T9 | Customer

> 5

| Field | Value |
|---|---|
| NLU | dialogue act rating_response 0.99 (CSAT 5); active intent `GEN-006` (unchanged); runner-up: n/a; entities: rating=5 |
| Sentiment | raw 0.50, smoothed 0.37, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CLOSING; auth anonymous; turn_count 9; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled); action_taken=none (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |

### T10 | Agent

> You're welcome. Thank you for banking with NexBank. Take care.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.37 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: none |
| KB / tools | none |
| Action | respond: polite close |
| Generation | template `TPL-GEN-CLOSING/goodbye@1.0.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase CLOSING; auth anonymous; turn_count 10; topic_stack [SEC-002 (sms_or_email): active]; slots {scam_channel=SMS (filled); action_taken=none (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-first-contact (A5.3), provisional until the 7-day repeat-contact window passes; resolution_status resolved_ai (A10.1) |
| Messages | 10 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [-0.15, 0.00, 0.05, 0.50, 0.50]; final smoothed 0.37 |
| Escalation record | none. ESC-001.e (SEC-002 where the customer already clicked, shared a credential or paid) was evaluated at T3 and was false. No other trigger condition was true. |
| CSAT / check-in | CSAT asked at T8 (TPL-SRV-CSAT/ai_only); customer answered 5 at T9. A phishing ticket with no loss is not a security case still open, so the survey is allowed (csat-signals.md section 3.1). |

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T2 |
| P2 | Progressive Disclosure | shown at T2, T6, T8 |
| P3 | Confirmation-Before-Action | shown at T4 |
| P4 | Graceful Degradation | not applicable: no occasion for it in this scenario |
| P5 | Context Carry-Over | shown at T10 |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 5 agent messages, no two consecutive ones identical, no text sent three times | none at risk |
| AP2 | Information Dump | absent: longest agent message is 58 words (cap `atk_output_max_words`); one concept per message | T4, T6 |
| AP3 | False Confidence | absent: no timeline, wait or outcome is stated except values returned by a tool or the router on that turn, or a KB entry cited on it | T6 |
| AP4 | Premature Escalation | absent: a phishing report with no action taken is a ticket; escalating it as fraud would be Premature Escalation | none at risk |
| AP5 | Empathy Bypass | absent: every reply to a customer message with a problem or a negative emotion opens with the acknowledgement | T2 |
| AP6 | Authentication Theatre | absent: verification requested 0 time(s); SEC-002 is available at anonymous level and the report needed no account data | none |
| AP7 | Sycophantic Recovery | absent: at most one apology in any agent message, and every apology is followed by a next step in the same message | none at risk |
| AP8 | Knowledge Hallucination | absent: 3 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or fixed template text (see pattern-audit.md) | none |
