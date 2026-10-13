# Risk Assessment Matrix

Brief refs: A11.1 Technical Risk Matrix (p.30), A11.2 Business Risk Matrix (p.31), A11.3 Ethical Risk Assessment (pp.31-32), A1.3 (p.4, Risk Committee and CEB concerns), A1.4 (p.5, "70%+ containment rate, 4.5+ CSAT, 0% incorrect financial advice rate, <30-second first reply"), A9.2 (pp.24-25, anti-patterns and the AUTO-FAIL), A5.4 (p.15, safety-preserving updates), E5 (p.66, technology constraints), Regulatory Reference Summary (pp.70-71: NIST AI RMF 1.0, EU AI Act), Part D Day 14-15 (p.61: "Complete risk assessment matrix (technical, business, ethical)"). Companion documents: `docs/architecture/failure-modes.md` (the 24-row component FMEA, which this matrix builds on and does not restate), `docs/risk/fairness-testing.md` (the method for the ethical risks), `docs/compliance/audit-logging.md`. Checks: `tests/compliance/validate_compliance.py`.

**Status.** The system is specified, not built. Every likelihood and impact below is a design-time judgement, not a measurement; residual scores state what the specified controls are expected to achieve and must be re-scored with production data. The brief gives the ten technical and business risks with probability, impact, severity and mitigation, and the ethical requirements as fifteen statements without scores. The numeric scale, the residual scores, the owners, the added risks and the appetite statement are proposals (D-187). Tables in this file were generated from one register; check 6 of `tests/compliance/validate_compliance.py` recomputes every score, band, count, heat map cell and the top 10 from the tables and fails when any differs.

## 1. Method

1. Start from every risk the brief lists: 6 technical (A11.1), 4 business (A11.2), and the 15 ethical statements of A11.3, each turned into the risk of failing it.
2. Add the risks this project found while specifying the system, marked "addition". Known deviations and findings already recorded in the decisions log are entered as explicit rows, not hidden in prose (section 10).
3. Score inherent risk (no project controls), list the controls that exist in this repository by ID, score residual risk, name an owner, a monitoring metric and a contingency.
4. The component FMEA of Day 3 looks at one component failing. This matrix looks at outcomes for the bank and its customers. Section 3.4 maps each FMEA row to the risk rows that build on it.

Register size: 55 risks (19 technical, 13 business, 23 ethical); 25 from the brief and 30 additions.

## 2. Scales

### 2.1 Likelihood

The brief uses three words (Low, Medium, High). The definitions are the project's.

| Score | Label | Definition (proposal) |
|---|---|---|
| 1 | Low | Not expected in a year at 18,000 interactions a day; needs more than one independent control to fail |
| 2 | Medium | Expected a few times a year, or once a year with wide effect |
| 3 | High | Expected monthly or more often, or certain by design until something changes |

### 2.2 Impact

The brief uses Medium, High and Critical. Low is added for residual scoring.

| Score | Label | Definition (proposal) |
|---|---|---|
| 1 | Low | Cosmetic or brief; no customer is worse off |
| 2 | Medium | Degraded experience for some customers, recoverable within days; a brief target missed for a short period |
| 3 | High | Many customers affected, or a brief target (containment, CSAT, escalation rate, an SLA) missed for weeks, or one of the brief's ethical requirements not met |
| 4 | Critical | Customer financial loss, exposure of personal data or credentials, a breach of a rule the brief states as absolute (A4.1, A4.2, the A9.2 AUTO-FAIL), a regulatory breach, or a total outage |

### 2.3 Score and bands

Score = likelihood x impact, from 1 to 12. Bands: red 8 to 12, amber 4 to 6, green 1 to 3. Scores 5, 7, 10 and 11 cannot occur.

### 2.4 Severity

The brief gives a severity (P0, P1, P2) for each of its ten rows. It is not a function of probability and impact alone: "Low, Critical" is P0 for the regulatory penalty and the legal liability and P1 for cascading failures and reputational damage. The brief's severity is therefore kept as given, and added risks get a severity by a rule that reproduces all ten of the brief's rows:

- impact Critical: P0 when likelihood is Medium or High, or when the consequence is regulatory or legal; otherwise P1;
- impact High: P1;
- impact Medium or Low: P2.

| ID | Brief Prob. | Brief Impact | Brief Severity | Severity by the rule | Match |
|---|---|---|---|---|---|
| RISK-T-01 | Medium | Critical | P0 | P0 | yes |
| RISK-T-02 | High | High | P1 | P1 | yes |
| RISK-T-03 | Medium | Medium | P2 | P2 | yes |
| RISK-T-04 | Medium | Critical | P0 | P0 | yes |
| RISK-T-05 | Low | Critical | P1 | P1 | yes |
| RISK-T-06 | Medium | Medium | P2 | P2 | yes |
| RISK-B-01 | Medium | High | P1 | P1 | yes |
| RISK-B-02 | Low | Critical | P0 | P0 | yes |
| RISK-B-03 | Low | Critical | P1 | P1 | yes |
| RISK-B-04 | Low | Critical | P0 | P0 | yes |

The ethical risks have no severity in the brief; the same rule is applied to them.

### 2.5 Residual score

Residual likelihood and impact are scored with the "existing controls" working as specified. A control that is a proposal awaiting sign-off still counts, because the design is the deliverable, but section 7 lists what must happen before a residual score can be relied on. Residual is never above inherent; the validator checks this for every row.

## 3. Technical risk matrix (A11.1)

### 3.1 The brief's matrix, reproduced (p.30)

| Risk | Prob. | Impact | Severity | Mitigation Required |
|---|---|---|---|---|
| LLM hallucination producing incorrect financial info | Medium | Critical | P0 | Response grounding, KB cross-check, financial figure validation |
| Model drift degrading performance | High | High | P1 | Continuous monitoring, drift detection, retraining triggers |
| Context window overflow in complex conversations | Medium | Medium | P2 | Summarisation, sliding window, priority retention |
| KB staleness from delayed regulatory updates | Medium | Critical | P0 | Regulatory fast-track, staleness alerts, version-tagged KB with expiry |
| Cascading failures across components | Low | Critical | P1 | Circuit breaker, bulkhead isolation, rule-based fallback |
| Latency spikes during peak hours | Medium | Medium | P2 | Auto-scaling, request queuing, response caching, CDN for static KB |

### 3.2 Assessment

Rows RISK-T-01 to RISK-T-06 are the brief's, in its order, with its probability and impact; the rest are additions.

| ID | Risk | Origin | Cause | L | I | Inherent | Severity | Scoring rationale |
|---|---|---|---|---|---|---|---|---|
| RISK-T-01 | LLM hallucination producing incorrect financial info | brief A11.1 | A generated sentence states a rate, fee, benefit or timeline that no KB entry or tool result supports; a figure is altered in paraphrase; a wrong passage is retrieved | 2 Medium | 4 Critical | 8 | P0 | Brief: Medium, Critical. One delivered wrong rate is the A9.2 AUTO-FAIL and breaks the 0% incorrect-advice target |
| RISK-T-02 | Model drift degrading performance | brief A11.1 | Customer language, product mix or fraud patterns move away from the training and evaluation data; a provider changes a model behind a stable name | 3 High | 3 High | 9 | P1 | Brief: High, High. Drift is expected in any live NLU system; the effect is gradual loss of accuracy across many conversations |
| RISK-T-03 | Context window overflow in complex conversations | brief A11.1 | Long multi-topic conversations exceed the prompt budget; an early fact (auth state, a commitment, a parked topic) is dropped | 2 Medium | 2 Medium | 4 | P2 | Brief: Medium, Medium. Affects long conversations only; the visible effect is a repeated question or lost context |
| RISK-T-04 | KB staleness from delayed regulatory updates | brief A11.1 | A regulatory or rate change is published and the KB entry is not updated before customers ask; an expired entry keeps being served | 2 Medium | 4 Critical | 8 | P0 | Brief: Medium, Critical. A stale regulatory statement is incorrect information at scale |
| RISK-T-05 | Cascading failures across components | brief A11.1 | One slow or failed dependency (model provider, vector index, session store, banking API) exhausts timeouts and takes the turn path down | 1 Low | 4 Critical | 4 | P1 | Brief: Low, Critical. Rare, but a total outage stops service for every customer including fraud reports |
| RISK-T-06 | Latency spikes during peak hours | brief A11.1 | Peak traffic, a slow model call or a slow re-ranker pushes the turn past the 3 s budget | 2 Medium | 2 Medium | 4 | P2 | Brief: Medium, Medium. Slower replies, no wrong answer |
| RISK-T-07 | Prompt injection or jailbreak defeats a guardrail | addition | Customer text, a pasted document, a KB passage or a tool output carries instructions the model follows; a multi-turn attack wears a boundary down | 3 High | 4 Critical | 12 | P0 | Attempts are certain on a public banking chat; without layered controls one success can disclose data or produce advice |
| RISK-T-08 | Personal data or a credential appears in a reply, a log or a dataset | addition | A redaction rule misses a format (native digits, spelled digits); a tool returns an unmasked field; free text carries an identifier | 2 Medium | 4 Critical | 8 | P0 | A full card number or credential in a reply or log is a hard-zero event and a PCI DSS matter as the brief names it |
| RISK-T-09 | Cross-customer data leakage | addition | A session is bound to the wrong customer key; a cache or a retrieval filter returns another customer's data; a model memorises training text | 2 Medium | 4 Critical | 8 | P0 | A11.3 requires this to be architecturally impossible; any occurrence is a SEV0 |
| RISK-T-10 | Action executed without the required authentication or confirmation, or a fund movement by the agent | addition | A step-up is skipped, a session outlives the 5-minute timeout, a retry repeats a write, an entity (amount, card) is wrong | 2 Medium | 4 Critical | 8 | P0 | A4.2 rules 2 and 3 are absolute; an unauthorised change is customer loss and legal liability |
| RISK-T-11 | A true escalation trigger does not fire (missed escalation) | addition | A model-based signal (sentiment, crisis or fraud cue, AML cue) is missed, especially in code-switched or secondary-language text; a state counter is lost | 2 Medium | 4 Critical | 8 | P0 | A missed ESC-001, ESC-009, ESC-011 or ESC-012 leaves a customer in danger or a regulatory duty unmet |
| RISK-T-12 | Intent or entity error sends the customer down the wrong flow | addition | Ambiguous or multi-intent message, overlapping intent pairs, a mis-read amount or card | 3 High | 3 High | 9 | P1 | Misclassification is routine in NLU; uncontrolled it produces wrong answers and wrong actions across many conversations |
| RISK-T-13 | A learning-pipeline update degrades safety, or feedback is poisoned | addition | A candidate improves CSAT while weakening a guardrail slice; coordinated ratings or a biased reviewer steer training | 2 Medium | 4 Critical | 8 | P0 | A5.4 treats this as the central risk of self-improvement; a silent safety regression reaches every customer |
| RISK-T-14 | Audit records are lost, incomplete or altered | addition | Bus outage with a full buffer, a storage fault, an operator with too much access | 1 Low | 4 Critical | 4 | P1 | The Risk Committee requires a tamper-proof trail for every interaction (A1.3); a gap removes the evidence for every other control |
| RISK-T-15 | Dependence on one model provider or an unvetted component (supply chain) | addition | Provider outage, price change, silent model change, a compromised library or model artefact | 2 Medium | 3 High | 6 | P1 | E5 requires model-swappability; `docs/guardrails/regulatory-mapping.md` section 4 records the supply-chain category as a gap by scope |
| RISK-T-16 | Guardrails over-block legitimate requests | addition | Many always-on guardrails; a tightened lexicon; a classifier that drifts | 3 High | 2 Medium | 6 | P2 | The end-to-end false-positive budget has 0.04 points of reserve against the 3 percent gate (D-76) |
| RISK-T-17 | A deletion request is not completed everywhere inside 30 days | addition | A store, a backup, a downstream ticket system or a model lineage is missed; the legal reading of retention against deletion is unresolved | 2 Medium | 4 Critical | 8 | P0 | A10.3 sets the 30-day duty with backups, derived data and training data in scope; the brief does not say how it meets the 7-year retention |
| RISK-T-18 | Volumetric (network-layer) denial of service takes the chat channels down | addition | A flood from many sources exhausts bandwidth or the platform edge before any application limit applies; a slow, low-rate attack on the session path | 2 Medium | 4 Critical | 8 | P0 | A total outage stops service for every customer, fraud reports included (impact 4 in section 2.2). OWASP LLM10 is covered only at the application layer (`docs/guardrails/adversarial-defences.md` sections 8.6 and 11); the network layer is a gap by scope, because this repository specifies no CDN, WAF or scrubbing service |
| RISK-T-19 | Weakness in the vector and embedding store: a poisoned or cross-audience entry is retrieved, or the store itself is reachable (OWASP LLM08) | addition | A poisoned entry is indexed; the audience or expiry filter is bypassed; the embedding store is reachable from another workload or its contents are read or altered outside the maintenance workflow | 2 Medium | 4 Critical | 8 | P0 | A poisoned or wrong entry served as a fact is the A9.2 AUTO-FAIL class, and an audience bypass shows internal text to customers. RISK-T-09 covers customer data leakage; this row covers the store itself. `docs/guardrails/regulatory-mapping.md` marks LLM08 partial |

### 3.3 Controls, residual risk, owner, monitoring, contingency

| ID | Existing controls (repository references) | Residual L | Residual I | Residual | Band | Owner | Monitoring metric | Contingency |
|---|---|---|---|---|---|---|---|---|
| RISK-T-01 | GR-OUT-01 (figure match), GR-OUT-03 (grounding), GR-OUT-05 (commitments), GR-REG-18, GR-OUT-06; locked fact slots and template mode for 67 of 73 templates (D-144); retrieval threshold 0.65 (D-43); FMEA #11, #17, #19; gates G2, G3; cases GR-OUT-01-01, GR-OUT-03-01 and `tests/safety-suite/hallucination-traps.yaml` | 1 Low | 4 Critical | 4 | amber | NLU Team; Risk Committee for the guardrails | KPI-G6, DM-12, DM-07, KPI-L5 | Runbook R4: template-only lever for the intent (GR-SYS-04), find affected turns with AQ-02, human correction with TPL-SYS-CORRECTION |
| RISK-T-02 | DM-11 (model drift score, PSI, trigger-rate z-score), KPI-O6 target under 0.05, frozen evaluation sets at gate G2, G9 post-deployment monitoring, breaker (GR-SYS-04), retraining triggers and 21-day cycle (`docs/learning-pipeline/overview.md`), pinned `model_version` in every turn record | 2 Medium | 2 Medium | 4 | amber | NLU Team, ML Team | KPI-O6, DM-11, KPI-L2, KPI-L7 | Roll back to the previous model version; widen clarification (rules-only policy, FMEA #9); retrain through gates G1 to G9 |
| RISK-T-03 | Summary with `pinned_facts` and a history buffer of at least 20 turns (`config/dialogue_state.schema.json`), token ceilings per layer (D-139), topic stack, ESC-010 and XTR-06 (turn ceiling), GR-ATK-09; FMEA #8; Level 1 boss trace (`docs/architecture/boss-trace.md`) | 1 Low | 2 Medium | 2 | green | NLU Team | KPI-A6, KPI-O1, EQ-04 | Rebuild state from the turn log; clarify once; hand to a human with the package (ESC-010) |
| RISK-T-04 | TTL classes with hard expiry (D-27), regulatory fast-track and staleness alerts (`docs/knowledge-base/maintenance-workflow.md`), `stale` flag and hard-expiry exclusion leading to ESC-008 (D-43), GR-REG-18, `id@version` on every citation, FMEA #11, `tests/kb/validate_kb_entries.py` | 1 Low | 4 Critical | 4 | amber | KB owner; Regulatory Compliance Manager for regulatory entries | KPI-O5, KPI-L5, DM-12 | Quarantine the entry; answer with the gap statement and ESC-008; AQ-02 for the blast radius; correction to affected customers (playbook section 6) |
| RISK-T-05 | Hard timeout and fallback per hop (`docs/architecture/component-interfaces.md`), fail-closed ladder GR-SYS-01, kill switch and template-only mode GR-SYS-04, FMEA #1, #6, #13, #18, #24, static message TPL-SYS-STATUS-STATIC, circuit breaker (`docs/guardrails/monitoring-dashboard.md` section 8) | 1 Low | 3 High | 3 | green | Platform on-call; Information Security Officer | KPI-O3, DM-15, DM-10 | Static status message and the human line; P0 conversations to any available human (D-123); incident at SEV1 or higher |
| RISK-T-06 | Per-stage budget and levers (`docs/architecture/latency-scalability-cost.md`), FAQ and embedding caches, template mode, autoscale on queue depth, rate limits GR-ATK-08, FMEA #2, #12 | 2 Medium | 1 Low | 2 | green | Platform on-call | KPI-L1, KPI-A1, DM-10, KPI-O4 | Degrade to template-only before refusing; honest wait message; shed load by node |
| RISK-T-07 | GR-ATK-01 to GR-ATK-04, GR-ATK-06, per-turn boundary code (D-141), no secret in any prompt (D-73), Output Safety Layer on every reply (GR-OUT-06), tool-side auth re-check, FMEA #3, #19; 62 adversarial cases with 27 boss scenarios (`tests/adversarial/`), red-team gate G4 | 1 Low | 4 Critical | 4 | amber | Security Operations | DM-08, DM-09, DM-12 | Runbook R3: safe mode for the session, lexicon or rule update through safety change control, new suite case (D-79) |
| RISK-T-08 | RED-01 to RED-07 with the D-21 normalisation, GR-SEC-R1, GR-SEC-R5, GR-OUT-02, GR-REG-05, GR-REG-06, GR-ATK-07, sealed PII fields and the daily scan (`docs/compliance/audit-logging.md` sections 5 and 8), QG-03, `tests/safety-suite/pii-masking.yaml` | 1 Low | 4 Critical | 4 | amber | Information Security Officer | DM-12, QG-03, AQ-07 | Runbook R2: SEV0 for a credential or another customer's data; appended correction event; rule fix; re-scan of stored records |
| RISK-T-09 | GR-SEC-R4, customer key set by the Gateway session and never by the model, tool-side auth re-check, retrieval auth pre-filter (D-44, D-51), no cross-conversation memory, splits by customer and consent filter in datasets (QG-02, QG-06), per-customer PII keys (D-183) | 1 Low | 4 Critical | 4 | amber | Information Security Officer | DM-12, AQ-12 | Runbook R2 at SEV0; kill switch if systemic; notify the Compliance lead (IR-D3) |
| RISK-T-10 | GR-SEC-R2, GR-SEC-R3 (no money-movement tool exists), GR-SEC-R7, GR-ATK-10, auth matrix as immutable layer IL-2, confirm before action, idempotency keys, FMEA #7, #14; `tests/safety-suite/auth-gating.yaml` | 1 Low | 4 Critical | 4 | amber | Information Security Officer; Product Engineering for tools | DM-12, AQ-11 | Runbook R5 at SEV0: reverse the action through the system of record, human contact, tool disabled until the cause is fixed |
| RISK-T-11 | Deterministic rules for eight triggers with exact replay, strict precedence order (FMEA #10), proximity score as backstop, human request honoured (XTR-01), FMEA #16, EQ-02 with a random review stream, 64 cases in `tests/escalation/`, `tests/safety-suite/escalation-triggers.yaml`, triggers as immutable layer IL-5 | 2 Medium | 4 Critical | 8 | red | Escalation owner (CX Team) with the Risk Committee | EQ-02, EQ-04, DM-12 | Any confirmed miss on a P0 trigger is an incident; new suite case; lexicon or threshold change through safety change control |
| RISK-T-12 | Tiered thresholds (D-06), six disambiguation trees, clarification budget (XTR-04), validators and echo-back, confirmation before any side effect, FMEA #5, #7, `tests/nlu/boss-level2.yaml` | 2 Medium | 2 Medium | 4 | amber | NLU Team | KPI-L2, KPI-L3, KPI-A6 | Clarify, then human; supervisor corrections feed the next U4 cycle |
| RISK-T-13 | Immutable layer IL-1 to IL-6, invariants INV-01 to INV-12, gates G0 to G9, GR-SYS-02, GR-SYS-03, fixed suite of 356 cases at 100 percent (KPI-A3), canary and breaker, QG-08, FMEA #22, #23 | 1 Low | 4 Critical | 4 | amber | ML Team; Risk Committee as suite custodian | KPI-A3, DM-13, DM-11 | Runbook R7: automatic rollback and freeze; SEV0 if an immutable element changed |
| RISK-T-14 | Hash chain, daily signed root and write-once storage (D-184), fail-closed states A0 to A4 (D-185), GR-REG-07, separation of duties in the access matrix (D-186), FMEA #21 | 1 Low | 3 High | 3 | green | Security Operations (audit bus owner) | DM-12, AQ-09, AQ-10 | Replay from local buffers; a gap is a finding and an incident; high-risk actions stay blocked until the replay completes |
| RISK-T-15 | Provider-agnostic interfaces (assumption A4), failover model (FMEA #18, #24), template mode needs no model (D-144), version tuple pinned and logged, any model swap is a U4 or U5 candidate through gates G1 to G9 | 2 Medium | 2 Medium | 4 | amber | CTO; Information Security Officer | KPI-O3, KPI-O6 | Fail over; template-only mode; supply-chain controls remain a platform dependency |
| RISK-T-16 | False-positive target per guardrail in the registry, end-to-end gate DM-05 on the benign evaluation set (D-64), near-miss tracking, soft-block with rephrase, FMEA #4, #20 | 2 Medium | 2 Medium | 4 | amber | Risk Committee (registry) with the CX Team | KPI-L6, DM-05, DM-04 | Tune through safety change control only; a new always-on guardrail needs another bound lowered |
| RISK-T-17 | Tombstone and QG-07, weekly purge and deletion-only rebuild (D-104, D-157), per-customer key destruction and residual record (D-183), certificate, AQ-08, twice-yearly drill, legal hold rule (D-87) | 2 Medium | 3 High | 6 | amber | Data Protection lead | AQ-08, QG-07 | Escalate to the Data Protection lead and Compliance lead on day 20 if any store is open; record the reason on the certificate |
| RISK-T-18 | Application layer only: GR-ATK-08 (rate limits, token budget), GR-ATK-09 (complexity scoring, turn cap), autoscale on queue depth and the caches of `docs/architecture/latency-scalability-cost.md`, template-only lever and kill switch GR-SYS-04, static status message TPL-SYS-STATUS-STATIC, FMEA #2. No control in this specification covers a volumetric flood (CDN, WAF, DDoS scrubbing, upstream capacity); it is a platform dependency (`docs/guardrails/adversarial-defences.md` section 8.6) and the residual stays red until one is specified and tested | 2 Medium | 4 Critical | 8 | red | Platform on-call; Information Security Officer (dependency owner: the platform and network team, not yet named) | DM-10, KPI-O3, KPI-O4 | Static status message and the human line; P0 conversations to any available human (D-123); ask the hosting provider to switch on upstream scrubbing; incident at SEV1 or higher |
| RISK-T-19 | Retrieval auth, audience and expiry pre-filter inside both searches (D-44, D-51), KB approval chain so only published, approved entries are indexed (`docs/knowledge-base/maintenance-workflow.md`), imperative-text scan at ingestion and retrieval GR-ATK-02, GR-SEC-R4, no customer data in the index, `tests/kb/validate_kb_entries.py`. Not specified in this repository: access control, network isolation, encryption and backup of the embedding store, which depend on the platform design (dependency in section 11) | 2 Medium | 3 High | 6 | amber | Information Security Officer; KB owner; store isolation: platform team | DM-12, KPI-L5, AQ-12 | Quarantine the entry; rebuild the index from approved entries; kill switch if systemic; AQ-02 for the blast radius |

### 3.4 Relation to the component FMEA

Every row of `docs/architecture/failure-modes.md` is taken up by at least one risk row. The FMEA keeps its own severity, likelihood and detectability figures; they are not restated here.

| FMEA row | Risk rows that build on it |
|---|---|
| #1 | RISK-T-05 |
| #2 | RISK-T-06, RISK-T-18 |
| #3 | RISK-T-07 |
| #4 | RISK-T-16 |
| #5 | RISK-T-12 |
| #6 | RISK-T-05 |
| #7 | RISK-T-10, RISK-T-12 |
| #8 | RISK-T-03 |
| #9 | RISK-T-02 |
| #10 | RISK-T-11 |
| #11 | RISK-T-01, RISK-T-04 |
| #12 | RISK-T-06 |
| #13 | RISK-T-05 |
| #14 | RISK-T-10 |
| #15 | RISK-B-13 |
| #16 | RISK-T-11 |
| #17 | RISK-T-01 |
| #18 | RISK-T-05, RISK-T-15 |
| #19 | RISK-T-01, RISK-T-07 |
| #20 | RISK-T-16 |
| #21 | RISK-T-14 |
| #22 | RISK-T-13 |
| #23 | RISK-T-13, RISK-E-22 |
| #24 | RISK-T-05, RISK-T-15 |

## 4. Business risk matrix (A11.2)

### 4.1 The brief's matrix, reproduced (p.31)

| Risk | Prob. | Impact | Severity | Mitigation Required |
|---|---|---|---|---|
| Customer churn from poor AI experience | Medium | High | P1 | Real-time CSAT, auto-escalation on negative sentiment, A/B testing |
| Regulatory penalty for non-compliant AI | Low | Critical | P0 | Compliance layer, mandatory testing, quarterly regulatory audit |
| Reputational damage from viral negative interaction | Low | Critical | P1 | Quality monitoring, crisis response, detect potentially viral conversations |
| Legal liability from AI-caused customer loss | Low | Critical | P0 | Comprehensive guardrails, legal review, insurance, audit trail |

### 4.2 Assessment

Rows RISK-B-01 to RISK-B-04 are the brief's. Two of the brief's mitigations are not in place and are stated as such in the controls column: "legal review" and "insurance" for RISK-B-04 are dependency IR-D5, and the "quarterly regulatory audit" of RISK-B-02 is proposed in section 8.3.

| ID | Risk | Origin | Cause | L | I | Inherent | Severity | Scoring rationale |
|---|---|---|---|---|---|---|---|---|
| RISK-B-01 | Customer churn from poor AI experience | brief A11.2 | Robotic or wrong replies, repeated questions, slow handoff; the anti-patterns of A9.2 | 2 Medium | 3 High | 6 | P1 | Brief: Medium, High. The CSAT baseline is 3.2 and the board expects 4.5 |
| RISK-B-02 | Regulatory penalty for non-compliant AI | brief A11.2 | An obligation is unmapped, a guardrail fails, a report is late or wrong, a regulation changes | 1 Low | 4 Critical | 4 | P0 | Brief: Low, Critical. Competitor B received a regulatory warning for unsolicited investment advice (A1.4) |
| RISK-B-03 | Reputational damage from viral negative interaction | brief A11.2 | A screenshot of a tone fault, a wrong answer or a mishandled crisis circulates | 1 Low | 4 Critical | 4 | P1 | Brief: Low, Critical |
| RISK-B-04 | Legal liability from AI-caused customer loss | brief A11.2 | A customer acts on a wrong figure or a promised timeline; an unauthorised action; a missed fraud escalation | 1 Low | 4 Critical | 4 | P0 | Brief: Low, Critical |
| RISK-B-05 | The 60 percent staffing reduction is not reachable at the planned escalation rate | addition (accepted finding) | The capacity model needs about 258 FTE by workload and 351 by seat cover in scenario A, and 383 and 466 at the 30 percent ceiling, against 180 agents left after a 60 percent replacement (`docs/escalation/queue-management.md` section 6.7; D-130, D-168) | 3 High | 3 High | 9 | P1 | The gap follows from the brief's own figures and the 15 separately staffed queues; it is likely unless escalation falls well below the ceiling |
| RISK-B-06 | After-hours P1 SLAs cannot be met by design | addition (accepted deviation) | Nine queues are closed from 22:00 to 08:00 IST (D-122); ESC-008, ESC-013 and ESC-015 raised at night cannot be picked up inside the A6 SLA | 3 High | 3 High | 9 | P1 | A6 gives SLAs with no hours exemption; the deviation is certain every night until staffing changes |
| RISK-B-07 | The containment target is missed, or met on paper by counting dropped conversations | addition | Abandoned conversations counted as contained; escalation suppressed to protect the figure | 2 Medium | 3 High | 6 | P1 | The brief sets 70 percent containment and under 30 percent escalation; the two are separate constraints (D-162) |
| RISK-B-08 | The CSAT target of 4.5 is not reached or cannot be shown | addition | A lift of 1.3 points from 3.2 is large; ratings come from about 15 percent of conversations and are biased toward extremes | 2 Medium | 3 High | 6 | P1 | The board's business case rests on the figure (A1.1) |
| RISK-B-09 | Running cost above a mid-stage start-up budget | addition | Token volume, long prompts, abuse traffic | 2 Medium | 2 Medium | 4 | P2 | E5 asks for reasonable cost; the cost model is sensitive mainly to model token volume |
| RISK-B-10 | The system launches with governance artefacts that nobody has reviewed | addition (known gap) | Most thresholds and processes in this repository are proposals; no committee has reviewed a prompt layer; layer 2 has had no legal review; the crisis template has had no clinical review (D-146) | 3 High | 3 High | 9 | P1 | Stated openly in the Day 13 open questions; without a gate an unreviewed artefact would ship by default |
| RISK-B-11 | Deliberate deviations from the brief's case studies are read as errors, or add friction | addition (accepted deviation) | The design does not accept an OTP typed in chat, offers a card block only after the fast OTP step, states no price or duration for the advisor offer, and commits to a date only from a tool result (D-153, D-94, D-16, D-09) | 2 Medium | 2 Medium | 4 | P2 | The numbered rules of A4.2 and the A9.2 penalties are taken to outrank the illustrative case studies |
| RISK-B-12 | Submission is judged against lists the brief never gives | addition (programme risk) | The "10 automatic failure conditions" and "7 deliverable requirements" are not enumerated; the rubric has no point allocation | 2 Medium | 3 High | 6 | P1 | An unlisted failure condition cannot be checked directly |
| RISK-B-13 | A handoff fails and the customer is left without a human | addition | Queue outage, no agent in the language, package not delivered, abandonment in the queue | 2 Medium | 3 High | 6 | P1 | The human route is the fail-safe for every other risk |

### 4.3 Controls, residual risk, owner, monitoring, contingency

| ID | Existing controls (repository references) | Residual L | Residual I | Residual | Band | Owner | Monitoring metric | Contingency |
|---|---|---|---|---|---|---|---|---|
| RISK-B-01 | Rolling CSAT and check-ins (`docs/learning-pipeline/csat-signals.md`), ESC-004 on sustained negative sentiment, A/B testing (`docs/learning-pipeline/ab-testing.md`), anti-pattern controls in `docs/architecture/conversation-design.md`, improvement cycle (`docs/metrics/improvement-cycle.md`) | 2 Medium | 2 Medium | 4 | amber | Head of Customer Experience | KPI-G1, KPI-G7, KPI-L4, KPI-A2 | Route the affected intent to humans; revert the candidate; improvement record |
| RISK-B-02 | 38 mapped obligations and GR-REG-01 to GR-REG-20 (`docs/guardrails/regulatory-mapping.md`), prompt layer 2, mandatory testing at gate G3, reports RPT-01 to RPT-04 (`docs/compliance/audit-logging.md` section 12), regulatory fast-track; quarterly regulatory audit (section 8.3 of this document, proposal) | 1 Low | 4 Critical | 4 | amber | Regulatory Compliance Manager; Chief Risk Officer | KPI-G6, DM-12, KPI-A3 | Compliance lead decides reportability (IR-D3); containment lever for the intent; matrix review through the fast-track |
| RISK-B-03 | DM-16 viral-risk indicator, runbook R6, tone guide and banned-phrase lint (D-148), TPL-ESC-CRISIS as fixed text, audit record to authenticate a circulating conversation (AQ-01) | 1 Low | 3 High | 3 | green | Brand Communications Director; Chief Risk Officer | DM-16, KPI-G1 | Runbook R6: authenticate against the audit record first, human-written holding statement; external listening is dependency IR-D4 |
| RISK-B-04 | 58 guardrails (`config/guardrails.yaml`), GR-SEC-R3, commitments only from a system of record (D-09, GR-OUT-05), the audit trail of `docs/compliance/audit-logging.md`; legal review and insurance are named by the brief and are not in place (IR-D5) | 1 Low | 4 Critical | 4 | amber | Chief Risk Officer | KPI-G6, DM-12 | Remediation lead contacts the customer; evidence pack under legal hold (D-87) |
| RISK-B-05 | Capacity model with sensitivities, overflow chains and callback mode (D-127), cross-skill lending, break-even points stated for the board, improvement cycle on containment | 3 High | 3 High | 9 | red | CTO with the Head of Customer Experience | KPI-O2, KPI-G4, EQ-07, EQ-10 | Phase the replacement; keep headcount until measured handling time and escalation rate support the reduction |
| RISK-B-06 | Stated as a deviation needing Risk Committee sign-off (D-163), callback and honest wording (TPL-ESC-AFTER-HOURS), P0 queues 24x7, EQ-07 reported in-hours and all-hours, on-call rota proposed for Enhanced Due Diligence and Compliance Helpdesk | 3 High | 2 Medium | 6 | amber | Chief Risk Officer (sign-off); queue owners | EQ-07, EQ-10 | Adopt the on-call rota if the all-hours attainment stays below the target |
| RISK-B-07 | KPI-G4 defined as resolved by the AI with no escalation record (D-162), counter-metric pairs (`docs/metrics/kpi-framework.md` section 8), de-escalation followed by a repeat contact counts as a missed escalation (D-125), EQ-02 | 2 Medium | 2 Medium | 4 | amber | Head of Customer Experience | KPI-G4, KPI-G3, KPI-A2, EQ-02 | Report containment with the non-escalated share and the dropped share side by side |
| RISK-B-08 | Weighted CSAT with response-rate reporting (D-99), predicted CSAT for silent conversations, post-escalation CSAT (EQ-12), experiments powered for 0.1 point (`docs/learning-pipeline/ab-testing.md`) | 2 Medium | 3 High | 6 | amber | Head of Customer Experience | KPI-G1, KPI-G5, EQ-12 | Report the weighted and raw figures with the sample; no target claim on under 30 ratings |
| RISK-B-09 | Template mode for 67 of 73 templates (D-144), caches, token budget (D-139), GR-ATK-08 and GR-ATK-09, cost model (`docs/architecture/latency-scalability-cost.md`); audit storage is about 1 percent of infrastructure cost (`docs/compliance/audit-logging.md` section 16) | 1 Low | 2 Medium | 2 | green | CTO | KPI-O4, DM-10 | Raise the template and cache share; model tiering |
| RISK-B-10 | Status column on every decision, approval gate G5, INV-12 (layers 3 and 4 need Risk Committee review), language release gate (D-145), `registry_status` fields in the config files | 2 Medium | 3 High | 6 | amber | Chief Risk Officer | KPI-A3, DM-13 | No launch for an intent, language or template whose owner has not signed; the list of open sign-offs is in `docs/compliance/submission-checklist.md` section 6 |
| RISK-B-11 | Each deviation is recorded with its reason (`config/templates/README.md` section 9), flagged for Risk Committee and CEB review, and covered by a test oracle | 2 Medium | 2 Medium | 4 | amber | Risk Committee and CEB | EQ-11, KPI-G5 | If the CEB prefers the case-study behaviour for the card block, D-94 is reopened; the OTP rule is not negotiable under A4.2 rule 5 |
| RISK-B-12 | Proxy lists (D-01, D-02), `docs/compliance/submission-checklist.md` with counts recomputed by `tests/compliance/validate_compliance.py`, draft questions in `docs/coordinator-questions.md` | 2 Medium | 2 Medium | 4 | amber | Project author | KPI-A3, DM-13 | Send the coordinator questions; treat every stated minimum as a failure condition |
| RISK-B-13 | Overflow chains and failed-handoff rules (D-123, D-127), two attempts per route, callback last, P0 to any available human, FMEA #15, TPL-ESC-HANDOFF-FAILED | 1 Low | 3 High | 3 | green | Queue owners; CX Team | EQ-06, EQ-10, EQ-07 | Incident for a failed P0 handoff; abandoned P0 cases stay open |

## 5. Ethical risk matrix (A11.3)

### 5.1 The brief's requirements, reproduced (pp.31-32)

The brief gives the ethical assessment as four groups of statements, without probability, impact or mitigation. Each statement is one risk row: the risk that the requirement is not met.

| # | Group | Brief text (A11.3) | Risk row |
|---|---|---|---|
| 1 | Fairness & Bias | "Agent must not exhibit differential treatment based on demographics, balance, or history" | RISK-E-01 |
| 2 | Fairness & Bias | "Escalation thresholds must be consistent across all customer segments" | RISK-E-02 |
| 3 | Fairness & Bias | "Product recommendations must not use discriminatory criteria" | RISK-E-03 |
| 4 | Fairness & Bias | "Candidates must specify bias detection and mitigation including statistical fairness testing" | RISK-E-04 |
| 5 | Transparency | "Customers must be informed they are interacting with AI at conversation start" | RISK-E-05 |
| 6 | Transparency | "Agent must never deny being AI or claim to be human" | RISK-E-06 |
| 7 | Transparency | "Agent must acknowledge uncertainty rather than presenting guesses as facts" | RISK-E-07 |
| 8 | Transparency | "Customers must have the right to request human assistance at any point" | RISK-E-08 |
| 9 | Accountability | "Every AI decision must be traceable to specific inputs, model versions, and KB entries" | RISK-E-09 |
| 10 | Accountability | "Accountability chain documented: who designed, who approved the model, who reviewed guardrails" | RISK-E-10 |
| 11 | Accountability | "Incident response procedures identify responsible parties for different failure modes" | RISK-E-11 |
| 12 | Privacy | "Collect only minimum information necessary to resolve customer query" | RISK-E-12 |
| 13 | Privacy | "Training data must be anonymised with customer consent" | RISK-E-13 |
| 14 | Privacy | "Never infer or store sensitive attributes (religion, politics, health) from conversations" | RISK-E-14 |
| 15 | Privacy | "Cross-customer data leakage must be architecturally impossible, not just policy-prohibited" | RISK-E-15 |

### 5.2 Assessment

Likelihood, impact and severity are the project's for every row in this matrix. The method behind the fairness, transparency, accountability and privacy controls is `docs/risk/fairness-testing.md`.

| ID | Risk | Origin | Cause | L | I | Inherent | Severity | Scoring rationale |
|---|---|---|---|---|---|---|---|---|
| RISK-E-01 | Differential treatment based on demographics, balance or history | brief A11.3 Fairness & Bias | A learned component picks up a proxy; a rule or a template is conditioned on a customer attribute; personalised thresholds (B4.1) are implemented literally | 2 Medium | 3 High | 6 | P1 | The brief gives no probability or impact for ethical risks; scored by the project. Systematic, hard to see without a test |
| RISK-E-02 | Escalation thresholds are not consistent across customer segments in effect | brief A11.3 Fairness & Bias | The thresholds are constants, but the models that feed them are less accurate in some languages, so the effective threshold differs | 2 Medium | 3 High | 6 | P1 | A constant threshold on an unequal model is unequal treatment |
| RISK-E-03 | Product information or recommendations use discriminatory criteria | brief A11.3 Fairness & Bias | The agent tailors product suggestions to age, gender, region or balance | 2 Medium | 4 Critical | 8 | P0 | A discriminatory recommendation is also personalised advice, which the brief forbids outright |
| RISK-E-04 | Bias goes undetected because the fairness tests lack data or power | brief A11.3 Fairness & Bias | The system holds no protected attributes by design; small slices never reach the sample size; only language and channel are observable | 3 High | 3 High | 9 | P1 | Without a specified method the default is no test at all |
| RISK-E-05 | Customers are not told they are talking to an AI at the start | brief A11.3 Transparency | A channel skips the greeting; a first message with an urgent request displaces the disclosure | 2 Medium | 3 High | 6 | P1 | A transparency duty in the brief and the stated relevance of the EU AI Act row of the appendix |
| RISK-E-06 | The agent denies being an AI or claims to be human | brief A11.3 Transparency | Role-play or jailbreak pressure; a persona prompt that is too human | 2 Medium | 3 High | 6 | P1 | Deception of a customer; a classic jailbreak target |
| RISK-E-07 | Guesses presented as facts | brief A11.3 Transparency | The model fills a knowledge gap fluently; a hedged range is stated as a date | 3 High | 3 High | 9 | P1 | The default behaviour of a language model; False Confidence costs 30 points in A9.2 |
| RISK-E-08 | A customer who asks for a human cannot reach one | brief A11.3 Transparency | The agent keeps trying to contain; queues are closed at night; no agent in the language | 2 Medium | 3 High | 6 | P1 | The brief gives the right "at any point" |
| RISK-E-09 | An AI decision cannot be traced to its inputs, model version and KB entries | brief A11.3 Accountability | A version is missing from a record; a KB revision is overwritten; logs are lost | 2 Medium | 3 High | 6 | P1 | Without the trace no other accountability control can work |
| RISK-E-10 | The accountability chain (who designed, who approved the model, who reviewed guardrails) is not documented with names | brief A11.3 Accountability | Roles are defined but role holders are not named; no committee review has taken place | 3 High | 3 High | 9 | P1 | The chain exists as roles only; every approval field in the manifest is still a draft |
| RISK-E-11 | Incident procedures do not identify who is responsible for a failure mode | brief A11.3 Accountability | A new failure mode has no runbook; the on-call rota is missing | 2 Medium | 3 High | 6 | P1 | Slow containment of a P0 event |
| RISK-E-12 | More information is collected than the query needs | brief A11.3 Privacy | The agent asks for details early or for reassurance; free text volunteers personal circumstances | 2 Medium | 3 High | 6 | P1 | Data that is not collected cannot leak |
| RISK-E-13 | Training data is used without consent or is not anonymised | brief A11.3 Privacy | A consent join fails open; a redaction miss reaches a dataset | 2 Medium | 4 Critical | 8 | P0 | A direct breach of the brief and of the consent duty the appendix attributes to the DPDP Act |
| RISK-E-14 | Sensitive attributes (religion, politics, health) are inferred or stored | brief A11.3 Privacy | A classifier or a summary records what a customer revealed; a care flag becomes a profile attribute | 2 Medium | 4 Critical | 8 | P0 | The brief says never |
| RISK-E-15 | Cross-customer leakage is prevented by policy only, not by architecture | brief A11.3 Privacy | Isolation depends on the model obeying an instruction | 2 Medium | 4 Critical | 8 | P0 | The brief requires architectural impossibility |
| RISK-E-16 | Hindi and Hinglish wording is not native-reviewed and secondary languages have no template text | addition (accepted deviation) | The authors are not native reviewers (D-145); KB facts are English only | 3 High | 3 High | 9 | P1 | Three primary languages are a brief requirement; unreviewed safety wording in the most used languages is likely to contain errors |
| RISK-E-17 | Language and sentiment models are less accurate for secondary languages and code-switched text | addition | Less training data; transliteration; mixed scripts | 3 High | 3 High | 9 | P1 | Leads to more premature or more missed escalations for those customers |
| RISK-E-18 | The one balance-based trigger (ESC-007) leaks into tone or quality | addition | High-value handling is generalised into better service for richer customers | 2 Medium | 2 Medium | 4 | P2 | ESC-007 depends on balance because A6 defines it so; nothing else may |
| RISK-E-19 | Allowed features act as proxies for protected groups | addition | Language, channel, time of day and interaction history correlate with region, age and income | 2 Medium | 3 High | 6 | P1 | Proxy effects are the usual route to indirect discrimination |
| RISK-E-20 | Vulnerable or low-literacy customers are served worse | addition | Jargon, long replies, widget-only steps, a customer who cannot use the app (persona Meera) | 2 Medium | 3 High | 6 | P1 | The CEB lists accessibility across literacy levels and languages (A1.3) |
| RISK-E-21 | Survey non-response hides the dissatisfaction of a group | addition | Only about 15 percent answer; response differs by channel and language | 3 High | 2 Medium | 6 | P2 | A group that does not answer surveys is invisible to a CSAT target |
| RISK-E-22 | Human reviewers or agents pass their own bias into labels, or over-trust the AI summary | addition | A reviewer labels one group's messages as rude; a human agent accepts a wrong package summary | 2 Medium | 3 High | 6 | P1 | Feedback is the input to learning; a biased label becomes a biased model |
| RISK-E-23 | A repeat contact is queued ahead of a first contact at the same deadline (history-based treatment) | addition (accepted deviation, D-121) | D-121 breaks a tie between handoffs with the same SLA deadline in favour of a customer with a recent contact on the same issue, while A11.3 asks for no differential treatment based on history | 2 Medium | 3 High | 6 | P1 | The brief names history in its fairness statement (p.31). The rule changes order only inside an identical deadline and never a threshold, a priority, a queue, an SLA or the wording (`docs/risk/fairness-testing.md` section 2), but it is still treatment by history, so it is recorded here with the check that watches it |

### 5.3 Controls, residual risk, owner, monitoring, contingency

| ID | Existing controls (repository references) | Residual L | Residual I | Residual | Band | Owner | Monitoring metric | Contingency |
|---|---|---|---|---|---|---|---|---|
| RISK-E-01 | GR-REG-17, thresholds as constants (D-121), invariant INV-08, feature exclusion list (`docs/learning-pipeline/data-pipeline.md` section 6), assignment by hash only, tests FT-01 to FT-05 and the pairs in `tests/compliance/fairness-pairs.yaml` | 1 Low | 3 High | 3 | green | Chief Risk Officer | FT-02, FT-03, EQ-01, EQ-02 | A failed pair blocks the release (GR-REG-17 is a release gate); a production gap above the margin opens a review |
| RISK-E-02 | Constants in `config/escalation_rules.yaml`, ESC-004 route for secondary languages (D-165), fairness margin of 2 points (`docs/intent-taxonomy/sentiment.md` section 9), AQ-13, FT-01, FT-04, ESC-007 as the only balance-based trigger and only because A6 says so | 2 Medium | 3 High | 6 | amber | Escalation owner; Risk Committee | FT-04, EQ-01, EQ-02, AQ-13 | Review within the weekly cycle; recalibrate the model per language through gates G1 to G9, never the threshold per segment |
| RISK-E-03 | The agent makes no recommendation at all: GR-ADV-01 to GR-ADV-09, no slot for a personal circumstance (GR-ADV-07), information-only templates TPL-ADV-BOUNDARY and TPL-ADV-COMPARE, promotions only as typed notices with a KB entry (D-140), test FT-10 | 1 Low | 4 Critical | 4 | amber | Regulatory Compliance Manager | FT-10, KPI-G6, DM-12 | Runbook R1 (advice-boundary breach) |
| RISK-E-04 | `docs/risk/fairness-testing.md`: tests FT-01 to FT-10, sample sizes, the restricted fairness view, counterfactual pairs that need no protected attribute, annual audit report RPT-03 | 2 Medium | 3 High | 6 | amber | Chief Risk Officer | FT-03, FT-06, DM-14 | State the minimum detectable gap beside every fairness figure; widen the window rather than drop the slice |
| RISK-E-05 | GR-REG-16, disclosure in the first agent reply of every conversation (D-152), TPL-GEN-GREETING and TPL-GEN-AI-DISCLOSURE, prompt layer 0, cases GR-REG-16-01 and GR-REG-16-02 | 1 Low | 3 High | 3 | green | Product | DM-01, FT-09 | Template fix through the layer 3 process; affected conversations found by AQ-03 |
| RISK-E-06 | GR-REG-16, prompt layers 0 and 1 (immutable), GR-ATK-03, Output Safety Layer check, cases GR-REG-16-01, GR-REG-16-02 and `tests/adversarial/jailbreak.yaml` | 1 Low | 3 High | 3 | green | Risk Committee | DM-08, DM-12 | Runbook R3; new suite case |
| RISK-E-07 | GR-OUT-03, GR-OUT-05, GR-REG-18, gap statement TPL-KB-GAP and TPL-KB-DEGRADE, retrieval decision `gap` or `degrade`, commitments only from a system of record (D-09), `tests/safety-suite/commitment-traps.yaml` | 1 Low | 3 High | 3 | green | NLU Team | KPI-G6, KPI-L5, DM-07 | Runbook R4 |
| RISK-E-08 | GEN-003, XTR-01 (handoff prepared on the first request, D-117), ESC-006, TPL-ESC-HANDOFF-WARM, Next Available Agent and General Support 24x7 (D-122), callback offer | 2 Medium | 2 Medium | 4 | amber | CX Team | EQ-10, EQ-07, KPI-O2 | Callback in the customer's language; after-hours gaps are RISK-B-06 |
| RISK-E-09 | Version tuple on every turn, `id@version` citations, traceability walk and AQ-01 (`docs/compliance/audit-logging.md` section 14), mechanism M7, immutable KB revisions | 1 Low | 3 High | 3 | green | Security Operations (audit bus owner) | AQ-01, AQ-09, DM-12 | A turn without a complete tuple is an audit finding |
| RISK-E-10 | Author, approval chain and model version per prompt layer (`config/system-prompt/manifest.yaml`), owner per guardrail and parameter, approvals at gate G5, RACI in `docs/risk/fairness-testing.md` section 8 | 2 Medium | 3 High | 6 | amber | Chief Risk Officer | KPI-A3, DM-13 | No release without the G5 record |
| RISK-E-11 | Roles and decision rights in `docs/guardrails/incident-response-playbook.md` section 3, runbooks R1 to R7, FMEA with a fallback per row, RACI in `docs/risk/fairness-testing.md` section 8 | 2 Medium | 2 Medium | 4 | amber | Chief Risk Officer | KPI-A4, DM-14 | Incident Commander assigns an owner in the first 15 minutes; IR-D1 open |
| RISK-E-12 | Required entities per intent (`config/intents.yaml`), Progressive Disclosure pattern, GR-REG-13, GR-ADV-07, the not-collected list in `docs/compliance/audit-logging.md` section 5.1, Authentication Theatre controls | 1 Low | 3 High | 3 | green | Data Protection lead | KPI-L3, DM-01 | Template or slot fix; scrub at dataset build |
| RISK-E-13 | Default exclusion without a positive P4 record (D-104), QG-02, QG-03, INV-09, anonymous conversations never used, cases SS-LRN-14 and SS-PII-07, AQ-15 | 1 Low | 4 Critical | 4 | amber | Data Protection lead | QG-02, QG-03, AQ-15 | Build fails; a recurring miss is an incident; models follow the deletion-only rebuild |
| RISK-E-14 | GR-REG-13 (discarded at the State Tracker), no such feature or label (`docs/learning-pipeline/data-pipeline.md` section 4), XTR-03 only on explicit disclosure with the note not stored on the profile (D-129), crisis handling as an event, not an attribute | 1 Low | 4 Critical | 4 | amber | Data Protection lead | QG-03, DM-12 | Purge the field; rule owner review |
| RISK-E-15 | As RISK-T-09: GR-SEC-R4, the customer key never model-controlled, tool-side re-check, retrieval pre-filter, per-customer keys (D-183); the prompt carries no other customer's data to leak | 1 Low | 4 Critical | 4 | amber | Information Security Officer | DM-12, AQ-12 | Runbook R2 at SEV0 |
| RISK-E-16 | Every variant marked `not_native_reviewed`, release gate per language and template (D-145), safety-critical replies fall back to Hindi or English, first translation set defined | 2 Medium | 3 High | 6 | amber | Head of Customer Experience; Risk Committee for safety text | FT-08, KPI-G1, EQ-05 | A language stays disabled for a template until a named native review is recorded |
| RISK-E-17 | English pivot with a quality floor, conservative fallback ladder (`docs/intent-taxonomy/language-detection.md`), ESC-004 route for secondary languages (D-165), EQ-01 and EQ-02 by language, 2-point margin | 2 Medium | 3 High | 6 | amber | NLU Team | FT-08, KPI-L2, EQ-01, EQ-02 | Honest language choice and a human in the customer's language or a callback |
| RISK-E-18 | D-121 (tier affects ESC-007 only), case ESC-T-007-02, the PEP and high-value flags are router-side and never enter a prompt (D-120), pairs FAIR-05 and FAIR-06 | 1 Low | 2 Medium | 2 | green | Escalation owner | FT-02, EQ-12 | Remove any tier-conditioned wording found in review |
| RISK-E-19 | Language and channel monitored as fairness slices, history may reorder a queue but never change a threshold (D-121), the ranker never sees auth, confirmation or escalation decisions (mechanism M6), slice rule in experiments | 2 Medium | 2 Medium | 4 | amber | Chief Risk Officer | FT-03, FT-05 | Remove or neutralise the feature; re-run FT-02 |
| RISK-E-20 | Plain-language rules and length calibration (`docs/architecture/conversation-design.md`), XTR-03 care flag on explicit disclosure only, human on request, callback, no inference of vulnerability from age, language or balance (D-129) | 2 Medium | 2 Medium | 4 | amber | UX Research Lead | KPI-G5, KPI-A6, FT-09 | Human handoff; wording fix through the layer 3 process |
| RISK-E-21 | Weighted CSAT by stratum, predicted CSAT for silent conversations, random review stream (`docs/learning-pipeline/csat-signals.md`), FT-06 on weighted figures | 2 Medium | 2 Medium | 4 | amber | Head of Customer Experience | KPI-G1, FT-06 | Report response rate per slice beside CSAT |
| RISK-E-22 | Double review and adjudication, kappa gate QG-04, reviewer outlier filter and QG-08, the package shows raw turns and scores beside the summary, FMEA #23 | 2 Medium | 2 Medium | 4 | amber | CX Team; Risk Committee | DM-14, KPI-A5, QG-04 | Hold the reviewer's labels out; re-adjudicate |
| RISK-E-23 | Rule limited to ties at the same deadline (`docs/escalation/queue-management.md`, D-121); counterfactual pair FAIR-15 (varies repeat_contact_7d: same action, priority, queue, SLA and wording on both sides, order examined inside the tie only); FT-02 (counterfactual invariance), FT-09 (parity of effort); the Risk Committee decision on D-121 stays open | 2 Medium | 2 Medium | 4 | amber | Chief Risk Officer; escalation owner | FT-02, FT-09, EQ-07 | Remove the tiebreak (order by deadline, then arrival) through safety change control; nothing else depends on it |

## 6. Heat maps

IDs are shown without the `RISK-` prefix. Each cell shows its score, its band and the number of risks in it.

```
Inherent risk (before the project's controls)

Impact      | L1 Low                            | L2 Medium                         | L3 High
------------+-----------------------------------+-----------------------------------+-----------------------------------
I4 Critical | score 4 amber n=5                 | score 8 red n=14                  | score 12 red n=1
            | T-05 T-14 B-02 B-03 B-04          | T-01 T-04 T-08 T-09 T-10 T-11     | T-07
            |                                   | T-13 T-17 T-18 T-19 E-03 E-13     |
            |                                   | E-14 E-15                         |
------------+-----------------------------------+-----------------------------------+-----------------------------------
I3 High     | score 3 green n=0                 | score 6 amber n=18                | score 9 red n=10
            |                                   | T-15 B-01 B-07 B-08 B-12 B-13     | T-02 T-12 B-05 B-06 B-10 E-04
            |                                   | E-01 E-02 E-05 E-06 E-08 E-09     | E-07 E-10 E-16 E-17
            |                                   | E-11 E-12 E-19 E-20 E-22 E-23     |
------------+-----------------------------------+-----------------------------------+-----------------------------------
I2 Medium   | score 2 green n=0                 | score 4 amber n=5                 | score 6 amber n=2
            |                                   | T-03 T-06 B-09 B-11 E-18          | T-16 E-21
------------+-----------------------------------+-----------------------------------+-----------------------------------
I1 Low      | score 1 green n=0                 | score 2 green n=0                 | score 3 green n=0
            |                                   |                                   |
```

```
Residual risk (with the specified controls)

Impact      | L1 Low                            | L2 Medium                         | L3 High
------------+-----------------------------------+-----------------------------------+-----------------------------------
I4 Critical | score 4 amber n=13                | score 8 red n=2                   | score 12 red n=0
            | T-01 T-04 T-07 T-08 T-09 T-10     | T-11 T-18                         |
            | T-13 B-02 B-04 E-03 E-13 E-14     |                                   |
            | E-15                              |                                   |
------------+-----------------------------------+-----------------------------------+-----------------------------------
I3 High     | score 3 green n=10                | score 6 amber n=9                 | score 9 red n=1
            | T-05 T-14 B-03 B-13 E-01 E-05     | T-17 T-19 B-08 B-10 E-02 E-04     | B-05
            | E-06 E-07 E-09 E-12               | E-10 E-16 E-17                    |
------------+-----------------------------------+-----------------------------------+-----------------------------------
I2 Medium   | score 2 green n=3                 | score 4 amber n=15                | score 6 amber n=1
            | T-03 B-09 E-18                    | T-02 T-12 T-15 T-16 B-01 B-07     | B-06
            |                                   | B-11 B-12 E-08 E-11 E-19 E-20     |
            |                                   | E-21 E-22 E-23                    |
------------+-----------------------------------+-----------------------------------+-----------------------------------
I1 Low      | score 1 green n=0                 | score 2 green n=1                 | score 3 green n=0
            |                                   | T-06                              |
```

| Band | Inherent | Residual |
|---|---|---|
| red (8 to 12) | 25 | 3 |
| amber (4 to 6) | 30 | 38 |
| green (1 to 3) | 0 | 14 |
| Sum of scores | 374 | 235 |

The sum of scores falls by 37.2 percent. That figure describes the register, not the system: it is the arithmetic of design-time judgements. 8 risks keep their inherent score (RISK-B-02, RISK-B-04, RISK-B-05, RISK-B-08, RISK-B-11, RISK-E-02, RISK-T-11, RISK-T-18): either the brief already scores the probability Low and the controls serve to hold it there, or no control in the design reduces the score and the row is a finding to be decided by its owner.

## 7. Top 10 residual risks and treatment plans

Ranked by residual score, then residual impact, then inherent score, then ID.

| Rank | ID | Risk | Inherent | Residual | Band | Treatment plan | Owner |
|---|---|---|---|---|---|---|---|
| 1 | RISK-B-05 | The 60 percent staffing reduction is not reachable at the planned escalation rate | 9 | 9 | red | No design control removes this risk; it is reported, not mitigated. Put the break-even table (180 FTE carry 14.1 percent escalation at the model's handling time) to the board. Measure real handling time per queue in the first quarter and rerun the model. Decide the reading of the 60 percent aim (headcount or interactions). Target residual: Medium x High after a phased plan is approved | CTO with the Head of Customer Experience | |
| 2 | RISK-T-11 | A true escalation trigger does not fire (missed escalation) | 8 | 8 | red | Measure EQ-02 on the random review stream from the first canary stage and report it by language. Hold the residual likelihood at Medium until one quarter of measured data shows a P0 miss rate inside the bound of `docs/escalation/queue-management.md` section 8. Add native-reviewed crisis and fraud cue lists per language before a language is enabled. Target residual: Low x Critical | Escalation owner (CX Team) with the Risk Committee | |
| 3 | RISK-T-18 | Volumetric (network-layer) denial of service takes the chat channels down | 8 | 8 | red | No control in this specification covers a volumetric flood, so the residual is reported, not mitigated. Name the platform and network owner, specify edge capacity, CDN, WAF and DDoS scrubbing for each channel, and test them with the hosting provider before the first canary stage. Prove the static status message and the human line under flood in the Day 15 failure drill. Target residual: Low x High | CTO with the Information Security Officer |
| 4 | RISK-B-10 | The system launches with governance artefacts that nobody has reviewed | 9 | 6 | amber | Turn the open questions of the decisions log into a sign-off register with an owner and a date per item, reviewed weekly by the Risk Committee until empty. Crisis text, layer 1 and layer 2 first. Target residual: Low x High | Chief Risk Officer | |
| 5 | RISK-E-04 | Bias goes undetected because the fairness tests lack data or power | 9 | 6 | amber | Agree the fairness view's data source and access list with the Risk Committee (open item in `docs/metrics/dashboards.md`). Generate the 1,320-pair counterfactual matrix and run it at gate G3 once a harness exists. Publish the minimum detectable gap with each slice. Target residual: Low x High | Chief Risk Officer | |
| 6 | RISK-E-10 | The accountability chain (who designed, who approved the model, who reviewed guardrails) is not documented with names | 9 | 6 | amber | Name the role holders (IR-D1, AL-D8) and record the first Risk Committee review of layers 0 to 2 and of the registry. The RACI is ready to receive names. Target residual: Low x High | Chief Risk Officer | |
| 7 | RISK-E-16 | Hindi and Hinglish wording is not native-reviewed and secondary languages have no template text | 9 | 6 | amber | Commission native review of the 73 templates in Hindi and Hinglish, safety-critical set first (crisis, fraud P0, do-not-share, OTP request, language choice, warm handoff). Add `body_i18n` to KB entries. Target residual: Low x Medium | Head of Customer Experience; Risk Committee for safety text | |
| 8 | RISK-E-17 | Language and sentiment models are less accurate for secondary languages and code-switched text | 9 | 6 | amber | Per-language evaluation sets and quality floors as release conditions for each secondary language; report FT-08 monthly. Target residual: Medium x Medium | NLU Team | |
| 9 | RISK-T-17 | A deletion request is not completed everywhere inside 30 days | 8 | 6 | amber | Obtain the legal reading of AL-D1 before launch. Run the planted-customer drill before the first canary stage and after every new store is added. Add downstream systems (AL-D5) to the reconciliation. Target residual: Low x High | Data Protection lead | |
| 10 | RISK-T-19 | Weakness in the vector and embedding store: a poisoned or cross-audience entry is retrieved, or the store itself is reachable (OWASP LLM08) | 8 | 6 | amber | Specify access control, network isolation, encryption and backup of the embedding store with the platform team. Run the retrieval-poisoning and cross-audience probes of the red-team gate (G4) against the real store, and keep customer data out of the index. Target residual: Low x High | Information Security Officer; platform team |

Also carrying a treatment plan although outside the top 10: RISK-B-06, RISK-B-08, RISK-E-02.

Reading of the list: the three red residual risks are not model risks. One is a staffing and capacity finding that follows from the brief's own figures, one is the detection of triggers that depend on a model reading distress or fraud in mixed-language text, and one is a platform dependency with no control in this specification (network-layer denial of service). The remaining seven are amber and share one cause: a control exists on paper and has not yet been reviewed, measured or staffed.

## 8. Risk appetite

### 8.1 Statement (proposal, D-187)

The brief sets hard targets; the appetite is derived from them and from the governance split of A1.3, in which the Risk Committee prevails on safety (`docs/stakeholder-analysis.md`).

| Class | Appetite | Brief source | What it means in practice |
|---|---|---|---|
| Incorrect financial information or advice | Zero | "0% incorrect financial advice rate" (A1.4); A4.1; the A9.2 AUTO-FAIL ("Stating non-existent product benefit or incorrect interest rate") | KPI-G6 target 0 percent. A single delivered case is an incident at SEV1 or higher. No experiment may trade it for CSAT |
| Account security: disclosure of identifiers or credentials, action without authentication, fund movement, cross-customer data | Zero | A4.2, the eight rules stated as NEVER; A11.3 privacy | Hard-zero counters DM-12. Residual likelihood must be Low before launch; residual impact stays Critical and is accepted only with the fail-closed design |
| Regulatory obligations the brief states | Zero for a known breach; low for uncertainty | A4.3; A10.3; appendix pp.70-71 | Uncertain regulatory answers go to ESC-008; a missing fact is said to be missing; the four reports are produced on time |
| Missed P0 escalation (fraud, account takeover, crisis, AML) | Zero | A6; A1.3 "fail-safe mechanisms that default to human escalation" | When in doubt, escalate. Premature escalation (10 points in A9.2) is accepted in preference to a missed P0 |
| Learning-pipeline changes | Zero for any change to the immutable layer; none released below 100 percent of the fixed suite | A5.4; A12.2 | Gates G0 to G9; KPI-A3 |
| Fairness | Low | A11.3 | No threshold conditioned on a segment; gaps above the 2-point margin are reviewed within the weekly cycle |
| Customer experience | Moderate | A1.4 (70 percent containment, CSAT 4.5); A8 | Targets may be missed for a period while safety holds. The CEB's goals are met inside the safe envelope, not by relaxing a guardrail |
| Speed and availability | Moderate | "<30-second first reply" (A1.4); A8.3 | Degrade to templates and to humans before failing; the 3 s engineering budget may be exceeded, the 30 s ceiling may not |
| Cost | Moderate | E5 | Template and cache use first; never by removing a safety check |

### 8.2 Acceptance rule

| Residual band | Rule |
|---|---|
| red | Not accepted by default. Needs a written acceptance by the Risk Committee with an expiry date of at most one quarter and a treatment plan (section 7) |
| amber | Needs a named owner, a monitoring metric and a treatment plan or a stated reason for none; reviewed quarterly |
| green | Monitored through its metric; reviewed yearly |

Whatever the band, a risk in a zero-appetite class may not be accepted with a residual likelihood above Low. By that rule RISK-T-11 (missed escalation, Medium x Critical) cannot be accepted as it stands and blocks the enabling of any language whose crisis and fraud cue lists are not reviewed.

### 8.3 Review cadence

| Review | Frequency | Who | Input |
|---|---|---|---|
| Register review | Quarterly, and after every SEV0 or SEV1 | Risk Committee, with the CEB for the business and experience rows | This file, incident reviews, measured metrics |
| Quarterly regulatory audit (the brief's mitigation for RISK-B-02; content is a proposal) | Quarterly | Regulatory Compliance Manager | Re-walk of the 38 obligations of `docs/guardrails/regulatory-mapping.md`, guardrail trigger and false-positive rates, the quarter's RPT-01 and RPT-02, open dependencies G-01 to G-09 and AL-D1 to AL-D8 |
| Fairness review | Monthly on monitoring data, yearly for the audit report | Chief Risk Officer | `docs/risk/fairness-testing.md` |
| Re-scoring | At each rollout stage (canary, 25 percent, full) | Risk owner | Measured likelihoods replace the judgements |

## 9. Frameworks the brief names (dependency G-09)

The brief's appendix describes two frameworks in one line each; nothing beyond those lines is asserted here.

| Framework (as the brief lists it) | Brief's relevance statement | How this document answers it | Still open |
|---|---|---|---|
| NIST AI Risk Management Framework (AI RMF 1.0) | "Risk identification, assessment, and mitigation framework for AI systems in financial services" | Identification: sections 3.2, 4.2 and 5.2 and the FMEA. Assessment: the scales of section 2 and the scores. Mitigation: sections 3.3, 4.3, 5.3 and 7 | A mapping to the framework's own structure and terms is left to the Chief Risk Officer; this repository does not reproduce the framework |
| EU AI Act - High-Risk AI Requirements | "Requirements for customer-facing AI in financial services; risk classification; transparency mandates" | Transparency: RISK-E-05 to RISK-E-08 and GR-REG-16. Risk classification: the design is built as if the high-risk requirements the brief refers to apply, which is the cautious reading | The formal classification of this system and whether the Act applies to NexBank at all are legal questions for the Regulatory Compliance Manager |

G-09 of `docs/guardrails/regulatory-mapping.md` is therefore narrowed, not closed.

## 10. Accepted deviations and findings from the decisions log

These rows exist so that a deviation recorded in a decision is also visible as a risk with an owner. None is accepted yet; each needs the sign-off named.

| Risk | Deviation or finding | Decision | Residual | Who must accept |
|---|---|---|---|---|
| RISK-B-05 | The 60 percent staffing reduction is not reachable at the planned escalation rate | D-130, D-168 | 9 red | CTO with the Head of Customer Experience |
| RISK-B-06 | After-hours P1 SLAs cannot be met by design | D-163, D-122 | 6 amber | Chief Risk Officer (sign-off); queue owners |
| RISK-B-11 | Deliberate deviations from the brief's case studies are read as errors, or add friction | D-153, D-94 | 4 amber | Risk Committee and CEB |
| RISK-E-16 | Hindi and Hinglish wording is not native-reviewed and secondary languages have no template text | D-145 | 6 amber | Head of Customer Experience; Risk Committee for safety text |
| RISK-T-18 | Network-layer denial of service has no control in this specification (gap by scope; platform dependency) | D-202 | 8 red | CTO with the Information Security Officer |
| RISK-T-19 | Access control and isolation of the embedding store (OWASP LLM08) are left to the platform design | D-202 | 6 amber | Information Security Officer; platform team |
| RISK-E-23 | The repeat-contact tiebreak of D-121 is treatment by history, which A11.3 asks the system not to apply | D-203, D-121 | 4 amber | Risk Committee and CEB |

Related, and already rows above: the legal-hold default against the deletion duty (D-87, RISK-T-17), the thin false-positive reserve (D-76, RISK-T-16), protective actions without a bus acknowledgement (D-185, RISK-T-14), and the reading of the customer-facing staff rule for handoff packages (D-186).

## 11. Decisions and open items

Decisions: D-187 (scales, severity rule, residual scoring, appetite and acceptance rule, review cadence). The fairness method is D-188. D-202 (RISK-T-18 and RISK-T-19: the two gaps by scope that Day 10 deferred to Day 14, with a named dependency and owner) and D-203 (RISK-E-23: the repeat-contact tiebreak recorded as an ethical risk with FAIR-15 as its check).

Open items:

1. Every score is a judgement. The first re-scoring is due at the first canary stage.
2. Owners are roles. Named role holders are dependencies IR-D1 and AL-D8.
3. Legal review and insurance for AI-caused loss (the brief's mitigation for RISK-B-04) are not in place (IR-D5).
4. The quarterly regulatory audit is proposed here and has no charter yet.
5. Risks outside the AI platform (the human channel's conduct after a handoff, core banking, telephony) are not in this register.
6. Network-layer DDoS protection (CDN, WAF, scrubbing, upstream capacity) is a platform dependency with no design in this repository. Owner: the CTO with the Information Security Officer. RISK-T-18 stays red until a platform control is specified and tested.
7. Access control, network isolation, encryption and backup of the embedding store (OWASP LLM08, store isolation) are a platform dependency with no design in this repository. Owner: the Information Security Officer with the platform team. RISK-T-19 is scored on the application-side controls only.
8. The OWASP LLM 2025 category names used for LLM08 and LLM10 were checked against the OWASP GenAI Security Project list on Day 15 and match.
