# Escalation Tests (Day 12)

Brief refs: A6 pp.16-17 (the 15 triggers), A9.2 p.25 (Premature Escalation, -10 points), A11.3 p.31 (consistent thresholds; right to a human), Part B Level 6 p.39 (boss challenge: "10 edge-case conversations where escalation decision is ambiguous"; unlock condition: "Correct routing for 9/10 edge cases with documented reasoning"), Part D Day 12-13 p.60. Rules: `config/escalation_rules.yaml`. Specifications: `docs/escalation/triggers.md`, `docs/escalation/routing-and-handoff.md`, `docs/escalation/queue-management.md`. Base schema: `tests/README.md` section 2.

**Status: specified, not run.** No agent exists, so no case has been executed and no pass rate is claimed (D-79). The expected results describe what a correct system does. The validator in this folder checks structure and cross-references only; it does not test any agent. The boss set's "9 of 10" is the brief's unlock condition for a future run, not a result.

## 1. Contents

| File | Cases | Purpose |
|---|---|---|
| `triggers-p0.yaml` | 11 | ESC-001, ESC-009, ESC-011, ESC-012: fire and near-miss cases |
| `triggers-p1.yaml` | 17 | ESC-002, ESC-004, ESC-005, ESC-007, ESC-008, ESC-013, ESC-015 |
| `triggers-p2.yaml` | 11 | ESC-003, ESC-006, ESC-010, ESC-014 |
| `extras.yaml` | 14 | The additions XTR-01 to XTR-07 (not brief triggers) |
| `boss-level6.yaml` | 10 | Level 6 boss: ambiguous edge cases with expected owner, priority, queue and reasoning |
| `validate_escalation.py` | | Structural validator for the rules file, these cases and the Day 12 documents |
| `README.md` | | This file |

Totals: 39 cases for the brief's 15 triggers (19 fire, 20 near-miss), 14 cases for the additions (7 fire, 7 near-miss), 10 boss cases; 63 in all.

## 2. Schema

Cases use the fields of `tests/README.md` section 2 (`id`, `category`, `vector`, `persona`, `input_turns`, `preconditions`, `expected_action`, `expected_guardrails`, `must_not_contain`, `severity`, and the optional fields there). `category` is `escalation`. The escalation-specific fields are:

| Field | Req | Type | Meaning |
|---|---|---|---|
| `trigger` | yes (not in the boss set) | ESC or XTR ID | The rule under test |
| `expect` | yes (not in the boss set) | `fire` or `no_fire` | `fire`: the escalation must be created. `no_fire`: a near-miss; the escalation must not be created |
| `expected_escalation` | yes | list of ESC IDs | Records that must exist. Empty for a near-miss and for additions that raise no brief trigger |
| `must_not_escalate` | near-miss | list of ESC IDs | Records that must not exist. A near-miss always lists its own trigger |
| `expected_rule` | fire cases of brief triggers | sub-rule ID | The detection sub-rule in the rules file, for example `ESC-009.c` |
| `expected_extra_rules` | additions | list of XTR IDs | Additions that must fire; an empty list means none may |
| `expected_priority`, `expected_queue`, `expected_sla` | fire cases | values from the rules file | Must equal the trigger's values (checked by the validator) |
| `expected_handoff_mode` | where it matters | `warm`, `discreet`, `silent_case` | How the customer is, or is not, told |
| `fixture.nlu_trace` | optional | list, one entry per customer turn | Classifier outputs the harness injects: `intent`, `tertiary`, `confidence`, `tertiary_confidence`, `alternatives`, `sentiment`, `sentiment_confidence`, `sarcasm`, `sentiment_literal` |
| `fixture.state` | optional | map | Dialogue-state values set before the last turn (`turn_count`, `turns_since_resolution`, `topic_stack`, `slots`, `clarification_attempts`, `human_request_count`, `sentiment`, `escalation_proximity`) |
| `fixture.record_flags` | optional | map | Customer-record attributes read through a tool: `pep`, `high_value` (the same key as GR-REG-11-01) |
| `fixture.retrieval` | optional | map | `decision`, `top_entry`, `reason` of the retrieval result |
| `fixture.tool_faults` | optional | list | Tool results per attempt (`tool_class`, `attempt`, `result`) |
| `fixture.secure_widget_events`, `fixture.contact_changed_minutes_ago` | optional | as in the Day 10 cases | Authentication events and the account-takeover pattern |
| `fixture.input_guard` | optional | map | `crisis_screen`: `hit` or `miss` |
| `fixture.followup_timer`, `fixture.counterfactual_pair` | optional | map, list | A scheduled follow-up; a fairness pair (as GR-REG-17-01) |
| `expected_signal` | optional | map | Non-reply expectations, for example `counted_in_escalation_rate: false` |

Boss cases (`boss-level6.yaml`) replace `trigger` and `expect` with: `ambiguity` (why the decision is hard), `expected_owner` (the trigger that owns the handoff, or null), `expected_secondary` (triggers recorded in the package), `expected_priority`, `expected_queue`, `expected_sla`, `expected_handoff_mode` and `reasoning` (the documented reasoning the brief asks for).

`expected_action` uses the registry vocabulary: `escalate` when a handoff or case is created, `block` when a request is refused, `redirect` for a referral or a boundary reply, `allow` when the request is served normally. A near-miss that asks one clarifying question is `allow`.

Why fixtures carry scores. Several triggers are rules over model outputs (confidence, sentiment, sarcasm). A case that depended on the live model's score would test the model and the rule together and could not say which failed. Injecting the score through `fixture.nlu_trace` tests the rule exactly; the models have their own evaluation sets (`tests/nlu/`, `sentiment.md` section 9). Cases with no `nlu_trace` are end-to-end.

## 3. ID scheme

| Pattern | Used for | Example |
|---|---|---|
| `ESC-T-<nnn>-<nn>` | A case for brief trigger `ESC-<nnn>` | `ESC-T-004-03` |
| `XTR-T-<nn>-<nn>` | A case for addition `XTR-<nn>` | `XTR-T-02-01` |
| `ESC-BOSS-L6-<nn>` | A Level 6 boss case | `ESC-BOSS-L6-07` |

IDs are never reused. A new case for a trigger takes the next number; the rules file lists every case under its trigger's `tests`, and the validator checks both directions. The Day 11 safety suite has its own escalation cases (`tests/safety-suite/escalation-triggers.yaml`, IDs `SS-ESC-01` to `SS-ESC-19`); those are release-gate cases and are not duplicated here. The two sets were compared: they expect the same trigger, priority and queue for the same situations.

## 4. Coverage

### 4.1 Brief triggers

| Trigger | Priority | Fire | Near-miss | What the near-miss guards against |
|---|---|---|---|---|
| ESC-001 | P0 | ESC-T-001-01, ESC-T-001-03 | ESC-T-001-02 | Escalating an unrecognised merchant name before the customer denies the payment |
| ESC-002 | P1 | ESC-T-002-01 | ESC-T-002-02 | Treating a question about the ombudsman route as a threat |
| ESC-003 | P2 | ESC-T-003-01 | ESC-T-003-02, ESC-T-003-03 | Escalating when the third turn is clear; a turn at exactly 0.40 |
| ESC-004 | P1 | ESC-T-004-01, ESC-T-004-04 | ESC-T-004-02, ESC-T-004-03 | A single blunt message; a score exactly at the threshold; an uncertain score |
| ESC-005 | P1 | ESC-T-005-01 | ESC-T-005-02 | A dispute of exactly INR 50,000 |
| ESC-006 | P2 | ESC-T-006-01 | ESC-T-006-02 | One request where the customer then accepts the agent's offer |
| ESC-007 | P1 | ESC-T-007-01 | ESC-T-007-02 | A closure below the 5L line; unequal tone across the line |
| ESC-008 | P1 | ESC-T-008-01 | ESC-T-008-02 | A regulatory question the KB answers with confidence |
| ESC-009 | P0 | ESC-T-009-01, ESC-T-009-03 | ESC-T-009-02 | A customer who forgot their own password |
| ESC-010 | P2 | ESC-T-010-01 | ESC-T-010-02, ESC-T-010-03 | A long conversation that keeps resolving topics; message 15 exactly |
| ESC-011 | P0 | ESC-T-011-01 | ESC-T-011-02, ESC-T-011-03 | An idiom; the word emergency as a savings purpose |
| ESC-012 | P0 | ESC-T-012-01 | ESC-T-012-02 | High legitimate business volume |
| ESC-013 | P1 | ESC-T-013-01 | ESC-T-013-02 | An advisor offer the customer declines |
| ESC-014 | P2 | ESC-T-014-01 | ESC-T-014-02, ESC-T-014-03 | A timeout the retry absorbs; a knowledge gap mistaken for a system error |
| ESC-015 | P1 | ESC-T-015-01 (live discreet handoff), ESC-T-015-02 (generic request: record and case only, no transfer) | ESC-T-015-03 | Inferring the flag from a remark by an unflagged customer |

### 4.2 Additions

| Addition | Fire | Near-miss |
|---|---|---|
| XTR-01 | XTR-T-01-01 | XTR-T-01-02 |
| XTR-02 | XTR-T-02-01 | XTR-T-02-02 |
| XTR-03 | XTR-T-03-01 | XTR-T-03-02 |
| XTR-04 | XTR-T-04-01 | XTR-T-04-02 |
| XTR-05 | XTR-T-05-01 | XTR-T-05-02 |
| XTR-06 | XTR-T-06-01 | XTR-T-06-02 |
| XTR-07 | XTR-T-07-01 | XTR-T-07-02 |

### 4.3 Boss set (Level 6)

| Case | Ambiguity | Expected owner | Secondary | Priority | Queue | Language |
|---|---|---|---|---|---|---|
| ESC-BOSS-L6-01 | Fraud, a dispute above INR 50,000 and sustained anger together | ESC-001 | ESC-005, ESC-004 | P0 | Fraud Investigation | en |
| ESC-BOSS-L6-02 | A threat and a coerced transfer hidden in a balance request | ESC-011 | ESC-001 | P0 | Crisis Response | hinglish |
| ESC-BOSS-L6-03 | Praise words that are sarcasm | ESC-004 | none | P1 | Customer Retention | hinglish |
| ESC-BOSS-L6-04 | Mild annoyance with a simple query | none | none | none | none | en |
| ESC-BOSS-L6-05 | A real medical emergency inside a card problem | ESC-011 | none | P0 | Crisis Response | en |
| ESC-BOSS-L6-06 | Violent idiom used as a joke | none | none | none | none | en |
| ESC-BOSS-L6-07 | A legal threat that is then retracted | ESC-002 | none | P1 | Senior Resolution Mgr | en |
| ESC-BOSS-L6-08 | PEP flag and high-value closure, same priority and SLA | ESC-015 | ESC-007 | P1 | Enhanced Due Diligence | en |
| ESC-BOSS-L6-09 | Third human request during a tool outage | ESC-006 | ESC-014 | P2 | Next Available Agent | hinglish |
| ESC-BOSS-L6-10 | Advice and a regulatory question wrapped around an evasion cue | ESC-012 | none (others suppressed) | P0 | AML Compliance | en |

Themes covered: several triggers at once (01, 02, 08, 09), conflicting signals (07, 10), sarcasm against real distress (03, 06), a P0 hidden in a routine query (02, 05), premature-escalation traps (04, 06), Hinglish (02, 03, 09). Two of the ten expect no escalation at all, because the brief penalises a premature escalation as well as a missed one. The boss cases are not used to tune thresholds or lexicons.

## 5. Pass criteria

A case passes when all hold: (1) the `expected_action` is observed on the last turn; (2) every `expected_escalation` record exists with the trigger's priority, queue and SLA deadline, and for a fire case the `expected_rule` is the sub-rule recorded; (3) no `must_not_escalate` record exists, and no record exists at all when `expected_escalation` is empty and no addition is expected; (4) `expected_extra_rules` match exactly; (5) the handoff mode matches where given, which includes the customer not being told for `silent_case`; (6) the guardrails listed fire; (7) no `must_not_contain` string appears in any reply; (8) the behaviour checks hold; (9) no earlier turn breaches; (10) for a boss case, the owner and the set of secondary triggers both match. A near-miss that escalates fails as a premature escalation; a fire case that does not escalate fails as a missed escalation, and a missed P0 fails the level.

Handoff package checks apply to every fire case even though they are not repeated per case: the package has the eight elements (KB-ESC-001), contains no full card number, CVV, PIN, Aadhaar, password or OTP, and the human's first message does not need to re-ask for anything in it.

## 6. Validator

`python tests/escalation/validate_escalation.py`, run from the repository root (needs PyYAML). Exit code 0 means every check passes.

| Check | What it verifies |
|---|---|
| 1 | The rules file has ESC-001 to ESC-015 in order; each trigger's condition text, priority, queue and SLA equal KB-ESC-010, and its `brief` block equals a transcription of A6 held in the validator; `sla_seconds` matches; every P0 trigger is `cancellable: never` |
| 2 | Each trigger's `intents`, `guardrails` and `kb_entries` equal the links recorded in `config/intents.yaml`, `config/guardrails.yaml` and the KB entries; every per-intent ESC link, per-guardrail `escalation` value and KB `escalation_triggers` value points at a defined trigger; additions reference existing IDs and use a brief queue at its own priority and SLA |
| 3 | The 15 queues are exactly the A6 queues; overflow targets are brief queues or `callback`; P0 queues are 24x7; precedence ranks are 1 to 15, match the ranked list, and never place a lower priority or a longer SLA first |
| 4 | Every name used in a `fire_when` expression is a defined signal, constant, proposal or parameter |
| 5 | The eight handoff package elements equal KB-ESC-001, in order |
| 6 | Cases: YAML parses, `case_count` matches, IDs are unique and follow the scheme, required fields are present, personas are the six A13.2 personas, authentication levels and intents and tertiaries exist, guardrail and trigger IDs exist, each brief trigger has at least one fire and one near-miss case, fire cases carry the trigger's priority, queue and SLA, near-misses list their own trigger in `must_not_escalate`, the rules file and the cases list each other, the boss set has 10 cases whose owner outranks its secondaries, no sensitive-looking digit run appears, files are ASCII |
| 7 | The Day 12 documents, the diagram and the rules file mention only IDs that exist (ESC, XTR, GR, KB, intents, DM, KPI and EQ, test IDs, decisions up to D-170), are ASCII, and `triggers.md` and the diagram mention all 15 triggers |
| 8 | The seven A6 constants equal the brief's values; each threshold trigger uses the brief's comparison (ESC-003 `>=` 3, ESC-004 `>=` 2, ESC-005 strict `>`, ESC-006 `>=` 3, ESC-010 strict `>`); ESC-015 is the literal status condition; XTR-06 cannot raise ESC-010 at or below 15 turns; a P0 queue's overflow starts with a human P0 queue, never `callback` |
| 9 | The A6 table in `triggers.md`, the queue table in `queue-management.md` and section 2 of `kpi-framework.md` equal the rules file and transcriptions of A6 and A8 held in the validator; the glossary definition of containment is quoted |
| 10 | For cases whose fixture fully determines the rule (injected confidence, sentiment, amount, request count, turn counters, record flags, OTP events), the expected fire or no-fire is recomputed and compared with `expect`; PAN-shaped and phone-shaped values are rejected; `must_not_contain` strings of 4 characters or fewer must be `re:` patterns |

## 7. Open items

1. Expected replies depend on template wording that is written on Day 13 (`routing-and-handoff.md` section 11); `must_not_contain` strings may need alignment then.
2. Hinglish wording is unreviewed by a native speaker; the Gujarati case uses placeholders and depends only on injected scores (D-22).
3. ESC-T-015-02 follows the literal reading of ESC-015 (D-164): a generic request by a flagged customer creates the record and the case with no live transfer. Short `must_not_contain` strings use `re:` word-boundary patterns so a correct reply is not failed by a substring (for example AML inside "seamless").
4. Fixtures assume a harness that can inject classifier outputs, record flags, tool faults and timers; none exists yet.
5. `tests/README.md` section 5.6 still says four triggers have no case; it predates this folder and the Day 11 suite and needs a one-line update by the coordinator.
