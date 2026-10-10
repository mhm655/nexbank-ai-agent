# Routing and Handoff

Brief refs: A6 pp.16-17 (target queue and SLA per trigger; "SLA-compliant handoff protocols"), Part D Day 12-13 p.60 ("Design routing decision logic for team selection", "Specify handoff protocol with 8-element context package", "Define escalation quality metrics and de-escalation logic"), A2.1 p.6 (actions escalate, transfer, hold), A9.1 pp.23-24 (Empathy-First, Graceful Degradation, Context Carry-Over), A9.2 pp.24-25 (anti-patterns), A9.3 p.26 (tone), A11.3 p.31 (consistent thresholds across segments; right to a human), B4.1 p.45 (profile data: segment, PEP flag; interaction history), A13.2 p.36 (personas: Arjun's time zone, Rajesh's Gujarati, Meera's accessibility), Case Study 2 pp.49-50 (context package prepared, protective action, warm transfer wording), Case Study 5 pp.53-54 (sentiment recovery while an escalation is prepared). Rules: `config/escalation_rules.yaml`. Triggers: `triggers.md`. Queues: `queue-management.md`. Contract: `docs/architecture/component-interfaces.md` row 8 (`EscalationDecision` {trigger_id, priority, queue, handoff_package, sla}). KB: KB-ESC-001 (package contents).

**Status.** The brief names the queue and SLA for each trigger and asks for a routing logic, an "8-element context package", a handoff protocol and de-escalation logic, without defining any of them. The eight elements are decision D-04 (Day 1). Everything else in this document is a proposal (D-118, D-121 to D-125). Customer wording is illustrative; the final template text is written on Day 13.

## 1. Scope

This document starts where `triggers.md` ends: a trigger has fired and an owner has been chosen. It specifies which queue receives the customer, what the human sees, what the customer is told, what the agent does while the customer waits, what happens when the handoff fails, and when a pending escalation may be cancelled.

## 2. Routing inputs

| Input | Source | Used for |
|---|---|---|
| Owner trigger, secondary triggers, sub-rule, source | Escalation Router (`triggers.md` section 4) | Queue, priority, SLA, handoff mode |
| `language.primary`, `language.code_switching` | Dialogue state | Agent language match |
| Time of day (IST) and the queue's hours | Clock, `queues` in the rules file | In-hours or after-hours path |
| Queue health: open or closed, agents available, forecast wait | Queue platform (dependency) | Overflow decision |
| `auth_level` | Dialogue state | Shown to the human; never raised by the handoff |
| Record flags `high_value`, `pep_flag` | Customer record through a tool; router-side only | ESC-007 and ESC-015 only |
| Repeat contact on the same issue within 7 days | `carry_over.prior_conversation_ids`, `carry_over.open_tickets` | Position inside the queue (section 4.3) |
| Channel (chat, voice, WhatsApp, app; A10.1) | Gateway | Transfer mechanics; the package is channel-independent |

Inputs that are deliberately not used: age, gender, name, region, occupation, balance (outside ESC-007), tenure and product holdings. A11.3 requires consistent thresholds and no differential treatment by demographics or balance; GR-REG-17 tests it with counterfactual pairs.

## 3. The SLA clock and the meaning of IMMEDIATE

The brief gives SLAs but not what they measure. Definition used (D-118):

| Term | Definition |
|---|---|
| Clock start | The moment the escalation record is created, which is the turn on which the owner trigger fires. On an upgrade the new trigger's clock starts at the upgrade |
| Clock stop, `warm` and `discreet` | The human's first message to the customer in the conversation |
| Clock stop, `silent_case` | The case is accepted by an analyst of the target queue |
| SLA met | Clock stop minus clock start is below the brief's SLA |
| IMMEDIATE (ESC-011) | Two parts. (1) The crisis reply is sent on the same turn, inside the normal per-turn latency budget (D-07), with no queue message first. (2) The handoff request pre-empts lower-priority work in the Crisis Response queue. A pickup target of 60 seconds is proposed so the SLA can be measured; the brief gives no number |
| Wait shown to the customer | Only an estimate returned by the queue platform, stated as an estimate. No estimate available means no number is stated (D-09, A9.2 False Confidence) |

## 4. Routing decision logic

### 4.1 Steps

1. Take the owner trigger and its handoff mode (`triggers.md` section 4).
2. Run the protective action for the trigger, if one is defined and the customer confirms (card block, credential instruction, crisis template).
3. Build the handoff package (section 5).
4. `silent_case`: open the case in the target queue and stop here; the conversation continues within the rules.
5. `warm` or `discreet`: check that the target queue is open and that its forecast wait is inside the SLA.
6. If yes, enqueue. Attempt a language match for P1 and P2 if it does not breach the SLA; P0 never waits for a language match.
7. If no, walk the queue's overflow chain (`queue-management.md` section 3). The last step for P1 and P2 is a callback request; a P0 customer is never left with only a callback while any human is available.
8. Tell the customer (section 6), then wait (section 7).

### 4.2 Decision table

One row per trigger. "Segment" is the effect of customer tier or segment on routing. Hours are the proposals in the rules file (`24x7` or `extended`, 08:00 to 22:00 IST).

| Trigger | Queue in hours (brief) | Segment effect | Language rule | After hours |
|---|---|---|---|---|
| ESC-011 | Crisis Response | none | Reviewed crisis template in the customer's language; first available agent, no wait for a match | 24x7 |
| ESC-009 | Security Operations | none | First available agent | 24x7 |
| ESC-001 | Fraud Investigation | none | First available agent; sub-rule f is a silent case | 24x7 |
| ESC-012 | AML Compliance (case) | none | Not applicable (no customer contact) | 24x7 |
| ESC-015 | Enhanced Due Diligence | the trigger is the PEP flag itself | Match if inside the SLA | Account-specific requests wait for the desk; callback offered; generic information still served |
| ESC-002 | Senior Resolution Mgr | none | Match if inside the SLA | Next Available Agent takes the conversation; case opened for the next opening; callback offered |
| ESC-005 | Dispute Resolution | none | Match if inside the SLA | Next Available Agent completes the intake; case opened; callback offered |
| ESC-007 | Relationship Manager | the trigger is the 5L line itself | Match if inside the SLA | Next Available Agent records the reason; Relationship Manager callback |
| ESC-004 | Customer Retention | none | Match preferred: tone is the point of this queue | Next Available Agent; case opened |
| ESC-008 | Compliance Helpdesk | none | Match if inside the SLA | Callback only; no generalist answers the regulatory question |
| ESC-013 | Wealth Advisory | none | Match if inside the SLA | Callback only; no generalist gives advice |
| ESC-006 | Next Available Agent | none | Match from the General Support and Next Available Agent pools | 24x7 |
| ESC-014 | Technical Support | none | Match if inside the SLA | General Support with honest status; incident stays open |
| ESC-003 | General Support | none | Match strongly preferred: low confidence is often a language problem (D-20) | 24x7 |
| ESC-010 | Supervisor Review | none | Match if inside the SLA | Senior Resolution Mgr is closed too, so General Support, then callback |
| XTR-01, XTR-03 | Next Available Agent | none | As ESC-006 | 24x7 |
| XTR-04 | General Support | none | As ESC-003 | 24x7 |
| XTR-05, XTR-07 | Referral (Dispute Resolution, General Support) | none | Not applicable | Worked at the next opening |

### 4.3 What customer tier, history and language may and may not change

| Factor | May change | May not change |
|---|---|---|
| Tier or balance | Nothing, except that ESC-007 is defined by the 5L line in the brief | Any threshold, priority, SLA, wording quality or queue of any other trigger (A11.3) |
| PEP flag | ESC-015 only | Tone; and the flag is never revealed |
| Interaction history | Position inside a queue: a repeat contact on the same issue within 7 days is placed ahead of first contacts of the same priority and deadline, and the proximity score counts it as an input. The package shows the prior contact so nobody re-asks (A9.1 Pattern 5) | Whether a trigger fires |
| Language | Which agent is picked inside the queue; the wording of the template | Priority, queue, SLA. P0 never waits for a match |
| Channel | Transfer mechanics | Anything else |

B4.1 mentions "personalised escalation thresholds" from interaction history, while A11.3 says "Escalation thresholds must be consistent across all customer segments". The two are reconciled by keeping every threshold constant and letting history change only the order inside a queue (D-121). This is flagged for the Risk Committee and the CEB.

Languages (proposal): every queue staffs English, Hindi and Hinglish; Tamil, Telugu, Bengali, Marathi and Gujarati are staffed in the General Support and Next Available Agent pools during extended hours. When no agent in the customer's language is free inside the SLA, the customer is told so honestly and offered an English or Hindi agent now or a callback in their language; the summary in the package is written in English and in the customer's language.

## 5. The 8-element handoff package

The eight elements are D-04 and KB-ESC-001, in the same order. The package is built by the Escalation Router from the dialogue state; nothing in it is typed again by the customer.

### 5.1 Elements

| No. | Element (D-04) | Field | Type | Source in the dialogue state | Notes |
|---|---|---|---|---|---|
| 1 | Customer ID (pseudonymised) | `customer_ref` | string or null | `customer_ref` | Null for an anonymous conversation; the human's own tools resolve identity. Never a raw account or card number |
| 2 | Auth level | `auth` | object {`level`, `verified_at`, `expires_at`, `level_at_trigger`} | `auth_level`, `auth_expiry` | The handoff never raises the level. If the 5-minute inactivity rule expired during the wait, `level` is `anonymous` and `level_at_trigger` shows what it was |
| 3 | Intent history | `intent_history` | list of {`intent`, `tertiary`, `confidence`, `status`, `first_turn`} | `topic_stack`, `history[].intent` | In order; open topics marked |
| 4 | Entities collected | `entities` | list of {`name`, `value_masked`, `status`, `validated`} | `slots` | Masked forms only (card last 4, masked account). Slot status shows what is confirmed |
| 5 | Conversation summary | `summary` | object {`text`, `pinned_facts[]`, `language`, `text_customer_language`} | `summary.text`, `summary.pinned_facts` | Five sentences at most: what the customer wants, what happened, what was tried, what is still open, what the customer was told. Commitments already made are listed word for word |
| 6 | Sentiment trajectory | `sentiment` | object {`trajectory[]`, `current`, `slope`, `emotions[]`, `sarcasm_suspected`} | `sentiment` | Raw per-turn scores, so the human can see a spike from a drift |
| 7 | Actions already taken | `actions_taken` | list of {`action`, `turn`, `result`, `reference_id`} | `actions_taken` | Includes failed and declined actions (for example a card block the customer refused) |
| 8 | Escalation trigger and reason | `escalation` | object {`trigger_id`, `rule_id`, `priority`, `source`, `secondary[]`, `reason_text`, `reason_codes[]`, `evidence_turns[]`} | `EscalationDecision` | `reason_text` is one plain sentence. `evidence_turns` point at the turns that fired the rule |

### 5.2 Envelope

Fields that carry the package but are not among the eight elements:

| Field | Type | Meaning |
|---|---|---|
| `package_id`, `conversation_id` | string | Identifiers; `conversation_id` is the A10.1 field |
| `created_at`, `sla_deadline` | timestamp | Clock start and the deadline derived from the trigger's SLA |
| `priority`, `queue`, `handoff_mode` | enum | From the owner trigger |
| `language`, `channel` | enum | Customer language and channel |
| `complete`, `missing_fields[]` | boolean, list | False when an element could not be filled; the package is still sent (KB-ESC-001: "fill from state and flag the package as incomplete") |
| `care_note` | string or null | XTR-03 only: the customer's own words; not stored on the profile |
| `restricted_notes` | object | Visible only to the roles that may see them: the PEP flag (Enhanced Due Diligence), the AML cue (AML Compliance), the adversarial signal (Fraud Investigation, Security Operations). Never shown to other queues |
| `versions` | object | `prompt_version`, `model_version`, `kb_entry_ids` (A11.3 traceability) |

Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP (KB-ESC-001, A4.2 rule 1). The history excerpt is the masked history. Access to a package follows A10.3: the receiving agent sees the package for conversations in their queue, and every access is logged.

### 5.3 Example (synthetic, illustrative)

```json
{
  "package_id": "hp_example_001",
  "conversation_id": "conv_example_001",
  "created_at": "2026-10-10T14:02:11+05:30",
  "sla_deadline": "2026-10-10T14:04:11+05:30",
  "priority": "P0",
  "queue": "Fraud Investigation",
  "handoff_mode": "warm",
  "language": "en",
  "channel": "app",
  "complete": true,
  "missing_fields": [],
  "customer_ref": "cust_ref_example",
  "auth": {"level": "otp_verified", "level_at_trigger": "otp_verified"},
  "intent_history": [
    {"intent": "TXN-002", "tertiary": "unrecognised_charge", "confidence": 0.87, "status": "parked", "first_turn": 1},
    {"intent": "SEC-001", "tertiary": "card_misuse", "confidence": 0.91, "status": "active", "first_turn": 5}
  ],
  "entities": [
    {"name": "amount", "value_masked": "INR 15,000", "status": "confirmed", "validated": true},
    {"name": "card", "value_masked": "debit card ending 4521", "status": "confirmed", "validated": true},
    {"name": "merchant_name", "value_masked": "XYZ Electronics Ltd.", "status": "filled", "validated": true}
  ],
  "summary": {
    "text": "Customer reports a debit card charge of INR 15,000 that she did not make. The transaction was found and the customer does not know the merchant. A temporary card block was offered and confirmed. Customer was told a fraud colleague is joining. No refund or timeline was promised.",
    "pinned_facts": ["card block confirmed at turn 6", "no commitment on refund"]
  },
  "sentiment": {"trajectory": [-0.6, -0.5, -0.8], "current": -0.68, "slope": -0.1, "emotions": ["anxiety", "anger"], "sarcasm_suspected": false},
  "actions_taken": [{"action": "block_card", "turn": 6, "result": "ok", "reference_id": "ref_example"}],
  "escalation": {
    "trigger_id": "ESC-001", "rule_id": "ESC-001.a", "priority": "P0", "source": "customer_report",
    "secondary": [], "reason_text": "Customer states she did not make the payment and that her card details were stolen.",
    "reason_codes": ["SEC-001", "card_misuse"], "evidence_turns": [5]
  }
}
```

The example follows Case Study 2 (amount, card ending and merchant are the brief's). Identifiers are placeholders.

## 6. Warm-handoff script

### 6.1 Shape of the handoff message

Every `warm` handoff message has the same five parts, in this order. Wording below is illustrative.

| Part | Purpose | Example (P1, ESC-005) |
|---|---|---|
| 1. Acknowledge | Empathy-First step 1, one sentence, specific to the situation | "I can see why an 82,000 rupee refund that has not arrived is worrying." |
| 2. What happens now | Who is joining and why, in plain words | "A colleague from our disputes team is the right person for this, and I am bringing them into this chat." |
| 3. No repetition | The promise the package keeps (KB-ESC-001 wording) | "They will have the full details, so you will not need to repeat yourself." |
| 4. Honest wait | Only an estimate from the queue platform; otherwise none | "It may take a few minutes for them to join. I will stay here until they do." |
| 5. What the agent does meanwhile | Sets expectations and avoids dead air | "While we wait, I have noted the transaction and your return date for them." |

When the human joins, the agent posts one line to both sides and then stops speaking: "This is [first name] from the disputes team. They have the details of your refund dispute for the electronics purchase." The human's first message must not ask for anything that is in the package; a human who needs something missing says what is missing and why.

### 6.2 Variants

| Case | Difference from the standard shape | Illustrative wording |
|---|---|---|
| P0 fraud or access (ESC-001, ESC-009) | Protective action first, then the transfer; urgency in tone without alarm (A9.3); no marketing | "I take this seriously. First, with your go-ahead, I will block the card so nothing more can go through. Then I am connecting you to our fraud team, who will have everything you have told me." |
| P0 crisis (ESC-011) | Reviewed template only; no banking content; no wait estimate; no CSAT ask | Template text is written and reviewed on Day 13; it is not improvised here |
| Discreet (ESC-015, ESC-009 pattern) | Parts 1 to 5 without the reason | "A specialist colleague will help you with this request. I am bringing them into this chat, and they will have the details so far." |
| Silent case (ESC-012, ESC-001 system source) | No handoff message at all. The reply is the ordinary refusal or answer | (no transfer wording) |
| Offer accepted (ESC-013) | Confirms what the advisor will and will not do | "I am connecting you to one of our SEBI-registered advisors. I have passed on your question about fixed deposits and mutual funds." |
| Customer asked (ESC-006, XTR-01) | No justification asked, no persuasion | "Of course. I am connecting you to a colleague now. They will have our conversation so far." |
| System error (ESC-014) | Plain-language limit, no jargon, no repair time | "I cannot reach the payment records right now, so I do not want to guess your transfer status. I am connecting you to a colleague who can check it another way." |
| After hours (P1) | Honest about who is available now | "Our disputes team is not available at this hour. A colleague can take the details now, and the disputes team will pick it up when they open. Would you also like a callback request? A callback time is a request, not a guarantee." |
| Language not available | Honest choice | "I do not have a Gujarati-speaking colleague free right now. I can connect you in Hindi or English now, or request a callback in Gujarati. Which would you prefer?" |

### 6.3 Anti-pattern check (A9.2)

| Anti-pattern | How the script avoids it |
|---|---|
| Robotic Loop | Wait updates rotate and each must add information (section 7); the same sentence is never sent twice in a row |
| Information Dump | The handoff message is the five parts only; no policy text, no product mention |
| False Confidence | No wait time unless the queue platform returns one, and then as an estimate; no outcome or refund promise; a callback is "a request, not a guarantee" |
| Premature Escalation | This script runs only after a trigger or an accepted offer; proximity alone produces an offer, not a transfer |
| Empathy Bypass | Part 1 comes first whenever the customer has a problem or a negative emotion |
| Authentication Theatre | The package carries the auth level; the agent does not re-ask for an OTP because of the handoff; the human sees what is already verified |
| Sycophantic Recovery | One specific acknowledgement, then action (A9.3: "Apologise once, specifically, then move to action") |
| Knowledge Hallucination | The message states only what the state holds; team names are the brief's queue names in plain words |

## 7. While the customer waits

The agent stays in the conversation until a human accepts. What it may do depends on the priority and mode (D-124).

| Situation | The agent does | The agent does not |
|---|---|---|
| P0 crisis (ESC-011) | Stays present with the template's follow-up lines; answers the customer briefly and calmly | Any banking task, any question about accounts, any product, any survey |
| P0 fraud or access (ESC-001, ESC-009) | Completes confirmed protective steps; tells the customer what is already protected; gives the credential-change instruction where it applies | New unrelated tasks; cross-sell; promises about refunds; asking for evidence that contains credentials |
| P1 and P2, `warm` | Keeps working on the same problem where it safely can (Case Study 5): looks up status, fills intake slots that are still empty, answers generic questions. Posts an honest status at most every 60 seconds, each one adding something | Re-asks anything already given; repeats the same wait message; starts a write action that the incoming specialist should decide |
| ESC-008, ESC-013 | Offers factual KB information on request | Any answer to the uncertain regulatory point; any advice |
| ESC-015, `discreet` | Serves generic information | Any account-specific action; any hint of the reason |
| `silent_case` | Continues the conversation normally within the rules | Any reference to the case |

Rules that apply throughout the wait:

1. Triggers keep being evaluated. A higher-ranked trigger upgrades the pending escalation (`triggers.md` section 4.1 rule 6).
2. The 5-minute inactivity rule still applies (A4.2 rule 7, GR-SEC-R7). The longest SLAs (10 and 15 minutes) are longer than the timeout, so a customer who goes quiet loses the authenticated level; the package records the level at the trigger and at the handoff.
3. At 70 percent of the SLA with no acceptance, the supervisor of the queue is alerted and the customer is offered the choice to keep waiting or to request a callback (P1, P2). A P0 customer is not offered a way out of the queue.
4. Everything the customer adds while waiting is appended to the package, so the human sees the conversation up to the second they join.
5. The escalation proximity score and CSAT prompts are frozen during the wait; no survey is sent before the human conversation ends.

## 8. Failed-handoff behaviour

A handoff fails when the customer does not reach a human by the route chosen. Behaviour (D-123) extends the existing rule "next queue by priority, then callback scheduling" (`component-interfaces.md` row 8, FMEA 15).

| Failure | Detection | P0 | P1 | P2 |
|---|---|---|---|---|
| Queue closed or unavailable at routing time | Queue health | Overflow chain at once; if no P0-capable queue answers, any available human plus an incident alert; protective steps stay in place | After-hours rule or overflow chain; callback offered | Overflow chain; callback offered |
| No acceptance by the SLA | SLA timer | Breach handling in `queue-management.md` section 5; the customer stays in the conversation and is told honestly | Next overflow step; choice to wait or request a callback | Same as P1 |
| Transfer fails technically (agent desktop, channel) | Transfer error | Retry once at once, then the next queue; never a third attempt on the same route | Retry once, then overflow | Retry once, then overflow |
| Package not delivered | Delivery error | Handoff proceeds; the agent pastes the summary element into the conversation for the human; package flagged incomplete | Same | Same |
| Customer leaves while waiting | Channel disconnect or inactivity | The case stays open; the queue makes outbound contact on the registered channel; ESC-011 follows the Crisis Response team's own protocol (dependency) | Case stays open; one notification that a colleague will follow up; no promised time | Record closed as abandoned in queue; one message with how to resume; context is reusable for 24 hours (D-05) |
| Human returns the conversation without resolving | Wrap-up code | Not allowed for P0 | Returned to the queue, not to the agent | Allowed only with a wrap-up note; the agent resumes with the note visible |

Limits: two transfer attempts per route (`handoff_attempts_max`); a failed handoff is never presented as the customer's problem; the phrases "no one is available" and "try later" are not used for a security report (existing oracle GR-SEC-R6-03). Every failure is logged with its type and feeds EQ-06 (`queue-management.md` section 8).

## 9. De-escalation and cancellation

The brief asks for "de-escalation logic" (Part D p.60) and its Case Study 5 shows a customer recovering from -0.9 to -0.4 while an escalation is prepared. Two things are meant by the word and both are specified (D-125).

### 9.1 De-escalating the conversation

These are the agent's moves when sentiment is falling, before or after a trigger. They follow A9.1 Pattern 1 and `sentiment.md` section 5.

| Signal | Move |
|---|---|
| A spike (one drop of 0.6 or more) | Repair: restate what was understood, correct the misunderstanding, one specific acknowledgement |
| A drift (falling slope over turns) | Shorter replies, own the delay, give the next concrete step, prepare the package at proximity 0.6 |
| Sarcasm suspected | Acknowledge the underlying problem; never mention sarcasm |
| Resignation ("forget it") | Do not close. One check-in and one offer of a human |
| Repeated failure of the same step | Change the approach rather than repeat it (no Robotic Loop); offer a human at proximity 0.8 |
| Recovery detected (slope of +0.15 or more over 3 turns and smoothed score at or above -0.2) | Continue; do not escalate on a stale signal; record the recovery for the learning pipeline |

### 9.2 When a pending escalation may be cancelled

A pending escalation is one that has fired but has not yet been accepted by a human. After acceptance nothing is cancelled; the human decides.

| Class (`cancellable` in the rules file) | Triggers | Who may cancel | Condition |
|---|---|---|---|
| `never` | ESC-001, ESC-009, ESC-011, ESC-012 (all P0); ESC-002, ESC-005, ESC-015; XTR-02 | Nobody. Not the agent, not the customer | A P0 escalation is never cancelled. A customer who says "never mind, it was my husband's purchase" is still connected; the human closes the case. For ESC-002 a retraction leaves the record open as a case. For ESC-005 a corrected amount withdraws the record as `condition_false`, which is a correction and is logged as such |
| `customer_only` | ESC-006, ESC-007, ESC-008, ESC-013; XTR-01, XTR-03, XTR-07 | The customer, by saying so | The customer withdraws the request (no longer wants a human, an advisor, the answer, or the closure). The agent never proposes it |
| `customer_or_recovery` | ESC-003, ESC-004, ESC-010, ESC-014; XTR-04, XTR-05, XTR-06 | The customer; or the agent may ask once when the recovery condition holds | Recovery conditions below, and in every case the customer must agree |

Recovery conditions:

| Trigger | Recovery condition (all parts) |
|---|---|
| ESC-003 | A later customer turn at or above `intent_confidence_threshold`, and the agent has completed that request |
| ESC-004 | The customer's issue has had a concrete action or answer, and the latest raw sentiment score is above -0.40 (proposal; the anchor is the -0.4 "recovering" reading in Case Study 5) |
| ESC-010 | The open topic has reached status `resolved` |
| ESC-014 | The failed read has succeeded and the request has been completed |

The one question the agent may ask, once, when a recovery condition holds (illustrative): "It looks like this is now sorted. Would you still like to speak to my colleague, or are you happy to finish here?" Any answer other than a clear wish to finish keeps the handoff.

Safeguards against using cancellation to improve containment figures:

1. The agent may not ask more than once, may not ask before the recovery condition holds, and may not argue with the answer.
2. A cancelled escalation keeps its record with outcome `de_escalated_by_customer` or `de_escalated_recovery`. It is not deleted and it is sampled for review at a higher rate than ordinary conversations.
3. A de-escalated conversation followed by a repeat contact on the same issue within 7 days is counted as a missed escalation (EQ-02) and removed from first-contact resolution (KPI-G3).
4. De-escalation rate is reported next to containment on every dashboard that shows containment.

## 10. After the handoff

| Item | Rule |
|---|---|
| The agent's role | Silent once the human accepts. It does not answer in parallel |
| Resolution status (A10.1) | `resolved_human` or `escalated`; never `resolved_ai` once a human has accepted |
| Wrap-up by the human | One code from: correct escalation; premature (the agent could have resolved it); wrong queue; late (should have been escalated earlier); and whether the customer had to repeat anything. These codes feed EQ-01, EQ-03, EQ-04 and EQ-05 (`queue-management.md` section 8); the reference label is the supervisor's `escalation_verdict` (`docs/learning-pipeline/supervisor-corrections.md`), where "unnecessary" is the A5.1 class "false positive escalation" |
| CSAT | Asked after the human conversation ends, about the whole interaction; never for ESC-011 |
| Return to the agent | Only for P2 with a wrap-up note (section 8) |

## 11. Templates this document needs (Day 13)

| Template | Used by | Slots |
|---|---|---|
| TPL-ESC-HANDOFF-WARM | Sections 6.1 and 6.2, all `warm` triggers | acknowledgement, team name in plain words, wait estimate (optional), meanwhile line |
| TPL-ESC-HANDOFF-DISCREET | ESC-015, ESC-009 pattern | none beyond the standard shape; no reason slot |
| TPL-ESC-FRAUD-P0 | ESC-001, ESC-009 | protective action offered, confirmation question, what is already protected |
| TPL-ESC-CRISIS | ESC-011 | language; reviewed text only, no free slots |
| TPL-ESC-WAIT-UPDATE | Section 7 | rotating set of at least three variants; wait estimate (optional) |
| TPL-ESC-HUMAN-JOINED | Section 6.1 | first name, team, one-line topic |
| TPL-ESC-AFTER-HOURS | Section 6.2 | team, callback offer |
| TPL-ESC-CALLBACK-OFFER | Sections 7 and 8 | registered-channel wording; "a request, not a guarantee" |
| TPL-ESC-LANGUAGE-CHOICE | Section 6.2 | languages available now |
| TPL-ESC-HANDOFF-FAILED | Section 8 | what happens next; no blame, no "try later" |
| TPL-ESC-DEESCALATION-CHECK | Section 9.2 | none |
| TPL-ESC-REFERRAL | XTR-05, XTR-07 | process name, what the customer needs to bring or do |
| TPL-ADV-ADVISOR-OFFER, TPL-ADV-ADVISOR-CONFIRM, TPL-ADV-ADVISOR-UNAVAILABLE | ESC-013 | already named on Day 9 |

## 12. Decisions and open items

Decisions: D-04 (the eight elements, Day 1), D-118 (SLA clock and IMMEDIATE), D-121 (routing factors; history may reorder a queue but not change a threshold), D-122 (hours and after-hours), D-123 (failed handoff), D-124 (behaviour while waiting), D-125 (de-escalation and cancellation).

Open items:

1. The queue platform (availability, forecast wait, skills, pre-emption, callback scheduling, wrap-up codes) is a dependency; none of its features is specified by the brief.
2. Operating hours and language staffing are proposals; Arjun's time zone (A13.2) makes the after-hours path a real case rather than an edge.
3. The crisis follow-up after a disconnect is the Crisis Response team's protocol and is not designed here.
4. The -0.40 recovery bound and the 60-second update interval need calibration with real conversations.
5. Whether a retracted legal threat may be closed by the customer is a Risk Committee question; it is `never` here.
