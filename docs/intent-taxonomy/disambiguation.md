# Intent Disambiguation

Brief ref: A3.4 (six confusable pairs, each with clarifying question sequences, confidence threshold logic and entity-based differentiation rules). Intents: `config/intents.yaml`. Thresholds: `docs/architecture/nlu-pipeline-overview.md` section 3. Trees: `diagrams/disambiguation-01..06-*.mmd`. Test cases (the Day 6 boss set of 10 ambiguous messages and the per-pair tests) will use IDs `NLU-DIS-<pair>-<nn>` in `tests/nlu/`.

## 1. Shared mechanics

**When a tree runs.** A pair tree replaces the generic clarifier when both members of the pair are within the top 3 hypotheses on the secondary layer (a third candidate may rank between them, as in pair 1's example: TXN-001 .52, TXN-003 .48, TXN-002 .44) and either the top score is < 0.70 or the gap between the two pair members is < 0.15 (dialogue-management.md transition guards; the 0.70 and 0.40 tiers are D-06; top-3 rule is D-36), or a safety-flow candidate (SEC-001, PRD-005) is one of the pair and above its 0.50 flow-entry gate. A pair tree may also pre-empt on a strong cue (for example a scam cue goes straight to SEC-001).

**Order of evidence, cheapest first.** (1) Entity cues in the message, (2) state and topic memory, (3) system-of-record evidence (ledger, open complaints, card list), (4) a question to the customer. A question is asked only when 1 to 3 cannot decide.

**Question design** (A9 patterns):

- One question per turn, closed form, rendered as quick-reply buttons with at most 3 options, each with a plain label. Free-text answers are accepted and classified.
- Questions state the evidence they used ("I can see complaint CMP-... open since ...") instead of asking blindly (Context Carry-Over).
- Wording changes on the second attempt and switches from text to buttons if it was text (Robotic Loop: never the same question the same way 3 or more times).
- Hinglish and Hindi variants are used when `language.primary` is `hinglish` or `hi`. English wordings below are the canonical ones; Hinglish examples show the pattern, and the final copy is a Day 13 template.

**Budget.** At most 2 clarification turns per ambiguity (`max_clarification_turns`). After that the pair's *safe default* applies, or a human offer with the gathered context if no safe default exists.

**Asymmetric thresholds.** Where one candidate is a safety flow (SEC-001, PRD-005) the gate is lower (0.50) than the 0.70 used for ordinary intents, because the cost of delay or an advice breach exceeds the cost of one extra question. A protective action never executes on confidence alone; it always needs explicit confirmation.

**Everything is logged.** The NLU frame stores `ambiguity.pair`, the gap, and which rule resolved it (`dis-01` to `dis-06`) so the learning pipeline can measure clarification rates, wrong-branch rates and the false-positive rate of the safety-biased gates.

## 2. Pair 1: TXN-001 (status) vs TXN-002 (dispute)

Diagram: `diagrams/disambiguation-01-txn-status-vs-dispute.mmd`.

**Why they collide.** "My payment hasn't come through" can be a harmless pending status or a wrong charge. A failed UPI payment (TXN-003) sits next to both.

| Evidence | Points to |
|---|---|
| Words: status, pending, done?, gone through, kab tak, abhi tak, track | TXN-001 |
| Words: wrong, galat, charged twice, double, refund, not delivered, overcharged, cancelled but debited | TXN-002 |
| Dispute-reason entity present (`dispute_reason`) | TXN-002 |
| Only `transaction_id` or `txn_description` with a status word | TXN-001 |
| "Didn't make / not me / unknown" | Exit to pair 5 |
| "Debited but not credited" for a UPI payment | TXN-003 |
| Sentiment <= -0.4 with an amount mentioned | Raises TXN-002 prior (feature, not a rule) |

**Threshold logic.** TXN-002 >= 0.70 and gap >= 0.15: go to the dispute intake. TXN-001 >= 0.70 and gap >= 0.15: read status. Otherwise the tree asks.

**Question sequence.**

1. Q1 (buttons): "Would you like me to check where this payment stands, or is something wrong with it?" Options: *Check status* / *Something is wrong*. Hinglish: "Payment ka status dekhna hai, ya kuch galat hua hai?"
2. If *Something is wrong*: pick the transaction from a masked list, then offer the tertiary reasons as buttons (wrong amount, charged twice, refund not received, not delivered).
3. If the customer replies in free text that still does not decide, the second attempt reframes it as an action: "I can look up the status now and raise a dispute if it shows a problem. Shall I start with the status?"

**Safe default (after 2 turns).** TXN-001: read the status first (LOW risk, and it often resolves the doubt), then offer the dispute in the same reply. Progressive Disclosure keeps this short.

**Hooks.** A status that shows success while the customer says the money did not arrive re-routes to TXN-003 or to TXN-002 `refund_not_received`. A dispute with amount > INR 50,000 is tagged ESC-005. No timeline is promised unless the system of record returned one (D-09).

**Examples.**

- "Mera 2000 ka payment pending dikha raha hai" -> `pending` + amount, no dispute word: TXN-001 at 0.84 (gap 0.31), no question.
- "Payment shows done but the merchant says not received" -> TXN-001 0.52, TXN-003 0.48, TXN-002 0.44: both pair members are in the top 3 and their gap is 0.08 (< 0.15), so the pair tree runs (Q1) even though TXN-003 sits between them. Q1 only offers the pair's two options; the "debited but not credited" cue in the table still exits to TXN-003 when present.

## 3. Pair 2: PRD-001 (information) vs PRD-005 (advisory)

Diagram: `diagrams/disambiguation-02-prd-info-vs-advice.mmd`. This is the information-versus-advice boundary of A4.1 and therefore the highest-risk pair.

**Why they collide.** The same product word appears in both: "NexFD rates" is information, "which FD should I pick" is advice.

**Rule: this pair does not ask a clarifying question.** Asking "do you want advice?" invites the customer to volunteer income, age or goals, which the agent must never use. Instead the reply is built to be safe either way: it answers the factual part and declines the recommendation.

| Evidence | Points to |
|---|---|
| what is, features, rate, how much, eligibility criteria, documents required, EMI for X at Y | PRD-001 to PRD-004 |
| should I, is it good, worth it, best for me, which is better, recommend, suggest, kya mujhe lena chahiye, accha rahega, right time | PRD-005 |
| Personal-circumstance cue (my salary, my age, my retirement, mere paise, meri umar) with any evaluative word | PRD-005 |
| Comparison with no recommendation verb ("FD vs mutual fund features") | PRD-001 `factual_comparison`: facts side by side, no "better" |
| Forex or gold timing (will the rupee fall, buy now) | PRD-005 `forex_timing_advice` |
| Affordability ("can I afford a 20L loan") | PRD-005 `loan_affordability_advice`; EMI calculator for given numbers stays PRD-002 |

**Threshold logic.** The advice detector (model plus rule layer) at >= 0.50 sets the boundary behaviour. The rule layer cannot be unset by the model: any hit on the recommendation-verb list together with a product word forces PRD-005. A score between 0.30 and 0.50 does not change the intent but adds a boundary sentence to the information reply.

**Response shape (template slots; Day 13 text).** Factual answer from the KB (version cited) + one boundary sentence ("I can share facts, but I can't tell you which option suits you") + offer of a SEBI-registered advisor (ESC-013, P1 Wealth Advisory) + an offer of more factual detail. No income, age or portfolio questions are asked.

**Examples (A4.1 categories).**

- "What's the 1-year FD rate?" -> PRD-003 0.91, answer from the KB entry.
- "Is FD better than a mutual fund?" -> PRD-005 `investment_product_advice`: states what each product is and its published features, declines the comparison verdict, offers an advisor.
- "Based on my salary can I take a 20L home loan?" -> PRD-005 `loan_affordability_advice`: gives published criteria (CIBIL > 700) and the EMI figure for the stated amount if asked; does not judge affordability.

## 4. Pair 3: ACC-003 (contact) vs ACC-004 (mailing address)

Diagram: `diagrams/disambiguation-03-acc-contact-vs-address.mmd`.

**Why they collide.** "Update my address" can mean postal address or email address; "update my details" names nothing. Both are Biometric-level HIGH writes, so a wrong guess starts the wrong secure flow.

| Evidence | Points to |
|---|---|
| Phone-shaped value (+91 or 10 digits starting 6 to 9) or the words phone, mobile, number, contact | ACC-003 `phone_number` |
| Email-shaped value or the word email, e-mail, mail id | ACC-003 `email_address` |
| Six-digit PIN code, flat, street, sector, "ghar ka pata", mailing, postal, communication address | ACC-004 |
| "Address on my Aadhaar/KYC", "KYC address", name correction | ACC-008 (KYC update) |
| "Address" alone, "update my details", "change my info" | Ambiguous: ask |

**The email-address trap.** "email address" contains "address". The entity extractor runs first: an email-shaped value or the token "email" forces ACC-003 even though the word "address" is present.

**Threshold logic.** Writes need >= 0.85 on the secondary layer for execution (nlu-pipeline-overview.md section 3, rule 2). Between 0.70 and 0.85, or with a gap under 0.15, the tree asks.

**Question sequence.**

1. Q1 (buttons): "Which detail would you like to update: your mobile number, your email, or your postal address?" Hinglish: "Aap kya update karna chahte hain: mobile number, email, ya postal address?"
2. On a vague answer ("my details"): one reframing with examples: "For example, a new phone number, or a new house address?"
3. After 2 turns with no answer: **no safe default** (both are HIGH-risk writes). Offer a human, with the context gathered.

**Multi-intent.** If the message names both a phone change and an address change: ACC-003 first, then ACC-004, because the contact change moves the destination of the OTP that confirms the address change (nlu-pipeline-overview.md section 4).

**Hooks.** A contact change followed shortly by a credential reset (SEC-003) is an account-takeover pattern: the rule layer raises ESC-009 for review.

## 5. Pair 4: CMP-001 (new complaint) vs CMP-003 (escalate)

Diagram: `diagrams/disambiguation-04-cmp-new-vs-escalate.mmd`.

**Why they collide.** An unhappy customer rarely says whether this is the first complaint. Treating a repeat as new restarts the clock and deepens frustration; treating a new complaint as an escalation sends it to the wrong queue.

| Evidence | Points to |
|---|---|
| Legal threat: court, lawyer, legal notice, consumer forum, ombudsman threat | CMP-003 `legal_threat` + ESC-002 (always, regardless of other scores) |
| `complaint_id` in the message | CMP-003 (or CMP-002 if asking status) |
| still, again, third time, phir se, abhi tak nahi hua, no response, "I already complained" | CMP-003 `repeat_unresolved` |
| Open complaint in CRM on the same subject (category or transaction) | Raises CMP-003 prior |
| Describes a new event, no repeat cue, no open complaint | CMP-001 |
| Asks for a senior, manager, supervisor | CMP-003 or CMP-005 (callback): if the customer wants a call back later, CMP-005; if they want escalation of the case, CMP-003 |

**Threshold logic.** With an open same-subject complaint and a repeat cue, CMP-003 >= 0.70 proceeds with a soft confirmation naming the complaint. Without any open complaint CMP-001 wins by default: one cannot escalate what does not exist, so this tree never asks in that case.

**Question sequence.**

1. Q1 (only when evidence is mixed), with the evidence shown: "I can see complaint CMP-... about *card charges*, opened on *date* and still open. Is this about that one, or a new issue?" Buttons: *That one* / *A new issue*.
2. If a new issue but the customer expresses repeated frustration, register it as CMP-001 and link the two for the reviewer.

**Safe default (after 2 turns).** Open the CMP-003 flow linked to the open complaint; a human reviewer splits it if it is in fact new. This favours the customer who has already waited.

**Style.** Empathy-First before any question (A9 Pattern 1, the Acknowledge and Assure steps come first), because CSAT in this category is 2.4 and resolution 58% (A1.2).

**Hooks.** Sentiment <= -0.7 for 2 turns fires ESC-004 independently of this tree. Conversation turn count > 15 without resolution fires ESC-010.

## 6. Pair 5: SEC-001 (fraud) vs TXN-002 (merchant dispute)

Diagram: `diagrams/disambiguation-05-sec-fraud-vs-txn-dispute.mmd`. The bridge between the two intents is the tertiary `TXN-002 > unrecognised_charge`.

**Why they collide.** "There is a charge I don't understand" is a dispute if the customer made the payment and something is wrong with it, and fraud if they did not make it. The customer often cannot tell.

| Evidence | Points to |
|---|---|
| Scam cue: shared OTP, clicked a link, fake bank call, installed a remote-access app | SEC-001 `scam_victim`, immediately (ESC-001 P0) |
| Not-me cue: didn't make/authorise, not me, hacked, unknown, maine nahi kiya, several unfamiliar charges, charge in another city while the card is in hand | SEC-001 `unauthorised_transaction` or `card_misuse` |
| Known-merchant cue: I bought, order, charged twice, wrong amount, refund, not delivered, cancelled | TXN-002 |
| Merchant name matches a past successful transaction with that merchant | Raises TXN-002 prior |
| Ledger shows a hold or pre-authorisation on that merchant | Raises TXN-002 prior (not fraud) |

**Threshold logic (safety-biased).** SEC-001 enters its flow at >= 0.50 with at least one fraud cue (flow-entry override); TXN-002 needs >= 0.70 with a known-merchant cue. When both apply, fraud wins. This is intended: a false fraud flow costs one extra question and a reclassification, and the customer keeps control because no block runs without explicit confirmation; a missed fraud report costs money and time.

**Question sequence.**

1. Q1 (buttons): "Did you make or approve this payment, even if the amount or merchant looks wrong?" Options: *Yes, I made it* / *No, I didn't* / *Not sure*. Hinglish: "Kya yeh payment aapne kiya ya approve kiya tha?"
2. If *Not sure*, Q2: "Do you recognise the merchant name, and do you have your card and phone with you?" The agent also checks the ledger for holds and pre-authorisations on that merchant.
3. Still unsure or unknown merchant: treat as `unauthorised_transaction`.

**Tone.** The agent never accuses the customer of lying or of a merchant of fraud. It says "let's make sure your account is safe" and keeps the dispute path open: a reclassification from SEC-001 to TXN-002 is allowed until a case has been handed to Fraud Investigation.

**Hooks.** SEC-001 fires ESC-001 (P0, Fraud Investigation, < 2 min). TXN-002 over INR 50,000 fires ESC-005 (P1). If both fire, P0 wins and the dispute is attached to the fraud case. Reports of an unauthorised access to the account (not just a transaction) fire ESC-009.

**Examples.**

- "Ek Rs 480 Swiggy charge samajh nahi aaya" -> TXN-002 `unrecognised_charge` 0.78, SEC-001 0.61, gap 0.17: gap is >= 0.15 but SEC-001 is above its 0.50 flow-entry gate and the merchant is known, so Q1 is asked (this is the Day 3 trace, turn 4 and 5).
- "I clicked a link and gave my OTP" -> SEC-001 `scam_victim` 0.93, no question, ESC-001.

## 7. Pair 6: CRD-001 (card block) vs SEC-001 (fraud report)

Diagram: `diagrams/disambiguation-06-crd-block-vs-fraud.mmd`.

**Why they collide.** Both end with a blocked card. The difference is the *fraud case*: SEC-001 also opens an investigation, lists unauthorised transactions and goes to a P0 queue; CRD-001 may be a lost card with no misuse, or a customer who simply wants to freeze it.

**Principle: contain first, classify second.** The block is common to both paths and is the urgent step, so the tree does not delay it with a classification question. The agent asks which card, takes explicit confirmation, blocks, and *then* asks the fraud question.

| Evidence | Points to |
|---|---|
| "Block my card", "freeze", "temporarily" | CRD-001 `block_temporary` |
| Lost, stolen, kho gaya, chori ho gaya, misplaced | CRD-001 `block_lost` / `block_stolen` |
| Someone used my card, transactions I didn't make, card cloned, shared card details | SEC-001 `card_misuse` (block is step 1) |
| "Unblock my card" | CRD-001 `unblock` (needs Biometric) |
| Block request shortly after a reported suspicious alert | SEC-004 -> SEC-001 |

**Threshold logic.** CRD-001 enters at >= 0.70. Executing the block needs >= 0.85 and explicit confirmation (nlu-pipeline-overview.md section 3, rule 2); between 0.70 and 0.85 the card pick-list and confirm step run first, so the block is never delayed past one confirmation. SEC-001 enters at >= 0.50 with any not-me or scam cue. If a message contains both a block request and a not-me cue, SEC-001 takes the lead and CRD-001 becomes its first step.

**Question sequence.**

1. If more than one card exists: pick-list "Which card? Debit ending 5678 / NexCredit Classic ending 4321".
2. Explicit confirmation: "I'll block the card ending 5678 now. Is that right?" (A9 Pattern 3). Never ask for the full number.
3. After the block, Q (buttons): "Do you see any payments you didn't make?" *Yes* -> SEC-001 `card_misuse` case with the transactions listed, ESC-001, then the replacement offer. *No* -> if lost or stolen, offer CRD-002 replacement as a chained step; otherwise explain the unblock path (Biometric).

**Safe default.** Block (confirmed, reversible), then ask. There is no case in which delay is the safer option.

**Hooks.** The block, the fraud case and the replacement are one chain, executed in that order. Replacement addresses follow ACC-004 rules, so a different delivery address is handled there first.

## 8. Coverage summary

| Pair | Tree | Clarifying questions | Entity rules | Threshold logic | Safe default |
|---|---|---|---|---|---|
| 1 TXN-001 / TXN-002 | dis-01 | Q1 status or wrong, then reason | Reason entity; id-only | 0.70 / gap 0.15 | Read status, offer dispute |
| 2 PRD-001 / PRD-005 | dis-02 | None by design | Evaluative verbs, personal cues | Advice detector 0.50, rule layer | Boundary reply |
| 3 ACC-003 / ACC-004 | dis-03 | Q1 which detail | Value shape, PIN, email token | 0.85 for writes | Human |
| 4 CMP-001 / CMP-003 | dis-04 | Q1 with evidence | complaint_id, open complaint, repeat cue | 0.70 with open complaint | CMP-003 flow, linked |
| 5 SEC-001 / TXN-002 | dis-05 | Q1 made or not, Q2 recognise | Scam cue, not-me cue, merchant history | SEC-001 0.50 / TXN-002 0.70 | `unauthorised_transaction` |
| 6 CRD-001 / SEC-001 | dis-06 | Card pick, then post-block fraud Q | Loss cue, not-me cue | CRD-001 0.70 / SEC-001 0.50 | Block, then ask |

All six pairs have a diagram, entity-based rules, threshold logic and a question sequence, as A3.4 requires.

## 9. Open items

- The Day 6 boss set (10 ambiguous messages: one per pair plus 4 cross-pair cases, 6 in Hinglish) is `tests/nlu/boss-level2.yaml`; its schema and scoring are in `tests/nlu/README.md`.
- Question and boundary-sentence wording is final only when the Day 13 templates are written; the wording above fixes the structure and the English canonical form.
- The 0.50 flow-entry gate and the 0.15 gap are defaults to be tuned on the NLU evaluation set; their change process is A12.3 (`intent_confidence_threshold`: NLU Team, A/B test required). The 0.50 gate for safety flows is a Risk Committee setting and should not be raised by an A/B result alone.
