# Level 1 Boss Trace: 20 turns, 12 topic switches

Walks one conversation through the dialogue state machine (`diagrams/dialogue-state-machine.mmd`). Intent labels follow the Day 4 taxonomy (`config/intents.yaml`); the provisional Day 3 labels were mapped in place (see `docs/intent-taxonomy/taxonomy.md` section 6). All data is synthetic. A *topic switch* is a high-confidence change of secondary intent that is not a slot answer or clarification (see `dialogue-management.md` §5.2).

Setup: a customer at `anonymous` auth, language Hinglish/English, sentiment starting near 0.

| T | Customer (synthetic) | NLU result | Phase transition | Topic stack (top first) | Auth | Agent action / notes |
|---|---|---|---|---|---|---|
| 1 | "Hi" | GEN-001 0.97 | INIT > INTENT_DETECT > RESPOND | [] | anon | Greeting plus AI disclosure. No switch (start) |
| 2 | "What's my balance?" | ACC-001 0.93 | INTENT_DETECT > AUTH_REQUIRED | [balance] | anon | **Switch 1.** Requires OTP; prompt secure OTP widget |
| 3 | (OTP entered in secure widget) | n/a (auth event) | AUTH_REQUIRED > RESPOND | [balance] | otp | Balance via template with locked slot. Topic resolved |
| 4 | "Ek ₹480 Swiggy charge samajh nahi aaya" ("I don't recognise a Rs 480 Swiggy charge") | TXN-002 (unrecognised_charge) 0.78; alt SEC-001 0.61 (gap 0.17) | INTENT_DETECT > CLARIFY | [txn_charge] | otp | **Switch 2.** Entities: amount 480, merchant Swiggy. Lookup found the txn. SEC-001 is above its 0.50 flow-entry gate, so pair 5 Q1 is asked ("Did you make or approve this payment?") |
| 5 | "I didn't make it" | disambiguation answer: SEC-001 (unauthorised_transaction) 0.88 | CLARIFY > SLOT_FILL | [fraud_report(txn_charge)] | otp | Continuation of topic 2 (not a switch): disambiguation resolves the intent to fraud. Escalation proximity rises. **ESC-001 fires** (P0, Fraud Investigation, < 2 min): `flag_fraud` runs and the handoff package is sent to the queue at once. The agent offers to connect now or carry on meanwhile; the customer's next message (block the card) shows they carry on, and the offer stays open |
| 6 | "Block my card ending 5678" | CRD-001 (block_after_fraud) 0.95 | SLOT_FILL > CONFIRM | [card_block, fraud_report(parked)] | otp | **Switch 3.** Security-related, so it pre-empts. Confirm: "Block card ending 5678? This can be reversed." |
| 7 | "Yes block it" | confirm 0.99 | CONFIRM > EXECUTE > RESPOND | [fraud_report] | otp | `block_card` with idempotency key; honest result; audit event. Gives the fraud case reference and says a specialist will contact them (no promised outcome, D-09) |
| 8 | "Also what's the 1 year FD rate?" | PRD-003 0.90 | RESPOND > INTENT_DETECT > RESPOND | [fd_info, fraud_report(parked)] | otp | **Switch 4.** Rate from the KB (template slot), cited with version |
| 9 | "Is it better than a mutual fund?" | PRD-005 0.82; advice detector fires | INTENT_DETECT > RESPOND (deflect) | [fd_info(advice_boundary), fraud_report(parked)] | otp | **Switch 5.** Advice boundary: factual FD features only, no recommendation; offer a human advisor option. `advice_deflections` = 1 |
| 10 | "Ok what was I asking before the card thing?" | anaphora > parked fraud_report 0.85 | INTENT_DETECT > RESPOND | [fraud_report] | otp | **Switch 6.** Pops the parked topic; reports the open fraud case for "the Rs 480 Swiggy charge" (reference, status from the system of record) and asks if they want to be connected now |
| 11 | "Also my UPI payment of 2000 failed" | TXN-003 0.91 | INTENT_DETECT > SLOT_FILL | [upi_failed, fraud_report(parked)] | otp | **Switch 7.** Amount 2000 captured; asks for the date/UPI ref |
| 12 | "Same thing happened last week" | implicit: TXN-003 0.73 (implicit cap) | SLOT_FILL > CLARIFY | [upi_failed, fraud_report(parked)] | otp | Continuation (not a switch). Ambiguous "same thing": asks whether it was the same amount/merchant. Implicit intent inherits the topic |
| 13 | "Forget that, how do I update my address?" | ACC-004 0.74; alt ACC-003 0.58 (gap 0.16) | INTENT_DETECT > CLARIFY | [address_update, fraud_report(parked)] | otp | **Switch 8.** UPI topic marked `abandoned` (explicit). "Address" alone is ambiguous (pair 3, email address vs postal), so Q1 is asked: "mobile number, email, or postal address?" |
| 14 | "Postal address. Can I do it here?" | ACC-004 0.91 (clarification answer) | CLARIFY > RESPOND | [address_update, ...] | otp | Continuation (not a switch). Self-service-link flow: the proof document is uploaded in the secure app and Biometric auth is required; the agent does not change records (an address change that alters KYC records would be ACC-008) |
| 15 | "This is ridiculous, nobody helps me!" | CMP-001 0.84; frustration, sentiment -0.7 | INTENT_DETECT > RESPOND (apologise) | [complaint, address_update(resolved), fraud_report(parked)] | otp | **Switch 9.** Tone shift: short empathy, then action. Proximity 0.62 prepares the handoff package |
| 16 | "I've been waiting 3 days for a refund" | CMP-003 (repeat_unresolved) 0.90 | RESPOND | [complaint, ...] | otp | Continuation (pair 4: open complaint plus a repeat cue). Looks up the dispute/refund status; only timelines from the system of record (D-09) |
| 17 | "What's the EMI on 5 lakh for 3 years on a personal loan?" | PRD-002 0.88 | INTENT_DETECT > RESPOND | [emi_calc, complaint, ...] | otp | **Switch 10.** Deterministic calculator with the catalogue rate; information only. Not pushed proactively (sentiment < -0.4), but the customer asked |
| 18 | "Never mind. Can I talk to a person?" | GEN-003 0.97; `human_request_count` = 1 | INTENT_DETECT > ESCALATING | [handoff] | otp | **Switch 11.** Hard trigger: honour human request. The policy may offer one quick option but must not stall |
| 19 | "Ok, thanks for blocking the card" | GEN-006 (thanks) 0.92 | ESCALATING > HANDOFF | [handoff] | otp | **Switch 12.** Brief acknowledgement; build the 8-element handoff package from state |
| 20 | (system) | n/a | HANDOFF > CLOSING | [] | otp | Warm handoff message, merged with the open ESC-001 case, summarising: card blocked (ref), unrecognised Rs 480 charge under the fraud case (ref), refund delay complaint, address-update route. The human accepts with no re-asking |

## Checks

- **Topic switches counted:** T2, T4, T6, T8, T9, T10, T11, T13, T15, T17, T18, T19 = **12**.
- **Safety invariants held:** no money movement or KYC change attempted; confirmation before the card block; advice boundary enforced at T9; hard human-request trigger at T18; the P0 fraud escalation (ESC-001) fires at T5 and is never bypassed or deferred by later topics (A4.2 rule 6).
- **Context management:** by T20 the history is exactly 20 turns, so nothing is lost to the summary; pinned facts (card block, open dispute, complaint, auth) would persist if the conversation continued past 20.
- **Anaphora/implicit/contradiction coverage:** T10 (anaphora to a parked topic), T12 (implicit intent), T13 (explicit abandonment, plus the pair 3 clarification answered at T14). A contradiction case (conflicting amount) is exercised in the Day 14 simulations.
- **Auth:** OTP at T3; the 5-minute inactivity rule (D-05) is not hit in this trace.
