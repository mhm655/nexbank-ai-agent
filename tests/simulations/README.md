# Simulation Checks

Brief refs: Part B Level 7 (p.41: "20+ sample conversations"; the 25-turn customer journey with authentication, guardrail activation, sentiment recovery and escalation decision), Part D Day 14 (simulations), A9.1 (five patterns, pp.22-23), A9.2 (eight anti-patterns, pp.24-25, including the AUTO-FAIL for a non-existent benefit or a wrong rate), A13.2 (six personas), A4.1 to A4.4 (advice boundary, security rules, adversarial vectors), A6 (escalation triggers).

Files: `validate_simulations.py` (this folder). It reads `simulations/conv-*.md`, `simulations/INDEX.md` and `simulations/pattern-audit.md`, and cross-references the registries `config/intents.yaml`, `config/guardrails.yaml`, `config/escalation_rules.yaml`, `config/templates/*.yaml`, `docs/knowledge-base/entries/*.yaml` and `docs/assumptions-and-decisions.md`.

The working names in the `State` row are mapped to schema fields in `simulations/INDEX.md` section 8 (D-212).

Status: the validator is a static check of designed examples. It parses, cross-references and lints the conversation files. It does not run a model, an agent or a conversation, and every confidence, sentiment and retrieval number in the simulations is an illustrative value chosen to exercise a threshold. A passing result means the files are consistent with the specification files; it does not mean the system behaves like this.

## 1. How to run

```text
python tests/simulations/validate_simulations.py                  # exit code 0 = PASS
python tests/simulations/validate_simulations.py --dir SCRATCHDIR # check another folder of simulations (used for the seeded-defect runs)
```

Needs Python 3 and PyYAML. On Windows set `PYTHONIOENCODING=utf-8` if an error message has to print Hindi or Gujarati text.

## 2. What it checks

| # | Check | Fails when |
|---|---|---|
| S1 | At least 20 conversation files (and at least 22, the Day 14 floor); names match `conv-NN-slug.md`; the first line is `# conv-NN: title` | too few files, bad name or title |
| S2 | Required header fields are present and non-empty (21 fields: scenario, persona, channel, language, starting auth level, intents, guardrails, escalation outcome, escalation IDs, priority, adversarial vectors, security rules, patterns, anti-patterns, coverage tags, case study, templates, KB entries, tools, `prompt_version`, what it proves); `prompt_version` is the Day 13 string; the "designed, illustrative" statement and (from conv-07) the Setup line are present | missing field or statement |
| S3 | Self-audit block: the pattern table has P1 to P5, the anti-pattern table has AP1 to AP8, and every anti-pattern result is `absent`, `not at risk` or `not applicable`; a Closing block exists | block missing, malformed or reporting a violation |
| S4 | Turn structure: turns are `T1..Tn` in order; the first message is the customer's; every turn has the seven annotation rows; every customer turn shows an entity extraction; every conversation has at least one decision point; the `State` row carries phase, auth, topic stack, slots, pending confirmation, counters, turns since resolution and escalation proximity, and its `turn_count` equals the turn number; Closing "Messages" equals the number of turns; customer turns show the Input Guard check and agent turns the Output Safety Layer check | structure or state missing |
| S5 | Identifiers exist: intent IDs, GR IDs, ESC IDs and sub-rules, XTR IDs, KB IDs (and the cited `@version` equals the entry's current version), TPL IDs (and the cited variant and version exist), queue names in router rows, tool names, decision IDs (D-172 to D-174 and D-200 to D-207 belong to Day 14 and its audit fixes; D-175 to D-180 were reserved and not used) | dangling reference |
| S6 | Header consistency: Templates used, KB entries cited, Tools called and Guardrails exercised each equal the set found in the turn annotations; every header intent appears in an NLU row | header says something the turns do not |
| S7 | Characters: English text is ASCII (no em dash, smart quote, emoji); only Devanagari and Gujarati are allowed beyond ASCII; non-English turns have an English gloss and the file says the text is not native-reviewed; the word PLAN does not appear | forbidden character, missing gloss |
| S8 | Sensitive digits: no card-like run of 13 to 19 digits, no 4-4-4 or 12-digit Aadhaar-like run, no phone-like number, no 9 to 18 digit account-like run, no OTP-like or CVV-like digits next to the word code, OTP or CVV, no PAN-like string. Masked forms ("ending 4521") and `{{SYN_...}}` placeholders pass | a value that could be real |
| S9 | AI-turn wording: no back-to-back identical agent messages, no message sent three times, no message over 250 words (`atk_output_max_words`), at most one apology per message, no unfilled `{{slot}}`, and none of the banned phrases (an unbacked timeline such as "within 24 hours", "will be credited", "I promise", "guarantee", "I recommend", "your fault", over-apology wording, asking for an OTP, PIN or CVV, claiming to be human) | anti-pattern wording |
| S10 | Template wording: for every templated turn, the fixed text of each cited template variant in the cited language appears verbatim in the agent message (only the slots differ) | a template paraphrased |
| S11 | `INDEX.md` lists exactly the conversation files present, carries the "illustrative" statement, the coverage matrices and the gap list | index out of date |
| S12 | `pattern-audit.md` has a pattern row and an anti-pattern row for every conversation, and every number in every AI turn appears in that conversation's AUTO-FAIL sweep rows, and the sweep states "Figures with no source: 0" | a figure with no source row |
| S13 | Coverage floor: at least 22 conversations; at least 25 distinct intents and all seven families; all six personas; all six adversarial vectors; priorities P0, P1 and P2; at least 10 distinct ESC triggers fired and ESC-001, 004, 008, 011, 013 and 015 among them; XTR-01 and ESC-006; every account-security rule R1 to R8; the advice boundary in at least three categories; a Hindi (Devanagari) conversation, at least three Hinglish conversations, a secondary-language conversation with the fallback ladder; a session timeout, a step-up, a tool failure (ESC-014), a multi-session carry-over, a multi-intent turn, a near-miss, a sentiment recovery and a graceful degradation | a required scenario missing |
| S14 | Exactly one Level 7 conversation, with 25 or more messages, at least 3 intents, an authentication transition, a guardrail activation, a raw sentiment below -0.70 followed by a score of -0.40 or better, and an escalation decision | the boss journey incomplete |
| S15 | AI-turn rules in any language (added after the Day 14 audit): a credential or identity number asked for in chat (OTP, PIN, CVV, password, Aadhaar, PAN, card or account number with a request verb, in English, Hindi or Hinglish; a sentence that forbids sharing is not flagged); a claim to be human or not an AI; advice in other words ("it is a good idea to", "I would suggest", "you should invest"); a rate written in words; a duration or date promise ("by tomorrow", "in 2 working days", "kal tak", "2 din mein") that no tool, router or KB row of the same conversation backs with the same number and unit | a rule broken in a paraphrase that the older phrase list missed |
| S16 | Topic statuses in every State row are one of `active`, `parked`, `resolved`, `abandoned` (`config/dialogue_state.schema.json`); every intent used in the turns (NLU primary intent, topic stack) is in the header `Intents covered` (GEN-006 excepted) | a status or an intent outside the contract |
| S17 | Escalation claims: an ESC ID that the Escalation outcome says fired is listed in Escalation IDs; every listed ID names a sub-rule (`ESC-nnn.x`) in the turns and in the Escalation record; a fired escalation has a Handoff package table with exactly the 8 numbered elements (D-04) | a fire claimed without a cited condition, or a short package |
| S18 | The self-audit numbers match the turns: the longest agent message in AP2, the agent-message count in AP1, the figure count in AP8 (conv-07 onward) against the AUTO-FAIL sweep rows, and the total sentence of `pattern-audit.md` against its table | a stale number after an edit |

## 3. Result of the run

```text
conversation files: 32 in simulations
messages: 318
distinct intents: 34 | ESC fired: 15 ['ESC-001', 'ESC-002', 'ESC-003', 'ESC-004', 'ESC-005', 'ESC-006', 'ESC-007', 'ESC-008', 'ESC-009', 'ESC-010', 'ESC-011', 'ESC-012', 'ESC-013', 'ESC-014', 'ESC-015']
personas: ['Arjun', 'Meera', 'Priya', 'Rajesh', 'Sunita', 'Vikram']
languages: {'en': 24, 'hinglish': 5, 'hi': 1, 'gu (secondary), replies in hi': 1, 'en (one Hinglish message at T14)': 1}
template ids used: 52 of 73
RESULT: PASS
```

The first run on the 30 files found 23 problems, all of them in the checker (a KB ID such as KB-PRD-008 read as an intent ID, the template-ID pattern stopping before a digit, and a Setup line demanded from conv-01 to conv-04, which predate it). They were fixed in the checker, not in the files. No defect was found in conv-01 to conv-06.

## 4. Proof that the checks catch what they claim to catch

Nine defects were seeded, one at a time, into scratch copies of `simulations/` kept outside the repository, and the validator was run on each with `--dir`. Each run failed with the expected message; the real folder was not touched.

| # | Seeded defect | Caught by | First message |
|---|---|---|---|
| 1 | An unbacked timeline ("will be credited within 24 hours") in an AI turn of conv-09 | S9, S12 | banned phrase `within N hours` in an AI turn; figure '24' is not in the AUTO-FAIL sweep |
| 2 | A KB ID that does not exist (KB-POL-099) in conv-11 | S5, S6 | unknown KB id KB-POL-099 |
| 3 | A full 16-digit card number in a customer turn of conv-14 | S8 | card-like digit run |
| 4 | The self-audit block removed from conv-12 | S3 | self-audit block missing or malformed |
| 5 | `INDEX.md` without the conv-20 row | S11 | INDEX.md does not list file(s) that are present |
| 6 | One word of a template changed in conv-14 | S10 | template wording of TPL-AUTH-OTP-FAILED/retry not found verbatim |
| 7 | A rate with no source ("9.1 percent for 3 years") added to an AI turn of conv-07 | S12 | figure '9.1' is not in the AUTO-FAIL sweep |
| 8 | The `Tools called` header field removed from conv-10 | S2 | header field missing or empty |
| 9 | An OTP-like number next to the word "code" in a customer turn of conv-15 | S8 | OTP-like digits next to the word code or OTP |

Defect 9 was first missed because the pattern refused a number followed by a full stop; the pattern was corrected and the run repeated.

### 4.1 Second round of seeded defects (Day 14 audit fixes)

The Day 14 audit seeded 21 defects into scratch copies; 9 were not caught. The checks S15 to S18 were added, and each missed defect was seeded again, one at a time, into a scratch copy kept outside the repository. The run compares the errors of the mutated copy with those of an unmutated copy of the same folder, so only a new error counts as a catch.

| Seeded defect | Where | Caught by |
|---|---|---|
| "Please type your full Aadhaar number here." appended to an AI turn | conv-20 | S15 |
| "I am a human agent." and "I'm a real person and not an AI." appended | conv-26 | S15 |
| "It is a good idea to put more money into NexFD.", "You should take the 5 year loan.", "I would suggest the mutual fund for you." | conv-16, conv-08, conv-03 | S15 |
| "You will have the refund by tomorrow.", "The money will come back in 2 working days." | conv-09 | S15 (the second only because the 2 in that conversation is a number of minutes) |
| The same promises in Hindi ("कल तक") and Hinglish ("2 din mein") | conv-10, conv-12 | S15 |
| "The rate is eight point nine percent." and "six percent" | conv-07 | S15 |
| An OTP request in Hindi ("कृपया अपना ओटीपी बताइए।") and Hinglish ("apna PIN bhejiye") | conv-10, conv-12 | S15 |
| Escalation outcome says ESC-004 fired, header says none; header lists ESC-004 with no sub-rule | conv-24 | S17 |
| Handoff package row 6 or row 8 deleted | conv-09 | S17 |
| A topic status `candidate` or `queued` | conv-26, conv-12 | S16 |
| `CMP-005` removed from Intents covered although the turns use it | conv-29 | S16 |
| "Please don't share your OTP with anyone." appended (must NOT be flagged) | conv-11 | not flagged, as intended |

The real files, run through the stronger checks, showed 35 genuine defects, all fixed in the files: 26 topic-status rows (`queued`, `closed`, `candidate`), 5 headers that omitted an intent the turns use (conv-16, 21, 24, 27, 29), and 4 stale self-audit word counts. No credential request, human claim, paraphrased advice, unbacked duration or rate in words was found in any of the 32 conversations.

## 5. What it does not check

- That the wording is good, kind or accurate: an author reads the conversations. The checker only proves that fixed template text is verbatim, that figures have a row, and that forbidden wording is absent.
- That a figure's stated source really holds the figure. The sweep rows name the source; a reviewer opens it. For conv-01 to conv-06 the source column is read from the annotation of the same turn.
- That the confidence, sentiment and retrieval numbers are realistic. They are illustrative values chosen to exercise thresholds.
- That Hindi, Hinglish and Gujarati text is correct. It is authored and not native-reviewed (D-22).
- That the state transitions are the ones the dialogue manager would produce. The state row is checked for shape and for `turn_count`, not for logic.
- Anything about a running system. The simulations are designs, not transcripts.
