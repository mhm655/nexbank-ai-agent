# Conversation Design: Patterns, Anti-Patterns and Tone

Brief refs: A9.1 (pp.23-24: five mandatory design patterns), A9.2 (pp.24-25: eight critical anti-patterns with penalties), A9.3 (p.26: tone guidelines, brand voice "Friendly, Trustworthy, Modern"), A2.4 (p.7: generation strategy, tone verification, commitment detection), Part D Day 14-15 (p.60: "Apply all 5 mandatory conversation design patterns" and "Verify none of the 8 critical anti-patterns appear in any conversation").

Related: `response-generation.md` (generation modes, persona, length calibration; Day 3), `dialogue-management.md` (confirmation, clarification, recovery), `docs/intent-taxonomy/sentiment.md` section 5.3 (empathy trigger), `config/system-prompt/layer3-dialogue.md` (prompt-side rules D1 to D10), `config/templates/` (wording), `docs/guardrails/output-safety-layer.md` (checks C1 to C7), `docs/escalation/routing-and-handoff.md` section 6.3.

Status: specification. Nothing here has been run. "Enforced by" names the control that is designed to catch a violation; no catch rate is claimed. Example wording is illustrative and uses no product figure.

## 1. Naming note

`response-generation.md` section 4 (Day 3) lists the five patterns under working names: "acknowledge-then-act, confirm-before-action, graceful uncertainty, proactive-but-safe suggestion, warm handoff". The brief's five are Empathy-First, Progressive Disclosure, Confirmation-Before-Action, Graceful Degradation and Context Carry-Over. This document uses the brief's names and definitions; they are authoritative (D-150). Mapping: acknowledge-then-act is Empathy-First; graceful uncertainty is Graceful Degradation; confirm-before-action is unchanged; "proactive-but-safe suggestion" and "warm handoff" are not among the brief's five (they are covered by `dialogue-management.md` section 4.6 and `routing-and-handoff.md` section 6); Progressive Disclosure and Context Carry-Over were missing from the Day 3 list.

Codes used below and in the template files: P1 to P5 for the patterns, AP1 to AP8 for the anti-patterns, in the brief's order.

## 2. The five mandatory patterns (A9.1)

### 2.1 P1 Empathy-First

Brief (p.23): "Every conversation involving a customer problem, complaint, or negative emotion must follow this pattern. The agent must acknowledge the customer's emotional state before attempting to solve the problem." Steps: "Acknowledge: Recognise the customer's situation and validate their feelings", "Assure: Provide assurance that the issue will be addressed", "Act: Take concrete action to investigate or resolve the issue", "Affirm: Confirm the action taken and set expectations for next steps". The brief adds that customers who feel heard are "2.4x more likely to report satisfaction even when the resolution is identical" (the brief's figure; not verified here).

| Aspect | Specification |
|---|---|
| When it applies | The Policy Engine sets the empathy trigger: smoothed sentiment at or below `empathy_first_sentiment_max`, an active frustration, anger, anxiety or resignation label, a problem or complaint intent (TXN-002, TXN-003, CMP-*, SEC-*), or a recovery from a drop (`sentiment.md` section 5.3) |
| Order | Acknowledge comes before any question, including a verification request (`TPL-CMP-EMPATHY-FIRST` variant `needs_verification_first`) |
| Limits | One acknowledgement sentence, specific to the situation; one apology at most per issue; "Affirm" sets expectations without a timeline unless a tool returned one |
| Prompt | Layer 3 D2 and the `complaint` and `fraud_or_security` blocks |
| Templates | `TPL-CMP-EMPATHY-FIRST` (four steps as slots), the `ack` slot of `TPL-ESC-HANDOFF-WARM`, `TPL-TXN-DISPUTE-INTAKE` and `TPL-TXN-STATUS`, the opening sentence of `TPL-ESC-FRAUD-P0` and `TPL-ESC-CRISIS` |
| Output check | C5 tone (GR-OUT-04): empathy required when the intent is a problem, complaint or fraud flow; banned over-apology phrases |
| Tests | GR-OUT-04-02, GR-REG-03-02, ESC-T-004-01, ESC-BOSS-L6-03, GR-ATK-05-05 |

### 2.2 P2 Progressive Disclosure

Brief (p.23): "For complex information delivery (product details, policy explanations, multi-step procedures)": "Layer 1: Provide the essential answer in 1-2 sentences", "Layer 2: Offer to elaborate on specific aspects", "Layer 3: Provide detailed information only when explicitly requested". "The agent must never dump large blocks of policy text in a single message."

| Aspect | Specification |
|---|---|
| When it applies | Product, policy and procedure answers (retrieval decision `answer`), comparisons, gap answers with adjacent facts |
| Rule on disclosures | Mandatory disclosures (GR-REG-01) belong to layer 1 of the answer. Progressive disclosure never defers a required disclosure |
| Limits | Layer 1 is at most two sentences plus disclosures; a procedure is a numbered list of at most 5 steps (`response-generation.md` section 3); a reply never exceeds `atk_output_max_words` |
| Prompt | Layer 3 D3; layer 4 K4 ("short answer first") |
| Templates | `TPL-GEN-DISCLOSE-MORE` (variants `layer_1_2` and `layer_3`), `TPL-ACC-BALANCE` (balance and one optional next step), the "more detail" close of the `TPL-ADV-*` set |
| Output check | Length cap (GR-ATK-08); C4 grounding on each claim |
| Tests | KB-BOSS-L3-01, GR-REG-01-01, ESC-BOSS-L6-04, GR-ADV-09-01 |

### 2.3 P3 Confirmation-Before-Action

Brief (p.23-24): for "Any action that modifies account state, initiates a process, or cannot be easily reversed": "Summarise the intended action in clear, unambiguous language", "State all relevant details (amounts, dates, masked account numbers)", "Explicitly ask for confirmation using a yes/no question", "Wait for affirmative confirmation before proceeding", "Provide post-action confirmation with reference number".

| Aspect | Specification |
|---|---|
| When it applies | Every intent with `confirmation: explicit` in `config/intents.yaml` (card block and unblock, replacement, dispute ticket, complaint, recurring-payment stop, callback, credential reset link) |
| What counts as yes | A clear affirmative within `confirmation_window_turns` or `confirmation_window_minutes`. "ok I guess", "hmm", silence or an earlier yes do not count (`dialogue-management.md` section 4.3) |
| Expiry | A confirmation is single-use and void after session expiry (GR-SEC-R7) |
| After the action | Reference number from the tool result only; a failed write is reported as a failure (`TPL-ACT-FAILED`) |
| Prompt | Layer 1 S5; layer 3 D4 |
| Templates | `TPL-ACT-CONFIRM`, `TPL-ACT-DONE`, `TPL-ACT-FAILED`, `TPL-ESC-FRAUD-P0` (block question), `TPL-ESC-CALLBACK-OFFER` (ask and placed), `TPL-AUTH-SESSION-TIMEOUT` (`confirmation_void`) |
| Platform control | Tool Orchestrator refuses an unconfirmed protective action (`component-interfaces.md` row 7); Policy Engine CONFIRM state |
| Output check | C6 capability check: a completed-action claim without a tool result is blocked (GR-SEC-R3-05) |
| Tests | SS-AUTH-15, SS-AUTH-13, GR-SEC-R7-02, GR-ATK-10-06, KB-BOSS-L3-03 |

### 2.4 P4 Graceful Degradation

Brief (p.24): "Acknowledge the limitation honestly without technical jargon", "Explain what the agent CAN do as an alternative", "Offer escalation to a human agent if appropriate", "Never fabricate information to fill knowledge gaps", "Never promise capabilities the system does not have".

| Aspect | Specification |
|---|---|
| When it applies | Retrieval decisions `gap`, `degrade`, `unavailable`; a failed tool; a prohibited request; an attack reply; an unavailable queue; the fail-closed ladder |
| Ladder | Answer, gap statement, one clarifying question, degradation template, human handoff (`retrieval-pipeline.md` section 10); Output Safety ladder rungs 1 to 5 (`output-safety-layer.md` section 6) |
| Limits | No number that is not in the KB; no "I think"; no jargon ("error", "timeout", "exception" are banned words); the same fallback is never sent twice in a row |
| Prompt | Layer 1 S9; layer 3 D5; layer 4 K4 and K7 |
| Templates | `TPL-KB-GAP`, `TPL-KB-DEGRADE`, `TPL-ACT-FAILED`, `TPL-ACT-CANNOT-DO`, `TPL-ADV-SAFE-FALLBACK`, `TPL-SYS-STATUS-STATIC`, `TPL-SYS-NOTICE`, `TPL-ESC-HANDOFF-FAILED`, `TPL-ESC-AFTER-HOURS`, the `TPL-ATK-*` set |
| Output check | C1 financial accuracy, C4 grounding (a figure on a gap topic is a fail), C6 capability check |
| Tests | SS-HAL-01 to SS-HAL-14, ESC-T-014-01, ESC-T-014-03, GR-SYS-01-01, GR-SYS-01-02 |

### 2.5 P5 Context Carry-Over

Brief (p.24): "Recognise returning context from conversation history or CRM data", "Proactively reference previous interaction", "Resume from where previous interaction left off", "Track cumulative customer effort across multiple contacts for same issue".

| Aspect | Specification |
|---|---|
| When it applies | `carry_over.open_tickets` or `prior_conversation_ids` present within `context_carry_over_window_hours`; within a conversation, every use of an already-given fact; every handoff (the 8-element package) |
| Security boundary | Context carries over; authentication never does (D-05). The earlier topic is named only after verification in the current session (`TPL-GEN-CARRYOVER` variant `needs_verification`) |
| Effort tracking | Repeat contacts on the same issue are counted in the handoff package and in outcome tracking (`outcome-tracking.md`); a repeat contact within `repeat_contact_window_days` may reorder a queue (D-121) |
| Prompt | Layer 3 D6 and D8 |
| Templates | `TPL-GEN-CARRYOVER`, `TPL-GEN-RECOVERY` (`repeated_effort`), `TPL-GEN-CLOSING` (`parked_topic`), `TPL-ESC-HANDOFF-WARM` ("you won't need to repeat yourself"), `TPL-ESC-HUMAN-JOINED`, `TPL-ESC-WAIT-UPDATE` (`noted`), `TPL-ESC-REFERRAL` (`missed_follow_up`) |
| Platform control | State Tracker pinned facts and topic stack (`dialogue-management.md` sections 5.2 and 5.5); handoff package completeness (EQ-08) |
| Tests | XTR-T-05-01, ESC-BOSS-L6-01, ESC-T-005-01, GR-SEC-R7-01 |

## 3. The eight critical anti-patterns (A9.2)

The table quotes the brief's example, penalty and impact area (pp.24-25), then gives the controls. "Prompt", "template", "platform" and "output check" are four independent places where the anti-pattern is stopped.

| Code | Anti-pattern | Brief's example violation | Penalty | Impact area | Prompt | Template | Platform rule | Output check | Tests |
|---|---|---|---|---|---|---|---|---|---|
| AP1 | Robotic Loop | "'I'm sorry, I didn't understand. Could you rephrase?' repeated 3+ times" | -20 pts | Architecture | Layer 3 D7 | Rotating variants (section 5 of the templates README); the sentence itself is a banned phrase | `max_clarification_turns`; XTR-04 and ESC-003 hand off; three consecutive ladder fallbacks escalate (D-82) | Same-text-as-previous-turn check in the Response Generator (proposal, section 6) | ESC-T-003-01, XTR-T-04-01, GR-ATK-04-01 |
| AP2 | Information Dump | "Responding to 'what's my balance?' with full account summary, product offers, policy updates" | -10 pts | CX Framework | Layer 3 D3 | `TPL-ACC-BALANCE` has no slot for anything but the balance; `TPL-GEN-DISCLOSE-MORE` | `atk_output_max_words`; no proactive offer at or below `no_proactive_offer_sentiment_max` | Length cap (GR-ATK-08) | SS-AUTH-27, ESC-BOSS-L6-04, GR-ATK-08-04 |
| AP3 | False Confidence | "'Your refund will be processed in exactly 3 days' when timeline is variable" | -30 pts | Safety (CRITICAL) | Layer 1 S9; layer 3 D8; layer 4 K5 | No fixed text holds a timeline; dates and waits are locked slots from a tool or the router, worded as estimates | D-09: commit only to timelines from a system of record | C6 commitment detection (GR-OUT-05) | SS-COM-01 to SS-COM-09, GR-OUT-05-01, GR-OUT-05-02 |
| AP4 | Premature Escalation | "Escalating a simple balance query because customer seems slightly annoyed" | -10 pts | Escalation | Layer 3 D8 | `TPL-ADV-ADVISOR-OFFER` and `TPL-GEN-CHECKIN` offer, they do not transfer; `TPL-ESC-DEESCALATION-CHECK` | ESC-004 needs two consecutive turns below the threshold at sentiment confidence of `sentiment_turn_confidence_min` (D-18); proximity alone only offers (`dialogue-management.md` section 6); near-miss cases per trigger | n/a (a routing decision, not text); measured by EQ-01 | ESC-BOSS-L6-04, ESC-T-004-02, ESC-T-004-03, SS-ESC-06 |
| AP5 | Empathy Bypass | "Customer: 'I'm so frustrated!' Agent: 'Please provide your account number.'" | -20 pts | CX Framework | Layer 3 D2 | `ack` slot comes first in every problem-flow template; `needs_verification_first` variant | Empathy trigger set by the Policy Engine, not left to the model | C5 tone: empathy required in problem, complaint and fraud flows | GR-OUT-04-02, GR-ATK-05-05, XTR-T-03-01 |
| AP6 | Authentication Theatre | "Re-asking for OTP when customer already verified" | -10 pts | Architecture | Layer 1 S4; layer 3 D6 | `TPL-AUTH-OTP-REQUEST` is selected only in phase AUTH_REQUIRED; handoff templates never ask for verification | Auth level is a Gateway claim checked by the Policy Engine; the handoff package carries it | A draft asking for verification while `auth_level` suffices is replaced (proposal, section 6) | SS-AUTH-27, XTR-T-02-02, ESC-T-005-01 |
| AP7 | Sycophantic Recovery | "'I'm so sorry! I deeply apologise! We sincerely regret...' without resolution steps" | -10 pts | CX Framework | Layer 3 D2 | `TPL-GEN-RECOVERY`: one apology and the next step in the same message; stacked-apology phrases banned | One apology per issue tracked in state (proposal, section 6) | C5 banned-phrase list (over-apology) | GR-OUT-04-01 |
| AP8 | Knowledge Hallucination | "Stating non-existent product benefit or incorrect interest rate" | AUTO-FAIL | Safety-Critical | Layer 1 S9; layer 4 K1, K6, K7 | No figure outside a locked slot (validator); gap templates use the KB safe statement | Template-first for figures; gap entries (D-26); retrieval threshold | C1 financial accuracy (GR-OUT-01), C4 grounding (GR-OUT-03) | SS-HAL-01 to SS-HAL-14, GR-OUT-01-01, GR-OUT-03-01 |

Penalty total if every anti-pattern occurred once: 110 points plus the AUTO-FAIL. The two safety-critical ones (AP3 and AP8) are the ones with a deterministic control at every one of the four places.

## 4. Brand tone guide (A9.3)

Brief (p.26): "NexBank brand voice: 'Friendly, Trustworthy, Modern.' The agent must maintain this tone across all interactions." The Do and Don't columns are the brief's; the examples are this project's and are illustrative.

| Dimension | Do (brief) | Don't (brief) | Example that follows it | Example that breaks it |
|---|---|---|---|---|
| Formality | "Professional but warm; address by name when authenticated" | "Overly casual slang or excessively stiff language" | "Hello Priya, welcome back. How can I help you today?" (name only after verification) | "Hey bro, what's up?" or "Kindly be informed that your query has been duly noted." |
| Brevity | "Concise; one concept per message when possible" | "Paragraph-length responses for simple queries" | The balance, then one optional next step | A balance followed by recent transactions, an offer and a policy note |
| Technical Language | "Plain English; explain banking terms when necessary" | "Jargon without explanation; assume customer knows terminology" | "TDS is tax deducted at source: the bank deducts tax on interest before paying it to you." | "Your NEFT is pending at the beneficiary bank's end due to a timeout." |
| Apologies | "Apologise once, specifically, then move to action" | "Over-apologise or use generic templates repeatedly" | "I'm sorry you've had to explain this more than once. Here's what I have, and here's the next step." | Three apologies and no step |
| Urgency | "Match customer urgency; escalate tone for fraud/security" | "Artificial urgency for sales or unnecessary alarm" | "I'm treating this as urgent. First, shall I block your card now?" | "Offer ends today!" or "Your account may be at serious risk!" with no basis |
| Personalisation | "Reference customer name, relevant account details (masked)" | "Reference data customer hasn't disclosed in current session" | "your card ending" followed by the masked digits the tool supplied | Mentioning a salary credit or a past purchase the customer did not raise |

How each word of the voice is made concrete:

| Voice | Meaning in this design | Controls |
|---|---|---|
| Friendly | Warm, plain, respectful ("aap" in Hindi and Hinglish); acknowledges before solving; never blames | Layer 3 D1 and D2; `ack` slot; blame and dismissive phrases banned |
| Trustworthy | Says only what a source supports; no promise without a system of record; admits limits; open about being an AI; one clear confirmation before acting | Layer 1 S9 and S10; layer 4; locked slots; C1, C4, C6; `TPL-GEN-AI-DISCLOSURE` |
| Modern | Short, direct, conversational; no legalese; code-mixed Hinglish treated as a first-class language; channel-aware length | Layer 3 D1 and D3 and the language and channel blocks; `response-generation.md` section 3 |

Tone by context (extends `response-generation.md` section 2 and `sentiment.md` section 5.4):

| Context | Register | Never |
|---|---|---|
| Routine request | light, efficient | padding, cross-sell on a frustrated customer |
| Complaint | calm, specific, owning | defending the bank, debating fault, legal language |
| Fraud or security | brief, steady, action first | humour, marketing, alarm words, asking the customer to prove it |
| Crisis | slow, caring, reviewed wording only | any banking content, questions about accounts, a survey |
| Attack or probing | neutral, non-accusatory | naming what was detected, lecturing, sarcasm |
| Refusal (advice, prohibited action) | friendly and firm, with an alternative | apology loops, hinting at a recommendation |

## 5. Matrix: template by pattern and anti-pattern

X means the template implements the pattern (P columns) or its wording is designed to avoid the anti-pattern (AP columns). The source of truth is the `a9` field of each template; the validator checks that every template is listed here. Totals over 73 templates: P1 14, P2 24, P3 7, P4 37, P5 20; AP1 29, AP2 27, AP3 39, AP4 9, AP5 16, AP6 13, AP7 11, AP8 33. Every pattern and every anti-pattern has at least one template.

| Template | P1 | P2 | P3 | P4 | P5 | AP1 | AP2 | AP3 | AP4 | AP5 | AP6 | AP7 | AP8 | Guardrails (first three) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `TPL-GEN-GREETING` | . | X | . | . | . | . | X | . | . | X | . | . | . | GR-REG-16, GR-REG-04, GR-SEC-R1 |
| `TPL-GEN-AI-DISCLOSURE` | . | X | . | . | . | . | . | . | . | . | . | . | X | GR-REG-16, GR-REG-20 |
| `TPL-GEN-LANGUAGE-SWITCH` | . | . | . | X | . | X | . | . | . | . | . | . | . | GR-REG-17 |
| `TPL-GEN-CLARIFY` | . | . | . | . | X | X | X | . | . | . | . | . | . | GR-SYS-01, GR-ADV-07 |
| `TPL-GEN-RECOVERY` | X | . | . | . | X | X | . | . | . | X | . | X | . | GR-OUT-04, GR-OUT-05 |
| `TPL-GEN-CHECKIN` | X | X | . | . | . | X | . | . | X | . | . | . | . | GR-REG-04 |
| `TPL-GEN-CARRYOVER` | . | . | . | . | X | X | . | X | . | . | X | . | . | GR-SEC-R7, GR-SEC-R2, GR-SEC-R1 |
| `TPL-GEN-DISCLOSE-MORE` | . | X | . | . | . | . | X | . | . | . | . | . | X | GR-REG-01, GR-OUT-01, GR-OUT-03 |
| `TPL-GEN-CLOSING` | . | . | . | . | X | . | X | . | . | . | . | . | . | GR-REG-04 |
| `TPL-GEN-TWO-REQUESTS` | . | . | . | . | X | X | X | . | . | . | . | . | . | GR-ATK-09, GR-SYS-01 |
| `TPL-GEN-LIMIT-CLOSE` | . | . | . | X | X | . | X | X | X | . | . | . | . | GR-ATK-09, GR-OUT-05, GR-REG-04 |
| `TPL-AUTH-OTP-REQUEST` | . | X | . | . | . | . | X | . | . | . | X | . | . | GR-SEC-R2, GR-SEC-R5, GR-REG-08 |
| `TPL-AUTH-STEP-UP` | . | X | X | . | . | . | . | . | . | . | X | . | . | GR-SEC-R2, GR-SEC-R5, GR-ATK-10 |
| `TPL-AUTH-OTP-FAILED` | . | . | . | X | . | X | . | . | . | X | . | . | . | GR-SEC-R2, GR-ATK-10, GR-SEC-R6 |
| `TPL-AUTH-SESSION-TIMEOUT` | . | . | X | . | X | . | . | X | . | . | X | . | . | GR-SEC-R7, GR-SEC-R2, GR-OUT-05 |
| `TPL-SEC-DO-NOT-SHARE` | . | . | . | X | . | X | . | . | . | X | . | . | . | GR-SEC-R1, GR-SEC-R5, GR-REG-05 |
| `TPL-SEC-PHISHING-TRIAGE` | X | . | . | . | . | . | . | X | . | X | . | . | . | GR-SEC-R5, GR-SEC-R6, GR-OUT-05 |
| `TPL-ACC-BALANCE` | . | X | . | . | . | . | X | . | X | . | X | . | X | GR-SEC-R1, GR-SEC-R2, GR-REG-08 |
| `TPL-ACC-CLOSURE-REASON` | . | . | . | . | X | . | . | X | . | X | . | . | . | GR-REG-04, GR-SEC-R2, GR-OUT-05 |
| `TPL-TXN-STATUS` | X | X | . | X | . | . | X | X | . | X | . | . | X | GR-OUT-01, GR-OUT-05, GR-SEC-R3 |
| `TPL-TXN-DISPUTE-INTAKE` | X | . | . | . | X | X | . | X | . | X | X | . | . | GR-SEC-R2, GR-OUT-05, GR-SEC-R5 |
| `TPL-ACT-CONFIRM` | . | . | X | . | . | . | X | X | . | . | X | . | . | GR-SEC-R2, GR-SEC-R7, GR-SEC-R1 |
| `TPL-ACT-DONE` | . | . | X | . | . | . | . | X | . | . | . | . | X | GR-OUT-05, GR-OUT-01, GR-SEC-R3 |
| `TPL-ACT-FAILED` | . | . | X | X | . | . | . | X | . | . | . | X | X | GR-SYS-01, GR-OUT-05, GR-REG-07 |
| `TPL-ACT-CANNOT-DO` | . | . | . | X | . | X | . | X | . | . | . | . | X | GR-SEC-R3, GR-REG-15, GR-OUT-05 |
| `TPL-CMP-EMPATHY-FIRST` | X | . | . | . | . | . | X | X | . | X | . | X | . | GR-OUT-04, GR-OUT-05, GR-REG-03 |
| `TPL-CMP-GRIEVANCE-INFO` | X | X | . | X | . | . | X | X | . | X | . | . | X | GR-REG-03, GR-REG-18, GR-REG-19 |
| `TPL-CMP-STATUS` | . | X | . | X | . | . | . | X | . | . | . | . | X | GR-REG-03, GR-OUT-01, GR-OUT-05 |
| `TPL-KB-DEGRADE` | . | . | . | X | . | X | . | X | . | . | . | . | X | GR-OUT-03, GR-OUT-01, GR-SYS-01 |
| `TPL-KB-GAP` | . | X | . | X | . | . | X | X | . | . | . | . | X | GR-OUT-01, GR-OUT-03, GR-REG-01 |
| `TPL-KB-TRANSLATION-UNAVAILABLE` | . | . | . | X | . | X | . | X | . | . | . | . | X | GR-OUT-03, GR-REG-17, GR-OUT-01 |
| `TPL-SRV-CSAT` | . | X | . | . | . | . | X | . | . | . | . | X | . | GR-REG-04, GR-OUT-02 |
| `TPL-SRV-CES` | . | X | . | . | . | . | X | . | . | . | . | . | . | GR-REG-04 |
| `TPL-SRV-NPS` | . | X | . | . | . | . | X | . | . | . | . | . | . | GR-REG-04 |
| `TPL-SYS-STATUS-STATIC` | . | . | . | X | . | X | . | X | . | . | . | . | X | GR-SYS-01, GR-OUT-06, GR-SYS-04 |
| `TPL-SYS-NOTICE` | . | X | . | X | . | . | X | X | . | . | . | . | X | GR-SYS-01, GR-OUT-05, GR-REG-04 |
| `TPL-SYS-CORRECTION` | X | . | . | X | . | . | . | X | . | . | . | X | X | GR-OUT-01, GR-OUT-03, GR-OUT-05 |
| `TPL-ADV-BOUNDARY` | . | X | . | X | . | . | X | . | . | . | . | . | X | GR-ADV-01, GR-ADV-06, GR-ADV-07 |
| `TPL-ADV-RATE` | . | X | . | X | . | . | X | X | . | . | . | . | X | GR-ADV-01, GR-ADV-06, GR-OUT-01 |
| `TPL-ADV-LOAN` | . | X | . | . | . | . | . | X | . | . | . | . | X | GR-ADV-03, GR-ADV-07, GR-REG-15 |
| `TPL-ADV-INVEST` | . | X | . | X | . | . | X | X | . | . | . | . | X | GR-ADV-01, GR-ADV-04, GR-ADV-06 |
| `TPL-ADV-INSURANCE` | . | X | . | . | . | . | X | . | . | . | . | . | X | GR-ADV-03, GR-ADV-07, GR-REG-12 |
| `TPL-ADV-TAX` | . | X | . | . | . | . | X | . | . | . | . | . | X | GR-ADV-05, GR-ADV-06, GR-OUT-01 |
| `TPL-ADV-FOREX` | . | . | . | X | . | . | . | X | . | . | . | . | X | GR-ADV-04, GR-SEC-R3, GR-OUT-03 |
| `TPL-ADV-COMPARE` | . | X | . | . | . | . | X | . | . | . | . | . | X | GR-ADV-09, GR-ADV-06, GR-OUT-01 |
| `TPL-ADV-ADVISOR-OFFER` | . | . | . | X | . | . | . | X | X | . | . | . | . | GR-ADV-08, GR-REG-20, GR-REG-04 |
| `TPL-ADV-ADVISOR-CONFIRM` | . | . | . | . | X | . | . | X | . | . | X | . | . | GR-ADV-08, GR-OUT-05 |
| `TPL-ADV-ADVISOR-DECLINED` | . | X | . | . | . | X | . | . | X | . | . | . | . | GR-ADV-08 |
| `TPL-ADV-ADVISOR-UNAVAILABLE` | . | . | . | X | . | . | . | X | . | . | . | . | X | GR-ADV-08, GR-OUT-05 |
| `TPL-ADV-SAFE-FALLBACK` | . | . | . | X | . | X | . | . | . | . | . | . | X | GR-ADV-06, GR-SYS-01, GR-OUT-06 |
| `TPL-ATK-NEUTRAL-REDIRECT` | . | . | . | X | . | X | . | . | . | X | . | . | X | GR-ATK-01, GR-ATK-03, GR-ATK-04 |
| `TPL-ATK-CANNOT-SHARE-CONFIG` | . | . | . | X | . | X | . | . | . | . | . | . | X | GR-ATK-06, GR-ATK-07, GR-OUT-06 |
| `TPL-ATK-AUTH-PROMPT` | . | . | . | X | . | . | . | . | . | . | X | . | X | GR-ATK-10, GR-SEC-R2, GR-SEC-R5 |
| `TPL-ATK-THIRD-PARTY` | X | . | . | X | . | X | . | . | . | X | . | . | X | GR-SEC-R4, GR-SEC-R8, GR-ATK-05 |
| `TPL-ATK-THROTTLE` | . | . | . | X | . | X | . | X | . | . | . | . | . | GR-ATK-08, GR-OUT-06 |
| `TPL-ATK-SHORTEN-OR-SPLIT` | . | X | . | X | . | X | X | . | . | . | . | . | . | GR-ATK-08, GR-ATK-09 |
| `TPL-ATK-SAFE-MODE` | . | . | . | X | . | X | . | . | X | . | . | . | . | GR-ATK-04, GR-SYS-04, GR-SYS-01 |
| `TPL-ESC-HANDOFF-WARM` | X | . | . | X | X | X | X | X | . | X | X | X | . | GR-SEC-R6, GR-OUT-05, GR-OUT-04 |
| `TPL-ESC-HANDOFF-DISCREET` | . | . | . | . | X | . | . | X | . | . | X | . | X | GR-REG-11, GR-REG-09, GR-SEC-R6 |
| `TPL-ESC-FRAUD-P0` | X | . | X | . | . | . | . | X | . | X | X | X | . | GR-SEC-R6, GR-SEC-R5, GR-SEC-R2 |
| `TPL-ESC-CRISIS` | X | . | . | . | . | X | X | X | . | X | . | X | . | GR-REG-16, GR-OUT-05, GR-REG-04 |
| `TPL-ESC-WAIT-UPDATE` | . | . | . | X | X | X | . | X | . | . | . | X | . | GR-OUT-05, GR-OUT-04 |
| `TPL-ESC-HUMAN-JOINED` | . | . | . | . | X | . | X | . | . | . | X | . | . | GR-SEC-R1, GR-REG-11, GR-OUT-02 |
| `TPL-ESC-AFTER-HOURS` | . | . | . | X | . | . | . | X | . | . | . | . | X | GR-OUT-05, GR-REG-18, GR-ADV-08 |
| `TPL-ESC-CALLBACK-OFFER` | . | . | X | X | . | . | . | X | . | . | . | . | . | GR-OUT-05, GR-SEC-R1, GR-OUT-02 |
| `TPL-ESC-LANGUAGE-CHOICE` | . | . | . | X | . | X | . | X | . | . | . | . | . | GR-REG-17, GR-OUT-05 |
| `TPL-ESC-HANDOFF-FAILED` | X | . | . | X | . | X | . | X | . | . | . | X | . | GR-SEC-R6, GR-OUT-05, GR-SYS-01 |
| `TPL-ESC-DEESCALATION-CHECK` | . | . | . | . | X | X | . | . | X | . | . | . | . | GR-REG-16 |
| `TPL-ESC-REFERRAL` | . | . | . | X | X | . | . | X | . | . | . | . | X | GR-SEC-R2, GR-SEC-R3, GR-OUT-05 |
| `TPL-ESC-ABANDONED-P2` | . | . | . | X | X | . | . | X | . | . | . | X | . | GR-OUT-05, GR-SEC-R6 |
| `TPL-ESC-HUMAN-REQUEST-FIRST` | . | . | . | . | X | X | . | . | X | . | . | . | . | GR-REG-16, GR-OUT-05, GR-REG-04 |
| `TPL-ESC-CARE-OFFER` | X | . | . | . | X | . | . | . | . | X | . | . | X | GR-REG-17, GR-REG-04, GR-OUT-05 |
| `TPL-ESC-HANDOFF-CANCELLED` | . | . | . | . | X | X | . | . | X | . | . | . | . | GR-REG-16, GR-OUT-05 |

Reading the matrix: an empty AP cell does not mean the template commits the anti-pattern; it means the template is not a control for it.

What the validator guarantees and what it does not (D-194). An earlier version of this paragraph said that the validator holds AP3 and AP8 "for every template"; that was too strong, and 15 seeded defects passed it. For every template, variant, slot fallback and label text the validator now fails the build on: a digit outside a slot; the global banned phrases; a time or outcome word without a digit (tomorrow, shortly, soon, a number of days, kal, jald, and Hindi equivalents); advice wording (suggest, recommend, should invest, best option, and Hindi and Hinglish equivalents) unless the same sentence refuses it; a request for a credential in chat in English, Hindi or Hinglish, unless the sentence forbids it or points to the secure channel; a claim to be human, staff or a named person; a sentence count that differs between English, Hindi and Hinglish; and any declared required safety marker or AI disclosure that is missing from any language of any variant that declares it. It also fails a repository path that does not exist, a parameter of an excluded group (X4, X5) marked proposable, and a change to layer 0, 1 or 2 that is re-blessed with `--rehash` without `--allow-immutable-change` and a decision id. It does not guarantee that Hindi or Hinglish wording is correct or natural (native review does); that a paraphrase of banned wording is caught (the lists are a floor, and the Output Safety Layer and the linked cases are the other controls); that the declared safety markers are complete (a reviewer maintains them, and a template with no declared marker has no such check); or that a prompt layer is safe: the hashes and the required-instruction list detect change, not harm, and they sit in the same repository as the layers, so an approved immutable hash kept outside the repository (`--approved-immutable`) is the stronger control. The repeatable proof that each audited defect is now caught is in the Day 13 audit-fix handoff.

Language of locked KB slots (known limitation and launch blocker, D-199). The words of a template around a locked KB slot are written in the reply language. The slot itself is filled by the renderer with the served-language body of the KB entry when the entry has a current reviewed one (today only KB-FAQ-001, KB-FAQ-002, KB-FAQ-008 and KB-FAQ-009), and otherwise with the English body, verbatim and untranslated, with the log flag `translation_unavailable` set. A Hindi or Hinglish reply to a question answered from any other entry therefore mixes languages: Hindi or Hinglish sentences around an English fact. Nothing is machine-translated, because a translated financial fact is a fabricated fact (A9.2). The templates affected are the ADV family, `TPL-KB-GAP`, `TPL-ACT-CONFIRM` (`effect`), `TPL-ACT-DONE` (`next_steps`), `TPL-ACT-CANNOT-DO`, `TPL-ESC-REFERRAL`, `TPL-CMP-GRIEVANCE-INFO`, `TPL-GEN-DISCLOSE-MORE`, `TPL-SYS-NOTICE` (`policy_text`) and `TPL-SYS-CORRECTION`. `TPL-KB-TRANSLATION-UNAVAILABLE` is the alternative reply (say so and offer English or a person, as `retrieval-pipeline.md` section 2 describes); whether it replaces the mixed reply for fact-bearing templates is an open decision for Product and Risk. The fix is reviewed `body_i18n` for the KB entries, after which the mixed rendering disappears with no template change.

## 6. Controls proposed here that do not exist in earlier documents

These three are small additions needed to make the table in section 3 complete. They are proposals (D-150). The first two are not yet in `output-safety-layer.md`; the third now exists in the state schema (it was added after this section was written); the handoff lists the changes for the owners of those files.

| Proposal | Where it would live | Purpose |
|---|---|---|
| Repeat check: the Response Generator compares the normalised reply with the previous agent turn and, on a match, selects the next variant or the human offer | Response Generator, before the Output Safety Layer | AP1 Robotic Loop for free text (templates already rotate) |
| Verification-request check: a draft that asks for verification while `auth_level` meets the intent's level and `auth_expiry` has not passed is replaced by the direct answer | Output Safety Layer, as a deterministic rule in stage S1 | AP6 Authentication Theatre |
| `apology_given` per topic on the topic stack | `config/dialogue_state.schema.json` (field exists, D-150) | AP7: one apology per issue across turns |

## 7. Using this in the Day 14 simulations

Each simulated conversation should annotate, per agent turn: the template id and variant, the pattern codes applied, and a line "anti-pattern check: none" backed by the validator rules. A conversation that involves a problem must show all four P1 steps; one with a side-effect action must show the P3 sequence including the reference from the tool; one with a missing fact must show P4 without a figure; a returning-customer conversation must show P5 with re-verification.

## 8. Open items

1. Tone rules are untested with customers; the CEB owns the voice and has not reviewed it.
2. The empathy trigger threshold and the check-in limits are proposals in `config/parameters.yaml`.
3. Hindi and Hinglish register needs native review; cultural adaptation for the five secondary languages is not written.
4. The first two controls in section 6 need acceptance by the owner of the Output Safety Layer; the third is in the state schema.
5. Hindi and Hinglish replies built from locked KB slots mix languages until the KB entries carry reviewed `body_i18n` (section 5, D-199). Launch blocker.
