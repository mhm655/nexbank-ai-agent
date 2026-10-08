# NLU Tests

Brief refs: A2.2 (hierarchy and thresholds), A3.4 (six disambiguation pairs), Part B Level 2 boss. Plan: section 6.1 (NLU evaluation set). Pipeline: `docs/architecture/nlu-pipeline-overview.md`. Rules under test: `docs/intent-taxonomy/disambiguation.md`. Intents: `config/intents.yaml`.

## Contents

| File | Purpose |
|---|---|
| `boss-level2.yaml` | The Level 2 boss: 10 ambiguous messages with expected intent, runner-up, pair, reasoning, action and clarifying question |
| `docs/intent-taxonomy/utterances.csv` | The labelled utterance library; its `test` split is the held-out NLU evaluation set (`dev` is for threshold and calibration tuning) |
| Per-pair test cases (`NLU-DIS-<pair>-<nn>`) | Reserved for later expansion; the boss set already uses this ID scheme |

## Schema: `boss-level2.yaml`

Top level: `schema_version`, `set_id`, `unlock_condition`, `coverage`, `cases[]`.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `NLU-DIS-<pair>-<nn>` for a case aimed at one pair (pair 1 to 6); `NLU-DIS-X-<nn>` for a cross-pair case |
| `message` | string | The customer text, synthetic, in the language named below. Never contains card numbers, OTP, CVV, PIN or Aadhaar values |
| `language` | enum | `en`, `hi`, `hinglish`, `ta`, `te`, `bn`, `mr`, `gu` (the `language` entity values) |
| `preconditions` | object | State the case assumes: `auth_level`, `open_complaints`, `cards_on_file`, `ledger`, `last_agent_act`. Same names as the dialogue state |
| `disambiguation_pair` | string | The pair or pairs in play, as `ID vs ID` |
| `candidates` | list | The 2 or 3 intents a naive classifier could return |
| `expected_intent` | intent ID | The intent the NLU frame must rank first |
| `runner_up` | intent ID | The intent that must rank second; it is also what the tree must not confuse with the first |
| `expected_action` | `clarify` or `act` | `clarify` = the policy asks a question before any flow starts. `act` = the policy proceeds without a classification question (it may still ask a slot question, a card pick-list or an explicit confirmation, and no write executes without confirmation) |
| `rule_ids` | list | Decision-tree rules that resolve the case (`dis-01` to `dis-06`) |
| `reasoning` | text | Why the case resolves this way: evidence used, threshold behaviour, safe default |
| `clarifying_question` | object or null | For `clarify`: English and Hinglish wording plus the button `options` (at most 3). `null` for `act` |
| `follow_up` | text or object | What happens next (slot question, confirmation, escalation hook, post-action question) |
| `must_not` | list | Behaviours that fail the case even if the intent is right |

Question wording is the canonical English form and a Hinglish pattern. Final copy is a Day 13 template, so the test checks structure (one question, closed form, at most 3 options, evidence stated), not exact strings.

## Scoring a boss case

A case passes only if all hold:

1. `expected_intent` is rank 1 and `runner_up` is rank 2 in the NLU frame (after the rule layer).
2. The policy's action equals `expected_action`.
3. For `clarify`: exactly one question, closed form, at most 3 options, wording differs on a second attempt, the budget is `max_clarification_turns` (2).
4. No `must_not` behaviour occurs.
5. The frame logs `ambiguity.pair` and the resolving rule ID from `rule_ids`.

The boss level is unlocked when all 10 pass (brief Part B). Boss cases are never used for training or threshold tuning.

## Evaluation metrics (utterance library)

Computed on the `test` split of `utterances.csv`; `dev` is used for tuning, `train` for training. Targets from the brief are intent accuracy > 92%, entity accuracy > 95%, guardrail false positive < 3%. All other floors below are my proposals, to be fixed after the first run (`nlu-pipeline-overview.md` open items).

| Metric | Definition | Notes |
|---|---|---|
| Per-layer accuracy | Share of test utterances whose predicted label matches the gold label, computed separately for the primary layer (6 classes), the secondary layer (intent ID) and the tertiary layer (label). Primary gold is derived from `config/intents.yaml` (card intents map to `account`, D-13) | Tertiary is scored only when the secondary is correct and also reported unconditionally |
| Macro-F1 | Unweighted mean of per-class F1 over the 41 intents (secondary) and over the 145 tertiary labels | Intents are balanced by construction (13 to 17 rows each), so macro and micro are close; report both. Proposed floor: secondary macro-F1 >= 0.90 |
| Pair confusion | For each of the 6 pairs (A, B): `confusion(A to B)` and `confusion(B to A)` as shares of the gold rows of each member, plus the clarify rate on pair rows | Pair 5 and 6 are safety-biased: a SEC-001 row predicted as TXN-002 or CRD-001 is reported separately as a **fraud miss**; its target is 0 on the boss set and as low as possible on the library. A TXN-002 row sent to SEC-001 is tolerated (the cost is one question, D-19) |
| OOS precision and recall | Positive class = `GEN-004`. Precision = GEN-004 predictions that are truly GEN-004; recall = GEN-004 rows detected. Scored on the OOS head decision (`out_of_scope` = true) so that in-domain low-confidence rows are not counted as OOS | The OOS set includes near-miss negatives (a competitor's product, an unsupported loan). In-domain `kb_gap` rows (ACC-007, CRD-004, PRD-003 `rd_rate_enquiry`, GEN-008) must **not** be flagged OOS |
| Entity accuracy | Exact match of `key=value` pairs against the `entities` column, per entity and overall (precision, recall, F1 over pairs). **Text track only**: gold is what the utterance text itself supports (D-37) | Values are compared after normalisation (`50k` equals `50000`); masked values compare on the masked form |
| Context-entity accuracy | Separate **context track**: entities injected or inferred from state, not from the text (`alert_reference` in SEC-004, `account_type` or `current_account_type` from a single account, `card_type` from topic memory or an ambiguous "credit card"). Gold comes from the case's `preconditions` or fixture, never from the CSV | Reported separately, never merged into the 95% text-entity target. Inferred values must still be confirmed before a side effect (`entities.md` section 5) |
| Safety-flow recall | Recall of SEC-001, SEC-004, GEN-003, GEN-007, PRD-005 at the 0.50 flow-entry gate | These intents are entered at a lower gate (D-19), so recall matters more than precision here; GEN-007 recall target is 1.0 on the library |
| Execution-gate check | Share of HIGH or CRITICAL write intents that would execute at secondary confidence < 0.85 | Target 0 |
| Clarification metrics | Clarify rate, wrong-branch rate after the answer, mean turns to resolution (budget 2) | Logged per pair rule (`dis-01` to `dis-06`) |

### Slices (reported for every metric above)

- **By language:** `en`, `hi`, `hinglish`, pooled secondary (`ta`, `te`, `bn`, `mr`, `gu`). The secondary test rows are too few for stable per-language numbers; the per-language view starts when the Day 14 simulations and any native-reviewed expansion add rows (`language-detection.md` section 8, D-22).
- **By `notes` tag:** `typo`, `sarcasm`, `code-switch`, `multi-intent`, `kb_gap`, `pair-1` to `pair-6`.
- **By split hygiene:** a row never appears in two splits; templated near-duplicates are kept in one split.

### Multi-intent rows

A multi-intent row carries the intent with the lowest `mi_rank` in `intent_id` (ties: order of mention) and the others in `notes` as `also <ID>`. The metric for these rows is segment-level: each intent in `intent_id` plus `also` is a gold segment, and the row counts as correct if all gold segments are detected in the right order (`nlu-pipeline-overview.md` section 4). Single-label accuracy is also reported for comparison.

## `utterances.csv` format

Columns: `id, intent_id, tertiary_label, language, text, entities, split, notes`.

- `id`: `U-<intent_id>-<nn>`, unique.
- `tertiary_label`: must be one of the intent's `tertiary` values in `config/intents.yaml`.
- `entities`: semicolon-separated `key=value`, keys from `config/entities.yaml`. **Text-derived only** (D-37): a value that is injected or inferred from context (`alert_reference`, inferred `account_type` or `card_type`) is not listed here and is scored in the context track. Empty if none. Sensitive identifiers appear only masked (last 4 digits, `n***@example.com`, `+91 98XXX XXX10`); no OTP, CVV, PIN, Aadhaar or full card or account number appears anywhere.
- `split`: `train`, `dev` or `test`, stratified per intent so every intent is present in `test`; the test split is also stratified by language class.
- `notes`: free tags separated by `;` (`typo`, `sarcasm`, `code-switch`, `multi-intent; also <ID>`, `pair-<n>`, `kb_gap`, `crisis`). `kb_gap` is on every row of an intent marked `kb_gap: true` in `config/intents.yaml` (ACC-007, CRD-004, PRD-003, GEN-008), including all PRD-003 tenure-wise FD rows. `postal-pin-exception` marks the RED-04 postal-code case (`U-ACC-004-10`).
- **Label convention (D-38, D-39).** TXN-003 `debited_not_credited` = the customer says money left the account but the UPI payment failed or the receiver was not credited, even if the text also says "failed" or "declined"; `payment_declined` = failed or declined with no debit stated. GEN-005 `explicit_request` = the customer asks for a language; `detected_code_switch` = the customer switches or struggles without naming a request.

Secondary-language rows were written by the author and are **not yet native-speaker reviewed**; they are provisional gold until the review described in `docs/architecture/multilingual.md` (Quality assurance) is done.

## How to run (spec)

A light harness is optional (D-11). The contract is: load `utterances.csv`, filter `split == test`, call the NLU service, write one JSONL row per utterance (`id`, predicted frame), compute the metrics above, and exit non-zero if a hard gate fails (execution-gate check, fraud-miss on boss cases, GEN-007 recall). A boss run loads `boss-level2.yaml`, applies each case's `preconditions` to the state, and checks the scoring rules above.
