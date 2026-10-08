# CHANGELOG

One entry per working day (15). Each entry: tasks, decisions with rationale, challenges, open questions, next-day plan.

## Day 1: Setup and analysis

**Tasks completed**
- Read the full 71-page brief and produced an implementation plan.
- Created the repository skeleton following the required structure (README, CHANGELOG, docs/, diagrams/, simulations/, tests/, config/).
- Wrote `docs/requirements-traceability.md` (requirement > brief section > file > status).
- Wrote `docs/assumptions-and-decisions.md` with assumptions A1-A6 and decisions D-01 to D-12 for the brief's open questions.
- Wrote `docs/stakeholder-analysis.md` (Customer Experience Board vs Risk Committee tension map).
- Drafted the coordinator query in `docs/coordinator-questions.md` (not sent).

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- Deliverable is documentation-first: Markdown, Mermaid, YAML/JSON, CSV.
- One CHANGELOG entry per working day (15), which satisfies "7 entries" either way.
- Response-time tiers: < 3 s p95 per turn (engineering), < 5 s (SLO), < 30 s (business ceiling).
- Safety wins over experience wherever the two governance bodies conflict, with experience protected by design inside the safe envelope.

**Challenges**
- The brief references "10 automatic failure conditions", "7 deliverable requirements" and an "8-element" handoff package without listing them. Proxy definitions are recorded as decisions.
- The 500 transcripts are not included; only the aggregate table in A1.2 exists.

**Open questions**
- Q1, Q2, Q10, Q12 are awaiting coordinator input (see `docs/coordinator-questions.md`).

**Next (Day 2)**
- 12-component architecture diagram, component interface contracts, agent/tool matrix.

## Day 2: Architecture, interfaces, agents

**Tasks completed**
- `docs/architecture/system-architecture.md`: principles, 12 components, agent/tool scope, per-turn flow, safety architecture, reference stack.
- `docs/architecture/component-interfaces.md`: input, output, error/fallback and p95 SLA contracts for all 12 components.
- `diagrams/architecture.mmd` and `diagrams/agents-and-tools.mmd` (Mermaid).
- Completed `docs/requirements-traceability.md` (left unfinished earlier on Day 1).

**Decisions**
- Policy Engine doubles as orchestrator; the Guardian is a separate, non-LLM veto component.
- No tool exists for fund transfer, nominee/KYC change or account closure (hard rule, builds on D-08).
- Every write tool takes an idempotency key and is never auto-retried.

**Challenges**
- Reconciling three response-time targets: handled through per-stage budgets that sum to about 2.85 s (D-07).

**Open questions**
- Unchanged from Day 1 (Q1, Q2, Q10, Q12).

**Next (Day 3)**: state schema and machine, policy and multi-turn reasoning, FMEA, latency/scale/cost, boss trace.

## Day 3: State machine, FMEA, latency and scale

**Tasks completed**
- `config/dialogue_state.schema.json` (JSON Schema 2020-12; validated as parseable JSON).
- `diagrams/dialogue-state-machine.mmd`, `diagrams/auth-flow.mmd`.
- `docs/architecture/dialogue-management.md`: phases, guards, auth sub-machine, action space, hybrid policy, confirmation/clarification/recovery/proactive strategies, anaphora, topic stack, implicit intent, contradictions, context-window management.
- `docs/architecture/response-generation.md`, `multilingual.md`, `failure-modes.md` (24-row FMEA), `latency-scalability-cost.md` (1x/10x/100x), `boss-trace.md`.

**Decisions**
- Topic switch = high-confidence secondary-intent change that is not a slot answer or clarification.
- Learned ranker is limited to safe candidate actions and has the lowest precedence.
- Hybrid generation uses locked fact slots that the LLM cannot alter.
- Cost-model unit prices are labelled illustrative placeholders, not quotes.

**Challenges**
- Level 1 boss trace needed 12 switches in 20 turns while still exercising safety invariants; achieved with a security pre-emption, an advice-boundary deflection and a human-request trigger.

**Open questions**
- The 15 ESC triggers are referenced but defined on Day 12; intent labels in the trace are provisional until Day 4.

**Next (Day 4)**: intent taxonomy (30+ intents), entity catalogue.

## Day 4: Intent taxonomy and entity catalogue

**Tasks completed**
- `config/intents.yaml`: 41 intents (32 from A3.1 to A3.3, plus ACC-008 KYC Update and 8 general intents GEN-001 to GEN-008), 145 tertiary labels, per-intent auth level, safety rating, action type, confirmation level, ESC links and multi-intent rank.
- `config/entities.yaml`: 51 extractable entities and 1 dialogue-act slot, each with type, extraction order, validation rule, sensitivity tier and storage handling. Seven Input Guard redaction rules (RED-01 to RED-07) for card, CVV, Aadhaar, PIN/password, OTP, PAN and account numbers.
- `docs/intent-taxonomy/taxonomy.md`: three-layer structure, intent register, tertiary table, rationale for auth and safety ratings, mapping from the provisional Day 3 labels.
- `docs/intent-taxonomy/entities.md`: sensitivity tiers, redaction, extraction approach, validation, slot-filling policy (required vs optional, defaults, question order, confirmation levels, contradictions).
- Cross-reference check by script: every entity named in an intent exists in the catalogue and every catalogue entity is used; both YAML files parse.
- Updated the Day 3 boss trace to the final intent IDs.

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-13: card intents sit under the primary class `account` so the primary layer stays at the six A2.2 classes.
- D-14: PAN accepted only in the secure form widget, never in free chat.
- D-15: recurring-payment setup is never executed by the agent; cancel is allowed with Biometric and explicit confirmation.
- D-16: fraud reports are accepted at any auth level; protective actions need OTP.
- D-17: auth levels and safety ratings the brief does not give (CRD, PRD, CMP, SEC) are my assignments, flagged for Risk Committee review.

**Challenges**
- A13.1 has no recurring-deposit product, account variants, EMI conversion fees or branch details. These intents are marked `kb_gap` so the agent never invents figures; they become hallucination-trap tests on Day 10.
- The brief lists the primary layer as six classes but the CRD intents as their own family; resolved by D-13.

**Open questions**
- Q1, Q2, Q10, Q12 still awaiting coordinator input.

**Next (Day 5)**: disambiguation trees for the six pairs, multi-intent and out-of-scope handling, per-layer thresholds, sentiment and emotion spec.

## Day 5: Disambiguation, multi-intent, out-of-scope, sentiment

**Tasks completed**
- `docs/intent-taxonomy/disambiguation.md` and `diagrams/disambiguation-01..06-*.mmd`: one decision tree per A3.4 pair, each with entity-based rules, threshold logic, a clarifying question sequence (English plus Hinglish pattern), a safe default and escalation hooks. All Mermaid files parse with the Mermaid parser.
- `docs/architecture/nlu-pipeline-overview.md`: NLU stages, NLU output frame, per-layer thresholds and fallbacks, execution gate and flow-entry overrides, multi-intent detection and ordering, out-of-scope detection and fallback ladder, latency split, failure behaviour.
- `docs/intent-taxonomy/sentiment.md`: continuous score, seven emotions, trajectory, slope and recovery, ESC-004 rule with safeguards, Empathy-First trigger, Indian-English and Hinglish cultural cues, sarcasm detection and handling, evaluation targets.
- `config/intents.yaml`: added `flow_entry_overrides` and `max_clarification_turns` to the thresholds block.

**Decisions**
- D-18: ESC-004 keeps the brief's raw-score rule, adding a per-turn confidence gate and an EMA route for secondary languages.
- D-19: asymmetric gates. Safety flows (SEC-001, SEC-004, GEN-003, GEN-007, PRD-005) are entered at 0.50; executing an action needs 0.85 and explicit confirmation.
- Pair 2 (information vs advice) never asks a clarifying question, because asking would invite the customer to volunteer income or age data the agent must not use.
- Pair 6 contains first, classifies second: the card is blocked (with confirmation) before the fraud question is asked.

**Challenges**
- Reconciling 0.70 as the act threshold with the lower safety-flow gate without weakening the rule that nothing protective runs unconfirmed.
- Pair 5 can be mistaken for an accusation; the spec keeps reclassification between fraud and dispute open until handoff, and the tone rules forbid accusing the customer.

**Open questions**
- Sentiment accuracy targets in `sentiment.md` are my proposals; the brief gives none.
- CEB view needed on the EMA route in D-18.

**Next (Day 6)**: utterance library (300+ across English, Hindi, Hinglish and secondary languages), language detection and code-switching spec, Level 2 boss set of 10 ambiguous messages in `tests/nlu/`.

**Day 4-5 audit fixes (applied after review)**
- Fixed 9 small defects found by the audit: tool name `send_credential_reset_link`, wrong section pointers, the `inferred` slot state, confirmation expiry wording, ACC-003 then ACC-004 chain, NLU frame to state mapping, a dead-end node in the pair 6 diagram, and boss-trace phases and labels.
- Boss trace: ESC-001 (P0) now fires at T5 when the intent resolves to fraud, so the fraud report is never left parked without escalation (A4.2 rule 6); T13 now asks the pair 3 question and T14 answers it; T17 carries `loan_type`.
- SEC-002 confirmation raised to explicit; the execution-gate comment now covers `ticket` actions.
- Citation fixes: the 0.15 ambiguity gap now cites the dialogue-management guards (D-06 defines only the 0.70 and 0.40 tiers); taxonomy mapping for the FD-rate turn is `fd_rate_by_tenure`; pair 6 wording now matches the 0.85 execution rule.
- Still open from the audit: clarification budget vs "escalate after 2 failed clarifications", agent/tool matrix gaps, and the `PLAN.md` references that sit outside the repo.


## Day 6: Utterance library, language detection, Level 2 boss

**Tasks completed**
- `docs/intent-taxonomy/utterances.csv`: 551 labelled utterances for all 41 intents (13 to 17 each) covering all 145 tertiary labels. Languages: English 213, Hinglish 167, Hindi 87, Tamil 26, Telugu 15, Bengali 15, Marathi 14, Gujarati 13. Includes typos (36), sarcasm (5), code-switched rows (Devanagari plus Latin and Roman Hinglish), 12 multi-intent rows, 14 crisis rows and the KB-gap traps. Split 69.5 / 15.3 / 15.3 (train / dev / test), stratified per intent and by language class, every intent present in test. No full card, Aadhaar, CVV, OTP, PIN or account value appears; only masked or last-4 forms.
- `docs/intent-taxonomy/language-detection.md`: language ID (script, classifier, decision table with proposed thresholds), Hindi and Marathi same-script handling, Roman-script secondary languages, code-switching rules, transliteration normalisation, digit folding, English-pivot translation pipeline with a quality gate, secondary-language fallback ladder, per-language gate, evaluation. `docs/architecture/multilingual.md` gets a pointer and stays consistent.
- `tests/nlu/boss-level2.yaml`: 10 ambiguous messages (one per pair, 4 cross-pair, 6 in Hinglish), each with expected intent, runner-up, pair, reasoning, action (4 clarify, 6 act) and clarifying question or follow-up.
- `tests/nlu/README.md`: schema, boss scoring rules, metrics (per-layer accuracy, macro-F1, pair confusion with a separate fraud-miss count, OOS precision and recall, entity accuracy, safety-flow recall, execution-gate check), slices and the CSV format.
- Verification by Python: CSV parses, no duplicate IDs or texts, every `intent_id` and `tertiary_label` exists in `config/intents.yaml`, every entity key exists in `config/entities.yaml`, script of each row matches its language label, no long digit runs or credential values, every intent has train, dev and test rows. Boss YAML parses with valid intent IDs and all six pairs covered.
- Updated README status and navigation, taxonomy.md pointer, disambiguation open items, requirements traceability (R-11, R-17, R-19 done).

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-20: language-ID thresholds and the secondary-language fallback are proposals; no automatic language switch without the customer's choice.
- D-21: Input Guard redaction runs on a digit-folded copy so native digits, separators and spelled digits cannot bypass RED-01 to RED-07.
- D-22: the library is synthetic and secondary-language rows are provisional until native-reviewed; secondary metrics are pooled.
- D-23: multi-intent rows carry the lowest-`mi_rank` intent in `intent_id` and the rest in `notes`.
- D-24: boss `expected_action` is `clarify` or `act`; pair 2 and pair 6 are `act` by design.

**Challenges**
- Keeping the secondary-language sentences natural without native review; the test split holds only 17 secondary rows, too few for per-language metrics.
- Writing sarcasm and safety rows (fraud, crisis) without inserting credential values; crisis rows contain no operational detail.
- Cross-pair boss cases where two trees disagree (pairs 5 and 6, pairs 1 and 5); resolved with the existing rules: not-me cue outranks status words, and SEC-001 leads while the block is its first step.

**Open questions**
- Native-speaker review for Tamil, Telugu, Bengali, Marathi and Gujarati rows and the translated template set (CEB concern).
- Whether human support exists for all five secondary languages and in which hours.
- Metric floors (macro-F1 >= 0.90, language-ID accuracy, 85% pooled secondary) are proposals; fix them after the first evaluation run.

**Next (Day 7)**: knowledge base schema, versioning, TTL, access control and the first KB entries.

## Day 7: Knowledge base schema and entries

**Tasks completed**
- `docs/knowledge-base/kb-schema.md`: entry schema (PLAN 3.3 fields plus `audience`, `ttl_class`, `status`, `intents`, `escalation_triggers`, `body_i18n`, gap fields), ER model (`diagrams/kb-er-model.mmd`, parses with the Mermaid parser), three formats with rules, ID convention `KB-<CAT>-<NNN>`, semantic versioning with live updates and immutable history, six TTL classes with hard and soft expiry, regulatory tag vocabulary mapped to the brief, auth-level access control as a pre-retrieval filter, intent links, gap-entry shape.
- `docs/knowledge-base/entries/`: 77 entries in six YAML files (product 12, policy 11, regulatory 11, FAQ 11, troubleshooting 10, escalation 21). Formats: 18 structured, 34 semi-structured, 24 unstructured. 11 are gap-handling entries covering the four `kb_gap` intents (ACC-007, CRD-004, PRD-003, GEN-008) and further topics A13.1 does not cover (RD, international transfer charges, card and loan fees, insurance premiums, ombudsman and cooling-off details, a generic unknown-question fallback). Four FAQ entries carry Hindi and Hinglish wording (review simulated; native-speaker check pending, see open questions). Every entry has intent links valid in `config/intents.yaml` and a `source_ref` to the brief (A13.1, A4.1 to A4.3, A6, appendix pages 70 and 71).
- `docs/knowledge-base/README.md`: index table (ID, title, category, format, auth, audience, intents) and coverage counts. 38 of 41 intents have at least one entry; CMP-004, GEN-005 and GEN-006 are answered by templates and need none.
- `tests/kb/validate_kb_entries.py`: validator. Result: PASS. Checks include parse, required fields, unique IDs, ID code matches category and file, valid enums and auth levels, `expires_at = effective_from + ttl_days`, intent and ESC IDs exist, `KB-` cross references resolve, every `kb_gap` intent has a gap entry, at least 55 entries, all categories and formats present, gap-entry shape (non-empty `gap_for`, five keys, no figures), and an allow-list scan of every number in titles, bodies, translated bodies and fields (YAML numbers included) plus an allow-list of number-and-time-unit pairs that reports timeline wording such as "working days".
- Manual check of every figure against the brief (A13.1 page 35, A4.1, A6, A1.2): rates 4.5, 6.0 to 7.25, 8.25, 10.5; tenures 7 days to 10 years, 30 and 5 years; 40 and 50 day interest-free; 2% cashback, 5x rewards; CIBIL 700 and 650; 90% LTV; 10 LPA; 1 Cr and 50L; SIP INR 100; gold INR 10, 24K; DICGC 5L; plus the A4.1 examples (6.5%, 8.5%, 17,356, 1.5L), A6 thresholds (INR 50,000, 5L) and A1.2 card-block turns (3.4). The EMI of 17,356 was recomputed (17,356.46).
- Audit fixes: the validator skipped YAML numbers in fields, translated bodies and any 19xx/20xx figure (for example an INR 2000 fee), and crashed on a null `escalation_triggers` or string `ttl_days`; it now scans them, checks gap-entry shape and timeline phrasing, and was re-tested against deliberately broken copies. Entries: KB-FAQ-001, KB-FAQ-003, KB-FAQ-008 and KB-FAQ-011 restate `rates` figures and moved to the `rates` TTL class; KB-ESC-014, KB-ESC-017 and KB-ESC-021 no longer restate rate, fee or limit figures (a 365-day gap entry is the fallback after a 90-day hard expiry); KB-ESC-020 no longer equates two failed clarifications with ESC-003; source refs corrected in KB-REG-002 (A10.3), KB-POL-007 (A9.2) and KB-FAQ-010 (project default).
- Updated requirements traceability (R-20 done) and README status, navigation and Day 7 pointer.

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-25: one multi-entry YAML file per category, IDs `KB-<CAT>-<NNN>`, validated by a script.
- D-26: explicit gap-handling entries for `kb_gap` topics; the only non-A13.1 figures are the brief's own A4.1 examples, labelled illustrative.
- D-27: six TTL classes (90, 90, 180, 180, 120, 365 days) with hard expiry for regulatory and rates and soft expiry for the rest; proposals, since the brief gives no values.
- D-28: "no annual fee Y1" read as year 1 only; later fees remain a gap.
- D-29: `auth_level_required` is a hard pre-retrieval minimum and `audience` separates customer-facing from agent-internal entries; an empty result after the filter triggers a step-up, not "no information".

**Challenges**
- A13.1 is thin (nine products, one line each) and the brief's regulatory text is one line per regulation, so most entries state what is known and list `not_in_catalogue` or `not_in_brief` items rather than fill them. Reaching 55+ without invention relied on policy, escalation, FAQ and troubleshooting entries built from A4, A6 and the taxonomy.
- A first pass of the YAML had unquoted commas inside flow maps (for example "INR 50,000" silently split a key). The validator now flags null-valued or non-string keys; the four affected entries were fixed.
- Some default values in entries come from the project's own taxonomy, not the brief (statement default of the last 30 days, session timeout wording). They are dialogue defaults, not bank facts, and are marked with their source in `source_ref`.

**Open questions**
- TTL values and the 30-day soft-expiry grace are proposals; Risk Committee view needed (Day 8 maintenance workflow will confirm).
- The brief names the Banking Ombudsman Scheme but gives no contact details, time limits or cooling-off length; kept as gaps (KB-ESC-019).
- Hindi and Hinglish wording in four FAQ entries is unreviewed by a native speaker.

**Next (Day 8)**: retrieval pipeline spec (hybrid fusion, re-ranker, query rewriting, confidence, latency, caching) and `diagrams/retrieval-pipeline.mmd`, graceful degradation template, knowledge update workflow with regulatory fast-track and staleness alerts, access-control matrix by auth level, and the Level 3 boss check (5 queries needing 3 or more entries, target confidence above 0.85).

**Day 6-7 audit fixes (applied after review)**
- Day 6: fixed 13 defects (Aadhaar-shaped UPI ref in the CSV and in `config/entities.yaml`, mislabelled intents/tertiary labels, gold entities absent from the text, boss-set runner-up and card wording, stale counts). Then resolved the open items: RED-04 postal-code exception (D-35), pair-tree trigger covers a third candidate between members (D-36), gold entities are text-derived only with a separate context track (D-37), GEN-005 rows corrected, library now 551 rows (D-38), `debited_not_credited` convention (D-39), `kb_gap` tags on all 53 rows of the four gap intents (D-40).
- Day 7: validator holes closed (14 mutation cases now caught), four FAQ TTLs moved to the 90-day `rates` class, figures removed from gap entries, KB-ESC-020 no longer conflates ESC-003, source_ref fixes. Then resolved the open items: detection rule moved from anonymous KB-TRB-007 to agent-internal KB-TRB-011 (D-30), `generic_info_auth` for SEC-003 and CRD-004 (D-30, D-31), KB-PRD-007/008/009 and KB-FAQ-004/006 on `rates` (D-32), SEBI_ROBO_ADVISORY removed from three entries (D-33), KB-REG-008 reworded to the regulation only (D-34), ER diagram gained a gap-for link (parser check passed, not rendered). KB now has 77 entries.
