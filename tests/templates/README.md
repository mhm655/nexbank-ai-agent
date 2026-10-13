# Template, Parameter and System-Prompt Checks

Brief refs: A12.2 (p.33: "Testable Assertions: Every instruction convertible to a testable assertion. If it cannot be tested, it is too vague"; "Version Control"), A12.3 (p.34), A9.2 (pp.24-25), Part D Day 12-13 (p.60: "15+ prompt templates with trigger conditions and safety annotations").

Files: `validate_templates.py` (the validator), `wording_lint.yaml` (the regular-expression lists of the extended wording lint, in three scripts so that Hindi stays in Devanagari), `prompt-assertions.yaml` (twelve test cases PA-T-01 to PA-T-12 for system-prompt assertions that had no proper test, D-194; not members of the safety-suite manifest, which they could join). The validator reads `config/templates/*.yaml`, `config/parameters.yaml`, `config/system-prompt/` and the reference registries (`config/intents.yaml`, `config/guardrails.yaml`, `config/escalation_rules.yaml`, `docs/knowledge-base/entries/`, `tests/**/*.yaml`).

Status: the validator is a static check. It parses, cross-references and lints. It does not render a template with real data, call a model, or test a conversation. The behavioural cases for templates are the existing cases in `tests/` that each template and each prompt assertion links to; none of those has been executed, because no agent exists.

## 1. How to run

```text
python tests/templates/validate_templates.py            # exit code 0 = PASS
python tests/templates/validate_templates.py --rehash   # after an approved change to a layer 3 to 5 text and a version bump: rewrite the manifest hashes
python tests/templates/validate_templates.py --rehash --allow-immutable-change D-NNN   # also needed when layer 0, 1 or 2 changed; logs the decision
python tests/templates/validate_templates.py --approved-immutable <sha256>   # also compare the immutable hash with a value kept outside the repository
```

Needs Python 3 and PyYAML. On Windows set `PYTHONIOENCODING=utf-8` if an error message has to print Hindi text.

## 2. What it checks

### 2.1 Templates

| # | Check | Fails when |
|---|---|---|
| T1 | Every template file parses; the file-level `review` block marks Hindi and Hinglish `not_native_reviewed` | parse error; missing mark |
| T2 | IDs match `TPL-<FAMILY>-<NAME>` and are unique | malformed or duplicate ID |
| T3 | Required fields present; `mode` is template, hybrid or llm-guided; `variant_selection` is single, condition or rotate | missing field, unknown value |
| T4 | Every referenced intent, guardrail, ESC trigger, KB entry and test case exists; `compose_with` names a template | dangling reference |
| T5 | At least 15 templates, and the 48 required ones exist: the 13 advice names, 7 attack-response names, 12 escalation names and the 16 other items Day 13 had to deliver | library incomplete |
| T6 | Legacy names from earlier documents (`graceful_degradation`, the seven RED reply keys) resolve to a template or variant | an earlier promise is unresolved |
| T7 | Every `TPL-` string anywhere in the repository (outside `graphify-out`) is an existing template ID, a family prefix such as `TPL-ESC-*`, or the lint fixture `TPL-TEST-INCOME-SLOT` | a document or test names a template that does not exist |
| T8 | Slots: every `{{slot}}` used in text is declared; every declared slot is used; the three languages of a variant use the same slots; non-LLM slots are `locked: true`; LLM slots are `locked: false` with `constraints.max_words` and a fallback in three languages; mode `template` has no LLM slot; a tool source names a known tool | undeclared, unused or unlocked slot |
| T9 | No slot is named for a personal circumstance (income, salary, age, savings, portfolio, goals, risk appetite) | GR-ADV-07 build-time lint (case GR-ADV-07-01) |
| T10 | Languages: English, Hindi and Hinglish text present for every variant; Hindi contains Devanagari; English and Hinglish are ASCII | missing or wrong-script text |
| T11 | Digits: no ASCII or Devanagari digit in template text or fallback text outside a slot, unless listed in the template's `allowed_literals` | a figure, duration or count in fixed text |
| T12 | Banned phrases (section 3) absent from English and Hinglish text; a short Hindi list absent from Hindi text; each template's own `must_not_contain` phrases absent from its own text | anti-pattern wording |
| T13 | A rotating template has at least 3 variants; a non-single template gives each variant a `when` | Robotic Loop control missing |
| T14 | `a9.patterns` and `a9.anti_patterns_avoided` are non-empty subsets of P1 to P5 and AP1 to AP8; a customer-facing template enforces at least one guardrail | missing annotation |
| T15 | No English variant shares `atk_prompt_overlap_words` (8) consecutive words with prompt layers 0 to 2 | the Output Safety Layer would block the template (GR-ATK-06) |
| T16 | `labels.yaml`: all 15 queues have a label in three languages; label intents exist; every trigger intent of the two AUTH templates has a request label | missing label |
| T17 | Every template ID is listed in `config/templates/README.md` and in the matrix of `docs/architecture/conversation-design.md` | index or matrix out of date |
| T18 | Extended wording lint (D-194) on every variant, slot fallback and label text: no time or outcome word without a digit (tomorrow, shortly, soon, "two days", kal, jald, Hindi equivalents); no advice verb (suggest, recommend, "should invest", "best option", Hindi and Hinglish equivalents) unless the same sentence refuses it; no request for a credential in chat in English, Hindi or Hinglish unless the sentence forbids it or points to the secure channel; no claim to be human, staff, a named person or "not a bot" | a bad phrase in any of the three languages |
| T19 | English, Hindi and Hinglish of a variant have the same number of sentences | a sentence was dropped or added in one language |
| T20 | `safety.required_markers`: every named variant carries one declared phrase per language; `safety.ai_disclosure`: the named variants say "AI" in all three languages; `safety.variant_must_not_contain`: per-variant bans | a safety sentence present in English but dropped or reversed in Hindi or Hinglish; an AI disclosure removed |
| T21 | `labels.yaml` tables added in D-198: keys are tools, intents or notice codes; three languages; scripts; no digit; one allowed token `{{card_last4}}`; the wording lint above also runs on label text | malformed or unsafe label |

### 2.2 Parameters

| # | Check | Fails when |
|---|---|---|
| P1 | `config/parameters.yaml` parses and `governed_parameters` holds exactly the 8 names of A12.3 | missing or extra name |
| P2 | Default, range, owner and change process equal the brief's table (hard-coded in the validator from p.34) | any difference |
| P3 | Default lies inside the brief range; `effective_range` lies inside the brief range and contains the default; `session_timeout_minutes` effective ceiling is 5 (D-56) | range error |
| P4 | Every `mirror` equals the value at the named path in `config/intents.yaml`, `config/guardrails.yaml` or `config/escalation_rules.yaml` | two copies of a value differ |
| P5 | Every scalar in `config/guardrails.yaml` `parameters` and in `config/escalation_rules.yaml` `constants` and `proposals` is registered | an ungoverned threshold |
| P6 | Project parameters: unique names; status is brief_fixed, decided, proposal or default; a brief_fixed value cites the brief; decision IDs well formed; `learning` is may_propose or no | malformed entry |
| P7 | A parameter of an excluded group is never `may_propose`: a registry parameter of `config/guardrails.yaml`, a constant of `config/escalation_rules.yaml`, or any X-class parameter (D-171, D-194) | an unsafe learning flag |
| P8 | The three A12.3 parameters that sit inside an ESC condition (`escalation_sentiment_threshold`, `max_conversation_turns`, `retrieval_confidence_threshold`) stay proposable only with `proposal_limits`: owner equal to the A12.3 owner, required approval, hard bounds inside the brief range that contain the default, a maximum step and the reason (D-197) | an unbounded proposal path |

### 2.3 System prompt

| # | Check | Fails when |
|---|---|---|
| S1 | All six layer files exist with the required metadata keys | missing file or key |
| S2 | Layer number, name, purpose and update frequency equal A12.1; layers 0 to 2 are `immutable_to_learning_pipeline`; layers 3 to 5 are not | drift from the brief |
| S3 | Prompt text is found between the markers, is ASCII, contains no digit (section labels such as "S1." excepted), no link, key or host pattern, and only the three assembly slots | figure, secret or stray slot in a prompt |
| S4 | Each layer has both SHOULD and MUST NOT instructions (A12.2 Positive and Negative Instruction) | one-sided layer |
| S5 | Assertion IDs `PA-L<layer>-<nn>` are unique; each maps to existing guardrails and at least one existing test case | untestable or dangling assertion |
| S6 | Estimated tokens (words x 1.35) do not exceed the layer's `token_budget` | layer too long |
| S7 | `manifest.yaml` hashes equal the recomputed layer, bundle and immutable hashes; layer versions equal the layer headers; `prompt_version` follows the scheme; A12.2 metadata present; the last entry of `immutable_change_log` ends at the current immutable hash | a layer changed without a version bump and rehash |
| S8 | `--rehash` refuses when a layer text changed but its version did not, and refuses when layer 0, 1 or 2 changed without `--allow-immutable-change D-NNN` (D-194) | an immutable layer re-blessed silently |
| S9 | Declared required instructions are present in each layer (for example "ask for any of them in chat" in S3, the rounding ban of K6, the no-human-claim of layer 0), and no layer says it may loosen or override a lower layer or that a notice may instruct (D-194) | a safety instruction deleted or weakened, even with a current hash |

### 2.4 Hygiene

Owned files exist; no reference to the planning file; no non-ASCII character outside Hindi fields; no decision ID above D-199; every repository path written in an owned file exists (D-194).

## 3. Banned-phrase list and why

The list lives in the validator (`BANNED`, `BANNED_HI`). Groups: persona ("as an AI language model"); certainty and guarantees (False Confidence, -30); outcome promises and "within N" timelines (D-09); stacked apologies (Sycophantic Recovery, -10); the brief's own Robotic Loop sentence (-20); blame; dismissive phrases (Empathy Bypass, -20); hedged guesses ("I think", "probably"); pressure selling (A4.3); recommendation wording (A4.1); "no one is available" and "try later" (oracle GR-SEC-R6-03); requests for an OTP, PIN, CVV or password (A4.2 rule 5); technical jargon (Pattern 4); flag vocabulary (PEP, AML, suspicious, flagged); slang.

It is a floor, not a tone model: it catches known bad wording in fixed text. Tone of generated text is the job of Output Safety check C5 at runtime.

## 4. Digit allow-list

Three templates carry `allowed_literals`, all survey scales: `TPL-SRV-CSAT` (1, 5: A5.2 "1 to 5"), `TPL-SRV-CES` (1, 7: A8.2), `TPL-SRV-NPS` (0, 10: standard NPS scale, a proposal). No other fixed text contains a digit. Numbers that customers need (amounts, dates, last four digits, references, wait estimates) arrive only through locked slots.

## 5. Limits of this validator

1. It cannot tell whether Hindi or Hinglish wording is natural or correct; only a native reviewer can.
2. Banned-phrase matching is literal; a paraphrase passes. The linked behavioural cases and runtime checks cover paraphrase.
3. It checks that a linked test exists, not that the test would pass or that it asserts the template's exact words. `must_not_contain` strings in earlier cases were written before the wording existed; the Day 13 handoff lists the cases whose strings were compared with the final wording.
4. It does not evaluate the `when` conditions or `trigger.state` text; those are prose.
5. Token counts are word-based estimates.
6. The lists of required markers and required prompt instructions are written by a reviewer; a safety sentence nobody declared has no check. The hashes and the manifest live in the same repository as the layers, so a change that is rehashed with the flag and a decision id passes; the control that does not depend on the repository is `--approved-immutable` with a value stored elsewhere.
7. Mutation checks: the Day 13 audit found 15 defects that the first version missed, and the Day 13 audit-fix handoff records the repeatable proof (each defect reproduced on a scratch copy and caught). The script itself does not run mutations.
