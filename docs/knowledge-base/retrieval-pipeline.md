# Retrieval Pipeline

Component [6] Knowledge Retrieval. Brief refs: A2.3 (dense, sparse or hybrid with fusion weights; cross-encoder re-ranking; contextual query modification; confidence scoring with an uncertainty threshold; maximum 200 ms at p95; graceful fallback), A4.3, A6 (ESC-008), A10 (logging), A11.1 (KB staleness, P0). Plan refs: section 3.4, section 4 Phase 3 items 3, 4 and 7, section 6.1. Decisions: D-41 to D-48 in `docs/assumptions-and-decisions.md`. Data model, TTL classes and auth levels: `kb-schema.md`. Diagram: `diagrams/retrieval-pipeline.mmd`. Interface contract: `docs/architecture/component-interfaces.md` row 6. Access rules: `access-control-matrix.md`. Update and staleness workflow: `maintenance-workflow.md`.

Thresholds are defaults here. The governed copies move to `config/parameters.yaml` on Day 13 (`retrieval_confidence_threshold` is already an A12.3 parameter name used in `nlu-pipeline-overview.md` and `language-detection.md`; its value 0.65 is the same in all three places).

## 1. Overview

```
Policy Engine request
  -> [1] query rewrite (rules, no LLM on the hot path)
  -> [2] hard pre-filter (index epoch, status, auth, expiry, audience lane)
  -> [3a] dense top-20   [3b] BM25 top-20      (parallel, both inside the filter)
  -> [4] weighted fusion 0.6 / 0.4, intent prior, gap-entry companions
  -> [5] cross-encoder re-rank -> top-5, calibrated relevance
  -> [6] confidence + decision (answer | gap | graceful degradation | ESC-008 | step-up)
  -> RetrievalResult {passages[{id@version, score, lane, flags}], confidence, decision, latency}
```

The retriever never writes text for the customer. It returns passages with scores and flags. The Policy Engine picks the action, the Response Generator builds the reply and the Output Safety Layer checks every number against the returned passages.

## 2. Request and response

| Field | Direction | Notes |
|---|---|---|
| `rewritten_query` | in | Output of section 3. Sanitised text only; the Input Guard has already redacted identifiers (D-21, D-35) |
| `original_query`, `language` | in | Kept for the multilingual path and for logging. `language` is one of `en`, `hi`, `hinglish`, `ta`, `te`, `bn`, `mr`, `gu` |
| `auth_level` | in | The session level at the moment of the turn (`anonymous` when the session has timed out). Missing or unreadable means `anonymous` (fail closed) |
| `intent_hint` | in | Top NLU intent and up to two alternatives. A soft prior, never a filter (kb-schema section 10) |
| `mode` | in | `answer` (customer evidence) or `guidance_only` (the Policy Engine wants only the agent-internal rules for an action, for example the advice boundary before a refusal) |
| `now` | in | Request time, used by the expiry filter. One clock per turn |
| `passages[]` | out | Up to 5 entries, each `{id, version, score, lane, stale, translation_unavailable, gap_handling}` |
| `confidence` | out | Section 8 |
| `decision` | out | `answer`, `gap`, `degrade`, `escalate_esc_008`, `step_up` or `unavailable` |
| `step_up_hint` | out, Policy Engine only | Required level, set only by the probe in section 5.4 |
| `latency` | out | Per stage milliseconds |

A locked kb slot is filled with the served-language body only when the entry has a current reviewed `body_i18n`; otherwise the English body is used verbatim and `translation_unavailable` is set. Nothing is machine-translated. `TPL-KB-TRANSLATION-UNAVAILABLE` is the alternative reply (say so and offer English, Hindi or a person); entries need reviewed `body_i18n` to close the gap (D-199).

## 3. Query rewrite

Rewrite runs in the "state and policy" slot of the per-turn budget (50 ms), not in the retrieval budget. It is rule-based: no LLM call on the hot path, because an LLM hop would cost more than the whole retrieval stage. An LLM rewriter is allowed only offline, to build evaluation variants.

| Step | Rule | Example |
|---|---|---|
| Anaphora | Resolve "it", "that card", "the same" against the dialogue state in the order of `dialogue-management.md` section 5.1 (active topic, parked stack, last 5 turns). Replace the pronoun with the entity's catalogue name. Two tied candidates: do not retrieve, ask the customer (the policy action is `clarify`) | "What is the interest-free period on it?" after a Premium card turn becomes "interest-free period NexCredit Card Premium" |
| Entity injection | Add non-sensitive entities from the state: product name, tertiary intent label, card type, topic (for example `fraud_report`, `cooling_off`). Never inject a masked card number, account number, UPI ID, amount, name or any CRITICAL or HIGH sensitivity entity from `config/entities.yaml`. The query is not a place for identifiers | Entity `card_type: premium` is injected; a masked last-4 is not |
| Implicit intent | A short follow-up inherits the active topic with `implicit: true` (dialogue-management section 5.3). The rewrite uses the inherited topic words | "and the Classic one?" becomes "NexCredit Card Classic" plus the previous question's topic |
| Multi-intent | NLU segments (cap of 3 acknowledged, nlu-pipeline-overview section 4) are retrieved separately, one request per segment, then merged by the Policy Engine | "FD rate and should I buy it" becomes two requests: PRD-003 facts and the PRD-005 boundary |
| Compound questions | One intent with several information needs (for example eligibility, rewards and fees in one question) is kept as one query. Section 8 defines how confidence works when several entries are synthesised | Boss query KB-BOSS-L3-01; the other four boss queries are multi-intent and are scored per segment (`tests/kb/README.md`, Scoring a case) |
| Normalisation | Lower-case for BM25, Unicode NFKC, digit folding (D-21), no stemming across languages, banking terms kept in the customer's form ("EMI", "FD", "OTP") | |
| Language handling, primary | `en`, `hi`, `hinglish`: the query is sent in the customer's own language and script. The multilingual dense model matches it to the English bodies and to the reviewed `body_i18n` texts. For BM25, a banking-term lexicon maps common transliterations to the English index terms (for example "byaaj" to "interest") so a Hinglish query still hits title and body terms. The lexicon is part of the NLU lexicons, reviewed by a native speaker (pending) | "FD pe tax benefit milta hai?" |
| Language handling, secondary | `ta`, `te`, `bn`, `mr`, `gu`: the **English pivot is the retrieval query** (`language-detection.md` section 6). The native text is passed along for logging and for the Output Safety Layer fact match. Pivot quality below `pivot_quality_floor` (0.60) means the turn counts as low retrieval confidence and goes to the fallback ladder in `language-detection.md` section 7 | |
| Language is not a filter | An entry is retrievable whatever its `languages`. If the best body in the customer's language is missing or stale, the English body is used and the flag `translation_unavailable` is set. The Response Generator then says so and offers Hindi, English or a human; it does not machine-translate a financial fact (`language-detection.md` section 6) | |
| Security | Retrieved text and the query are data, never instructions. A query that contains instruction-like text is handled by the Input Guard before this point; the rewrite adds no free text of its own | |

Fail-safe: if the rewrite cannot resolve a reference and the policy cannot ask (for example the channel is a one-way voice prompt), the retrieval runs on the un-rewritten query and the result is tagged `rewrite_unresolved`; the answer then needs confidence at the normal threshold with no help from entity injection.

## 4. Index layout

- **Unit.** One index document per `id` and language body. The text indexed is `title`, `body` (or the `body_i18n` text for that language) and the flattened `structured_fields` as `key: value` lines, so a figure in a structured entry is both searchable by BM25 and checkable. Entries are short, so there is no chunking; one entry is one passage. If an entry ever grows beyond what the re-ranker accepts, it is split by section and the part keeps the parent `id`.
- **Metadata stored with each document, used by the filter:** `id`, `version`, `status`, `effective_from`, `expires_at`, `ttl_class` (hard or soft), `auth_level_required` (as rank), `audience`, `category`, `regulatory_tags`, `intents`, `gap_handling`, `gap_for`, `languages`.
- **Dense index.** Multilingual embeddings of the document text, one vector per language body. Approximate nearest neighbour search with the filter applied inside the search (pre-filter).
- **Sparse index.** BM25 with a title field boosted over the body (the boost is tuned on the `dev` split) and per-language analysers for the `hi` and `hinglish` bodies.
- **Version serving.** Only the version with `effective_from <= now` and status `published` is searchable per `id`. A deprecated version stays in the version store, not in the search index, so a retired text cannot be returned (kb-schema section 6). Each publish or rollback creates a new `index_epoch`.
- **Corpus size.** The sample KB has 77 entries, so top-20 per list already covers a large part of the corpus. The design does not depend on that. At production size (thousands of entries) the same 20 plus 20 holds and the re-ranker budget does not grow.

## 5. Hard pre-filter

The filter runs inside both searches (dense and BM25), not after them. A post-filter would let a high-ranked ineligible entry take one of the 20 slots and starve the re-ranker; it would also compute scores for entries the customer must not see. The filter is a conjunction. An entry that fails any clause does not exist for this request.

| # | Clause | Rule |
|---|---|---|
| 1 | Index epoch | The search runs on one `index_epoch`. A publish during a turn is invisible until the next turn |
| 2 | Status | `status == published`. Draft, in review, approved (not yet live), deprecated and expired entries are not searchable |
| 3 | Effective date | `effective_from <= now` |
| 4 | Expiry | Hard classes (`regulatory`, `rates`): `now < expires_at`. Soft classes (`product_features`, `policy`, `faq_troubleshooting`, `escalation_procedure`): `now < expires_at + 30 days` (the grace period of D-27, confirmed in `maintenance-workflow.md`). A soft entry past `expires_at` is served and flagged `stale` (section 7); a review ticket already exists |
| 5 | Auth level | `rank(session.auth_level) >= rank(entry.auth_level_required)`. Order: `anonymous` < `otp_verified` < `biometric_verified` < `full_kyc` (kb-schema section 9) |
| 6 | Audience lane | `customer_facing` entries go to the **evidence** lane (the Generator may quote or paraphrase). `agent_internal` entries go to the **guidance** lane (they steer the agent and are never quoted; the Output Safety Layer rejects a reply that copies one). Both lanes use the same auth clause. In `mode: answer` both lanes are searched and ranked together; in `guidance_only` only the guidance lane is searched. Customer-visible citations list only evidence-lane IDs. The cached FAQ path (section 11) serves evidence-lane entries only |

What the filter does not use: the NLU intent (soft prior only), the language (section 3), and the regulatory tags (they drive grouping and the ESC-008 rule, section 9). A misclassified intent therefore cannot hide the right entry.

### 5.1 Hard expiry outcomes

An entry excluded by a hard expiry is simply absent. The consequences are fixed:

- For a `rates` topic (a figure), the matching gap entry is the fallback. Gap entries live in the 365-day class and hold no figure, so serving one after the source expired is safe (kb-schema section 11). The reply states no figure and offers a human.
- For a `regulatory` topic, the fallback is KB-ESC-008 and ESC-008 (section 9), not an answer from memory.
- Both cases raise a P0 staleness alert (A11.1 lists KB staleness from delayed regulatory updates as likelihood Medium, impact Critical, P0) to the owner and the Regulatory Compliance Manager (`maintenance-workflow.md` section 6).

### 5.2 Empty after filtering is not "no information"

If the filter removed entries that would have scored well, the customer must be stepped up, not told the topic is unknown (kb-schema section 9, D-29). Because the filtered entries are invisible to the search, the step-up probe in section 5.4 detects this case.

### 5.3 Why no ranking leakage

Scores, ranks and counts of filtered entries are never exposed to the customer or to the Response Generator. The only trace is the aggregate count in the log (section 12), which is an operations field.

### 5.4 Step-up probe

Runs only on the low-confidence path (section 9), when `auth_level` is below `full_kyc`, so it adds no time to a confident answer.

1. Run the same rewritten query against a **metadata-only** copy of the index (`id`, `auth_level_required`, `audience`, an embedding of the title) with the auth clause relaxed and every other clause kept.
2. Only `customer_facing` (evidence-lane) entries count as probe hits: a guidance entry gives the customer nothing to unlock, and counting it would let an under-privileged session sense agent-internal detection rules (D-30). The title-embedding score is mapped to the calibrated scale by its own calibration, fitted on the `dev` auth-trap queries (section 15.2), so "at or above the threshold" means the same as in section 8. If the best hit would have scored at or above `retrieval_confidence_threshold` and needs a higher level, return `step_up_hint: {required_level}`. Never return the id, title or any text to any consumer except the Policy Engine's internal reason code.
3. The Policy Engine moves to `AUTH_REQUIRED` for that level, using its normal step-up sequence (`diagrams/auth-flow.mmd`), and re-runs retrieval after success.
4. If the probe finds nothing, the decision is the ordinary graceful degradation.

5. **Identical step-up wording (D-51).** The step-up prompt is one fixed template. Its wording carries no topic, entry, title or target level and does not vary with the probe outcome; it asks for the next level only (principle 2 of `access-control-matrix.md`). The Policy Engine never adds a reason such as "this information is protected".
6. **Rate limit per session (D-51).** A session gets at most 2 probe-driven step-up prompts (proposal, tuned on `dev`; log counter `step_up_prompts`). After that the probe is not consulted and the decision is the ordinary graceful degradation with a human offer, so repeated rephrased questions cannot map which topics sit behind verification. The cap counts prompts, not outcomes. A session that reaches the cap raises a low-severity security signal for review.

This keeps the identity and content of guarded entries private while still avoiding a false "I don't know". The residual signal is one bit per probe-driven prompt: verification would help with this request. The intent-level auth check (`access-control-matrix.md` section 1, point 1) already gives a comparable signal, and D-51 bounds the probe's extra signal with the fixed wording and the per-session cap. The Risk Committee review of this residual signal is open (D-51). A customer who is anonymous and asks about unblocking a card (KB-TRB-008, `biometric_verified`) is told the step is available after verification, using only the anonymous KB-POL-003 (account actions are gated by verification); KB-POL-006, which states that unblocking needs `biometric_verified`, is itself retrievable only from `otp_verified`.

## 6. Dense and sparse retrieval

| Item | Dense | Sparse (BM25) |
|---|---|---|
| Input | Rewritten query, in the customer's language (secondary: English pivot) | Normalised tokens plus lexicon expansion (Hinglish) |
| Candidates | Top 20 inside the filter | Top 20 inside the filter |
| Strength | Paraphrase, Hindi and Hinglish queries against English bodies | Exact terms: product names, "80C", "LTV", "CIBIL", ID-like strings, numbers |
| Weakness | Rare tokens, exact figures | Vocabulary mismatch, transliteration |
| Run | Parallel with the other branch | Parallel with the other branch |
| Budget (p95) | embed 20 ms then ANN 30 ms | 20 ms |

## 7. Fusion

**Decision (D-41): weighted score fusion, dense 0.6 and sparse 0.4, over min-max normalised scores per list.** The union of the two lists (at most 40 entries) is scored as `0.6 * dense_norm + 0.4 * sparse_norm`, with 0 for a list in which the entry did not appear. An additive intent prior is applied (section 7.1). The fused list is truncated to 20 candidates for the re-ranker (proposal, sized to fit the 80 ms re-rank budget).

Why weighted rather than Reciprocal Rank Fusion:

1. The brief asks for "hybrid with fusion weights". Weights are explicit, auditable and governed config, while RRF has only a constant.
2. The weights are tunable per language class. Hinglish and secondary-language pivots may need a different dense share; a weight is a one-line config change that goes through the A/B gate, an RRF constant is less interpretable.
3. The fusion stage only has to maximise **recall into the candidate set**. The cross-encoder decides the final order and the confidence, so the fusion rule is not safety-relevant.
4. Weighted fusion keeps score magnitude, so a query where the sparse side finds an exact figure match is not diluted by a rank-only rule.

The weakness of weighted fusion is that it needs score normalisation and is sensitive to the score distributions of the two systems. Mitigation: normalisation is per request, and RRF stays in the evaluation as a **challenger arm** (section 15). If RRF beats weighted fusion on Recall@20 on the `dev` split by a margin the Search Lead and the Chief Risk Officer accept, the change is a config change under the same gate. The 0.6 / 0.4 starting split is the plan's initial value (PLAN 3.4), not a measured optimum.

### 7.1 Intent prior and gap companions

- **Intent prior.** Entries whose `intents` contains the top NLU intent receive a small additive boost on the fused score (proposal 0.05, tuned on `dev`). It is a prior only. An entry that does not list the intent is still a candidate.
- **Gap companions.** If the top intent has `kb_gap: true`, or the top candidates include an entry with `gap_handling: true`, the entries listed in `gap_for` for that intent, and the `known_adjacent_facts` of the gap entry, are added to the re-rank set even if they were not in the top 20. This makes the gap entry and the real nearby facts compete fairly, and it means a gap entry is always available to the policy. Companions still pass the filter.
- **Guardrail companions.** For intents PRD-005 and the other advice-boundary cases (the Input Guard's advice detector fired), the guidance entry KB-POL-001 is added to the re-rank set. This is a retrieval-side convenience; the advice guard itself is a Day 9 rule layer.

## 8. Re-rank, confidence and the threshold

**Cross-encoder.** A multilingual cross-encoder scores each `(rewritten query, candidate text)` pair, where the candidate text is the title plus the body in the served language. It returns the top 5, one version per `id`. The raw logit is converted to a **calibrated relevance** in [0, 1] by a monotone calibration (Platt or isotonic) fitted on the `dev` gold set and re-fitted on every re-ranker or index version change. Calibration is what makes 0.65 and 0.85 mean the same thing across versions.

**Confidence (D-42).**

| Quantity | Definition | Use |
|---|---|---|
| `top1_confidence` | Calibrated relevance of the rank-1 entry | Compared with `retrieval_confidence_threshold` (0.65). This is the gate |
| Evidence floor | An entry below 0.65 is dropped from the evidence set and is never cited | Keeps a weak sixth-best match out of a synthesised answer |
| `synthesis_confidence` | Mean calibrated relevance of the entries the response actually cites (runtime) or of the required gold entries (evaluation). Every one of them must be in the top 5 (of its own segment's request for a multi-intent query, section 3) | The quality measure. The brief's relevance target is > 0.85. The boss queries use it |
| Telemetry bands | below 0.65, 0.65 to below 0.85, 0.85 and above | Dashboards only (uses the brief's two numbers). Behaviour changes only at 0.65 |

Below 0.65 the agent must acknowledge uncertainty (A2.3 "uncertainty acknowledgment threshold"): see section 9. A gap entry below 0.65 is outside the evidence set like any other entry, so a gap hit is taken only on the confident branch; below the gate the low-confidence rows apply (regulatory-uncertain first, then step-up probe, then degrade). At or above 0.65 the answer is built from the evidence set; facts and figures still come through the template-first path of `response-generation.md` and are checked by the Output Safety Layer against the passage fields.

Notes: the threshold is the same for every language (`language-detection.md` section 6 states the retrieval threshold is unchanged for pivots). A poor pivot lowers confidence through the pivot quality gate, not through a different threshold.

## 9. Decisions after retrieval

| Case | Detection | Decision | Customer-facing behaviour (templates named only; the Day 13 files write them) |
|---|---|---|---|
| Confident answer | `top1_confidence >= 0.65`, rank-1 is not a gap entry | `answer` | Facts from the evidence set. Stale-flagged entries are used, and the reply stays template-first for figures. Companion guidance entries steer wording, for example KB-POL-008 disclosures for a loan answer |
| Gap hit | `top1_confidence >= 0.65`, a gap entry (`gap_handling: true`) is in the evidence set (its own calibrated relevance is also at least 0.65, section 8) and the question asks for a fact in its `unknown` list | `gap` | Template `graceful_degradation` with the entry's `safe_statement`, the `known_adjacent_facts` the retriever also returned, and the `offer` (human, callback). No number that is not in the KB |
| Low confidence, non-regulatory | `top1_confidence < 0.65` and the topic carries no regulatory tag | `degrade` | Template `graceful_degradation`: say it is not certain, name the nearest known topic only if an entry in the top 5 lists the top NLU intent (which must have reached the act tier of D-06 on the NLU scale), by title and with no figure; no retrieval score floor is used for this, because the NLU and retrieval scales differ (section 8); offer a clarifying question once, then a human. KB-ESC-020 is the generic gap entry. Two failed clarifications use the existing safe default (`max_clarification_turns`) |
| Regulatory-uncertain | See below | `escalate_esc_008` | Template `handoff` to the Compliance Helpdesk (ESC-008, P1, under 10 min per KB-ESC-008). The agent states what the KB does say (that the obligation exists) and that it is not certain of the specifics. It never quotes a regulation from memory |
| Filtered by auth | Low confidence, auth below `full_kyc`, probe finds a qualifying hit | `step_up` | Policy Engine starts the step-up (section 5.4). Template `confirmation_before_action` wording for the verification step is a Day 13 item |
| Index down | Section 13 | `unavailable` | Cached FAQ, else template `handoff` (technical support, ESC-014) |

**Regulatory-uncertain (D-43).** A request is regulatory-uncertain when it maps to a regulatory tag (kb-schema section 8) or to an intent whose `escalation` list in `config/intents.yaml` carries ESC-008 (PRD-001 when a regulation is asked about, PRD-004) and one of these holds:

1. `top1_confidence < 0.65`; or
2. the best-matching entries are a gap entry that lists `ESC-008` in `escalation_triggers` and the requested fact is in its `unknown` list (a known unknown, for example the cooling-off length or an ombudsman time limit in KB-ESC-019, or the insurance details in KB-ESC-021); or
3. the only entries that would have answered it were removed by a **hard** expiry (`regulatory` class).

In all three cases the result is `escalate_esc_008`. A non-regulatory gap (for example RD in KB-ESC-011) uses `gap` or `degrade`, not ESC-008, unless the customer insists, in which case the human handoff in the entry's `offer` applies. The Policy Engine, not the retriever, fires the escalation; the retriever supplies the `decision` and the reason code.

`consecutive_low_conf` (ESC-003) counts NLU intent confidence only. A low retrieval score on a clearly understood intent does not count toward it (it would turn a KB gap into a false "customer is confused" escalation).

## 10. Graceful degradation and fallback ladder

Order, each step used only if the previous one cannot answer, always fail-closed:

1. Answer from the evidence set (confident, section 8).
2. Gap entry `safe_statement` plus `known_adjacent_facts` (the topic is known to be missing).
3. Clarifying question, once, when the rewrite or the intent is ambiguous (not when the topic is a known gap).
4. `graceful_degradation` template: acknowledge, nearest known topic, offer a human or callback.
5. Human handoff (`handoff`), with the 8-element package of KB-ESC-001. ESC-008 for a regulatory case; ESC-014 when the tools or index are down.

Rules that apply to every step: never a number that is not in the KB; never "I think"; never the same fallback sentence twice in a row (Robotic Loop anti-pattern: the template pool rotates); empathy first when the customer is upset; a callback time is a request, not a promise (KB-POL-007).

## 11. Caching

| Cache | Key | Value | Rules |
|---|---|---|---|
| FAQ result cache | normalised rewritten query hash, language, auth class, `index_epoch` | Ranked passage IDs and calibrated scores (not generated text) | Anonymous, evidence-lane entries only. No personalised or entity-injected query is cached. Entries are dropped when `index_epoch` changes, and the cache lifetime never exceeds the earliest `expires_at` of an included entry. A cache hit still passes the auth and expiry checks at serve time |
| Embedding cache | normalised query hash, embedding model version | Query vector | Safe for all auth levels because it holds no KB content |
| Rerank-pair cache (optional) | query hash, entry id@version, reranker version | Calibrated score | Same invalidation as above |

Cache hits skip embed, ANN, BM25 and re-rank (the FAQ result cache) or embed only (the embedding cache). The cached FAQ path is also the index-down fallback. The cache is never a source of an answer on its own: its output is the same `RetrievalResult` contract, so confidence and flags still apply. Hit rates are not assumed in this document; they are measured (section 15).

## 12. Latency budget (p95)

| Stage | Budget (ms) | Notes |
|---|---|---|
| Embed query | 20 | Skipped on an embedding or result cache hit |
| ANN search (filtered) | 30 | In parallel with BM25 |
| BM25 search (filtered) | 20 | In parallel with ANN; hidden behind the ANN time when it finishes first |
| Fusion, gap companions, build candidate texts | in overhead | Small, bounded by 40 candidates |
| Cross-encoder re-rank | 80 | The largest item. Candidates are capped at 20 |
| Overhead (filter build, serialisation, network, enqueue log) | 30 | |
| **Total** | **about 160 to 180** | 160 when BM25 overlaps ANN fully (20 + 30 + 80 + 30); 180 if the two searches are charged in sequence (20 + 30 + 20 + 80 + 30). Under the < 200 ms requirement with 20 to 40 ms of headroom. Matches `latency-scalability-cost.md` (retrieval 200 ms line) |

- Alert at 70% of the stage budget, as in `latency-scalability-cost.md` section 4 (retrieval: 140 ms p95).
- Hard timeout for the whole retrieval call is the 200 ms budget. On a partial result the rules of section 13 apply.
- **The "Retriever" badge (< 150 ms p95)** is **not claimed** by this budget, which sits at 160 to 180. Levers that could bring the measured p95 under 150 ms are: embedding and result cache hits (a hit removes 20 ms or more), trimming the re-rank candidate count below 20, a smaller re-ranker, and skipping re-rank when the fused top score is far ahead of the second (proposals, each needing a recall check). Whether the badge is reachable is a Day 14 load-test question, not a design claim.
- Retrieval runs in parallel with independent tool calls (`latency-scalability-cost.md` section 1). Pure tool intents (balance, statement) skip retrieval.

## 13. Failure modes

| # | Failure | Detection | Behaviour (fail closed) |
|---|---|---|---|
| 1 | Auth level missing, malformed or stale | Validation at request | Treat as `anonymous`; elevated entries drop out |
| 2 | Dense service or embedder down | Error or timeout | BM25 only, flag `degraded: sparse_only`. The re-ranker and the 0.65 gate still apply |
| 3 | BM25 down | Error or timeout | Dense only, flag `degraded: dense_only`. Exact-figure queries may score lower and degrade |
| 4 | Re-ranker down or timed out | Error or timeout | Fused scores are not calibrated, so `top1_confidence` cannot be computed. Result is `degrade`; regulatory topics go to ESC-008; the cached FAQ may answer |
| 5 | Both searches down or whole index unavailable | Health check | `unavailable`: cached FAQ, else `handoff` to technical support (ESC-014) |
| 6 | Latency over budget | p95 monitor, 70% alert | Reduce candidates, serve cache, skip retrieval for pure-tool intents, template mode for factual turns; never answer without the KB for a regulatory topic |
| 7 | Stale passage served | Soft-expired flag, hard-expired absent | Soft: serve, flag `stale`, review ticket (already open). Hard: absent, section 5.1 |
| 8 | Wrong passage with high confidence | Output Safety Layer grounding and number check, supervisor sampling of low-score and random turns | Block or rewrite the reply. A repeat feeds the maintenance workflow (rewrite the entry or add a gap entry) and the gold set |
| 9 | Auth leak (an entry above the session level returned) | Post-retrieval assertion: every returned `auth_level_required` <= session level | Drop the passage, raise a P0 incident (security rule 2, A4.2), freeze the index epoch until reviewed. Target: zero in the evaluation and in production |
| 10 | Expired or unpublished entry returned | Same assertion on status and expiry | Same as 9 |
| 11 | Instruction text inside a KB body or the query | Input Guard on the query; KB bodies are approved content, but are still passed to the model as data in a separate delimited section | The Generator never treats KB text as instructions (PLAN 3.6 item 3 and `system-architecture.md` section 5: instruction and data separation) |
| 12 | Rewrite picks the wrong referent | Tie detection; the customer's correction | Ask on a tie; the correction re-runs retrieval; log `rewrite_applied` for review |
| 13 | Translation missing or stale | `languages` and stale marks (kb-schema section 6) | English body, flag `translation_unavailable` |
| 14 | Stale cache across a publish | `index_epoch` in the key | Entry is not matched; the epoch change flushes related keys |
| 15 | Calibration drift | Weekly reliability check on the gold set; drift target below 0.05 (A8) | Pause threshold or weight changes (nlu-pipeline-overview risk table); re-fit calibration |
| 16 | Corpus change breaks recall | Pre-publish retrieval regression run (`maintenance-workflow.md` section 4) | The publish is blocked |

## 14. Observability and log fields

Every retrieval writes one record, joined to the turn record by `conversation_id`, `turn_index` and `trace_id` (A10.2, A11.3). Content of the customer's message is not copied into this record; only the rewritten query hash and the IDs are.

```yaml
retrieval_log:
  kb_entry_ids: ["KB-PRD-003@1.0.0", "KB-PRD-004@1.0.0"]   # the entries cited in the reply (id@version)
  candidate_ids: ["KB-PRD-011@1.0.0", "..."]               # the top 5 returned, with scores
  scores: [0.91, 0.88, 0.74]                               # calibrated, same order
  top1_confidence: 0.91
  synthesis_confidence: 0.89
  decision: answer                                         # answer|gap|degrade|escalate_esc_008|step_up|unavailable
  reason_codes: [REG_UNCERTAIN, GAP_HIT, LOW_CONF, STEP_UP_PROBE, DEGRADED_SPARSE_ONLY]
  gap_entry_id: null
  esc_trigger: null                                        # ESC-008 when raised
  auth_level: otp_verified
  filtered_counts: {status: 3, effective: 0, expiry: 1, auth: 6, audience_lane: 0}  # operations only
  stale_ids: []
  translation_unavailable_ids: []
  language: hinglish
  rewrite_applied: true
  rewrite_unresolved: false
  rewritten_query_hash: "..."
  cache: {result_hit: false, embedding_hit: true}
  index_epoch: 41
  versions: {embedder: "...", reranker: "...", calibration: "...", fusion_weights: [0.6, 0.4]}
  latency_ms: {embed: 18, ann: 27, bm25: 15, fuse: 3, rerank: 71, overhead: 22, total: 141}
```

Metrics and alerts: p95 and p99 latency per stage; share of turns per `decision`; mean `top1_confidence` and `synthesis_confidence` (target mean relevance > 0.85); share of turns below 0.65 by language and by intent; `stale_ids` served; hard-expiry exclusions; cache hit rates; auth assertion failures (alert on any); ESC-008 raises. A rise in below-0.65 turns for one intent is a gap-entry or authoring signal and goes to the KB owner (`maintenance-workflow.md` section 6).

## 15. Retrieval evaluation plan

Source: PLAN 6.1, "Retrieval evaluation: a query set with gold KB IDs, measured by Recall@5, MRR, nDCG, mean relevance (target > 0.85) and p95 latency". Schema and the first hard slice are in `tests/kb/boss-level3.yaml` and `tests/kb/README.md`.

### 15.1 Metrics

| Metric | Definition | Target |
|---|---|---|
| Recall@5 | Over answerable queries: fraction of **required** gold IDs found in the top 5 (averaged per query) | Gate proposal 0.90 (D-47). The brief gives no value |
| MRR | Mean of 1 / rank of the first required gold ID | Gate proposal 0.80 (D-47) |
| nDCG@5 | Graded relevance: 2 for a required gold ID, 1 for a supporting ID, 0 otherwise | Gate proposal 0.85 (D-47) |
| Mean relevance | Mean `synthesis_confidence` over answerable queries (calibrated cross-encoder relevance of the required gold entries), cross-checked against a human 0 to 1 rating on a sample | **> 0.85** (brief) |
| p95 latency | End-to-end retrieval time over the load-test set, with and without cache | **< 200 ms** (brief); < 150 ms is a stretch (section 12) |
| Safety counters | Auth leaks, expired or unpublished entries returned, a figure in a gap answer, a regulatory-uncertain case not escalated | **0** each (not statistical) |
| Gap behaviour | For gap queries: the gap entry is in the top 5 and the decision is `gap` or `escalate_esc_008` | 1.0 (all) |

### 15.2 Gold query set design

- **One record per query**: `id`, `query`, `language`, `auth_level`, `intent`, `answerable`, `required_ids` (graded 2), `supporting_ids` (graded 1), `forbidden_ids` (must not be returned at that level), `expected_decision`, `expected_behaviour`, `notes`. The full schema is in `tests/kb/README.md`.
- **Coverage.** At least one query for every entry in the index (so every entry has a way to be found), written in different words from the entry text; plus the strata in the next row. Query counts are a proposal (D-47) because the brief sets none.
- **Strata**: language class (`en`, `hi`, `hinglish`, secondary via pivot), category, auth level (each query is run at the entry's level and one level below, to test both access and filtering), compound and synthesis queries (3 or more entries; the boss set is the hard slice), gap queries (the four `kb_gap` intents and the other gap entries), regulatory-uncertain queries, expiry cases (a copy of the index with a clock set past `expires_at`), near-duplicate pairs (PRD-003 / PRD-004, PRD-005 / PRD-006, TRB-001 / TRB-002), and adversarial or injection-bearing queries.
- **Negative sets.** *Auth traps*: queries whose best entry is above the session level; pass means the entry is absent and the decision is `step_up` or `degrade`. *Expiry traps*. *Hallucination traps*: questions about non-existent products or rates (RD, forex, premium amounts); pass means a gap entry and no figure.
- **Splits.** `dev` for fusion weights, intent prior, calibration and thresholds; `test` for reporting; split by query, stratified like the NLU library (D-22), with near-duplicates kept in the same split.
- **Labelling.** Gold IDs are written by the KB owner and reviewed by a second person from a different team (the same four-eyes principle as the publish chain). Disagreements go to the Regulatory Compliance Manager for regulatory topics. Every gold ID is validated by a script against the entries and the auth rules (the Day 8 checker, section 16).
- **Ablation arms**: dense only, BM25 only, weighted fusion (0.6 / 0.4), RRF, each with and without re-rank, and with and without the intent prior. Report Recall@20 for the fusion arms, since fusion is judged on candidate recall.
- **When it runs**: on every index build (publish gate, `maintenance-workflow.md` section 4), on every embedder, re-ranker or weight change (A/B gate), and weekly for drift.

### 15.3 What this document does not claim

No measured result exists: the project is a specification. The only numbers quoted as targets from the brief are 0.85 mean relevance, 200 ms p95 and the < 150 ms badge. 0.65 is the plan's `retrieval_confidence_threshold`; 0.6 / 0.4 is its initial fusion split; every other value in this file marked "proposal" is logged in decisions D-41 to D-48 and is tuned on `dev`.

## 16. Verification of this specification

The Day 8 checker (scratchpad, not in the repo) confirms that every gold ID in `tests/kb/boss-level3.yaml` exists, is published, passes the auth clause at the stated level, and that every `forbidden_ids` entry is above that level. The retrieval gold-set schema and the checker's rules are described in `tests/kb/README.md` so the check can be promoted to the Day 15 cross-reference lint.
