# Entity Catalogue and Slot-Filling Policy

Source of truth: `config/entities.yaml` (51 extractable entities plus 1 dialogue-act slot). Intent-to-entity links: `config/intents.yaml`. Brief refs: A2.2 (entity table), A3 (required entities), A4.2 rules 1, 2 and 4, A10 (PII). The eight entity types in the A2.2 table are all present with the brief's sensitivity labels.

## 1. Sensitivity tiers and handling

| Tier | Meaning | Entities (examples) | In logs | Visible to the LLM | In dialogue state |
|---|---|---|---|---|---|
| LOW | Public or non-personal | merchant_name, product_name, date, language | plain | yes | plain |
| MEDIUM | Personal context, not an identifier | amount, transaction_id, upi_ref, complaint_text | plain | yes | plain |
| HIGH | PII | account_id, phone_number, email, new_address, nominee_name | masked | masked form only | masked or opaque ref |
| CRITICAL | PCI or KYC | card_last4, aadhaar_last4, pan, proof_document | never raw | no | masked or opaque ref |

A2.2 labels: Account Number HIGH-PII, Transaction Amount MEDIUM, Card Number (Partial) CRITICAL-PCI, Aadhaar (Partial) CRITICAL-KYC, PAN CRITICAL-KYC, UPI ID MEDIUM, Phone Number HIGH-PII, Merchant Name LOW. All kept.

## 2. Input Guard redaction (before NLU)

Some values must never reach the NLU model, the LLM, the state store or the logs. The Input Guard (component 2) redacts them first and passes NLU a typed placeholder plus a flag, so the NLU can still tell that "the customer sent a card number" without ever holding it.

| ID | Detects | Placeholder | Reply |
|---|---|---|---|
| RED-01 | Full card number: 13 to 19 digits passing Luhn | `[CARD_REDACTED]` | Ask the customer not to share it; offer the last-4 route |
| RED-02 | CVV/CVC next to 3 to 4 digits | `[CVV_REDACTED]` | Same, plus a security note |
| RED-03 | Full Aadhaar: 12 digits passing the Verhoeff check | `[AADHAAR_REDACTED]` | Explain that only the last 4 digits are ever needed |
| RED-04 | PIN, password or passcode value | `[SECRET_REDACTED]` | Never ask for or accept; point to the reset flow (SEC-003) |
| RED-05 | OTP typed in chat | `[OTP_REDACTED]` | Redirect to the secure OTP widget; if the OTP was given to a third party, run the SEC-001 `scam_victim` check |
| RED-06 | Full PAN | `[PAN_REDACTED]` | Redirect to the secure form (D-14) |
| RED-07 | Full account number | `[ACCT_REDACTED]` | Switch to a masked reference or a pick-list |

**RED-04 postal-code exception (D-35).** A 6-digit Indian PIN code in an address context is address data, not a credential: "address change karna hai, pin code 452001" (`U-ACC-004-10`) must reach NLU so `new_address` can be captured. The 6 digits are left unredacted only when all of these hold: (a) they match `[1-8][0-9]{5}` and follow an explicit postal marker ("pin code", "pincode", "postal code", "zip"), or the address slot is open and the digits sit inside an address phrase (city, state, locality, house or flat tokens); (b) no credential cue precedes them ("pin", "mpin", "atm pin", "upi pin", "card pin", "password", "passcode", "pwd" without "code" directly after "pin"); (c) the message or turn holds no OTP or credential cue and the agent has not just asked for a PIN (SEC-003 flow). Any doubt means redact (fail closed: a false redaction costs one re-ask). Credential PIN redaction stays strict: "my PIN is 482910", "mpin 4829" and a bare 4 to 6 digit reply to a PIN request are always redacted. The stored `new_address` stays HIGH, `ref_only`.

This is A4.2 rule 1 (never display, read out or transmit full account, card, CVV, PIN, password or Aadhaar numbers) applied on the way in as well as the way out. False positives (a 16-digit order number that passes Luhn) cost one polite redirect and are accepted; a miss is a compliance incident. Expected false-positive handling and measurement belong to the Day 9 guardrail spec.

**Decision D-14 (PAN).** A2.2 lists PAN with "Format + NSDL verification" but marks it CRITICAL-KYC, and rule 1 does not name PAN. I treat it as never accepted in free chat: the value is entered in the secure form widget, which performs the NSDL check, and the chat keeps `ABCDE****F` only.

## 2a. Entity scoring convention (D-37)

The `entities` column of `utterances.csv` holds **text-derived entities only**: a pair is gold only if its value can be read, looked up or normalised from the utterance text itself (`50k` to `50000`, "Hindi mein" to `language=hi`, "NexSave" to `account_type=savings`). Entities that come from context are **not** in the CSV: `alert_reference` (injected by the SEC-004 alert flow), `account_type` or `current_account_type` inferred from the customer's only account, and `card_type` inferred from topic memory or from an ambiguous phrase ("credit card" does not give `credit_classic` or `credit_premium`). They are scored in a separate **context track** (gold comes from the test fixture's `preconditions`, not from the CSV) so the text-only entity accuracy (target > 95%) is not penalised for values the text cannot contain. Slot-filling from context (section 5) is unchanged; this convention only fixes what the NLU is scored on. See `tests/nlu/README.md`.

## 3. Extraction approach

Methods run in this order for each entity; the first to succeed with confidence wins, and the LLM is the last resort.

1. **Regex and checksum** for structured identifiers (account ID, UPI ref, UTR, PAN-like shapes, phone, email, amount patterns).
2. **Lookup** against closed lists (product names, enums, merchants, banks, cities, Hindi and Hinglish aliases).
3. **NER** (the fine-tuned multilingual encoder named in the reference stack) for amounts with words, names, addresses, dates.
4. **LLM extraction**, schema-constrained, only for free-form values (complaint text, descriptions, close reasons). An LLM-extracted value never overrides a regex or lookup value, and any LLM-extracted entity that feeds an action is echoed back for confirmation.
5. **Dialogue extraction** for values that come from the flow, not the text (`proof_document`, `alert_reference`, `confirmation`).

Hinglish and code-switching: lookup tables include Devanagari and Romanised forms (for example `kal`, `parso`, `paanch hazaar`, `har mahine`, `ghar ka loan`). Number words and Devanagari digits are normalised before the amount and date rules run.

## 4. Validation rules (summary)

Each entity has a full rule in `config/entities.yaml`. The ones that matter most for safety:

- **Ownership first.** `account_id`, `transaction_id`, `card_last4`, `complaint_id` and `upi_ref` are resolved only inside the authenticated customer's own records. A value that is not theirs gets a neutral "I can't find that" and never confirms or denies that it exists elsewhere (A4.2 rule 4).
- **Never more than the last four.** `card_last4` and `aadhaar_last4` accept exactly 4 digits. Entering more triggers the redaction path.
- **Product names resolve to A13.1 only.** An unknown product is not mapped to the nearest match, so "Tata AIG term plan" does not become NexProtect (hallucination trap).
- **Amounts are compared to the ledger.** A mismatch between a stated amount and the ledger amount is a contradiction handled per `dialogue-management.md` section 5.4, not silently overwritten.
- **Dates are made absolute** against the conversation clock (IST), so "kal" and "last Friday" are stored as dates.
- **A write needs the exact value.** `new_value` is stored as a pending change and applied only after OTP to the old and new contact (ACC-003).

## 5. Slot-filling policy

**Slot states** (as in the state schema): `empty`, `filled`, `inferred`, `confirmed`, `invalid`, `conflicting`. `inferred` marks a value resolved from anaphora or topic memory; it must be confirmed before any side effect (`dialogue-management.md` section 5.1).

### 5.1 Required, optional and defaults

- **Required** slots must be `filled` (and for writes, `confirmed`) before the action runs. `{any_of: [...]}` is satisfied by one member.
- **Optional** slots are never asked for unless the answer changes the outcome.
- **Defaults** are used only when a single, safe answer exists:

| Slot | Default | Condition |
|---|---|---|
| account_id (ACC-001) | The customer's only account | Exactly one account held |
| date_range (ACC-002) | Last 30 days | Always, stated back |
| statement_format (ACC-002) | PDF | Always, stated back |
| email destination (ACC-002) | Registered email | Never a new address in the same turn |
| complaint_id (CMP-002) | The single open complaint | Exactly one open |
| callback phone (CMP-005) | Registered phone | Always |
| card_type | The card named earlier in the conversation | Resolved from topic memory |

A default is shown to the customer ("I'll send the last 30 days as a PDF to your registered email") and is never applied to a HIGH or CRITICAL write.

### 5.2 Order of questions

1. Fill from what was already said: the current message, then topic memory, then Context Carry-Over from earlier contacts (A9 Pattern 5), then CRM data.
2. Ask only for missing required slots, **one question per turn**, most discriminating first (it should narrow the ledger candidates or fix the intent).
3. **Offer a pick-list** instead of free text whenever candidates exist (accounts, recent transactions, cards, beneficiaries). Pick-lists show masked values.
4. After two failed attempts at the same slot, change method: switch from free text to a widget or a pick-list. After three, offer a human (the robotic loop anti-pattern: never ask the same question the same way three times).
5. If the customer changes topic while a slot is open, park the slots with the topic (topic stack, `dialogue-management.md` section 5.2).

### 5.3 Confirmation strategy

| Level | Used for | Form |
|---|---|---|
| None | LOW-risk reads (ACC-001, TXN-001, TXN-004, CRD-005, CMP-002) | Answer directly |
| Implicit (soft) | MEDIUM reads and tickets (ACC-002, TXN-003, CMP-001, ACC-008) | State the value used in the answer; the customer can correct it |
| Explicit | Every state change, ticket with HIGH or CRITICAL safety, and protective action (A9 Pattern 3) | Summary, all relevant details with masked numbers, a yes/no question, wait for an affirmative, then give a reference number |

Explicit confirmation rules: the confirmation must answer the open `pending_confirmation`; silence, "ok" in reply to something else, and an answer after a topic switch do not count. A confirmation expires at the end of the confirmation window (default 2 turns or 2 minutes, `dialogue-management.md` section 2), on a topic switch, or at the session timeout (5 minutes, A12.3), whichever comes first.

### 5.4 Contradictions and corrections

If a new value conflicts with a filled one, the slot becomes `conflicting` and the agent asks which is right, naming both ("You said Rs 480 earlier and Rs 840 now"). A correction by the customer ("no, I meant 840") replaces the value and re-opens confirmation for any dependent action.

## 6. Entity coverage by intent

Every entity in the catalogue is required or optional for at least one intent, and every entity named in `config/intents.yaml` exists in the catalogue (checked by script on Day 4; the cross-reference lint on Day 15 repeats it).

## 7. Open items

- Sample utterances that exercise each entity in English, Hindi and Hinglish arrive on Day 6.
- `desired_account_type` and `current_account_type` stay thin because A13.1 lists one account product; Day 7 KB entries decide whether variants exist.
- Callback hours and PSP and bank lists are configuration data, not specified in the brief.
