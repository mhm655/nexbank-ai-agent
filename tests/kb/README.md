# Knowledge Base Tests

Brief refs: A2.3 (retrieval architecture, confidence, 200 ms p95, graceful fallback), Part B Level 3 boss. Plan: section 6.1 (retrieval evaluation), section 4 Phase 3 item 7. Pipeline: `docs/knowledge-base/retrieval-pipeline.md`. Access rules: `docs/knowledge-base/access-control-matrix.md`.

## Contents

| File | Purpose |
|---|---|
| `validate_kb_entries.py` | Entry validator (Day 7). Run from the repo root: `python tests/kb/validate_kb_entries.py` |
| `boss-level3.yaml` | The Level 3 boss: 5 queries that each need 3 or more entries synthesised, with gold IDs, expected answer outline and grounding (Day 8) |
| Retrieval gold set (later) | One or more queries per entry plus strata; same schema as the boss set (retrieval-pipeline.md section 15.2) |

## Retrieval evaluation schema (`boss-level3.yaml` and the future gold set)

Top level: `schema_version`, `set_id`, `unlock_condition`, `target_synthesis_confidence_gt`, `coverage`, `cases[]`.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `KB-BOSS-L3-<nn>` for the boss set; `KB-GOLD-<nnn>` reserved for the gold set |
| `query` | string | Synthetic customer text in the stated language. No card number, OTP, CVV, PIN or Aadhaar value |
| `language` | enum | `en`, `hi`, `hinglish`, `ta`, `te`, `bn`, `mr`, `gu` |
| `auth_level` | enum | Session level for the query. Every required and supporting ID must be retrievable at this level |
| `intents` | list | NLU intents expected (IDs in `config/intents.yaml`); a soft prior for retrieval, not a filter |
| `answerable` | `true`, `partial` or `false` | `false` = the facts asked for are not in the KB (a known gap or regulatory unknown) |
| `required_ids` | list | Gold entries (3 or more in the boss set). All must appear in the top 5. Graded relevance 2 |
| `supporting_ids` | list | Helpful entries; not required. Graded relevance 1 |
| `forbidden_ids` | list | Entries that must not be returned (above the session level, expired, or unpublished). May be empty |
| `expected_decision` | enum | `answer`, `gap`, `degrade`, `escalate_esc_008`, `step_up` (retrieval-pipeline.md section 9) |
| `policy_route` | optional | A route the Policy Engine adds (for example `ESC-013`); not fired by the retriever |
| `expected_esc_trigger` | optional | ESC ID the decision must raise |
| `target_synthesis_confidence_gt` | number | The brief's relevance target (0.85) |
| `expected_answer_outline` | list | What a correct answer contains, in order |
| `grounding` | list | `{claim, entries, figures}`: which entries and which figures support each claim. Every required ID must be cited at least once; every figure string must appear in a cited entry |
| `must_not` | list | Behaviours that fail the case even if retrieval is right |
| `notes` | text | Traps and rationale |

## Scoring a case

A case passes only if all hold:

1. Every `required_ids` entry is in the top 5 of the retrieval result, and no `forbidden_ids` entry is returned.
2. `synthesis_confidence` (mean calibrated relevance of the required entries) is above `target_synthesis_confidence_gt`. For `answerable: false`, this measures retrieval of the right gap and regulatory entries.
3. The decision equals `expected_decision` (and `expected_esc_trigger`, if set).
4. The answer outline is met and no `must_not` item occurs (checked by the response tests on Day 13 and 14; here it is a human-reviewed rubric).

Multi-intent queries (KB-BOSS-L3-02 to -05): NLU splits the query into segments and each segment is a separate retrieval request (retrieval-pipeline.md section 3). Rule 1 then applies per segment: each required entry must be in the top 5 of the segment it answers. `synthesis_confidence` is the mean over all required entries across the segments, and the decision in rule 3 is the one the Policy Engine takes on the merged result.

Set-level metrics (retrieval-pipeline.md section 15.1): Recall@5, MRR, nDCG@5, mean relevance (> 0.85), p95 latency (< 200 ms). Safety counters (auth leaks, expired or unpublished entries returned, figures in gap answers, missed ESC-008) must be zero.

## Static checks (Day 8 checker)

The checker is a small script kept outside the repo during Day 8 (scratchpad). It loads `docs/knowledge-base/entries/*.yaml` and `config/intents.yaml` and verifies, per case:

- every ID in `required_ids`, `supporting_ids` and `forbidden_ids` exists, is `published` and is live on the check date;
- every required and supporting ID has `auth_level_required` at or below the case `auth_level`;
- every forbidden ID is above that level;
- `required_ids` has at least 3 entries; all intents exist;
- every `grounding` entry is a gold ID, every required ID is grounded, and every `figures` string occurs in the cited entries;
- every number in `expected_answer_outline` (ignoring ID references) occurs in a gold entry, so the set invents no figures;
- the level counts match `docs/knowledge-base/README.md` (anonymous 64, otp_verified 10, biometric_verified 1, full_kyc 2).

Result on Day 8 (case 5 replaced in the follow-ups, D-49: a Hinglish NexSave, NexFD and tenure-gap synthesis query instead of three gap entries): PASS for all 5 cases (after the Day 8 audit added KB-ESC-001 to KB-BOSS-L3-04, whose outline cites the handoff package, and an explicit "not held" line for the NexFD minimum deposit in KB-BOSS-L3-02). It is a candidate for promotion into `tests/kb/` and the Day 15 cross-reference lint. Dynamic checks (ranking, calibration, latency) need the built system and are specified, not run.
