# Output Safety Layer: Response Safety Specification

Brief refs: A4 (guardrails, response safety), A9.1 (patterns 3 and 4), A9.2 (anti-patterns: False Confidence, AUTO-FAIL item), A9.3 (tone), A10.2 (turn-level log fields), A11.1 (hallucination P0), A11.3 (transparency, privacy). `latency-scalability-cost.md` section 1 (300 ms budget) and `system-architecture.md` section 5 (output verification, fail-closed). Registry: `config/guardrails.yaml` (GR-OUT-01 to GR-OUT-06, GR-SYS-01, GR-SYS-04 and the related GR-ADV, GR-REG and GR-SEC entries named below). Architecture: `docs/architecture/response-generation.md` section 5, `docs/architecture/component-interfaces.md` rows 10 and 11, `docs/architecture/failure-modes.md` (FMEA #17, #19, #20). Companion docs: `financial-advice.md`, `account-security.md`, `regulatory-mapping.md`, `monitoring-dashboard.md`, `incident-response-playbook.md`.

**Status.** Every threshold, timeout and budget share marked "proposal" is unmeasured and needs Risk Committee review (D-64 conventions). Decisions: D-80 to D-82, D-88, D-89 in `docs/assumptions-and-decisions.md`.

## 1. Purpose and position

The Output Safety Layer (OSL, component 10) is the last automated control before text reaches the customer. It receives the `DraftResponse` {text, mode, citations[]} from the Response Generator together with the dialogue state, the locked fact slots, the `ToolResult` data and the retrieved passages, and returns a `SafetyVerdict` {pass, rewrite, block, checks[]} plus the final text (component-interfaces.md row 10).

Rules that apply to every check:

1. **No bypass.** Every outbound customer message, including templates and escalation notices, carries a `SafetyVerdict`. A message without a verdict is not delivered (GR-OUT-06, proposed in section 11 and registered by D-90).
2. **Rule floor.** In a hybrid check the rule result is a floor; a model score can raise the result to a stricter outcome but never lower a rule hit (D-54, D-58).
3. **Immutable.** The learning pipeline cannot edit a check, a threshold or an action (GR-SYS-02). Classifier weights change only through safety change control (D-58).
4. **Fail closed.** A check that times out, errors or is inconclusive counts as failed for that check (component-interfaces.md row 10, GR-SYS-01).
5. **Facts are locked.** In hybrid mode the LLM wraps a template; it cannot change `{{...}}` fact slots (response-generation.md section 1). The OSL verifies that the final text still carries them.

## 2. Check catalogue

Seven checks, run on every draft. The brief fixes the outcomes (no wrong figure, no PII, no hallucination, no false promise, no advice); mechanisms and thresholds are design choices.

| # | Check | Registry IDs | Mechanism | Inputs | Pass condition | On fail (first rung) |
|---|---|---|---|---|---|---|
| C1 | Financial accuracy | GR-OUT-01 (CRITICAL); related GR-REG-01 | hybrid | final text, locked slots, `ToolResult.data`, cited passages (id, version), catalogue allow-list (KB-PRD IDs) | every numeric token and product name is in the allowed set; tolerance 0 (section 3.1) | re-inject the slot value; else template version |
| C2 | Regulatory compliance | GR-REG-01, GR-REG-02, GR-REG-04, GR-REG-18, GR-REG-20 (see section 3.2) | hybrid | text, intent, flow state, KB passages with `regulatory_tags` | required disclosure present where the flow requires it; no guarantee, pressure, advisory claim or regulatory guess | add the mandated disclosure; else compliant template; GR-REG-18 hit: ESC-008 |
| C3 | PII leak | GR-OUT-02 (CRITICAL); related GR-SEC-R1, GR-REG-05, GR-REG-06, GR-REG-13, GR-SEC-R4 | rule | text, RED-01 to RED-07 patterns (`config/entities.yaml`), authenticated `customer_id`, tool results | no full card, CVV, Aadhaar, PIN, password, OTP, PAN or account number; no data of another customer | mask; credential type: block |
| C4 | Grounding and hallucination | GR-OUT-03 (CRITICAL) | hybrid | text split into factual claims, passages (id, version, `stale`, `lane`), tool data | every factual claim maps to a source (section 3.4) | remove the claim; clarify or escalate |
| C5 | Tone | GR-OUT-04 (MEDIUM); related GR-REG-04 | model plus phrase list | text, sentiment, emotion, intent, language | no banned phrase; professionalism and empathy scores above the floors (section 3.5) | one deterministic rewrite; else template |
| C6 | Commitment (Q9, D-09) | GR-OUT-05 (HIGH); related GR-SEC-R3, GR-REG-15 | hybrid | text, `ToolResult` with `source_ts`, KB-POL-007 permitted timelines, KB-POL-004 capability limits | every promise of outcome, timeline or capability is backed by a system of record or a hedged range | rephrase as a hedged range or remove |
| C7 | Advice boundary | GR-ADV-06 (CRITICAL); related GR-ADV-04, GR-ADV-05, GR-ADV-09, GR-REG-12, GR-REG-20 | hybrid | text, intent (PRD-001 to PRD-005), advice score | output advice score below 0.50 (D-54) | information-only wording; ESC-013 offer |

GR-OUT-01 to GR-OUT-05 are the check IDs; GR-OUT-06 (D-90) guards delivery, not content. The OSL also runs two adversarial scans specified in `adversarial-defences.md`: GR-ATK-06 (prompt-overlap and canary scan) and GR-ATK-07 (foreign identifiers, link and image allow-list), inside the S1 rule-scan stage. C2 and C7 are realised by GR-REG and GR-ADV entries whose enforcement points include the OSL; no separate OUT ID was created for them (D-80).

## 3. Per-check specification

### 3.1 C1 Financial accuracy (GR-OUT-01)

- **Rule part.** Extract every number, rate, fee, amount, tenure, date and count from the final text after normalisation (rupee, INR, lakh, crore, percent, Devanagari and other native digits per D-21, spelled numbers). Each must equal a locked slot, a `ToolResult.data` field, or a value in a cited passage whose version matches the version in the audit record. Rounding is allowed only when the template itself rounds. A derived number (EMI, interest) is allowed only when a calculator tool returned it.
- **Model part.** Resolves paraphrases the rule part cannot (for example "about a lakh" for a slot of 1,00,000) and detects named products or benefits that are not in the catalogue allow-list. A non-existent product, benefit or rate is the A9.2 AUTO-FAIL item.
- **Thresholds (proposal).** Numeric tolerance 0 for rates, fees, limits and cover amounts. Numeric-extraction recall of at least 0.99 on a labelled set before release (the target also feeds the dashboard). A hit of the AUTO-FAIL type raises the incident path (`incident-response-playbook.md`, runbook R4).
- **Fail.** Replace the figure with the slot value (rung 1); if the sentence cannot be repaired, render the template version of the whole reply (rung 2). The rewritten text is checked again.

### 3.2 C2 Regulatory compliance

| Sub-check | Guardrail | Rule or model | Pass |
|---|---|---|---|
| Disclosures present in product information (rate, fee, T&C pointer) | GR-REG-01 | rule: required-disclosure list per product intent | present, else add from KB-POL-008 / KB-REG-001 |
| Cooling-off information on sign-up flows | GR-REG-02 | rule | stated as an obligation; no length unless the KB holds one (G-01) |
| No pressure or artificial urgency | GR-REG-04 | rule phrase list plus classifier | none |
| Regulatory answer not guessed | GR-REG-18 | hybrid | answer is from a current regulatory entry, else ESC-008 |
| No advisory registration claim, no "guaranteed returns" | GR-REG-20 | rule plus classifier | none |
| AI disclosure; no claim to be human | GR-REG-16 | rule | none (OSL scan; registry updated, D-90) |

### 3.3 C3 PII leak (GR-OUT-02)

Pure rule. Pattern set RED-01 to RED-07 with their validators (Luhn, Verhoeff, PAN pattern, NexBank account format) is re-run on the outgoing text, because a tool result or an LLM can reintroduce what the Input Guard removed. Allowed forms: last four digits of a card, a masked account reference. Cross-customer check: any identifier in the text must resolve to the authenticated `customer_id` (GR-SEC-R4). Threshold: zero full identifiers; no model can waive a hit. Postal-code exception follows D-35.

### 3.4 C4 Grounding and hallucination (GR-OUT-03)

- The draft is split into factual claims (sentences with a number, a named product, a policy, a time or an eligibility statement). Each claim needs a source: a locked slot, a tool field, or a passage in `citations[]`.
- Hybrid: the rule part checks that each cited passage id exists in the turn's `RetrievalResult` and is neither `stale` nor hard-expired (D-27); the model part (entailment) scores support of the claim by the cited text.
- **Thresholds (proposal).** Support at least 0.80 passes; 0.50 to 0.80 removes the sentence and re-checks; below 0.50 or a contradiction blocks the draft to the template. Claims that are not factual (empathy, transitions) are not scored.
- Gap topics (KB entries with `gap_handling`, D-26) may only be answered with the gap wording; a figure on a gap topic is a fail.
- Regulatory topic with an ungrounded claim: no clarify rung; ESC-008 (GR-REG-18, D-43).

### 3.5 C5 Tone (GR-OUT-04)

- **Banned-phrase list (rule floor).** Pressure phrases, flippant wording near fraud, loss or complaint, over-apology templates ("deeply apologise ... sincerely regret" without resolution steps), jargon without explanation, and claims of human experience (A9.2, A9.3, response-generation.md section 2).
- **Model.** Scores professionalism and empathy for the context. Proposals: both at least 0.60 to pass; empathy required (acknowledge first) when the intent is a problem, complaint or fraud flow (A9.1 pattern 1).
- **Fail.** One deterministic rewrite (phrase substitution from the approved phrase table, not an LLM re-call, D-81); a second failure sends the template. The tone check never overrides a safety template: templates are exempt from the empathy score, not from the banned-phrase list.

### 3.6 C6 Commitment detection (GR-OUT-05, Q9, D-09)

- **Rule part.** Patterns for outcome and timeline promises: "will be credited/refunded/resolved", "within N hours/days", "exactly", "guaranteed", "definitely", "by tomorrow", and capability promises ("I will transfer", "I have increased your limit"). A match is allowed only when the value equals a locked slot sourced from a `ToolResult` with `source_ts`, or is a timeline stated in KB-POL-007.
- **Model part.** Promissory-intent classifier for phrasings the patterns miss, including Hinglish. Fail at score 0.50 or above (proposal).
- **Capability check.** A promised action must be in the agent's capability set; KB-POL-004 lists what the agent cannot do (no fund movement, no record change). A promise of a human callback needs a created ESC record, otherwise the draft says only what was actually queued.
- **Fail.** Rephrase as a hedged range or remove (rung 1); write failures are reported honestly with no promise (component-interfaces.md row 7).

### 3.7 C7 Advice boundary (GR-ADV-06)

Detailed signals and thresholds are in `financial-advice.md` section 4.2. The OSL scans for second-person recommendations, suitability or affordability verdicts, comparative verdicts not quoted from a source, and future-direction claims. Output score at or above 0.50 rewrites to the information-only wording; 0.30 to 0.50 samples for review (D-54). Locked KB facts are excluded from the rewrite. Inconclusive: the safe template, never delivery. The reply to a rewritten advice draft ends with the ESC-013 offer (once per topic).

## 4. Execution model and latency budget

The 300 ms share is fixed by `latency-scalability-cost.md` section 1; the split inside it is a proposal.

| Stage | Work | Budget p95 (ms, proposal) | Timeout behaviour |
|---|---|---|---|
| S0 | normalise text, build allowed-value sets, split claims | 10 | error: template |
| S1 | deterministic scans in parallel: C1 rule part, C2 rule part, C3, C5 banned phrases, C6 patterns | 30 | error: template |
| S2 | model checks in parallel: C1 and C6 model parts, C2 and C7 classifiers, C4 entailment, C5 scores | 150 | hard timeout 150 ms: block the LLM text and send the template version; rule floor results still apply |
| S3 | verdict assembly and deterministic repair (mask, slot re-injection, hedge, information-only wording), re-run S1 on the repaired text | 40 | repair fails: next rung |
| S4 | template render if needed, emit audit event (async buffer) | 20 | audit failure never blocks the turn (high-risk actions excepted, FMEA #21) |
| Headroom | scheduling, network | 50 | |
| **Total** | | **300** | |

- Template-only turns skip S2 (the text is pre-approved) and run S0, S1, S3 and S4: at most 100 ms of stage budget.
- Streaming: the generator may stream into an OSL buffer, but no unverified token reaches the channel. S1 may run per sentence as the buffer fills; S2 runs on the full draft. If this cannot meet the budget, factual turns use template mode (latency levers in `latency-scalability-cost.md`).
- Repairs are deterministic so that the ladder never adds an LLM call inside the 300 ms (D-81).
- Alert when the OSL p95 exceeds 210 ms (70 percent of the share, same convention as D-45); see `monitoring-dashboard.md`.

## 5. Verdict composition

All checks run (no early exit, so the log shows every failed check). The final outcome is the strictest of the individual outcomes: block over rewrite over pass. Precedence when repairs conflict: C3 mask first, then C1 slot re-injection, then C4 claim removal, then C6, C7, C2, and C5 last. After any repair the text is re-checked once; a second failure goes to the next rung, never to a second repair.

## 6. Fail-closed ladder (GR-SYS-01, D-82)

| Rung | Action | When |
|---|---|---|
| 1 | Deterministic repair inside the check (mask, slot, hedge, information-only wording) | repairable and re-check passes |
| 2 | Safe template for the intent and state (names in `financial-advice.md` section 6 and the templates in `config/templates/`) | repair fails, check timed out, or LLM text blocked |
| 3 | Clarify: one targeted question from a pre-approved template | only where allowed (below) |
| 4 | Escalate with the handoff package (KB-ESC-001): ESC-008 for regulatory or ungrounded regulatory claims, ESC-013 for advice (offer), ESC-003 / ESC-014 per GR-SYS-01 | clarify not allowed, or clarify used and the next draft fails |
| 5 | Static status message and the human line | every rung fails or the OSL is unavailable (FMEA #24) |

Where the clarify rung is skipped:

| Context | Reason | Behaviour |
|---|---|---|
| PRD-005 and disambiguation pair 2 | asking invites the customer to volunteer income, age or portfolio (`financial-advice.md` section 8, GR-ADV-07) | information-only template plus ESC-013 offer; never a question |
| Contain-first flows, disambiguation pair 6 (CRD-001, SEC-001, SEC-004 to SEC-001) | the block must not be delayed by a question | confirmed protective action, then escalate (ESC-001) |
| D-19 safety-biased intents (SEC-001, SEC-004, GEN-003, GEN-007, PRD-005) | cost of a miss is delayed fraud, missed crisis or advice breach | template, then escalate; GEN-007 goes to ESC-011 at once |
| Credential or PII block (C3 block) | a question could draw the secret again | template that tells the customer not to share it (GR-SEC-R5), then R6 if security-critical |
| Regulatory-uncertain topic (GR-REG-18) | a clarifying question cannot make the answer certain | ESC-008 |

Clarify limits elsewhere: at most one OSL-triggered clarify per turn; it counts toward `max_clarification_turns`; the same fallback text is not repeated (robotic loop anti-pattern, A9.2). Three consecutive ladder fallbacks in one conversation escalate (routing to be confirmed with the escalation matrix on Day 12, like D-65).

Honesty rule: a template fallback never says the system checked something it did not; it says what the agent can do and offers a human (A9.1 pattern 4).

## 7. Logging (A10.2)

Per turn the OSL writes to the audit bus: `guardrails_checked` (all seven check IDs plus the related GR IDs evaluated), `guardrails_triggered`, `response_generation_method` before and after repair, `response_latency_ms` and per-stage latency, `action_taken`, `SafetyVerdict` per check (outcome, score, rung reached), prompt_version, model_version and KB entry versions (cross-cutting rule in component-interfaces.md). Draft text that failed a check is stored encrypted with PII redacted (A10.3 double encryption) under the same retention as the turn (7 years, A10.1) so incidents can be replayed; it is never shown to the customer. At conversation level `guardrails_activated` is the union of triggered IDs. Audit write failure on a high-risk action blocks that action (FMEA #21); otherwise logging is async and never blocks the turn.

## 8. Test hooks

Reserved test IDs: GR-OUT-01-01, GR-OUT-01-02; GR-OUT-02-01, GR-OUT-02-02; GR-OUT-03-01, GR-OUT-03-02; GR-OUT-04-01, GR-OUT-04-02; GR-OUT-05-01, GR-OUT-05-02 (registry `tests_reserved: 2` each). The related ADV and REG IDs keep their own ranges. Beyond fixed cases, a regression corpus of drafts with injected faults (wrong rate, extra digit, invented product, promise with a timeline, advice verdict, leaked card) measures per-check recall and false-positive rate on the benign set (D-64 gate).

## 9. Metrics emitted

Per check: evaluations, triggers by outcome (repair, template, block, escalate), rung reached, timeouts, stage latency, near-misses (D-88) and sampled-review verdicts. These feed `monitoring-dashboard.md`.

## 10. Failure behaviour

| Situation | Behaviour |
|---|---|
| OSL service down | template-only mode, no free-form generation (account-security.md section 7, GR-SYS-01) |
| Model classifier down | rule floors remain; hybrid checks use the stricter result; LLM text is not delivered |
| Entailment model down | C4 fails closed: factual claims outside locked slots are removed or the template is sent |
| Audit bus down | local buffer; high-risk and payment actions blocked until the write succeeds |
| Over-blocking detected | raise through the dashboard; tune only by safety change control (FMEA #20, GR-SYS-03) |

## 11. Open items and proposals

1. GR-REG-16 (AI disclosure, no human claim) did not list the OSL as an enforcement point; this spec adds a verification scan and the registry now lists the OSL (D-90).
2. New IDs proposed here and registered on Day 10 (D-90): **GR-OUT-06** "no delivery without a SafetyVerdict" (rule, L4; the gateway refuses an outbound message that lacks one) and **GR-SYS-04** "kill switch and template-only mode control" (rule, L1/L5; access-controlled switch that can only move the system toward safer behaviour, D-86). Each has two reserved tests with written cases (`tests/guardrails/output-safety-system.yaml`).
3. The split of the 300 ms budget, all scores and the empathy floors are proposals to be set on the dev set and approved by the Risk Committee.
4. Hinglish and the other four languages need native review of the banned-phrase list and the commitment patterns (D-22: no native reviewers exist).
5. The OSL check set does not replace the input-side controls; adversarial vectors (the GR-ATK family, Day 10) are covered in `adversarial-defences.md`.
