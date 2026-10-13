# NLU Pipeline Overview

Component [3] Language & NLU Service. Brief refs: A2.2, A3.4, A6 (ESC-003), A12.3. Intents: `config/intents.yaml`. Entities: `config/entities.yaml`. Interface contract: `component-interfaces.md`. State: `config/dialogue_state.schema.json`. Thresholds below are defaults; the governed copies move to `config/parameters.yaml` on Day 13.

## 1. Stages

```
raw message
  -> [2] Input Guard: redaction (RED-01..07), injection and crisis screen
  -> 3.1 Language ID and code-switch tagging        (multilingual.md)
  -> 3.2 Normalisation: transliteration, number words, Devanagari digits, spelling
  -> 3.3 Context features: last agent act, open slots, topic stack, auth level
  -> 3.4 Encoder (shared, multilingual) with parallel heads:
         a. hierarchical intent (primary > secondary > tertiary)
         b. OOS / domain head
         c. sentiment, emotion, sarcasm heads        (sentiment.md)
         d. advice-detector head (PRD-005 boundary)
  -> 3.5 Entity extraction: regex, lookup, NER, constrained LLM (entities.md section 3)
  -> 3.6 Multi-intent segmentation and per-segment classification
  -> 3.7 Fusion and calibration -> NLU frame
  -> [4] Dialogue State Tracker
```

Reference model (provider-agnostic, per system-architecture.md): a fine-tuned multilingual encoder (MuRIL, IndicBERT or XLM-R class) with multi-head outputs, and an LLM fallback used only when the encoder is not confident. Calibration is by temperature scaling on a held-out split so that the numbers below behave like probabilities.

## 2. NLU frame (output)

```json
{
  "turn_index": 4,
  "language": {"primary": "hinglish", "code_switching": true},
  "intents": [
    {"label": "TXN-002", "layer_path": ["transaction", "dispute", "unrecognised_charge"],
     "layer_confidence": {"primary": 0.94, "secondary": 0.78, "tertiary": 0.71},
     "segment": [0, 41]},
    {"label": "SEC-001", "layer_path": ["security", "report_fraud", "unauthorised_transaction"],
     "layer_confidence": {"primary": 0.61, "secondary": 0.61, "tertiary": 0.55}, "segment": [0, 41]}
  ],
  "ambiguity": {"pair": "SEC-001|TXN-002", "gap": 0.17, "rule": "dis-05"},
  "out_of_scope": {"score": 0.04},
  "entities": [{"type": "amount", "value": 480, "currency": "INR", "span": [8, 13], "conf": 0.99, "source": "regex"},
               {"type": "merchant_name", "value": "Swiggy", "span": [14, 20], "conf": 0.97, "source": "lookup"}],
  "sensitive_flags": [],
  "sentiment": {"score": -0.42, "emotions": {"confusion": 0.6, "anxiety": 0.3}, "sarcasm": 0.05},
  "advice_detector": 0.02
}
```

The frame maps onto the state's `intent` (`label`, `confidence` = the secondary-layer score, `layer_path`, `layer_confidence`, `alternatives`, `multi_intent`, `out_of_scope` = true when OOS is detected per section 5, `implicit`) and `sentiment` objects. Confidence is reported per layer so the policy engine can apply the layer rules below.

## 3. Confidence thresholds and fallbacks per layer

A2.2 requires a threshold for each layer. Defaults:

| Layer | Act (proceed) | Clarify band | Fail-safe (floor) | Fallback when below |
|---|---|---|---|---|
| Primary | >= 0.85 | 0.50 to 0.85 | < 0.50 | Primary alone never triggers an action; it narrows the secondary candidates. Below the floor: open question with a quick-reply menu of the 5 most common topics |
| Secondary | >= 0.70 (A12.3 `intent_confidence_threshold`) | 0.40 to 0.70, or top-2 gap < 0.15 | < 0.40 | Clarify with at most 3 labelled options built from the top alternatives. Below the floor: FAIL_SAFE and `consecutive_low_conf` + 1 |
| Tertiary | >= 0.65 | 0.40 to 0.65 | < 0.40 | Proceed at secondary level using the default variant; ask the tertiary question only if the answer changes the action, template or auth level |

Rules that sit on top of the layers:

1. **Ambiguity gap (dialogue-management.md transition guards; the 0.70 and 0.40 tiers are D-06).** If the top two secondary hypotheses are within 0.15, the policy clarifies even if the top score is >= 0.70, unless the pair has a dedicated tree (`disambiguation.md`), which then runs instead of a generic clarification. A pair tree also fires when a third candidate ranks between the two pair members, provided both members are within the top 3 and the gap between them is < 0.15 (D-36; example: TXN-001 .52, TXN-003 .48, TXN-002 .44).
2. **Execution gate for safety-rated actions.** For HIGH or CRITICAL intents whose action is `write`, `protective_write` or `ticket`, executing needs secondary confidence >= 0.85 **and** explicit confirmation. Confidence of 0.70 to 0.85 sends the customer to the clarify or confirm step. Confirmation always follows, so the gate is a second line, not a substitute.
3. **Flow-entry overrides (asymmetric by design).** To *start* a safety flow the gate is lower: SEC-001, SEC-004, GEN-007, GEN-003 and PRD-005 enter their flows at >= 0.50. The cost of a false positive is one extra question or a boundary sentence; the cost of a miss is delayed fraud handling, a missed crisis or an advice breach. No protective action runs at this confidence; each still needs confirmation.
4. **Low-confidence counter (ESC-003).** Each customer turn with secondary confidence < 0.40 raises `consecutive_low_conf`. Three consecutive such turns fire ESC-003 (P2, General Support). Any turn >= 0.40 resets the counter; a clarification the customer answers also resets it.
5. **Clarification budget.** At most 2 clarification turns per ambiguity (`max_clarification_turns`, consistent with dialogue-management.md section 4.4). Then: the pair's safe default if it has one, otherwise a human offer with the gathered context.
6. **Session and context features.** Open slots, the last agent act and the topic stack are inputs, so a bare "yes", "5000" or "the second one" is classified as a slot answer or confirmation (not as a new intent) and does not count as a topic switch.
7. **Implicit intents** (anaphora, "same thing happened") inherit the topic's intent with a confidence cap of 0.75 (as in the Day 3 trace), so they cannot reach the 0.85 execution gate without a confirmation.

**Targets (from the brief).** Intent accuracy > 92%, entity accuracy > 95%, guardrail false positive < 3%. Evaluation is by held-out split with per-layer accuracy, macro-F1, confusion on the six pairs, and OOS precision and recall (plan section 6.1). The A/B rule for changing `intent_confidence_threshold` is set in A12.3 (0.50 to 0.95, NLU Team, A/B test required).

## 4. Multi-intent handling

A message can carry more than one intent ("block my card and also tell me the FD rate"; "my card is lost and my UPI payment failed").

**Detection**

1. Segment on clause boundaries and connectors: `and`, `also`, `plus`, `aur`, `saath mein`, `aur ek baat`, `ek aur`, `bhi`, sentence ends and bullet-like lists.
2. Classify each segment; entities are assigned to the nearest segment (proximity, then shared-entity rule: an amount in a trailing clause that has no amount attaches to the previous segment only if that segment needs one).
3. A secondary intent counts when its confidence is >= 0.60 (`multi_intent_second_min`); this is lower than the 0.70 act threshold because the question here is "is there a second request", not "execute it". The state flag `multi_intent` is set.
4. Two segments with the same intent but different entities are two *instances* ("two failed UPI payments"), handled one at a time.

**Ordering**

Intents are handled in `mi_rank` order (`config/intents.yaml`), lowest first:

| Rank | Intents | Why |
|---|---|---|
| 0 | GEN-007 | Crisis outranks everything |
| 1 | SEC-001, SEC-004 | Active fraud: time-critical, P0 |
| 2 | CRD-001, GEN-003 | Containment (card block) and human request |
| 3 | CRD-002, SEC-002, SEC-003 | Security follow-through and replacement |
| 4 | TXN-002, TXN-003, CMP-001, CMP-003 | Disputes, payment failures, complaints |
| 5 | Remaining account, transaction, card and complaint intents (17) | Routine reads and changes |
| 6 | PRD-001 to PRD-005, CMP-004, GEN-002 | Information and feedback |
| 7 | GEN-001, GEN-005, GEN-008 | Conversation management |
| 8 | GEN-004, GEN-006 | Out of scope and closure |

Rules:

- **Security first.** Any intent with rank <= 1 pre-empts: the others are parked on the topic stack with their entities and the customer is told ("I'll sort out the fraud report first, then come back to your FD question").
- **Dependent chains stay together.** CRD-001 then CRD-002 (block, then replace) is one chain: the block is done and confirmed before the replacement starts. ACC-003 then ACC-004 is another: the contact change moves the OTP destination that confirms the address change (`disambiguation.md` section 4).
- **Ties** use the order the customer gave.
- **Cap of 3.** At most 3 intents are acknowledged in one reply. A fourth is parked silently and surfaced when the earlier ones close (avoids the Information Dump anti-pattern).
- **Acknowledge all, act on one.** The first reply names every request so none feels ignored (Empathy-First, Context Carry-Over), then asks only for the slots of the first intent. One question per turn still applies.
- **Auth is least-privilege and step-up.** Authenticate for the first intent's requirement; step up only when the chain reaches an intent that needs more (for example OTP for the balance, Biometric when the customer then asks to change a phone number).
- **Conflicts.** Intents that cannot both be true (ACC-005 closure with ACC-007 upgrade in one message) are surfaced and the customer picks. A request that conflicts with safety (fraud report together with "close the account") is handled fraud first, and ACC-005 is handed to a human with ESC-007 checks.
- **Compound messages with advice.** A mixed message ("what's the FD rate and should I buy it") splits: PRD-003 is answered, PRD-005 gets the boundary reply, in one response.

## 5. Out-of-scope (OOS) handling

**Detection (any two of three signals, or the OOS head >= 0.80 alone)**

1. OOS/domain head: trained on in-domain intents against a synthetic OOS set that includes near-miss in-domain-looking negatives (other banks' accounts, loans NexBank does not offer).
2. Low maximum intent confidence together with a high energy or distance score from in-domain data.
3. Retrieval signal: the KB top result is below `retrieval_confidence_threshold` (0.65) for a query that is neither a known intent nor a follow-up.

OOS is separated from *low-confidence in-domain* by the domain head: an in-domain message with unclear intent is clarified; an out-of-domain message is not.

**GEN-004 categories and responses**

| Tertiary | Example | Response |
|---|---|---|
| off_topic | "Who will win the match?" | One-line friendly decline plus what the agent can help with (3 options). No opinions, no web answers |
| chit_chat | "How are you?", "tell me a joke" | Short template reply from a pool (brand tone: friendly), then redirect |
| unsupported_banking_request | "Open my account with another bank", "car loan", "buy bitcoin" | Honest limit (Graceful Degradation: acknowledge, offer what is possible, offer a human). Product names not in A13.1 are not confirmed or denied beyond "I don't have information on that" |
| adversarial_or_harmful | Injection, jailbreak, exfiltration, impersonation | Never answered by the LLM. The Guardian (`guardrails`, Day 9/10) returns the deflection template and logs the vector; repeated attempts escalate |

**Fallback ladder** (avoids the Robotic Loop anti-pattern, which penalises the same fallback repeated 3 or more times):

1. First OOS: acknowledge the limit, say what the agent can do, no apology repetition.
2. Second OOS in a row: change the format to quick-reply buttons for the top intents.
3. Third: offer a human with the gathered context (and `consecutive_low_conf` follows its own rule if scores are also below 0.40).

**Looks OOS but is not**

| Message | Correct handling |
|---|---|
| "Is HDFC's FD rate better than yours?" | PRD-005 (advice) or PRD-003 limited to NexBank's own rates; competitor data is never quoted |
| "Is it a good time to buy gold?" | PRD-005 forex-or-investment timing, not OOS |
| "Someone is threatening me" | GEN-007 (crisis flow), never OOS |
| "Tell me my friend's balance" | A4.2 rule 4 refusal; classified GEN-004 adversarial_or_harmful with the impersonation or third-party tag |
| "Tax filing help" | OOS (unsupported). Tax benefits of NexFD (Section 80C) are PRD-003 |

## 6. Latency budget

Per-turn budget for NLU is 250 ms (latency-scalability-cost.md). Proposed split, p95 (assumptions; not measured, nothing is built): language ID 10 ms, normalisation 10 ms, shared encoder with all heads 70 ms, entity extraction (regex, lookup, NER) 60 ms, segmentation and fusion 20 ms, calibration and frame 10 ms, headroom 70 ms. The LLM fallback runs only when the encoder is below the act threshold or extraction needs a free-text value. Because those turns end in a clarification and have no tool call, the fallback borrows from the unused tool-call slack so the < 3 s per-turn p95 still holds.

## 7. Failure behaviour

| Failure | Behaviour |
|---|---|
| NLU service down or timeout | Rule-based fallback for the top intents (keyword and regex for balance, card block, fraud, human, language) and the safety patterns; otherwise FAIL_SAFE and offer a human (FMEA in `failure-modes.md`) |
| Sentiment head down | Sentiment treated as unknown, not neutral; escalation proximity relies on other signals; empathy template applies on lexicon hits |
| Entity extraction conflict (regex vs LLM) | Regex or lookup wins; the conflict is logged |
| Calibration drift | Reliability diagram is part of the weekly metrics; a drift above 0.05 pauses threshold changes (A8 drift target) |

## 8. Open items

- Tertiary and entity targets per class (macro-F1 floor) are set from the class balance of the utterance library (`docs/intent-taxonomy/utterances.csv`).
- Language ID and the translation pipeline are specified in `docs/intent-taxonomy/language-detection.md` (`multilingual.md` holds the outline).
