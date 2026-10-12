# Dialogue Management

State schema: `config/dialogue_state.schema.json`. Diagrams: `diagrams/dialogue-state-machine.mmd`, `diagrams/auth-flow.mmd`. Thresholds are defaults and live in `config/parameters.yaml` (Day 13).

## 1. State summary

The State Tracker owns: current intent (label, per-layer confidence, alternatives), a topic stack, slot status per slot, a rolling history of at least 20 turns, a summary with pinned facts, sentiment trajectory, auth level and expiry, guardrail state, escalation proximity, consecutive low-confidence count, human-request count and multi-session carry-over flags.

## 2. Dialogue phases

`INIT`, `INTENT_DETECT`, `CLARIFY`, `AUTH_REQUIRED`, `SLOT_FILL`, `CONFIRM`, `EXECUTE`, `RESPOND`, `ESCALATING`, `HANDOFF`, `CLOSING`, `FAIL_SAFE`. Transitions and guards are in the state diagram.

### Transition guards

| From > To | Guard |
|---|---|
| INTENT_DETECT > RESPOND/SLOT_FILL | confidence >= 0.70, auth sufficient |
| INTENT_DETECT > CLARIFY | 0.40 <= confidence < 0.70, or an ambiguous pair (alt within 0.15) |
| INTENT_DETECT > FAIL_SAFE | confidence < 0.40 (increments `consecutive_low_conf`) |
| FAIL_SAFE > ESCALATING | `consecutive_low_conf` >= 3 (ESC-003) |
| CLARIFY > ESCALATING | `clarification_attempts` >= 2 for the same intent |
| any > AUTH_REQUIRED | intent's required auth > current `auth_level` |
| SLOT_FILL > CONFIRM | tool has side effects (protective actions, ticket creation) |
| CONFIRM > EXECUTE | explicit affirmative within the confirmation window (default 2 turns or 2 minutes) |
| any > ESCALATING | any escalation trigger fires (ESC table, Day 12) |

## 3. Authentication sub-machine

Levels: `anonymous` < `otp_verified` < `biometric_verified` < `full_kyc`. Intent risk sets the minimum level. Auth expires after 5 minutes of inactivity (D-05); the conversation context may be reused for 24 hours but the customer must re-authenticate. Three failed OTP attempts lock the flow and go to the security queue. OTP, PIN, CVV, full card number and full Aadhaar are never stored in state or logs. See `diagrams/auth-flow.mmd`.

## 4. Policy

### 4.1 Action space

| Action | Meaning |
|---|---|
| respond | Give information or complete a read-only request |
| clarify | Ask one targeted question to resolve ambiguity or fill a slot |
| confirm | Restate an action and its parameters and ask for explicit yes/no |
| escalate | Hand to a human queue with a handoff package |
| transfer | Route to a different specialised agent or channel (for example branch or app flow) |
| hold | Pause while waiting on a tool or customer input; set a timeout |
| recommend | Offer information-only product guidance from the catalogue (never suitability advice) |
| apologise | Acknowledge failure or inconvenience, then take the next action |

### 4.2 Hybrid decision logic

Evaluated in strict order; the first rule that fires decides the action.

1. **Safety rules (deterministic, immutable):** Input Guard blocks, crisis, fraud signals, prohibited requests (fund transfer, nominee change) lead to refuse/escalate.
2. **Auth rules:** insufficient auth leads to `AUTH_REQUIRED` (transfer to the auth flow).
3. **Escalation triggers:** human request (honoured from the first explicit request, XTR-01; ESC-006 at the third, `docs/escalation/triggers.md` section 5), repeated low confidence, high frustration, regulatory uncertainty, and so on.
4. **Deterministic flows:** confirm-before-act for side-effect tools; slot-filling for known intents.
5. **Learned ranker (lowest precedence):** chooses among *safe* candidate actions (clarify wording, proactive suggestion, recommend timing). It can never override rules 1-4 and cannot add tools.

### 4.3 Confirmation strategy

| Risk | Strategy |
|---|---|
| Read-only, low sensitivity | No confirmation |
| Read-only, sensitive (statement, profile) | Implicit confirmation by echoing the parameters in the answer |
| Protective write (card block, dispute ticket) | Explicit confirmation of the exact action and card (last 4 digits) |
| Prohibited (money movement, nominee, KYC, closure) | Not executed; explain and route to the proper channel |

Confirmations are single-use and expire. Ambiguous answers ("hmm", "maybe") are not a yes.

### 4.4 Clarification

One question at a time, offering at most 3 labelled options built from the top alternatives (for example "a payment to the wrong merchant, or a charge you didn't make?"). After 2 failed clarifications for the same intent, escalate with the context gathered.

### 4.5 Recovery

Misunderstanding detected (customer says "no, I meant...", contradiction, repeated rephrasing): apologise once, restate understanding, offer the top alternative, then continue. Tool failure: state honestly what did not happen, offer retry or human help, never imply success.

### 4.6 Proactive strategies

Allowed when safe and factual: surface a pending open ticket status, remind of a related step (for example "your replacement card takes the standard delivery time listed in the catalogue"), suggest a self-service path. Never proactive: investment suggestions, product pushes on a frustrated customer (sentiment < -0.4), anything requiring advice.

## 5. Multi-turn reasoning

### 5.1 Anaphora resolution

Resolve "it", "that", "the same", "the first one" against, in order: the most recent entity of the matching type in the active topic, then the parked topic stack, then the last 5 turns of history. If two candidates tie, ask. Resolved references are written into slots with `status: inferred` and confirmed before any side effect.

### 5.2 Topic switching

A topic switch is a change of secondary-intent label with high confidence (>= 0.70) that is not a clarification or slot answer. The active topic is pushed onto the **topic stack** with a snapshot of its slots; the new topic becomes active. Rules:
- Switches to a **security/fraud** topic always take priority and can pre-empt the current action.
- A parked topic is surfaced again when the active topic resolves ("Earlier you asked about the Swiggy charge, shall we continue?") or when the customer refers back to it.
- A topic abandoned explicitly ("forget that") is marked `abandoned` and not resurfaced.
- Stack depth is capped (5); the oldest low-priority topic is summarised into pinned facts.

### 5.3 Implicit intent

Short or elliptical utterances ("and last week's?", "can I do it here?") inherit the active topic's intent with `implicit: true` and confidence capped at 0.75; if the inherited slots do not fit, clarify.

### 5.4 Contradictions

When a new value conflicts with a slot (different amount, card, date): mark `conflicting`, ask which is right, and do not act until resolved. When an assertion conflicts with system-of-record data, trust the system and say what the record shows.

### 5.5 Context-window management

Keep the last 20 turns verbatim (masked). Older turns collapse into `summary.text`; `pinned_facts` are always carried: auth state, confirmed slots, actions taken, commitments made, open complaints and the escalation context. Summaries are regenerated every 10 turns and on topic switch. Retrieved passages are not stored in state, only their IDs and versions.

## 6. Escalation proximity score

A 0-1 score updated each turn from: sentiment slope and level, number of clarification failures, human-request count, intent priority (fraud/complaint), time in conversation, and repeated topic. Thresholds: >= 0.6 prepares a handoff package; >= 0.8 offers a human proactively. This is advisory; hard triggers (ESC rules) fire independently.
