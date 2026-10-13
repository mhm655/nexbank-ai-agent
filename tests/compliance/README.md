# Compliance and Risk Tests

Brief refs: A10.1 and A10.2 (pp.27-28, the log schemas), A10.3 (pp.28-29, encryption, access, retention, deletion, reporting), A11.1 to A11.3 (pp.30-32, risk matrices), Part D Day 14-15 (pp.60-61, deliverables and the failure-condition check). Documents under test: `docs/compliance/audit-logging.md`, `docs/compliance/submission-checklist.md`, `docs/risk/risk-matrix.md`, `docs/risk/fairness-testing.md`. Decisions: D-181 to D-190.

**Status: specified, not run.** The validator checks the specification files against each other and against a transcription of the brief. It does not run an agent, and no fairness pair has been executed. A passing result means the documents are consistent; it does not mean the system is compliant or fair.

## 1. Contents

| Path | Purpose |
|---|---|
| `validate_compliance.py` | The validator. Run from the repository root: `python tests/compliance/validate_compliance.py`. Needs PyYAML; uses `jsonschema` when it can be imported and otherwise a structural check (it prints which) |
| `fairness-pairs.yaml` | 15 counterfactual pairs (30 cases), `FAIR-01-a` to `FAIR-15-b`. Method: `docs/risk/fairness-testing.md` section 6 |
| `examples/conversation-record.json` | One A10.1 conversation record, synthetic |
| `examples/turn-record-customer.json`, `examples/turn-record-agent.json` | Two A10.2 turn records, synthetic; the agent record shows the retrieval, template, tool call and safety verdict fields |
| `../../config/audit_log.schema.json` | The log schema (JSON Schema 2020-12). Top-level properties are the brief's fields; every project addition sits under `ext` |

The fairness pairs are not part of the fixed safety suite (`tests/safety-suite/manifest.yaml`) and are not in its locked manifest. They follow the case schema of `tests/README.md` section 2 plus the fields `pair`, `side` and `varies`.

## 2. Checks

| # | Check | Fails when |
|---|---|---|
| 1 | The schema is a valid JSON Schema and the three examples validate | The schema is invalid or declares another draft; an example does not validate |
| 2 | Example hygiene | An example holds a full card, Aadhaar, PAN, phone or OTP-like value (a run of digits is no longer excused as a UUID), or a `ciphertext` field holds readable text instead of a sealed or synthetic-ciphertext marker; the examples do not cover a conversation record, a customer turn and an agent turn |
| 3 | Brief fields in the schema | A field of the transcription list (11 from A10.1 with type and retention, 14 from A10.2 with sub-fields and value sets) is missing, has another type or range, or lacks the brief's retention in its description; the schema has another top-level field; `additionalProperties` is not false |
| 4 | Brief fields in the document | A field is missing from the tables of `audit-logging.md` sections 2.1 and 3.1, a row carries another type or retention, one of the eleven A10.3 requirement lines is not quoted exactly as the brief prints it (checked against a transcription held in the script), a numbered section is missing, or fewer than 10 audit queries are worked |
| 5 | Cited IDs exist | A GR-, ESC-, KB-, D-, DM-, KPI-, RISK-, EQ-, FT-, AQ-, RPT-, QG-, INV-, RED-, XTR-, TPL-, FAIR- or SS- ID cited in the owned files is defined nowhere. D-181 to D-190 and D-200 to D-207 are in `docs/assumptions-and-decisions.md`; the script tolerates them with a warning if a log row goes missing |
| 6 | Risk register | A column is empty; a likelihood or impact is outside 1 to 3 and 1 to 4 or its label does not match; a score is not likelihood x impact; residual is above inherent (as a score, or in likelihood or impact); a band is wrong; a brief row differs from the transcription of A11.1 and A11.2, or the reproduced tables of sections 3.1 and 4.1 differ from it in any cell (risk, probability, impact, severity, mitigation); the severity rule does not reproduce the brief's ten severities; the counts, band table, sum of scores, the "falls by" percentage, the list of unchanged scores, both heat maps or the top 10 differ from a recomputation; a control cites a file that does not exist; the FMEA mapping misses a row |
| 7 | Fairness pairs | The file does not parse; the header counts are wrong; fewer than 12 pairs; a pair lacks side a or b; the two sides differ in anything other than the attribute named in `varies` (language pairs may also differ in `input_turns`); any expected outcome field differs; a guardrail, intent or trigger ID is unknown |
| 8 | Numbers | A figure in `audit-logging.md` section 16 differs from the volume model recomputed in the script (`volume()`); a sample size, time-to-sample, minimum detectable gap, discordance bound or matrix size in `fairness-testing.md` differs from its recomputation; a repository count quoted in `risk-matrix.md` or `fairness-testing.md` (guardrails, suite cases, obligations, templates, adversarial cases, escalation cases, triggers) differs from the repository |
| 9 | Submission checklist | A count in `submission-checklist.md` differs from the repository; a status says `met` when the count does not meet the brief's number (or the reverse); an evidence file does not exist; a row is missing. |

Exit code 0 when no error is found. Warnings are printed and do not fail the run.

## 3. What the transcription lists are

`validate_compliance.py` holds its own copy of the brief's text for A10.1 (11 fields, type, retention), A10.2 (14 fields and the sub-fields the brief names), and the ten technical and business risks of A11.1 and A11.2 (probability, impact, severity). They were transcribed from the PDF. The PDF's A11 tables are interleaved in the text extraction; the transcription reads them by row order. If the brief changes, change the lists in the script and the documents together.

## 4. Seeded defects

Each defect below was applied to a scratch copy of the owned files (never to the repository) and run with `COMPLIANCE_OWN_ROOT` pointing at the copy. All 12 were caught.

| # | Defect | Caught by |
|---|---|---|
| D1 | `pii_detected` removed from the schema | checks 1 and 3 |
| D2 | `csat_score` retention written as 7 years in the document | check 4 |
| D3 | Residual of RISK-T-02 raised above its inherent score | check 6 |
| D4 | One fairness pair changed in two attributes | check 7 |
| D5 | Checklist says 70 KB entries, repository holds 77 | check 9 |
| D6 | Citation of `GR-XYZ-99` and `KB-FAQ-999` | check 5 |
| D7 | Turn records per day written as 298,000 instead of 288,000 | check 8 |
| D8 | Equivalence sample size written as 8,900 instead of 8,993 | check 8 |
| D9 | Inherent score of RISK-T-07 written as 9 for 3 x 4 | check 6 |
| D10 | Contingency column of RISK-B-09 left empty | check 6 |
| D11 | `retrieval_confidence` renamed in the turn table of the document | check 4 |
| D12 | A full card number placed in an example | checks 1 and 2 |

## 5. Limits

- The checks read documents; they cannot tell whether a likelihood, an impact or an owner is a sound judgement.
- Check 5 accepts an ID if it is defined anywhere in `docs/`, `config/` or `tests/` (a table row, a YAML `id`, a bold or heading label). It does not check that the definition means what the citation says.
- Check 8 recomputes the numbers from the stated assumptions. The assumptions (record sizes, prices, base rates, response rate) are assumptions, not measurements.
- The structural fallback of check 1 (used only when `jsonschema` is not importable) checks required and unknown top-level fields, not types.
