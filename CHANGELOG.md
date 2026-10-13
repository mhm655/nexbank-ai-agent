# CHANGELOG

One entry per day of the brief's 15-day plan (15). Each entry: date, tasks, decisions with rationale, challenges, open questions, next-day plan. Dates are taken from the commit history; where several days share a date the work was done in consecutive sessions on that date; session times were not recorded.

## Day 1: Setup and analysis

**Date**: 2026-10-03


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
- Q1, Q2, Q10, Q12 (the question numbers are the rows D-01, D-02, D-10 and D-12 of `docs/assumptions-and-decisions.md`) are open: the query is drafted in `docs/coordinator-questions.md` and was not sent.

**Next (Day 2)**
- 12-component architecture diagram, component interface contracts, agent/tool matrix.

## Day 2: Architecture, interfaces, agents

**Date**: 2026-10-04


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

**Date**: 2026-10-04 (the state machine diagram was added in a later commit on 2026-10-06)


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
- Level 1 boss trace needed 12 switches in 20 turns while still exercising safety invariants; achieved with a security pre-emption, an advice-boundary deflection and a human-request trigger. (Amended on Day 15 (D-210): the trace now uses a duplicate-charge dispute and a lost-card block instead of a fraud report, so no P0 is raised and then left waiting; still 20 turns and 12 switches.)

**Open questions**
- The 15 ESC triggers are referenced but defined on Day 12; intent labels in the trace are provisional until Day 4.

**Next (Day 4)**: intent taxonomy (30+ intents), entity catalogue.

## Day 4: Intent taxonomy and entity catalogue

**Date**: 2026-10-07


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
- Q1, Q2, Q10, Q12 still open (query drafted, not sent).

**Next (Day 5)**: disambiguation trees for the six pairs, multi-intent and out-of-scope handling, per-layer thresholds, sentiment and emotion spec.

## Day 5: Disambiguation, multi-intent, out-of-scope, sentiment

**Date**: 2026-10-07


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
- Sentiment accuracy targets in `sentiment.md` are project proposals; the brief gives none.
- CEB view needed on the EMA route in D-18.

**Next (Day 6)**: utterance library (300+ across English, Hindi, Hinglish and secondary languages), language detection and code-switching spec, Level 2 boss set of 10 ambiguous messages in `tests/nlu/`.

**Day 4-5 audit fixes (applied after review)**
- Fixed 9 small defects found by the audit: tool name `send_credential_reset_link`, wrong section pointers, the `inferred` slot state, confirmation expiry wording, ACC-003 then ACC-004 chain, NLU frame to state mapping, a dead-end node in the pair 6 diagram, and boss-trace phases and labels.
- Boss trace: ESC-001 (P0) fired at T5 when the intent resolved to fraud, so the fraud report was never left parked without escalation (A4.2 rule 6; amended on Day 15 (D-210): T4 to T6 are now a duplicate-charge dispute and a lost-card block, and no P0 fires in the trace); T13 now asks the pair 3 question and T14 answers it; T17 carries `loan_type`.
- SEC-002 confirmation raised to explicit; the execution-gate comment now covers `ticket` actions.
- Citation fixes: the 0.15 ambiguity gap now cites the dialogue-management guards (D-06 defines only the 0.70 and 0.40 tiers); taxonomy mapping for the FD-rate turn is `fd_rate_by_tenure`; pair 6 wording now matches the 0.85 execution rule.
- Still open from the audit: clarification budget vs "escalate after 2 failed clarifications", agent/tool matrix gaps, and the references to the external planning file, which sits outside the repo.


## Day 6: Utterance library, language detection, Level 2 boss

**Date**: 2026-10-08


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

**Date**: 2026-10-08


**Tasks completed**
- `docs/knowledge-base/kb-schema.md`: entry schema (brief A2.3 fields plus `audience`, `ttl_class`, `status`, `intents`, `escalation_triggers`, `body_i18n`, gap fields), ER model (`diagrams/kb-er-model.mmd`, parses with the Mermaid parser), three formats with rules, ID convention `KB-<CAT>-<NNN>`, semantic versioning with live updates and immutable history, six TTL classes with hard and soft expiry, regulatory tag vocabulary mapped to the brief, auth-level access control as a pre-retrieval filter, intent links, gap-entry shape.
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

## Day 8: Retrieval pipeline, maintenance workflow, access matrix, Level 3 boss

**Date**: 2026-10-09


**Tasks completed**
- `docs/knowledge-base/retrieval-pipeline.md`: query rewrite (anaphora, safe entity injection, primary and secondary language handling), hard pre-filter inside both searches (epoch, status, effective date, hard and soft expiry, auth rank, evidence and guidance audience lanes), dense top-20 plus BM25 top-20, weighted 0.6/0.4 fusion with intent prior and gap companions, cross-encoder re-rank to top-5 with calibrated confidence and the 0.65 gate, decision table (answer, gap, degrade, ESC-008, step-up, unavailable), fallback ladder, caching, 160-180 ms p95 budget, 16 failure modes, log fields including `kb_entry_ids`, and the retrieval evaluation plan (Recall@5, MRR, nDCG, mean relevance > 0.85, gold-set design with auth, expiry and hallucination traps).
- `diagrams/retrieval-pipeline.mmd`: flowchart of the pipeline and its decisions.
- `docs/knowledge-base/maintenance-workflow.md`: roles and chains by category, lifecycle, authoring, review, compliance approval, staged publish with canary and circuit breaker, rollback, regulatory fast-track for RBI circulars (quarantine and TTL reset), staleness alerts by `ttl_class` with worked dates, versioning, feedback loop from retrieval and supervisors, audit trail, retirement.
- `docs/knowledge-base/access-control-matrix.md`: enforcement points, level by category and audience matrix (64, 10, 1, 2 entries first visible per level), level-assignment rules, the 41-intent by level by entries matrix, 12 step-up scenarios, audience rules, 8 worked examples tied to real IDs.
- `tests/kb/boss-level3.yaml`: 5 queries each needing 3 or more entries (card comparison, information-vs-advice, fraud with an auth trap, regulatory-uncertain, Hinglish multi-gap), with gold IDs, outline and grounding. `tests/kb/README.md` documents the retrieval eval schema and static checks. Checker (scratchpad): PASS; `validate_kb_entries.py`: PASS.
- Updated README (Day 8 of 15), requirements traceability (R-21 done; R-35 and R-36 added), decisions D-41 to D-48.

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-41: weighted fusion 0.6/0.4, RRF as challenger. D-42: calibrated confidence, 0.65 gate, synthesis confidence > 0.85. D-43: regulatory-uncertain includes known-unknown gaps that list ESC-008. D-44: pre-filter semantics and metadata-only step-up probe. D-45: latency, cache, badge not claimed. D-46: maintenance workflow, fast-track, quarantine. D-47: proposed eval gates and level-change rule. D-48: boss pass rule for gap cases.

**Challenges**
- The brief gives a threshold but no definition of retrieval confidence, and a known gap retrieves with high confidence, so confidence alone would not trigger ESC-008. D-43 adds the gap-entry rule.
- Pre-retrieval auth filtering hides the evidence needed to decide a step-up. The metadata-only probe on the low-confidence path solves it without leaking existence or costing happy-path latency.
- The 160-180 ms budget does not support the under-150 ms Retriever badge; it is recorded as a Day 14 measurement question, not claimed.
- Boss queries had to use only figures in the entries; amounts in queries were avoided and a checker confirms every outline number occurs in the gold entries.

**Open questions**
- Risk Committee: TTL classes, 14-day alert, 30-day grace, fast-track time target, and the eval gates (all proposals).
- Native-speaker review of Hindi and Hinglish wording, including the Hinglish graceful-degradation template (Day 13).
- None for the diagram: the Day 8 audit parsed `diagrams/retrieval-pipeline.mmd` and the workflow state diagram with the Mermaid 10.9 parser (OK).

**Day 8 audit fixes**
- `boss-level3.yaml`: KB-BOSS-L3-04 outline cited the eight-element handoff package without KB-ESC-001 in its gold IDs (added, with grounding rows for it and KB-PRD-006); KB-BOSS-L3-02 gained a "not held" line for the NexFD minimum deposit and SIP tax. `tests/kb/README.md`: per-segment scoring rule for multi-intent boss queries.
- `retrieval-pipeline.md`: ESC-008 intent-hook example corrected to PRD-001 and PRD-004 (CMP-003 has no ESC-008 in `config/intents.yaml`); step-up probe counts only customer_facing entries and uses a calibrated score (D-44 updated); the unblock example no longer relies on KB-POL-006 (otp_verified) for an anonymous session; broken `system-architecture` section 3.6 reference fixed. Diagram: the failure node no longer sends a re-ranker failure to `unavailable`.

**Day 8 follow-ups**
- `boss-level3.yaml` KB-BOSS-L3-05 replaced (D-49): Hinglish NexSave, NexFD, tax and tenure-gap query needing 5 entries (was three gap entries). `tests/kb/README.md` updated; checker PASS.
- D-43 spread (D-50): `kb-schema.md` section 8 rule 3, `component-interfaces.md` row 6 (adds `decision`, `lane`, flags, `step_up_hint`), KB-ESC-008 v1.1.0 (effective 2026-10-08, expires 2027-10-08).
- Step-up probe residual signal (D-51): identical wording plus 2 prompts per session cap in `retrieval-pipeline.md` section 5.4; Risk Committee review open.
- Gap-hit condition made explicit in spec and diagram (D-52); section 9 'intent-level floor' reworded; `troubleshooting.yaml` header count 11; R-35 and R-36 moved into numeric order.

**Next (Day 9)**: advice, security and compliance guardrails: information-vs-advice spec, the 8 account-security rules with enforcement points, and the regulatory mapping matrix (tag to guardrail to test), reusing the KB tags and the retrieval-side auth assertions.

## Day 9: Advice, security and compliance guardrails

**Date**: 2026-10-09


**Tasks completed**
- `docs/guardrails/financial-advice.md`: information-versus-advice boundary for the six A4.1 categories (brief wording quoted, cross-checked against KB-POL-001), three-question test, per-category detection signals and allowed information with KB sources, layered enforcement (rule floor, advice classifier, output check), thresholds 0.50 and 0.30 aligned with disambiguation pair 2, 13 safe-response template names (text on Day 13), the ESC-013 offer-then-escalate route and its split from ESC-008, no-elicitation rule (no income, age or portfolio questions), 16 borderline cases, false-positive analysis, reserved test IDs.
- `docs/guardrails/account-security.md`: the 8 A4.2 rules quoted verbatim and numbered R1-R8, component enforcement matrix, auth-level interplay table, and per rule the enforcement point, mechanism, failure behaviour, Day 10 attack surface and reserved test IDs; decision order, immutability and change control, metrics hooks.
- `docs/guardrails/regulatory-mapping.md`: 38 matrix rows (regulation, obligation, guardrail, component, real KB IDs, test placeholders) across the 12 appendix regulations plus KYC/AML and the A13.1 facts, KB tag index (14 of 14 tags mapped), OWASP LLM 2025 cross-reference, coverage statement (0 unmapped obligations), 9 residual dependencies with owners, draft status of the 2025 RBI circular stated.
- `config/guardrails.yaml`: registry of 45 guardrails (ADV 9, SEC 8, REG 20, OUT 5, SYS 3; rule 23, hybrid 20, model 2), each with type, layers, enforcement points, action, ESC, intents, KB IDs, severity, false-positive bound, immutable flag, fail mode and reserved tests (124 IDs).
- `diagrams/guardrail-layers.mmd`: five defence layers with guardrail IDs; Mermaid 10.9 parser: OK (not rendered).
- Checker (scratchpad, not in repo): YAML parses, every GR ID in the docs and diagram exists in the registry and vice versa, linked intent, ESC, KB, RED, D- and G- IDs exist, 8 rules present and verbatim against the brief text, A4.1 wording equals KB-POL-001, KB tag counts, test IDs within reserved ranges, ASCII only. PASS.
- Updated README (Day 9 of 15), requirements traceability (R-22 to R-24 done; R-37 added), decisions D-53 to D-63.

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-53: rule numbering R1-R8 and the ID and test scheme. D-54: output-side advice thresholds and the rule-floor hybrid. D-55: volunteered circumstances are not stored or echoed; ESC-013 is an offer. D-56: session timeout ceiling 5 minutes despite the A12.3 range 3-15. D-57: false-positive bounds by type (proposals). D-58: immutability covers all guardrails; classifiers change only by safety change control. D-59: definition of "facilitate". D-60: authority claims plus a request go to ESC-001. D-61: reading of the regulatory appendix table. D-62: what "zero gaps" means and the G-01 to G-09 dependency list. D-63: A9.2 and fail-closed guardrails registered now.

**Challenges**
- The A4.2 bullets carry no numbers and the A12.3 timeout range (3-15) conflicts with rule 7 (5 minutes); numbering by order and a ceiling of 5 resolve both.
- The A4.1 examples (a 1-year FD rate, an EMI) are illustrations, while the KB treats any other tenure rate as a gap; the document separates "category example" from "figure the agent may state".
- The appendix regulation table is garbled in the PDF text; the reading used is stated (D-61). Cooling-off length, IRDAI thresholds and AML indicators are not in the brief, so they are listed as dependencies instead of being invented.

**Open questions**
- Risk Committee: output-side advice thresholds, per-class false-positive bounds, timeout ceiling, definition of "facilitate", authority-claim routing, joint-account handling (all proposals or assumptions).
- Regulatory Compliance Manager: G-01 (cooling-off length), G-02 (IRDAI thresholds), G-08 (final RBI Responsible AI text).
- OWASP LLM 2025 category names to be verified against the OWASP publication on Day 15.
- Day 9 audit follow-ups: D-64 restates the false-positive target as an end-to-end gate (below 3 percent of benign messages) with per-guardrail bounds as diagnostics lowered to rule 0.10, hybrid 0.15, model 0.30 percent (typical path 10 + 6 + 2 guardrails sums to 2.50 percent, reserve 0.50); `config/guardrails.yaml` fp_target_pct values and parameters and `financial-advice.md` section 10 updated; supersedes the D-57 figures.
- Day 9 audit follow-ups: D-66 adds OWASP LLM04 and LLM08 (partial) to `regulatory-mapping.md` section 4 and moves LLM10 to a gap with a Day 10 dependency (no rate-limit guardrail is registered); section 4 is not part of the 38 M-rows, so matrix counts are unchanged.
- Day 9 audit follow-ups: D-65 records ESC-009 for GR-SEC-R2 and ESC-001 for GR-SEC-R3 as design choices to confirm on Day 12; D-67 clarifies the D-61 "interleaved" wording. Decisions now run D-01 to D-67.

**Next (Day 10)**: adversarial defences for the six A4.4 vectors (`GR-ATK-*`), 55+ guardrail and adversarial tests in the reserved ID ranges with 20 boss scenarios, response safety layer spec, monitoring dashboard with trigger heat map, incident response playbook.

## Day 10: Adversarial defences, response safety layer, monitoring, incident response

**Date**: 2026-10-09


**Tasks completed**
- `docs/guardrails/adversarial-defences.md`: defences for the six A4.4 vectors (Prompt Injection, Jailbreak Attempts, Social Engineering, Data Exfiltration, Denial of Service, Identity Spoofing): canonicalisation, instruction/data separation, leak-tolerant system prompt, rate limiting and complexity scoring, attack-response contract that avoids the A9.2 anti-patterns (D-68 to D-77).
- `config/guardrails.yaml`: GR-ATK-01 to GR-ATK-11 plus GR-OUT-06 (no delivery without a SafetyVerdict) and GR-SYS-04 (kill switch and template-only mode); Output Safety Layer added to GR-REG-16 (D-90). Registry: 58 guardrails (rule 29, hybrid 26, model 3), 190 reserved test IDs.
- `tests/adversarial/`: 62 cases (60 attacks, 2 controls), 27 boss scenarios over all six vectors, 26 multi-turn, 9 Hinglish or Hindi. `tests/guardrails/`: 128 cases. All 190 reserved IDs have a written case. All are specified, not run (D-78, D-79). `tests/README.md` gives schema, ID scheme and coverage.
- `docs/guardrails/output-safety-layer.md`: seven checks C1 to C7 mapped to registry IDs, 300 ms split into stages, deterministic repairs, fail-closed ladder respecting D-19, pair 2 and pair 6 (D-80 to D-82).
- `docs/guardrails/monitoring-dashboard.md`: metrics DM-01 to DM-16, trigger heat maps, false-positive budget panel, near-miss definition, sampling plan, circuit-breaker spec (D-85, D-88, D-89).
- `docs/guardrails/incident-response-playbook.md`: SEV0 to SEV3 aligned to P0-P2, eight tighten-only containment levers, seven runbooks; only A10.3 duties cited, other notification duties listed as dependencies IR-D1 to IR-D5 (D-83, D-84, D-86, D-87).
- Regulatory mapping section 4 rewritten: LLM10 closed at the application layer by GR-ATK-08 and GR-ATK-09, LLM03 stated as a gap by scope.

**Decisions** (D-68 to D-90, mostly proposals): ATK registry design, session score and safe mode, ESC-001 for authority claims (D-72), DoS limits of 20 messages a minute, 4,000 characters, 250 reply words and 3 tool calls a turn (proposals), end-to-end false-positive budget (D-76: always-on ATK guardrails draw 0.46 so the typical path is 2.96% against the 3% gate; GR-ATK-11 stays in shadow mode), registration of GR-OUT-06 and GR-SYS-04 (D-90).

**Challenges**
- Two agents wrote the adversarial and operational docs in parallel; the audit aligned the registry, wording and false-positive table.
- The reserve is thin: 0.04 points remain, so any new always-on guardrail needs another bound lowered.

**Audit fixes**: registered the two IDs that had only been proposed, aligned output-safety, dashboard and playbook wording with the registry, fixed one test oracle (GR-ATK-07-03), added a pointer to the post-Day-10 totals in `financial-advice.md` section 10.

**Open questions**
- Risk Committee: false-positive targets of 0.00 for GR-OUT-06 and GR-SYS-04; thin reserve; legal hold against the 30-day deletion duty (D-87).
- ESC targets for jailbreak and spoofing (D-72, D-65) to confirm on Day 12; ESC-003, -004, -007 and -011 have no test case yet (Day 11).
- OWASP LLM 2025 names and Hindi/Hinglish wording remain unverified (Day 13, Day 15). One test uses a real pin code (GR-SEC-R5-06); a placeholder would be cleaner.
- Day 10 review follow-ups:
  - Second-pass review fixes: 5 cases now expect ESC-001; ten banned-phrase checks and three required-phrase checks tightened; GR-REG-16 gains the L4 tag; M-32 row added; template-only timing wording aligned.
  - D-91: D-72 clarified; the data target means another person's data, credentials or secrets, system prompt or admin access, an override or a transaction. A verified customer's own full-card request is masked, counts toward the GR-ATK-04 counter, never escalates alone (GR-ATK-04-02, GR-ATK-07-02 carry `expected_escalation: []`).
  - D-92: GR-ATK-10 added to the GR-ATK-04 flagged-turn sources; a failed identity challenge escalates via D-16, not the counter.
  - D-93: layer-tag rule (L4 iff `output_safety_layer` is an enforcement point; model type carries L2); L4 added to GR-ADV-04, GR-ADV-05, GR-REG-17, GR-SYS-01, GR-SYS-04, output_safety_layer added to GR-SEC-R5, L4 dropped from GR-REG-15 and GR-ATK-02 (the latter gets L2), L2 added to GR-OUT-04. Counts unchanged (58 guardrails, 190 IDs).
  - D-94: GR-ATK-05-07 card block offered after the fast OTP step (D-16); deviation from brief Case Study 2 flagged for Risk Committee/CEB review.

**Next (Day 11)**: continuous learning pipeline, A/B testing framework, safety-preserving update protocol, 200+ case safety suite index, Level 5 boss.

## Day 11: Continuous learning pipeline, A/B testing, safety suite, Level 5 boss

**Date**: 2026-10-11


**Tasks completed**
- `docs/learning-pipeline/overview.md`: the loop mapped to A8.4 (DETECT to DOCUMENT) with the A5.4 protocol inside DEPLOY; five update classes in order of preference (U1 KB, U2 prompt layers 3-5, U3 A12.3 parameters, U4 NLU and retrieval models, U5 policy and generation model) and six excluded artefact groups (layers 0-2, rule layer, all 58 guardrails, registry parameters, ESC triggers, the suite and breaker); cadence (safety immediately, quality daily, style weekly); update strategy per class with incremental versus full retraining; roles; pipeline health metrics.
- `docs/learning-pipeline/supervisor-corrections.md`: four brief sampling streams plus the Day 10 guardrail stream, review-tool wireframe and record schema, severities S0 to S4 with component and error type, propagation timeline, Cohen's kappa with a worked 5x5 example (kappa 0.648; S1 against the rest 0.789), workload model from the brief's 18,000 interactions and 50 reviews per day (576 conversation reviews, 15 supervisors on the floor, 19 on the roster).
- `docs/learning-pipeline/csat-signals.md`: check-in rules at natural breakpoints, post-chat CSAT 1-5 with comment, 11 implicit signals, two-stage silent-dissatisfaction detector with allowed and forbidden uses, post-stratification weighting with a worked example (raw 4.20 against weighted 4.01), four attribution levels.
- `docs/learning-pipeline/outcome-tracking.md`: the five A5.3 classes with decision rules and the mapping to the four A10.1 `resolution_status` values, verification follow-ups, repeat-contact matching at 7, 14 and 30 days, FCR and false-resolution definitions, retention and adoption analysis with its limits.
- `docs/learning-pipeline/data-pipeline.md`: collection from the A10 schemas, second-pass redaction with RED-01 to RED-07, consent purposes, feature registry and exclusions, dataset manifest and versioning, quality gates QG-01 to QG-08, right-to-deletion propagation into datasets, backups and models inside 30 days.
- `docs/learning-pipeline/ab-testing.md`: customer-level randomisation, the A/B test as the 25% stage of the 1/5/25/100 ladder with an equal concurrent control, three-tier metric hierarchy (guardrail constraints, CSAT and FCR primaries, secondaries), pre-registration template, power analysis with formulas and arithmetic (4,153 ratings per arm for CSAT, 10,804 conversations per arm for FCR), two looks per primary with Lan-DeMets O'Brien-Fleming spending (boundaries 3.1698 and 2.2510), repeated intervals, stopping rules S-1 to S-7, novelty checks, approval workflow for each A12.3 parameter.
- `docs/learning-pipeline/safety-invariants.md`: immutable layer contents IL-1 to IL-6 and mechanisms M1 to M8, invariants INV-01 to INV-12 mapped to suite cases, suite composition, pass rule and governance, gates G0 to G9 with a gate-by-class matrix, canary ladder with what each stage can and cannot detect, rollback mechanism per class, post-deployment monitoring, safety change control. The circuit breaker is referenced from `monitoring-dashboard.md` section 8 and not redefined.
- `docs/learning-pipeline/boss-level5.md`: Level 5 boss as a simulated worked example (clearly labelled; assumed, simulated and computed figures marked): a layer 3 wording candidate traced through G0 to G9; simulated weighted CSAT lift +0.347 (repeated interval +0.307 to +0.387), FCR +1.8 points, no Tier 0 constraint breached; the simulation script and its output are in the appendix.
- `diagrams/learning-loop.mmd`: loop, gates, breaker and immutable layer; Mermaid 10.9.1 parser: OK (not rendered).
- `tests/safety-suite/`: fixed safety regression suite of 291 cases = the 190 Day 10 cases by reference plus 101 new `SS-` cases (PII masking 10, auth gating 27, escalation triggers 19, hallucination traps 14, commitment traps 9, learning-pipeline invariants 22). Generated `manifest.yaml` with a SHA-256 per case, `README.md`, and `validate_manifest.py`. Every ESC-001 to ESC-015 now has a positive case (ESC-003, -004, -007, -011 were missing). All cases are specified, not run (D-79).

**Decisions** (D-95 to D-114; proposals unless the brief fixes the value): update classes and exclusions (D-95); sampling rates and workload (D-96); taxonomy codes and what "immediate" means (D-97); kappa thresholds (D-98); CSAT survey rules and a 15% response-rate planning assumption (D-99); silent-dissatisfaction detector and its permitted uses (D-100); non-response weighting (D-101); attribution levels, with only experiments justifying a release (D-102); outcome class rules and the 7-day FCR window (D-103); consent purposes and deletion propagation, models treated as derived data (D-104); dataset manifest and quality gates (D-105); cadence and full retraining every 21 days by default (D-106); randomisation unit and split (D-107); metric hierarchy and planning values (D-108); sequential design (D-109); margins, 14-day minimum, novelty and holdback (D-110); experiment governance per A12.3 owner (D-111); suite composition, 100% pass with repetition, add-only governance (D-112); gates G0 to G9 and canary floors (D-113); the boss is a labelled simulation (D-114).

**Challenges**
- The brief gives no statistical parameters. Every one (significance split, power, minimum effects, rating spread 1.3, response rate 15%, design effects 1.10 and 1.17) is a labelled planning value with a sensitivity table; all arithmetic was recomputed by script.
- At 18,000 interactions a day the sample size is reached in about 6 days, so the 14-day minimum exposure (two weekly cycles) is the binding rule, not power. Small effects (0.05 CSAT points) are not detectable in 14 days and the document says so.
- A canary cannot prove the absence of rare harm: zero events in 180 conversations bounds the rate only below 1.65%. The suite, the red-team run and the rule layer carry the safety argument; the canary limits blast radius.
- The 30-day deletion duty covers "derived data including model training data". Read strictly, a warm-started model still carries deleted rows, so the default became full retraining on a purged dataset every 21 days.
- FCR needs 7 days to mature, so the two primaries have different look calendars (CSAT day 7 and 14; FCR day 14 and 21).
- Three escalation triggers (ESC-005, ESC-007, ESC-011) are owned by no registered guardrail, so some suite cases carry an empty `expected_guardrails` list and name the Escalation Router rule instead.

**Open questions**
- Risk Committee and Data Protection lead: whether trained model weights are "derived data" under A10.3 (D-104); consent notice and legal basis for training use (G-05).
- Risk Committee: suite governance roles (D-112); the 3-repetition pass rule; dwell times and sample floors of the canary stages (D-113).
- CEB and CX Team: the 15% response-rate assumption, CSAT survey rules, non-responder follow-up (D-99, D-101).
- Circuit-breaker condition 3 (false-positive rate) cannot be evaluated on canary-sized labelled samples; `safety-invariants.md` section 7 states how it is read by stage and leaves the wording of `monitoring-dashboard.md` to its owner.
- Crisis handling (ESC-011) has no entry in the guardrail registry; a registry entry would touch the thin false-positive reserve (D-76).
- All statistical planning values are to be replaced by observed values after the first A/A test.
- Hinglish wording of the 5 new Hinglish cases needs native review with the Day 13 templates.

**Next (Day 12)**: escalation triggers, routing, handoff package, queue management, metrics framework and dashboards; reconcile FCR, containment and escalation-rate definitions between `docs/metrics/` and `docs/learning-pipeline/outcome-tracking.md`; decide whether `tests/escalation/` cases join the fixed suite manifest.

**Day 11 audit fixes** (independent audit, 26 findings; decisions D-156 to D-160): (1) deletion deadline: the 21-day retrain cycle did not meet the 30-day duty once gates G6 to G8 are counted (day 41 to 48), so a deletion-only rebuild path was added (same code and hyper-parameters, data minus tombstones; G1, G2 equivalence, G3, 1% and 5% canary, no A/B; 14-day cycle, old model retired by day 20) in `overview.md`, `data-pipeline.md` and `safety-invariants.md` (D-157); (2) over-strict oracles: 20 SS cases whose substring oracles failed correct replies ("loan" matching "alone", "will be approved" matching "cannot promise it will be approved") now use assertive, negation-aware patterns, checked against 37 sample replies; (3) `validate_manifest.py` hardened: new `manifest.lock.yaml` (floor, SHA, kind, expected_action, change log), `--rebuild` refuses a changed case without `--accept-change <ID> --decision <ref>`, refuses when the lock is absent unless `--init`, non-control SS cases need a non-empty oracle, PAN- and credential-shaped literals are rejected; the reviewer's mutations were re-run on scratch copies and are all caught; the docs now say plainly that a hash only detects change relative to a copy the changer cannot write (D-156); (4) Level 5 boss: states why a prompt-layer change is offered as the "model update" and what differs for a U4 or U5 candidate, adds the post-update suite run (assumed input), decision moved to day 21 (D-160); (5) experiment analysis: intention to treat with no post-assignment exclusions, SRM on randomised units, a 3-day CSAT maturity rule with a late-rating sensitivity analysis, a harm test for slices in place of an unattainable per-slice non-inferiority proof, an early one-sided harm rule (z at or below -2.0), arms frozen from day 14 to the day-21 decision, the Lan-DeMets convention named (D-158); (6) learning-invariant cases: `expected_guardrails` now holds only the control that rejects, protected guardrails moved to `covers`; SS-AUTH-05 no longer expects GR-SEC-R6; SS-HAL-14 escalates to ESC-008; SS-ESC-16 gains a tipping-off oracle; boundary control SS-ESC-20 added (message 15 does not fire ESC-010); (7) smaller items: workload model includes canary doubling (18 on the floor, 23 on the roster during an A/B stage), canary bounds quoted at the sample floors, holdback no longer "optional", pre-registration frozen at G5 in text and diagram, containment stated as 1 minus the escalation rate, closing confirmation exempt from the check-in limits, a precedence table for conflicting feedback sources (D-159). Suite: 349 cases (102 SS), 34 existing cases changed under D-156, all specified, not run.

## Day 12: Escalation triggers, routing and handoff, queues, KPI framework, dashboards

**Date**: 2026-10-11


**Tasks completed**
- `config/escalation_rules.yaml`: machine-readable rules for ESC-001 to ESC-015 (brief wording quoted with page, priority, queue, SLA, `fire_when` expression over 35 defined signals, 28 sub-rules, precedence rank, cancellable flag, handoff mode, linked intents, guardrails, KB entries and tests), 7 additions XTR-01 to XTR-07 marked `origin: addition`, the 15 queues with hours, overflow chains and after-hours rules, the 8-element handoff package. Priorities, queues and SLAs equal KB-ESC-010 and the PDF (A6 pp.16-17): no mismatch found.
- `docs/escalation/triggers.md`: the 15 triggers as the brief defines them, a specification block per trigger (detection signal, owning component, state fields, links, what must not fire, tests), precedence and conflict resolution (P0 always wins; SLA, then rank; one owner, nothing dropped; parallel compliance cases; upgrade never downgrade; suppression), the additions, what is not an escalation, the Day 12 confirmations of D-65 and D-72, signals and proposed state fields.
- `docs/escalation/routing-and-handoff.md`: SLA clock and the reading of IMMEDIATE, routing steps and decision table (trigger by segment, language and hours), the 8-element package as a field schema with envelope and a synthetic example, warm-handoff script with variants and an A9.2 anti-pattern check, behaviour while the customer waits, failed-handoff behaviour, de-escalation moves and the cancellation rules (never for P0), 13 template names for Day 13.
- `docs/escalation/queue-management.md`: queue table, overflow, after-hours routing, SLA-breach handling, resolution horizon, capacity model (Erlang C per queue, two scenarios, computed by script), priority rebalancing, escalation quality metrics EQ-01 to EQ-12 with labels mapped to the Day 11 correction record, queue alerts.
- `diagrams/escalation-routing.mmd`: trigger evaluation, precedence and routing. Mermaid 10.9.1 parser: OK (not rendered).
- `tests/escalation/`: 63 cases (39 for the brief's triggers: 19 fire, 20 near-miss; 14 for the additions; 10 Level 6 boss cases with owner, secondary triggers, priority, queue and reasoning), README, and `validate_escalation.py`. All specified, not run.
- `docs/metrics/kpi-framework.md`: the 20 A8 metrics plus the A1.4 and A2.3 figures, classified leading, lagging and operational, each with the brief's definition, formula, numerator and denominator, log source, brief target and frequency, owner, alert thresholds and anti-gaming notes; 9 further measures the brief names; guardrail metrics DM-01 to DM-16 and Day 11 definitions linked, not redefined; counter-metric pairs; A10.3 reporting map.
- `docs/metrics/improvement-cycle.md`: Detect, Diagnose, Design, Deploy, Validate, Document with artefacts, roles, timings, the 15-minute budget, a symptom-to-component table, an impact, effort and risk score, the improvement record, and two worked examples labelled illustrative. Deploy and Validate point at the Day 11 gates and ladder.
- `docs/metrics/dashboards.md`: ASCII wireframes (layout only, no values) and panel specifications for the Real-Time, Daily and Weekly dashboards; all 16 A8.5 items mapped to a panel; audiences, refresh, drill-down, access rules (A10.3), alert handling.
- Validator `python tests/escalation/validate_escalation.py`: PASS (15 triggers, 7 additions, 15 queues, 63 cases, 9 documents checked).
- Fixed safety suite: grew from 291 to 348 cases when the 57 Day 12 escalation cases joined by reference, and is 355 after the audit fixes (6 escalation cases added; `validate_manifest.py` reports 355).

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-115: D-65 and D-72 targets confirmed or corrected. D-116: precedence. D-117: human requests (XTR-01, ESC-006 as backstop). D-118: SLA clock and IMMEDIATE. D-119: turn unit and "without resolution". D-120: proposed state additions. D-121: routing factors. D-122: hours and after-hours. D-123: failed handoff. D-124: behaviour while waiting. D-125: de-escalation and cancellation. D-126: ESC-015 scope and the reading of 5L. D-127: overflow and rebalancing. D-128: breach handling, attainment targets, resolution horizon. D-129: additions XTR-01 to XTR-07. D-130: capacity assumptions. D-131: escalation quality metrics. D-132: KPI formulas. D-133: improvement cycle and dashboards. D-134: escalation test scheme.

**Challenges**
- A6 is only the table: detection, precedence, cancellation, hours, overflow, the SLA clock and every metric formula are silent in the brief, so most of the day is labelled proposals.
- Three earlier files disagreed on when a human request is honoured (first, second or third request); XTR-01 reconciles them without changing ESC-006.
- Case Study 5 meets the ESC-004 condition at turn 3 yet shows no handoff; it is read as the brief's evidence for de-escalation.
- The capacity model shows that meeting the 30 percent escalation ceiling does not by itself deliver the 60 percent staffing reduction: under the stated assumptions the design mix (20.2 percent escalation) needs about 258 FTE by workload and 354 by seat cover against 180. These are model outputs on judgement inputs, not measurements.
- Day 11 was written in parallel; containment, FCR, CSAT weighting, retention and the review streams are now linked to its definitions instead of restated.

**Open questions**
- Risk Committee: ESC-015 scope (account-specific requests versus every contact); precedence ranks; P0 cost of routing three failed OTP entries to ESC-009; whether a retracted legal threat may be closed; attainment targets.
- CEB: honouring the first explicit human request (lowers containment); whether containment should mean "no escalation" (brief, used) or "resolved by AI"; funnel definitions; NPS and CES survey design.
- AML Compliance: indicator list for ESC-012 (G-03). Product: meaning of "5L" and of a "turn".
- The `escalation` state object and two correction-record sub-reasons are proposed, not yet in the schema or the Day 11 record.
- Wealth Advisory: a 30-minute consultation behind a 10-minute live SLA is the largest P1 workload.

**Next (Day 13)**: 6-layer system prompt, `config/parameters.yaml` (A12.3), 15+ templates including the TPL-ESC set, conversation design patterns (R-29).


**Day 12 audit fixes** (25 findings: all HIGH and MEDIUM applied, all LOW applied; none rejected)
- Containment now follows the brief's glossary (p.68, "fully resolved by AI without human intervention"): KPI-G4 is `resolved_ai` with no escalation record over all conversations; "non-escalated share" is the named secondary. The escalation ceiling and the containment target are two constraints, not one. `kpi-framework.md` section 1.1 and KPI-G4 rows, `queue-management.md` capacity labels and 6.7, `outcome-tracking.md` 4.3 and `ab-testing.md` 4.1 changed (D-162).
- After-hours routing is stated as a deviation from A6 needing Risk Committee sign-off; EQ-07 is reported in-hours and all-hours; after-hours ESC-008, ESC-013 and ESC-015 count as SLA misses and only the target-queue pickup counts for ESC-002/004/005/007; an on-call rota is proposed as the SLA-compliant alternative (D-163).
- ESC-015 is literal: record and parallel due-diligence case on every contact by an identified, flagged customer (sub-rule a, silent case); live discreet handoff only when the request is account-specific (sub-rule b). ESC-T-015-02 is now a fire case (D-164, amends D-126).
- ESC-004 route b waives only the confidence gate: it still needs 2 consecutive raw scores strictly below the threshold (D-165). Precedence rule 6: after a change of owner the deadline is the earlier of the two and never moves later (D-166). ESC-001.c gains the coercion cue and sub-rule a matches a SEC-001 alternative in a multi-intent turn; `dispute_open` covers a parked TXN-002 topic with a validated amount; in a medical emergency with a banking blocker the crisis handler has a card or payments colleague joined (D-167).
- Capacity model recomputed by script: night spill limited to the four queues with a generalist intake (78 a day, not 133); seat-cover FTE 351.0 (was 353.5) and 466.0 (was 468.5); workload FTE unchanged (257.9, 382.8); fraud category at 100 percent restated as an upper-bound assumption with a 60 percent sensitivity (18.9 percent escalation, 239 FTE by workload); four unstated assumptions added to table 6.2 (D-168).
- Rules: Crisis Response overflow now starts with the two P0 queues; AML cases never shown to another queue; XTR-06 cannot raise ESC-010 at or below 15 turns; XTR-04 counter rule stated; ESC-006 reported as "ESC-006 plus relabelled XTR-01" (D-169). Diagram dead end fixed (KEEP to WAIT); Mermaid 10.9.1 parser: OK.
- Dashboards: weekly scorecard gains KPI-L1, L4, L7 rows; sentiment-slope target shown as positive or stable. `kpi-framework.md` gains section 4.3 "Customer satisfaction framework" linking to `csat-signals.md`.
- Tests: 63 escalation cases (was 57): 6 new boundary and near-miss cases (ESC-T-003-03, ESC-T-010-03, XTR-T-04-02 to XTR-T-07-02); boss oracles 01, 02, 05, 09 made derivable from the rules; short `must_not_contain` strings replaced by word-boundary patterns. GR-SEC-R2-02 no longer expects GR-SEC-R6 (ACC-005 is not in its scope). Safety-suite manifest rebuilt: 355 cases, 6 added, 14 changes accepted under D-161.
- Validator: checks 8 to 10 added (A6 constants and comparison operators, document tables against A6 and A8 transcriptions, oracles recomputed from fixtures, PAN and phone patterns, P0 overflow floor). All 10 reviewer mutations and 6 further ones are now caught on a scratch copy (16 of 16). Escalation, safety-suite and KB validators pass. All cases specified, not run (D-170).

## Day 13: Six-layer system prompt, governed parameters, template library, conversation design

**Date**: 2026-10-12


**Tasks completed**
- `config/system-prompt/`: one file per A12.1 layer (Identity, Safety, Regulatory, Dialogue, Knowledge, Operational) with the brief's name, purpose, content and update frequency, a metadata header (version, owner, mutability, change process, approval chain, author, last reviewed, deployment date, model version, token budget), the prompt text and 84 testable assertions (`PA-L<layer>-<nn>`) each mapped to guardrail IDs and to existing test cases. Layers 0 to 2 are immutable to the learning pipeline. Every boundary has a SHOULD and a MUST NOT in the brief's six layers taken together (not for S11, K2, D4, D9, K4 individually; see Day 13 audit fixes). The text discloses AI identity, enforces the information-versus-advice boundary and the eight A4.2 rules, separates instructions from data with a per-turn boundary code, is leak-tolerant (no secret, no threshold, no figure, no tool name; states what to do when asked for it) and contains no digit outside section labels. Layer 3 has eight conditionally activated blocks (A12.2). Layer 5 is a fixed frame plus typed notice slots that cannot carry an instruction.
- `config/system-prompt/README.md` and `manifest.yaml`: assembly order, precedence, ownership, conditional activation, token budget, versioning and hash scheme, and the `prompt_version` string logged per turn (current draft `sp-1.0.0+518d5a1e.n000000`).
- `config/parameters.yaml`: the 8 A12.3 parameters exactly as the brief lists them (default, range, owner, change process) with an effective range where a decision narrows it (D-56), 98 project thresholds collected by reference (value, status, decision, home file, whether the learning pipeline may propose a change) and 14 families held by reference only. 46 values are mirrored from `config/intents.yaml`, `config/guardrails.yaml` and `config/escalation_rules.yaml` and compared by the validator. No existing value was changed.
- `config/templates/`: 63 templates with 131 variants in 7 files (GEN 9, AUTH 4, SEC 1, ACC 1, TXN 2, ACT 4, CMP 2, KB 2, SRV 3, SYS 3, ADV 13, ATK 7, ESC 12), each with trigger, generation mode (57 template, 5 hybrid, 1 llm-guided), slots with source and lock, English, Hindi and Hinglish text, safety annotations, A9 pattern and anti-pattern codes and linked tests. All 32 names promised on Days 9, 10 and 12 are written. `labels.yaml` holds plain-language queue and intent labels. `README.md` is the index and schema.
- `docs/architecture/conversation-design.md`: the 5 mandatory patterns and 8 anti-patterns quoted from A9 with penalties, the enforcement of each at four places (prompt layer, template, platform rule, output check), the brand tone guide with do and don't examples, and the template by pattern by anti-pattern matrix.
- `tests/templates/validate_templates.py` and `README.md`: 17 template checks, 6 parameter checks, 7 prompt checks and hygiene. Result: PASS (0 errors). 11 seeded defects were each detected (only those 11 were tried; see Day 13 audit fixes).

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-136: template ID scheme, schema and change control. D-137: assembly order, precedence, owners, conditional activation, citation form. D-138: versioning, hashes, `prompt_version`. D-139: token budget. D-140: layer 5 typed notice slots. D-141: per-turn boundary code and tracer. D-142: structure of the parameter file and the learning flag. D-143: effective ranges for `max_conversation_turns` and `guardrail_strictness_level`. D-144: generation modes. D-145: languages, review gate, secondary languages. D-146: crisis wording without helpline numbers. D-147: variant rotation. D-148: wording rules and the lint. D-149: survey wording. D-150: A9 names and three added controls. D-151: free-slot constraints. D-152: greeting and disclosure. D-153: deviations from the case studies. D-154: correction and static status templates. D-155: assertion scheme.

**Challenges**
- Earlier days had named 32 templates descriptively, so a numeric `TPL-<FAMILY>-<NN>` scheme would have broken published references; descriptive IDs were kept for all 63.
- The overlap scan of GR-ATK-06 blocks a reply that repeats 8 consecutive words of layers 0 to 2, so no template sentence may be quoted in a prompt; the validator checks this in both directions.
- "A request, not a guarantee" (KB-POL-007) conflicts with a blanket ban on guarantee wording; it is rendered as "a request and may change".
- Several case-study replies cannot be templates as written: the OTP typed in chat (Case Study 1), the free 30-minute consultation (Case Study 3), "credited within 24 hours" (Case Study 5).
- The brief names an owner for layer 1 only and gives no token budget, hash scheme or notice format; these are proposals.
- Queue names had no customer-facing form; `labels.yaml` adds one without editing the rules file.

**Open questions**
- Launch blocker: no Hindi or Hinglish text is native-reviewed; no secondary-language template text exists; KB facts and gap statements are English only.
- `TPL-ESC-CRISIS` needs review by the Crisis Response team and a clinical adviser, and has no helpline number because the brief and KB hold none.
- Risk Committee: owners of layers 0, 2, 3, 4; effective floor of 15 for `max_conversation_turns`; MEDIUM strictness untested; which templates change under safety change control. No committee has reviewed any layer; layer 2 has had no legal review.
- CEB: the voice, the assistant's name and grammatical gender in Hindi, CES and NPS sampling.
- Learning pipeline: whether non-A12.3 thresholds marked `may_propose` are update class U3.
- Seven prompt assertions have no dedicated test case; five label tables are not written; token counts are word estimates.

**Next (Day 14)**: 20+ annotated simulations (template IDs, pattern codes, anti-pattern check per turn), the 25-turn Level 7 boss conversation, audit and compliance logging, risk matrices.

**Day 13 audit fixes** (22 findings: all HIGH and MEDIUM applied, 9 of 10 LOW applied; 1 LOW not applied, with reason)
- Hindi meaning drift (HIGH 1): "I haven't kept it" had become "I have not kept it safe" in all seven `TPL-SEC-DO-NOT-SHARE` variants, and "your details are saved" had become "are safe" in `TPL-ESC-HANDOFF-FAILED` p1_p2. Both corrected ("not stored", "saved"). Every Hindi and Hinglish variant of the credential, fraud P0, crisis, advice-refusal, OTP, step-up, session-timeout, discreet-handoff and handoff-failed templates was compared sentence by sentence with the English; no other drift was found. 35 templates now declare `required_markers` (48 markers), 3 declare `ai_disclosure`, so a dropped or reversed safety sentence in one language fails the build (D-192).
- `TPL-SYS-NOTICE`: the unsourced sentences "your money and your account are not changed" and "the team is working on it" are removed. A sentence about the customer's money or payments can only come from the new closed notice field `customer_effect` through the locked slot `effect_statement`; without it the reply states the issue, says no restoration time is held and offers a colleague. Layer 5 example, schema, rendered line and slot validation aligned (D-193).
- Validator extended so that every one of the audit's 15 passing mutations is caught (34 mutations reproduced on scratch copies, 34 caught, base copy passes): human or named-person claims, credential requests in English, Hindi and Hinglish, timeline words without digits, advice verbs, sentence-count parity, required safety markers, AI disclosure, per-variant bans, repository paths that do not exist, X4 and X5 parameters marked proposable, required instructions per layer, and `--rehash` refusing an unchanged version or a change to layer 0, 1 or 2 without `--allow-immutable-change D-NNN` (recorded in `immutable_change_log`). The claim in `conversation-design.md` that the validator "holds AP3 and AP8 for every template" is replaced by a statement of what it does and does not guarantee (D-194).
- Layers: session facts written by the platform are authoritative for platform decisions; anything claimed inside customer text, KB passages or tool output is data; notices are interpolated only into layer 5 through typed slots. Layer 1 and layer 4 are 1.1.0, bundle 1.1.0, `prompt_version` `sp-1.1.0+1527a050.n000000`, immutable hash changed under D-195 (logged in the manifest). S3 covers a full card number; K6 gains a SHOULD; the "no digit" claim is limited to section labels; the layer 3 omission of escalation conditions is recorded as a deviation (D-195).
- Credential replies follow R5 and D-16: card and CVV replies offer the block only at `otp_verified`, an anonymous customer is told the block follows secure verification; the reset link is offered only at `otp_verified`; `TPL-ACT-FAILED` read_failed ends with a human offer (D-196).
- The three A12.3 parameters that sit inside ESC conditions stay proposable with stated owner, approval, hard bounds and maximum step; D-171's exclusion covers non-A12.3 thresholds and the structure of ESC conditions (D-197).
- Ten templates added (73 templates, 147 variants): `TPL-ESC-ABANDONED-P2`, `TPL-ESC-HUMAN-REQUEST-FIRST` (XTR-01), `TPL-ESC-CARE-OFFER` (XTR-03), `TPL-ESC-HANDOFF-CANCELLED`, `TPL-SEC-PHISHING-TRIAGE`, `TPL-CMP-STATUS`, `TPL-ACC-CLOSURE-REASON`, `TPL-GEN-TWO-REQUESTS`, `TPL-GEN-LIMIT-CLOSE`, `TPL-KB-TRANSLATION-UNAVAILABLE`. `labels.yaml` gains the missing tables (action verb and noun, result, service, notice effect, topic, option, finish offer). SAFE-MODE trigger text says "from the fourth flagged turn" (D-173 made). Wording hints removed from greeting, redirect, carry-over, static status and safe-mode text; detail offers added to the tax, forex and tenure-gap replies; wrong file references corrected (D-198).
- Tests: twelve cases PA-T-01 to PA-T-12 (`tests/templates/prompt-assertions.yaml`) replace the mappings that did not test their assertion (PA-L3-02, PA-L3-03, PA-L1-11, PA-L3-09, PA-L2-10 data-use half) and give a dedicated case to PA-L0-07, PA-L3-08 and PA-L5-03 to PA-L5-07. Specified, not run, not yet safety-suite members.
- Known limitation, open launch blocker: Hindi and Hinglish replies that contain locked KB slots render the English KB text verbatim and mix languages until the KB entries carry reviewed `body_i18n` (D-199).
- Corrections to earlier claims: "11 seeded defects detected" was true only of the 11 tried; 15 further defects passed and are now caught. "Every boundary has a SHOULD and a MUST NOT" holds for the brief's six layers in the aggregate but not for S11, K2, D4, D9, K4 and K6 individually (K6 now has a SHOULD; the claim should be softened). "No layer contains a digit" means no digit outside section labels.
- Not applied: finding 22 (a9 pattern claims by surveys, OTP-REQUEST and GEN-CHECKIN): the schema requires a non-empty pattern list, so removing a vacuous claim needs a schema decision (see (d)).

## Day 14: Simulations, audit logging, risk

**Date**: 2026-10-12


**Tasks completed**
- `simulations/conv-07` to `conv-30`: 24 new annotated conversations, with conv-01 to conv-06 (the brief's six case studies re-run, kept as they were) 30 in all, 291 messages, 51 of the 63 templates used. Format is that of conv-06 (header with 21 fields, per-turn NLU / sentiment / guardrails / KB and tools / action / generation / state rows, decision points, closing, 8-element handoff package where a handoff occurred, self-audit of the 5 patterns and 8 anti-patterns).
- Coverage: 30 of the 41 intents and all 7 families; all 6 personas (Meera is new); all 6 adversarial vectors (denial of service in conv-13 and identity spoofing in conv-14 are new); 14 of the 15 ESC triggers fired (ESC-010 only appears as a condition that is not reached) and XTR-01, 02, 03, 05, 07 fired and XTR-06 evaluated; P0, P1 and P2; all of R1 to R8; the information-versus-advice boundary in all six A4.1 categories (investment conv-03, loan products conv-08, interest rates conv-10 in Hindi, forex and tax planning conv-16, insurance conv-30); Hindi in Devanagari (conv-10, conv-29), 5 Hinglish conversations, Gujarati with the secondary-language fallback ladder (conv-29); sentiment recovery without escalation (conv-24), non-escalation near-misses (conv-15, 22, 24, 30), multi-intent turns (conv-12, 14, 16), topic switch and return (conv-12, 30), gap and degrade responses (conv-07, 08, 16, 25, 30), tool failure (conv-28), step-up (conv-11, 20, 21), session timeout (conv-11), XTR-01 and the ESC-006 backstop (conv-27), crisis (conv-17), PEP (conv-18), structuring (conv-19).
- `simulations/conv-30-level-7-integration-journey.md`: the Level 7 boss, exactly 25 messages, 5 intents (ACC-001, TXN-003, PRD-005 insurance, CRD-005, CRD-004), authentication, the advice-boundary guardrail, a drop to -0.85 and recovery to -0.10, ESC-004 fired at T18 and cancelled by recovery at T22 after the de-escalation check, one Hinglish message without a language switch, XTR-06 evaluated at the ceiling, full state on every turn.
- `simulations/INDEX.md`: table of all conversations, totals, what conv-01 to 06 already covered against what conv-07 onward adds, 11 coverage matrices, intent-by-conversation table, required scenarios by conversation, and a gap list.
- `simulations/pattern-audit.md`: pattern and anti-pattern checklist with turn references for all 30 conversations, and the AUTO-FAIL sweep of all 140 figures in AI turns with their sources (0 without a source).
- `tests/simulations/validate_simulations.py` and `README.md`: 14 groups of checks (structure, state shape, identifiers, header consistency, characters, sensitive digits, AI-turn wording, verbatim template text, INDEX, figure sweep, coverage floor, Level 7). Result: PASS. 9 seeded defects were each detected on scratch copies.
- `docs/compliance/audit-logging.md`: the brief's A10.1 conversation schema (11 fields, retention 7 years, `csat_score` 3 years) and A10.2 turn schema (14 fields) reproduced without change, with the project's readings of each field, a rule for the four `resolution_status` values, and every project addition kept under one `ext` object; field sensitivity and masking (never-logged list, class P/Q/O for every field); event taxonomy; hash-chain integrity with a daily signed root; AES-256 / TLS 1.3 / separate PII key / quarterly HSM rotation as the brief states, with a key hierarchy; access matrix of 14 roles by 8 log classes with break-glass; retention schedule; deletion workflow day by day with the certificate fields; the four regulatory reports with source fields; 16 worked audit queries (AQ-01 to AQ-16); answer-to-version traceability; fail-closed states A0 to A4 when the audit bus is down; volume and cost estimate at 18,000 interactions a day (1x and 10x).
- `config/audit_log.schema.json` (JSON Schema 2020-12), three synthetic example records in `tests/compliance/examples/`, `diagrams/audit-log-flow.mmd` (parses with the Mermaid parser).
- `docs/risk/risk-matrix.md`: three matrices with 52 risks (17 technical, 13 business, 22 ethical; 25 from the brief, 27 additions), each with ID, likelihood, impact, inherent score, repository-referenced controls, residual score, owner, monitoring metric and contingency; ASCII heat maps (inherent and residual); top 10 residual risks with treatment plans; risk appetite statement, acceptance rule and review cadence; mapping from the 24 FMEA rows to risk rows.
- `docs/risk/fairness-testing.md` and `tests/compliance/fairness-pairs.yaml`: tests FT-01 to FT-10 with margins and decision rule, sample sizes, 14 counterfactual pairs (28 cases), RACI for an AI error, appeal path, privacy purposes.
- `docs/compliance/submission-checklist.md`: 36 mandatory-minimum rows, 10 proxy failure-condition rows (D-01), 7 proxy deliverable rows (D-02), the Part D Day 14-15 deliverables, 13 open sign-offs. 34 of 36 minimum rows met, 2 pending (CHANGELOG entries and the 20 conversations).
- `tests/compliance/validate_compliance.py` and `README.md`: 9 checks. Result: PASS. 12 seeded defects, each detected on a scratch copy.

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-172: simulation composition conventions. D-173: reading of the third flagged adversarial turn (already cited by conv-04). D-174: the turn-ceiling reply is the 25th message.
- D-181: record structure, `ext` namespace, readings of the brief's fields. D-182: retention for classes the brief does not cover. D-183: erasure against the 7-year record (residual record, per-customer PII keys, key hierarchy). D-184: integrity (write-once, sequence, hash chain, daily signed root). D-185: fail-closed states and action classes H1, H2, R. D-186: access matrix, break-glass, the handoff-package reading of the customer-facing staff rule. D-187: risk scales, severity rule, residual scoring, appetite, acceptance rule. D-188: fairness tests, margins, decision rule, restricted fairness view. D-189: fairness pair IDs and status. D-190: reporting production rules, volume assumptions, and the checklist and validator method.

**Challenges**
- Only four KB entries (KB-FAQ-001, 002, 008, 009) have reviewed Hindi and Hinglish bodies, and most templates take their KB slots (`effect`, `process_name`, `what_to_bring`, `safe_statement`, `cover_facts`, `criteria`) from entries with English bodies only. A Hindi or Hinglish reply built from them would mix languages or machine-translate a financial fact. The Hindi and Hinglish conversations therefore use the four translated bodies, tool values and tool-only templates.
- About ten short replies have no template (the XTR-03 offer, the XTR-01 offer, a two-request acknowledgement, the phishing triage question, the closure-reason question, a complaint status, a rewards answer, a cancelled-handoff line, the turn-ceiling close). They are free text with a decision-point note (D-172); the full list is in section (e.2).
- The Level 7 turn count: the brief counts 25 turns and XTR-06 fires at `turn_count >= 25`; the journey is designed so that message 25 is the polite close (D-174).
- ESC-004 and ESC-011 can be true together (conv-17); the crisis route owns it and ESC-004.a is recorded as a secondary trigger, which `triggers.md` section 4 rule 4 supports but no document states for this pair.
- The brief's A11 tables are interleaved in the PDF text extraction; the ten technical and business rows were reassembled by row order (probability, impact, severity, mitigation) and kept as a transcription in the validator.
- The brief's severity (P0 to P2) is not a function of probability and impact ("Low, Critical" is P0 for two risks and P1 for two others); the brief's severities are kept as given and a rule for added risks was fitted to reproduce all ten.
- The brief requires both 7-year retention and deletion within 30 days including backups; the design erases everything personal and keeps a de-identified residual record, and says openly that this is a legal question (AL-D1).
- "Customer-facing staff access only anonymised, aggregated metrics" conflicts with a human agent needing the handoff package; the package is treated as pushed service data, not log access (D-186).
- The brief gives no list of its "10 automatic failure conditions" or "7 deliverable requirements"; the checklist uses the D-01 and D-02 proxies and says so.
- The first-pass numbers were re-derived by script (volume model, sample sizes, risk scores) and all matched the documents; the scripts now live in the validator so they are reproducible from the repository.

**Open questions**
- Launch blocker (unchanged): no Hindi, Hinglish or Gujarati wording is native-reviewed; there are no reviewed Gujarati templates, so the ladder in conv-29 replies in Hindi.
- Product, Risk, CEB: the missing templates in (e), the label tables in (e), whether a phishing report needs its own tool, and whether the reward-points balance (CRD-005 points_balance) needs a tool.
- ESC-010 and XTR-04 are not fired by any conversation (ESC-010 needs more than 15 messages without a resolved topic; XTR-04 cannot fire because a below-floor turn is not a clarification, D-169).
- Legal reading of retention against deletion and of "derived data" (AL-D1); report formats, recipients and due dates (AL-D2); encryption mode and meaning of "rotated quarterly" (AL-D3); named role holders (AL-D8, IR-D1); legal review and insurance for AI-caused loss (IR-D5).
- Whether protective actions may proceed on a local acknowledgement while the audit bus is down (class H2).
- Whether `docs/compliance/` and `docs/risk/` satisfy the "exact structure" of Part D p.62.
- Fairness margins, the restricted fairness view and the 1,320-pair generated matrix (no harness exists).
- The two red residual risks: the 60 percent staffing aim (RISK-B-05) and missed-escalation detection in mixed-language text (RISK-T-11).

**Next (Day 15)**: cross-reference audit, polish, submission: cross-reference validation of the whole repository, final README and CHANGELOG, a pass over the open sign-offs list (`docs/compliance/submission-checklist.md` section 6), repository transfer.


**Day 14 audit fixes** (23 findings: all HIGH, MEDIUM and LOW applied except two wording items of finding 17 that belong to the templates; none rejected)
- Level 7 (conv-30) is now consistent at the close: the ticketed payment (TXN-003) is `resolved` with its ticket reference from T7, returns to `active` at T14 and T22 closes it again, so XTR-06 and ESC-010 (open means active or parked) agree with the closing reply, which now names ticket DSP-SYN-3001. Every status in the conversation is one of the four schema values. The advisor offer (ESC-013, declined) is in the header and INDEX 4.4, "twice this month" is gone, and the EMI gap reply no longer resets `turns_since_resolution` or offers an illustration without the customer's own rate (D-201).
- ESC-004 recovery is now non-strict: the latest raw score at or above -0.40 (the brief's "-0.4 (recovering)", Case Study 5 turn 5, p.53). conv-05 still hands over because the customer asks for the escalation. ESC-T-004-05 tests the boundary; the safety-suite manifest was rebuilt add-only (356 cases) (D-200, amends D-125).
- conv-14 now carries `flagged_turns` at every turn: the second flagged turn with a data target opens a silent ESC-001.f case, the third starts safe mode, and the lock raises one live ESC-009.c handoff with the silent case linked; the second retry reply is worded differently (D-206). conv-17 and conv-23 counters follow their own sentiment values. conv-23 gives the grievance route in the first agent reply (D-205).
- Risk matrix: RISK-T-18 (network-layer DDoS, residual red, platform dependency) and RISK-T-19 (OWASP LLM08, store isolation) added, RISK-E-23 records the repeat-contact tiebreak of D-121 with fairness pair FAIR-15 as its monitor; totals, heat maps and top 10 regenerated by script (55 risks); the two forward references in `adversarial-defences.md` now point at the rows (D-202, D-203).
- Two new conversations: conv-31 (disambiguation pair 3, ACC-003 vs ACC-004, email trap, multi-intent order) and conv-32 (CRD-003; ESC-010 fires on message 16 and not on message 15). 32 conversations, 318 messages, 34 of 41 intents, 15 of 15 brief triggers (D-207).
- Validators: the simulation validator now catches credentials in English, Hindi and Hinglish, human claims, advice in other words, durations and dates no tool, router or KB row backs, rates in words, ESC fires with no cited sub-rule, handoff packages under 8 elements, topic statuses outside the schema enum, intents missing from the header, and stale self-audit numbers; the compliance validator holds the brief's A11.1, A11.2 and A10.3 text and rejects readable text in a ciphertext field. Every missed mutation of the audit was reproduced on scratch copies and is caught. The stronger checks found 35 real defects in the files, all fixed (D-204).
- Lower findings: conv-20 no longer asks for a reason the customer gave, conv-18 reads the flag before acting on it and records why ESC-015.b is the one place treatment differs, the 1.5L source label (conv-16), the pattern-audit totals are generated from the table, intent headers and statuses corrected, conv-29 sentiment confidence follows the language-ID gap, conv-04 T10 gives the one fact asked, MM-30 quotes the brief's "7 daily entries". The conversations were also re-synced to the Day 13 template library (43 version bumps, 6 wording changes) and to prompt_version sp-1.1.0+1527a050.n000000.

## Day 15: Cross-reference audit, polish, submission

**Date**: 2026-10-13

**Tasks completed**
- Planning-file reference cleanup: 54 references to a planning file that sits outside the repository, in 18 files, were replaced by in-repo references (brief sections, decisions or documents). None remains; the two places that describe the absence check keep the word on purpose.
- `tests/validate_crossrefs.py`: a repo-wide cross-reference lint with seven checks (cited paths and section numbers exist, every cited ID is defined in its home file, README counts match the files, no placeholder text, ASCII-only English text, stale future-tense wording, no planning-file citation). It was tried against seeded defects in a scratch copy, which it caught. Its first run found two real errors (a decision and a reserved range, both fixed below) and a stale README count.
- Final cross-reference audit of the whole repository (27 findings: 6 HIGH, 14 MEDIUM, 7 LOW), and the fixes applied for all of them except the items listed under open questions:
  - CHANGELOG: a Date line on every entry, taken from the commit history; this Day 15 entry; the three places that said a coordinator was "awaiting input" now say the query was drafted and not sent.
  - `README.md` rewritten as the front door: status, overview, architecture summary with the 12 components and the diagram, setup and the seven validator commands, reading order, navigation naming every document, known limitations.
  - `docs/innovations.md` (new): 16 project additions with what, why, the brief requirement extended and the evidence file; linked from the README, from `docs/requirements-traceability.md` (R-65) and from `docs/knowledge-base/maintenance-workflow.md`.
  - Level 1 boss trace revised (D-210): T4 to T6 are a duplicate-charge dispute and a lost-card block, so no P0 fires and then waits while unrelated turns are served; T17 states the published starting rate and computes no EMI without a customer-stated rate. Still 20 turns and 12 topic switches (recounted).
  - Level 1 documents: the latency sum in `component-interfaces.md` now agrees with the 2,850 ms budget (the Escalation Router's 50 ms applies only on an escalating turn); a "Message shapes" section with field tables built from the existing schemas; the A12.3 turn ceiling and ESC-010 guards added to `docs/architecture/dialogue-management.md`; a note on the audit-down exception in row 11; forward links in `system-architecture.md`; an accessibility and proactive service section in `conversation-design.md`.
  - Traceability: R-01, R-34 and R-63 updated; R-65 to R-70 added (innovations, E5 constraints, A1.2 and A1.4 inputs, B4.1 data layers, dependency map with a Mermaid graph, accessibility).
  - Simulations: `simulations/INDEX.md` section 8 maps the working counter names of the State rows to `config/dialogue_state.schema.json` fields or to "derived, not stored" (D-212); one stale sentence removed from conv-04.
  - Claims that were not true were corrected: native-speaker review and LLM-as-judge calibration (`tests/README.md`), the sentiment lexicon "built with native-speaker review" (`docs/intent-taxonomy/sentiment.md`). The OWASP LLM01 to LLM10 names were checked against the OWASP GenAI Security Project list on Day 15 and match; the open items in `adversarial-defences.md`, `regulatory-mapping.md`, `risk-matrix.md` and `config/guardrails.yaml` are closed.
  - Coordinator status made consistent: `docs/coordinator-questions.md` is a draft that was not sent; Q1 to Q12 are the rows D-01 to D-12; "Decided (coordinator ruling)" became "Decided (project decision)" (D-164, D-191).
  - KB-ESC-003 now states the D-117 rule (version 2.0.0, because the rule changed; the simulations that cite it were updated); the duplicated sentence in the GEN-003 notes removed; `diagrams/learning-loop.mmd` says 356 cases; three `in_schema` flags in `config/escalation_rules.yaml` set to true.
  - Submission checklist: all 36 minimum rows met, the Day 15 CHANGELOG row met, FC-02 to FC-09 point to `simulations/pattern-audit.md`, the 32-conversation count, the process wording removed; `tests/compliance/validate_compliance.py` and its README updated to match. The transfer row stays pending.
  - About 40 forward references to days that are past were reworded to name the file that now holds the content. The 18 redundant `.gitkeep` files were removed.
- Hash-protected test case GR-REG-17-01 had its planning-file reference replaced; the manifest was rebuilt with `--accept-change GR-REG-17-01 --decision D-208`.

**Decisions (rationale in `docs/assumptions-and-decisions.md`)**
- D-208: the GR-REG-17-01 change and the manifest rebuild. D-209: CHANGELOG dates come from the commit history; no session times are recorded. D-210: the Level 1 boss trace no longer fires a P0 and then serves unrelated turns. D-211: `docs/innovations.md`. D-212: the State-row counter names and their mapping.
- D-175 to D-180 were reserved and not used; the log records the gap. The OWASP rows D-61, D-66 and D-77 and the turn-ceiling row D-174 were updated to their final status.

**Challenges**
- A rule in a later document (the P0 waiting rule, `routing-and-handoff.md` section 7) contradicted an early artefact (the Level 1 boss trace). The trace was changed and the rule was left alone, because XTR-01 cites turn 18 of the trace and the safety rule is the stronger source.
- The brief asks for the date and time of each work session; only commit dates exist. The dates are taken from the commit history and the header says so; where several days share a date the work was done in consecutive sessions that day, and no time of day is claimed.
- A KB entry that changes a rule is a MAJOR version under `docs/knowledge-base/kb-schema.md`, which meant updating every simulation turn that cites the entry's version.

**Open questions**
- Native-speaker review of the Hindi and Hinglish wording is still pending (launch blocker, D-145). KB facts render in English inside Hindi and Hinglish replies because only four KB entries carry Hindi and Hinglish bodies (D-199).
- Proposals await sign-off by the Risk Committee or the Customer Experience Board; no committee has reviewed any layer (`docs/compliance/submission-checklist.md` section 6).
- The coordinator questions (Q1, Q2, Q10, Q12) were drafted and never sent.
- "10 automatic failure conditions" and "7 deliverable requirements" are proxies (D-01, D-02); the brief does not list them.
- Nothing has been executed against a real system: no test case, simulation, metric or load figure is a result.
- A staffing gap against the 60 percent replacement aim is recorded and needs a decision; the after-hours SLA deviation needs Risk Committee sign-off.
- SEC-004 has no simulation (D-207).
- No LLM-as-judge calibration is specified; behaviour checks need human review until a judge is calibrated.
- The Retriever badge is not claimed (the retrieval budget of 160 to 180 ms is above 150 ms), and no stretch profile was added.

**Next**: Repository transfer to @ZethetaIntern: pending, to be done by the repository owner.
