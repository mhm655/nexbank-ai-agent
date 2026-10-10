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

## Day 8: Retrieval pipeline, maintenance workflow, access matrix, Level 3 boss

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

## Day 12: Escalation triggers, routing and handoff, queues, KPI framework, dashboards

**Tasks completed**
- `config/escalation_rules.yaml`: machine-readable rules for ESC-001 to ESC-015 (brief wording quoted with page, priority, queue, SLA, `fire_when` expression over 35 defined signals, 27 sub-rules, precedence rank, cancellable flag, handoff mode, linked intents, guardrails, KB entries and tests), 7 additions XTR-01 to XTR-07 marked `origin: addition`, the 15 queues with hours, overflow chains and after-hours rules, the 8-element handoff package. Priorities, queues and SLAs equal KB-ESC-010 and the PDF (A6 pp.16-17): no mismatch found.
- `docs/escalation/triggers.md`: the 15 triggers as the brief defines them, a specification block per trigger (detection signal, owning component, state fields, links, what must not fire, tests), precedence and conflict resolution (P0 always wins; SLA, then rank; one owner, nothing dropped; parallel compliance cases; upgrade never downgrade; suppression), the additions, what is not an escalation, the Day 12 confirmations of D-65 and D-72, signals and proposed state fields.
- `docs/escalation/routing-and-handoff.md`: SLA clock and the reading of IMMEDIATE, routing steps and decision table (trigger by segment, language and hours), the 8-element package as a field schema with envelope and a synthetic example, warm-handoff script with variants and an A9.2 anti-pattern check, behaviour while the customer waits, failed-handoff behaviour, de-escalation moves and the cancellation rules (never for P0), 13 template names for Day 13.
- `docs/escalation/queue-management.md`: queue table, overflow, after-hours routing, SLA-breach handling, resolution horizon, capacity model (Erlang C per queue, two scenarios, computed by script), priority rebalancing, escalation quality metrics EQ-01 to EQ-12 with labels mapped to the Day 11 correction record, queue alerts.
- `diagrams/escalation-routing.mmd`: trigger evaluation, precedence and routing. Mermaid 10.9.1 parser: OK (not rendered).
- `tests/escalation/`: 57 cases (37 for the brief's triggers: 18 fire, 19 near-miss; 10 for the additions; 10 Level 6 boss cases with owner, secondary triggers, priority, queue and reasoning), README, and `validate_escalation.py`. All specified, not run.
- `docs/metrics/kpi-framework.md`: the 20 A8 metrics plus the A1.4 and A2.3 figures, classified leading, lagging and operational, each with the brief's definition, formula, numerator and denominator, log source, brief target and frequency, owner, alert thresholds and anti-gaming notes; 9 further measures the brief names; guardrail metrics DM-01 to DM-16 and Day 11 definitions linked, not redefined; counter-metric pairs; A10.3 reporting map.
- `docs/metrics/improvement-cycle.md`: Detect, Diagnose, Design, Deploy, Validate, Document with artefacts, roles, timings, the 15-minute budget, a symptom-to-component table, an impact, effort and risk score, the improvement record, and two worked examples labelled illustrative. Deploy and Validate point at the Day 11 gates and ladder.
- `docs/metrics/dashboards.md`: ASCII wireframes (layout only, no values) and panel specifications for the Real-Time, Daily and Weekly dashboards; all 16 A8.5 items mapped to a panel; audiences, refresh, drill-down, access rules (A10.3), alert handling.
- Validator `python tests/escalation/validate_escalation.py`: PASS (15 triggers, 7 additions, 15 queues, 57 cases, 9 documents checked).

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
