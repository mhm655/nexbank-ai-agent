# Guardrail Incident Response Playbook

Brief refs: A8.4 (detect within 15 minutes, DETECT/DIAGNOSE/DESIGN/DEPLOY/VALIDATE/DOCUMENT), A5.4 (circuit breaker, safety suite, immutable layer), A6 (ESC-001 to ESC-015, priorities P0 to P2, SLAs), A10.1 to A10.3 (log schema, encryption, access control, retention, deletion, regulatory reporting), A11.1 and A11.2 (hallucination P0, KB staleness P0, drift P1, reputational damage and viral conversations), A11.3 (accountability: "incident response procedures identify responsible parties for different failure modes"), A12.3 (guardrail_strictness_level, change owners), A9.2 (AUTO-FAIL items). Brief Part D, Day 9-10 (incident response playbook). Registry: `config/guardrails.yaml`. Companion docs: `output-safety-layer.md`, `monitoring-dashboard.md`, `financial-advice.md`, `account-security.md`, `regulatory-mapping.md`.

**Status.** The brief asks for the playbook and names its content (severity levels, owners, containment, customer remediation, regulatory notification) but gives no incident timings, no named people and no external notification deadlines. Severity timings and role assignments below are proposals (D-83); notification duties not in the brief are listed as dependencies with an owner, not invented (D-84). Decisions: D-83 to D-89.

## 1. Principles

1. **Contain first, investigate second.** The first move is the least disruptive lever that stops further harm; diagnosis follows (the same logic as the contain-first card block, disambiguation pair 6).
2. **Levers move toward safety only.** Any on-call responder may tighten (roll back, template-only, disable a flow). Loosening a guardrail, raising a threshold or restoring a lever needs the Chief Risk Officer (Risk Committee approval where A12.3 requires it) (D-86).
3. **The agent never fixes money.** Remediation that moves funds, reverses charges or changes records is done by authorised human staff; the agent never initiates a transfer (GR-SEC-R3) and never states a remedy it cannot back (GR-OUT-05).
4. **Preserve before you change.** Snapshot evidence (section 8) before a rollback overwrites versions or a purge removes data.
5. **Fix at the right layer.** Fixes to the rule layer, thresholds and prompt layers 0-2 go through safety change control, never through the learning pipeline (GR-SYS-02, D-58). KB, prompt layers 3-5 and thresholds the pipeline owns follow their own gates.
6. **Every incident leaves a test.** A closed incident adds at least one case to the fixed safety suite (at least 200 cases, A5.4) and a registry or document update where a gap was found.

## 2. Severity levels

SEV0 to SEV3 align with the priorities the brief already uses: ESC priorities P0, P1, P2 (A6) and the risk severities P0, P1, P2 (A11). SEV0 and SEV1 are the two incident-grade levels of P0; SEV2 and SEV3 map to P1 and P2.

| Level | Aligns with | Definition | Examples | Targets (proposal): acknowledge / contain / first Risk Committee briefing |
|---|---|---|---|---|
| SEV0 | P0, "Critical" impact | Customer harm or regulatory exposure has occurred or is actively occurring and is not bounded | a transfer or write executed without authority; full credential, card or another customer's data delivered; advice or a wrong financial figure delivered at scale; a successful jailbreak that bypasses CRITICAL guardrails; an immutable layer changed by the learning pipeline | 5 min / 30 min / 1 hour |
| SEV1 | P0 | A CRITICAL guardrail was breached, but the blast radius is known and bounded (one or few conversations), or a SEV0 is likely if not contained | one delivered hallucinated rate (A9.2 AUTO-FAIL) found in sampling; one advice-boundary breach; one PII slip of masked-form data; circuit breaker trip on a hard-zero counter | 15 min / 2 hours / 4 hours |
| SEV2 | P1 | A HIGH guardrail breach or a systemic degradation without customer harm confirmed | commitment or tone violations delivered; OSL over-blocking above the gate (E2E FP at 3 percent or more); drift at or above 0.05; guard latency breach for over 10 minutes | 1 hour / 1 working day / next weekly review |
| SEV3 | P2 | Near-miss or contained event; no delivery of a violating response | OSL caught a violating draft; blocked attack; one-off classifier error found in review | next working day / 5 working days / weekly dashboard |

Rules: when unsure, declare the higher level and downgrade after triage. Severity is set by impact, not by cause: the same prompt-injection is SEV3 if blocked and SEV0 if it caused a disclosure. A delivered AUTO-FAIL figure (A9.2) is at least SEV1. A hard-zero counter above 0 (monitoring-dashboard.md DM-12) opens at SEV1 or higher at once. The customer-facing escalation SLAs of A6 (ESC-001 and ESC-009 under 2 minutes, ESC-011 immediate) apply to customer handoffs; they are not incident response times, but an incident with an affected customer in progress creates the matching ESC record in parallel.

## 3. Roles and owners

Named individuals, the on-call rota and paging tools are not in the brief; they are dependencies (section 7, IR-D1). Roles are drawn from the governance structure in A1.3 and the A12.3 owners.

| Role | Held by (proposal) | Duties |
|---|---|---|
| Incident Commander (IC) | on-call lead from the ML Team or platform, one per incident | declares severity, runs the timeline, authorises tightening levers, hands over explicitly |
| Technical lead | ML Team (generation, classifiers), NLU Team (input side), KB owners | diagnosis by component (A8.4 DIAGNOSE), rollback, fix |
| Security lead | Information Security Officer; Security Operations | adversarial incidents, data exposure, evidence handling, key and access control |
| Compliance lead | Regulatory Compliance Manager; Compliance Helpdesk (ESC-008 queue) | decides reportability, regulator contact, wording of any regulatory statement |
| Risk owner | Chief Risk Officer | approves loosening or restoring levers, closes SEV0 and SEV1, informs the Risk Committee |
| CX and communications lead | Head of Customer Experience; Brand Communications Director | customer messaging, viral response, CEB briefing |
| Remediation lead | Customer operations lead with Relationship Manager and Senior Resolution Manager queues | contacts affected customers, applies human-approved remedies |
| Scribe | a second on-call | timestamps every decision and lever |

Decision rights: IC may engage levers 1 to 6 (section 4) alone; lever 7 (kill switch) needs the IC and one of the Security lead, Compliance lead or Risk owner, and is reported to the Risk owner at once; restoring any lever needs the Risk owner. SEV0 and SEV1 are briefed to the Risk Committee members (Chief Risk Officer, Regulatory Compliance Manager, Information Security Officer); tone and viral incidents also brief the Customer Experience Board.

## 4. Detection and triage

### 4.1 Detection sources

| Source | Examples | Target |
|---|---|---|
| Dashboard alerts | hard-zero counters, trigger-rate anomalies, FP, latency, drift, circuit breaker (monitoring-dashboard.md section 6) | visible within 15 minutes of occurrence (A8.4) |
| Audit sampling and review | delivered turns with no trigger; near-misses | daily |
| Escalation signals | ESC-002 (legal threat), ESC-001, ESC-009, ESC-005, ESC-008, complaints mentioning wrong information | real time |
| Human staff | supervisors, Compliance Helpdesk, Wealth Advisory advisors | any time |
| Red team and tests | safety suite failure, adversarial test regression | per run |
| External | media, social platforms, regulator queries (48-hour response duty, A10.3) | dependency IR-D4 |

### 4.2 First 15 minutes

1. Anyone who suspects an incident opens it in the incident channel (dependency IR-D1) with: what, where (conversation ids or turn ids), when, and the guardrail IDs seen.
2. IC is named; Scribe starts the timeline.
3. Triage: is a violating response delivered (yes: at least SEV1)? Is it still happening (check the heat map cell and the release strip)? Is there customer impact or an executed action (SEV0 candidate)? Is the cause a recent change (rollback candidate)?
4. Set severity (section 2), tell the roles required for that level, and start evidence preservation (section 8) before changing anything.
5. Pick the first containment lever (section 5).

## 5. Containment

Levers are ordered from least to most disruptive. The kill switch and template-only mode are design choices not defined in the brief; they were proposed as GR-SYS-04 (D-86) and are now registered (D-90).

| # | Lever | Effect | Who may pull | Side effects | Restore |
|---|---|---|---|---|---|
| 1 | Feature-flag rollback of the latest change (prompt layers 3-5, thresholds, model version, KB epoch pointer) | returns to the last known good version | IC | candidate improvements lost | Risk owner after the fix passes the safety suite |
| 2 | Circuit breaker (automatic) | rolls back a canary stage on a metric breach (monitoring-dashboard.md section 8) | automatic; IC confirms | freezes further stages | Risk owner |
| 3 | Disable one flow or intent | the intent goes to a safe template or escalation (for example PRD-005 stays advice-boundary only; a faulty write intent routes to a human queue) | IC | more human load; ESC-014 or ESC-003 style handoffs | IC after fix |
| 4 | KB quarantine of an entry or tag | affected entries leave retrieval (status `expired`, D-46 quarantine) | KB owner on IC's order | gap handling takes over (ESC-008 for regulatory) | KB approval chain |
| 5 | Template-only mode (global or per intent) | no free-form LLM text; hybrid slots only; the OSL still runs | IC | flatter conversations, lower CSAT; lowest risk of new violations | Risk owner |
| 6 | Raise `guardrail_strictness_level` to CRITICAL (A12.3 range) | stricter thresholds on configurable guardrails | IC with Risk owner (A12.3 says Risk Committee approval is required; a standing pre-approval for raising only is proposed, D-86) | more false positives, watched against the 3 percent gate | Risk Committee |
| 7 | Kill switch | the agent stops serving; the static status message and the human line are shown; open conversations are handed to human queues (FMEA #24 fallback) | IC plus one of Security lead, Compliance lead, Risk owner | full loss of containment; queue overload risk, honest wait message (FMEA #2) | Risk owner |
| 8 | Block high-risk and payment actions | write tools disabled at the Tool Orchestrator | IC | no protective actions by the agent; card-block requests go to a human (ESC-001) | Risk owner |

In all cases: confirm the lever worked by watching the heat map cell and the relevant hard-zero counter for two clean windows; record the lever time in the timeline.

## 6. Customer remediation

1. **Identify affected customers** from the audit record: conversations with the guardrail ID in `guardrails_activated`, the affected `model_version` or prompt_version, the time window from the first bad deployment to containment, plus text search over `agent_response` for the violating pattern. Count by severity of harm: information only, decision likely made on it, financial effect, data exposure.
2. **Immediate protection:** exposed credential or card: the customer is told to change it and protective action is offered with confirmation (GR-SEC-R5, D-08); suspected misuse is ESC-001 (P0, Fraud Investigation); unauthorised access is ESC-009 (P0, Security Operations).
3. **Correction:** a human (Remediation lead) contacts affected customers through an approved channel with a pre-approved, factual correction. AI-generated outreach is not used for SEV0 and SEV1.
4. **Remedies:** goodwill, fee reversal, loss refund and dispute handling are human, business-owned decisions (Risk owner and Relationship Manager); the playbook does not set amounts. Disputes above INR 50,000 go to ESC-005 (P1).
5. **Grievance:** grievance redressal information is given within 2 turns of any complaint (GR-REG-03); a legal threat is ESC-002; severe distress is ESC-011.
6. **Records:** every remediation is a complaint ticket with category and timestamps so that it appears in the quarterly Ombudsman analysis (GR-REG-19).
7. **Closure check:** each affected customer has a recorded outcome (contacted, corrected, no response after the attempts defined by the Remediation lead, remedy given or declined).

## 7. Regulatory notification

The brief states these reporting duties (A10.3); it states **no** deadline for notifying a regulator of an AI incident or data breach. Nothing else is asserted here.

| Obligation in the brief | Timing in the brief | Incident relevance | Owner |
|---|---|---|---|
| Ad-hoc regulatory query responses | within 48 hours of receipt | an incident that prompts a regulator query is answered inside 48 hours; the evidence pack (section 8) is prepared to make that possible | Regulatory Compliance Manager |
| Monthly AI interaction summary for RBI | monthly | content specified: volume, escalation rates, complaint categories; whether incident counts are added is not specified (IR-D2) | Chief Risk Officer |
| Quarterly customer complaint analysis per Banking Ombudsman requirements | quarterly | remediation tickets feed it (GR-REG-19) | Chief Risk Officer |
| Annual AI system audit report | annual | covers accuracy, fairness and safety metrics; incidents and their closure are evidence for it | Chief Risk Officer |
| Right-to-deletion requests | processed within 30 days; deletion includes backups, derived data and training data; certificates stored | interacts with evidence preservation (D-87) | Data Protection lead |

Dependencies (not closed by this document; no timelines asserted):

| ID | Dependency | Safe default meanwhile | Owner |
|---|---|---|---|
| IR-D1 | Incident channel, on-call rota, paging tool and named role holders | roles in section 3 are the interim assignment | Chief Risk Officer |
| IR-D2 | Whether and how incidents are reported inside the monthly RBI summary and the annual audit report | record every incident with category, severity and closure so any format can be filled later | Regulatory Compliance Manager |
| IR-D3 | Any statutory or contractual duty and deadline to notify a regulator, card scheme, partner or affected customer after a data exposure, advice breach or payment-security incident (RBI, SEBI, IRDAI, PCI DSS, DPDP; the matrix mechanics for DPDP are G-05 in `regulatory-mapping.md`) | SEV0 and SEV1 go to the Compliance lead at once, who decides reportability; customers are told only what Compliance has approved; no deadline is quoted to anyone | Regulatory Compliance Manager with Information Security Officer |
| IR-D4 | External monitoring of media and social platforms for viral conversations | internal indicator DM-16 only | Brand Communications Director |
| IR-D5 | Legal review and insurance position for AI-caused customer loss (A11.2 lists legal review and insurance as mitigations) | escalate to the Risk owner | Chief Risk Officer |

Statements to regulators, the press or customers are never generated by the agent and are approved by the Compliance lead (regulators) or the CX and communications lead (customers and press).

## 8. Evidence preservation (A10)

Preserve before rollback. The evidence pack is assembled by the Security lead; the Scribe records who accessed what (meta-audit trail, A10.3).

| Item | Source | Notes |
|---|---|---|
| Conversation records for each affected `conversation_id` | audit store, A10.1 fields: `customer_id` (hashed), `channel`, `authentication_level`, `primary_intent`, `resolution_status`, `guardrails_activated`, `model_version`, `turn_count`, `pii_detected` | legal-hold flag set; retention otherwise 7 years |
| Turn-level records | A10.2 fields: `turn_id`, speaker, encrypted `raw_message` with PII redacted, `intent_classification`, `entities_extracted`, `sentiment_score`, `knowledge_items_retrieved`, `retrieval_confidence`, `agent_response`, `response_generation_method`, `guardrails_checked`, `guardrails_triggered`, `response_latency_ms`, `action_taken` | exported read-only, hashed on export |
| OSL verdicts and the failed draft | `SafetyVerdict` per check, rung reached, draft text (encrypted, PII redacted) | shows whether the OSL caught, repaired or missed it |
| Version tuple | prompt_version, model_version, KB entry versions and epoch, rules version, flag state, thresholds | captured before rollback |
| Tool calls | `ToolCall` and `ToolResult` with idempotency keys, `auth_proof` results, Tool Orchestrator re-check outcomes | proves what executed |
| Circuit breaker readings and dashboard snapshot | metrics at trip time, heat map, release strip | |
| Configuration diff | difference between the last good and the bad version | |
| Timeline and decisions | Scribe log, lever times, approvals | |

Handling: all evidence stays under AES-256 at rest and TLS 1.3 in transit, PII fields under the separate key (double encryption), keys rotated quarterly through the HSM (A10.3); access by least privilege, logged; copies are made only inside the controlled store; export hashes and a custody list are kept. Tamper-proof logging is a Risk Committee concern (A1.3); a gap in bus sequence numbers during an incident is itself a finding (FMEA #21).

Retention and deletion: incident evidence follows the 7-year retention of the schema. The brief requires deletion within 30 days of a right-to-deletion request including derived data; whether incident evidence under hold may outlast a deletion request is a legal question the brief does not answer (D-87). Safe default: do not delete evidence under hold, tell the Data Protection lead and the Compliance lead the same day, and record the decision with the deletion certificate.

## 9. Post-incident review

- **Timing (proposal):** blameless review within 5 working days of closure for SEV0 and SEV1, 10 working days for SEV2, weekly dashboard review for SEV3.
- **Content:** timeline from first bad deployment to containment; detection gap (why not within 15 minutes); root cause by component as in A8.4 DIAGNOSE (NLU, retrieval or KB, generation, escalation logic, Output Safety Layer, learning pipeline, tool authorisation); contributing factors; what worked; customers affected and remediation status; regulatory decisions (Compliance lead).
- **Actions:** each with owner and due date: fix and its change path (KB edit, prompt layer 3-5, threshold, model, or, for the rule layer, thresholds and layers 0-2, safety change control with HITL and Risk Committee approval); new test cases (IDs in the reserved style `<guardrail ID>-<NN>`, added to the fixed suite); registry or document updates; dashboard alert changes.
- **Loop:** follows DESIGN, DEPLOY (staged, A/B where customer-facing), VALIDATE (monitor for the side effects), DOCUMENT (A8.4). Safety fixes propagate immediately, quality fixes daily, style fixes weekly (A5.1).
- **Accountability:** the review records who designed the guardrail, who approved the model and who reviewed it (A11.3 accountability chain).
- **Closure:** Risk owner signs SEV0 and SEV1; the Risk Committee receives the report; learnings enter the maintenance record.

## 10. Runbooks

Common sequence for every runbook: declare, preserve (section 8), contain (section 5), investigate, remediate (section 6), assess notification (section 7), review (section 9). The tables give what is specific.

### R1 Advice-boundary breach

| Item | Content |
|---|---|
| Guardrails | GR-ADV-06 (output), GR-ADV-01 to GR-ADV-05, GR-ADV-09, GR-REG-20, GR-OUT-03 |
| Indicators | OSL near-miss or sampled delivered turn with a recommendation, suitability verdict or return prediction (the six A4.1 categories); customer says the bank "told me to invest"; Wealth Advisory (ESC-013) reports a customer quoting the agent; any claim of advisory registration |
| Default severity | SEV1 for a single delivered breach; SEV0 if repeated across customers, if the agent claimed to be an advisor, or if a customer acted on it with loss |
| Immediate | search `agent_response` for the signals of `financial-advice.md` section 4.2 in the window; check which check missed it (classifier, rule, OSL threshold) |
| Containment | lever 5 for PRD-001 to PRD-005 (information-only templates plus the ESC-013 offer); lever 1 if a release is implicated; never lower thresholds |
| Remediation | human contact with a neutral correction ("that was general information, not advice") and an offer of ESC-013 Wealth Advisory; no personalised advice from the agent as a substitute |
| Notification | Compliance lead decides (IR-D3); SEBI robo-advisory relevance is mapped in `regulatory-mapping.md` section 2.5 |
| Closure | cause fixed through safety change control; added tests in GR-ADV-06 range; 7 days with DM-12 advice counter at 0 (proposal) |

### R2 PII leak

| Item | Content |
|---|---|
| Guardrails | GR-OUT-02, GR-SEC-R1, GR-SEC-R4, GR-SEC-R5, GR-REG-05, GR-REG-06, GR-REG-13 |
| Indicators | OSL mask or block on RED-01 to RED-07 patterns in a draft; `pii_detected` anomaly; customer reports seeing another person's details; full identifier found in a stored log (log leak) |
| Default severity | SEV0 for another customer's data, a credential or a full card or CVV delivered, or a full identifier in logs; SEV1 for last-four formatting errors and masked-form slips |
| Immediate | stop the leak path: lever 8 if tool data is the source, lever 5 otherwise; identify the source (tool field, KB text, LLM, state, log writer); check isolation controls (A11.3: cross-customer leakage must be architecturally impossible, so any occurrence is a design defect) |
| Containment | disable the offending field or tool scope; purge only after preserving evidence under hold (D-87); rotate keys only on the Security lead's decision |
| Remediation | affected customers contacted by a human; credential or card exposure: customer instructed to change the credential and offered a confirmed protective block (GR-SEC-R5, D-08, ESC-001); suspected misuse ESC-001; unauthorised access ESC-009 |
| Notification | Compliance lead and Information Security Officer decide under IR-D3 (DPDP mechanics G-05, PCI DSS G-06); no timeline quoted |
| Closure | root cause fixed at both the producing component and the OSL; GR-OUT-02 regression case added; leak counters at 0 for 14 days (proposal) |

### R3 Successful prompt injection or jailbreak

| Item | Content |
|---|---|
| Guardrails | the GR-ATK family for the A4.4 vectors (GR-ATK-01 to GR-ATK-11; defences in `adversarial-defences.md`), GR-SEC-R8, GR-SYS-02, GR-OUT-01 to GR-OUT-05 as backstops |
| Indicators | a sampled turn shows a response that follows an instruction from user text or retrieved content; policy statements revealed; persona broken; a guard flag bypassed; repeated attempts from one session or many (DM-08) |
| Default severity | by consequence: SEV0 if an action, disclosure or CRITICAL violation resulted; SEV1 if policy text or a rule was bypassed without harm; SEV2 to SEV3 if contained by a downstream layer |
| Immediate | isolate the session(s); extract the payload and the path (user text, tool output or retrieved passage); search all sessions for the same pattern or indicator |
| Containment | lever 3 or 5 for the flows exposed; KB quarantine (lever 4) if a passage carried the payload; block the actor's sessions under Security Operations rules; defence updates to the rule layer or Input Guard go through safety change control (GR-SYS-02), not the learning pipeline |
| Remediation | if any customer was affected, R2 or R5 applies in parallel |
| Notification | Security lead decides with Compliance lead (IR-D3) |
| Closure | the payload and 3 or more variants added to the adversarial suite; defence-in-depth gap identified (which of the layers L1 to L5 should have caught it); red-team retest passes |

### R4 Hallucinated figure

| Item | Content |
|---|---|
| Guardrails | GR-OUT-01, GR-OUT-03, GR-OUT-05, GR-REG-01 |
| Indicators | delivered rate, fee, limit, tenure or benefit that is absent from or conflicts with the KB or the tool result; a product that does not exist (A9.2 AUTO-FAIL); sampled review; customer or advisor complaint; Compliance Helpdesk finding |
| Default severity | SEV1 for a single delivered case; SEV0 if systemic or if customers acted on it |
| Immediate | classify the source: generator invented it, stale or wrong KB entry (A11.1 KB staleness P0), wrong tool data, or OSL false negative |
| Containment | stale or wrong KB entry: quarantine (lever 4) and correct through the KB chain (D-46); generator: lever 5 for factual intents so figures come only from locked slots; OSL miss: tighten through safety change control |
| Remediation | affected customers receive the correct figure from a human; whether a commercial remedy is owed is a business decision of the Risk owner |
| Notification | Compliance lead decides (IR-D3) |
| Closure | the missed pattern added to the GR-OUT-01 and GR-OUT-03 corpus; extraction recall re-measured; DM-12 figure counter 0 for 14 days (proposal) |

### R5 Unauthorised action

| Item | Content |
|---|---|
| Guardrails | GR-SEC-R2, GR-SEC-R3, GR-SEC-R4, GR-SEC-R6, GR-REG-08, GR-REG-14, GR-SYS-02 |
| Indicators | a write executed without the required authentication level, a protective action without explicit confirmation, a transfer, payment or record change attributed to the agent, a Tool Orchestrator re-check that failed after the Policy Engine allowed the call, a security-critical intent not escalated |
| Default severity | SEV0 |
| Immediate | lever 8 (block writes) at once; confirm whether funds moved (the agent never moves funds, so a movement points to a tool or authorisation defect); ESC-001 (fraud) or ESC-009 (unauthorised access) for the affected customers |
| Containment | disable the tool scope; preserve `ToolCall` and `auth_proof` evidence; check idempotency keys for duplicates (FMEA #14) |
| Remediation | reversal and recovery by authorised human teams; reversible protective actions undone with the customer's consent; compensation per Risk owner |
| Notification | Compliance lead and Information Security Officer under IR-D3 (payment security G-06) |
| Closure | both the Policy Engine decision and the independent tool-layer re-check explain the miss; fix reviewed by the Security lead; added tests in GR-SEC ranges; writes restored only by the Risk owner |

### R6 Viral or reputational incident

| Item | Content |
|---|---|
| Guardrails | GR-OUT-04, GR-REG-04, GR-OUT-01 to GR-OUT-05 (the content that caused it); A11.2 requires quality monitoring, crisis response and detection of potentially viral conversations |
| Indicators | DM-16 flags; a customer says they will publish a screenshot; a conversation circulating externally (IR-D4); journalist or regulator enquiry; sudden cluster of complaints quoting the same reply |
| Default severity | by reach and content: SEV1 for a circulating conversation with a factual or tone fault; SEV0 if it shows a CRITICAL breach (advice, data exposure, unauthorised action) or reaches the press or a regulator |
| Immediate | authenticate the material against the audit record (is it a real turn, edited, or fabricated; which version produced it); do not confirm or deny publicly before that is established |
| Containment | if the behaviour is real and systemic: the relevant runbook R1 to R5 and levers 1 to 5; if a tone fault: lever 1, phrase table update, lever 5 for the intent |
| Communication | holding statement and responses written and approved by humans (CX and communications lead; Compliance lead for regulatory content); the agent posts nothing publicly; contact the customer concerned personally (Senior Resolution Manager queue, ESC-002 if a legal threat) |
| Remediation | as section 6 for customers affected beyond the one in the post |
| Closure | public and internal timeline documented; a monitoring gap analysed (why was it not caught as DM-16 before posting); CEB briefed |

### R7 Learning-pipeline regression

| Item | Content |
|---|---|
| Guardrails | GR-SYS-02, GR-SYS-03; the safety suite and circuit breaker (A5.4); FMEA #22 (bad update) and #23 (feedback poisoning) |
| Indicators | circuit breaker trip; safety suite below 100 percent; hard-zero counter in a canary cohort; drift at or above 0.05; trigger-rate shift correlated with a candidate release; anomaly in supervisor corrections (poisoning); any attempted change to a rule, threshold or layers 0-2 from the pipeline |
| Default severity | SEV1 if rolled back automatically with no delivered violation; SEV0 if a violation reached customers or an immutable element was changed |
| Immediate | confirm automatic rollback completed (lever 2); freeze promotion of all candidates; snapshot candidate, data batch and gate results |
| Containment | quarantine the feedback batches and reviewers' labels under suspicion; revert to the last version that passed the full suite; keep the pipeline in read-only mode until the cause is known |
| Investigation | which gate should have caught it and why not; was the suite stale; sampled review coverage; if an immutable element changed, treat as a gate defect (GR-SYS-02 must have rejected it) |
| Remediation | as the violation type requires (R1 to R5) |
| Closure | the missed case becomes a fixed-suite case; gate repaired; staged rollout resumes from 1 percent; Risk owner approves the restart |

## 11. Exercises and maintenance

Drills (proposal): each lever is drilled in a non-production environment at least quarterly, including the kill switch and rollback (rollback drills follow the circuit-breaker drill cadence of the learning pipeline); one tabletop per runbook per year, rotating; a viral-incident tabletop with the CEB. After a drill the playbook, owners and thresholds are updated. The playbook is reviewed after every SEV0 or SEV1 and whenever the registry gains a guardrail family.

## 12. Open items

1. IR-D1 to IR-D5 (section 7) need owners to supply the facts; until then the safe defaults apply.
2. Severity targets, review timing, the standing pre-approval for raising strictness and the evidence-hold rule are proposals (D-83, D-86, D-87).
3. Registry additions proposed here, GR-SYS-04 (kill switch and template-only mode control) and GR-OUT-06 (no delivery without a verdict), are now in `config/guardrails.yaml` (D-90); the approval rules remain proposals (D-86).
4. Customer-facing wording for corrections and holding statements is written by humans in the incident; the pre-approved correction message is `TPL-SYS-CORRECTION` (`config/templates/support.yaml`).
