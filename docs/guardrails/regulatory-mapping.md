# Regulatory Mapping Matrix

Brief refs: A4.3 (regulatory compliance guardrails), "Regulatory Reference Summary" (appendix, pages 70-71), A10 (regulatory reporting, retention), A11.3 (ethical risk), A13.1 (product regulatory column), Part B badge "The Regulator" (RBI, PCI DSS and KYC/AML mapping with zero compliance gaps). Registry: `config/guardrails.yaml`. KB: `docs/knowledge-base/entries/regulatory.yaml` (KB-REG-001 to KB-REG-011) and the `regulatory_tags` on all 77 entries. Companion docs: `financial-advice.md`, `account-security.md`.

Rule for this document: **only the regulations and obligations the brief states are claimed.** Where the brief gives a regulation only a one-line relevance statement, the obligation is that statement; what the brief does not say is listed as a residual dependency with an owner (section 6), never filled in from memory (project delivery risk: hallucinated regulations are an AUTO-FAIL, brief A9.2).

## 1. Sources and status

| Regulation or guideline (as the brief lists it) | Authority | Brief's relevance statement | KB tag |
|---|---|---|---|
| Master Direction on Digital Payment Security Controls (April 2024) | Reserve Bank of India | End-to-end encryption for all digital payment channels including AI-assisted transactions | RBI_DIGITAL_PAYMENT_SECURITY |
| Circular on Responsible AI in Financial Services (**Draft, 2025**) | Reserve Bank of India | Explainability for AI decisions affecting customer outcomes; prohibits fully automated credit decisions | RBI_RESPONSIBLE_AI |
| Guidelines on Robo-Advisory (2024) | SEBI | SEBI registration required for personalised investment advice; information-only services exempt | SEBI_ROBO_ADVISORY |
| Guidelines on AI in Insurance Distribution (2024) | IRDAI | Human oversight required for AI-recommended insurance products above specified thresholds | IRDAI_AI_DISTRIBUTION |
| IT (Reasonable Security Practices) Rules, 2011 | MeitY | Defines sensitive personal data handling requirements applicable to AI systems | IT_SPDI_RULES |
| Digital Personal Data Protection Act, 2023 | Government of India | Data processing requirements, consent management, data localisation for customer-facing AI | DPDP_ACT |
| PCI DSS v4.0 | PCI SSC | Payment card data handling in conversational interfaces; masking, encryption, logging requirements | PCI_DSS |
| Digital Lending Guidelines (September 2022) | Reserve Bank of India | Fair practices for AI/ML models; mandatory disclosures; cooling-off periods; no high-pressure tactics | RBI_DIGITAL_LENDING |
| Banking Ombudsman Scheme, 2006 (amended 2017) | Reserve Bank of India | Grievance redressal mechanism must be available within 2 turns of any complaint | RBI_OMBUDSMAN |
| NIST AI Risk Management Framework (AI RMF 1.0) | NIST (USA) | Risk identification, assessment and mitigation framework for AI systems in financial services | (none) |
| EU AI Act, high-risk AI requirements | European Union | Requirements for customer-facing AI in financial services; risk classification; transparency mandates | EU_AI_ACT |
| OWASP Top 10 for LLM Applications (2025 Edition) | OWASP Foundation | Security vulnerabilities specific to LLM-powered applications; prompt injection defences | (none) |
| KYC / AML requirements | named in A4.3 and in the "Regulatory Compliance (India)" role | Verify identity before account information; flag suspicious patterns; no money-laundering facilitation; PEP enhanced due diligence | KYC_AML |
| DICGC cover, Section 80C, TDS (A13.1 regulatory column) | DICGC; tax | NexSave DICGC cover up to 5L; NexFD Section 80C benefits and TDS applicable | DICGC, TAX_80C, TDS |

Reading of the appendix table (D-61): the PDF text interleaves the last rows' columns. The relevance statements are assigned as above, in row order; the 2-turn grievance statement sits under the Ombudsman Scheme and is also an A4.3 obligation under the Digital Lending heading, so it is mapped to both.

**Draft status.** The brief names the RBI Responsible AI circular as "Draft, 2025". Every use in the KB (KB-REG-009) and in this matrix treats it as a draft: the agent builds to its two stated aims (explainability, no fully automated credit decisions) now, never tells a customer it is final law, and the matrix is re-reviewed through the regulatory fast-track when RBI issues the final text (maintenance-workflow.md section on fast-track).

## 2. Matrix: regulation to obligation to guardrail to KB to test

Columns: Ref; Obligation (brief wording or the brief's relevance statement); Guardrails; Enforcement component(s); KB entries; Test ID placeholders (written Day 10; scheme `<guardrail ID>-<NN>`). `-` means no test of that kind is applicable.

### 2.1 RBI Digital Lending Guidelines (September 2022), A4.3

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-01 | All product information includes mandatory disclosures (interest rates, fees, T&C) | GR-REG-01, GR-OUT-01 | Response Generator, Output Safety Layer | KB-REG-001, KB-POL-008, KB-PRD-003, KB-PRD-004, KB-PRD-005, KB-PRD-006, KB-ESC-017, KB-ESC-018 | GR-REG-01-01, GR-REG-01-02, GR-OUT-01-01 |
| M-02 | Cooling-off period information for all new product sign-ups | GR-REG-02 | Policy Engine, Output Safety Layer | KB-REG-001, KB-ESC-019, KB-POL-008 | GR-REG-02-01, GR-REG-02-02 |
| M-03 | Grievance redressal mechanism information within 2 turns of any complaint | GR-REG-03 | Policy Engine, State Tracker | KB-REG-001, KB-REG-002, KB-ESC-005 | GR-REG-03-01, GR-REG-03-02, GR-REG-03-03 |
| M-04 | No high-pressure sales tactics or artificial urgency | GR-REG-04, GR-OUT-04 | Output Safety Layer, Response Generator | KB-POL-008 | GR-REG-04-01, GR-REG-04-02, GR-OUT-04-01 |
| M-05 | Fair practices for AI/ML models (appendix) | GR-REG-17, GR-ADV-03 | Policy Engine, Learning Pipeline gate | KB-REG-001, KB-REG-009 | GR-REG-17-01, GR-REG-17-02 |

### 2.2 RBI Master Direction on Digital Payment Security Controls (April 2024)

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-06 | End-to-end encryption for all digital payment channels including AI-assisted transactions | GR-REG-14 | Gateway, Tool Orchestrator | KB-REG-008 | GR-REG-14-01 |
| M-07 | AI-assisted transactions carry no money movement by the agent; session and authentication controls apply | GR-SEC-R3, GR-SEC-R2, GR-SEC-R7 | Tool Orchestrator, Policy Engine, Gateway | KB-REG-008, KB-POL-004, KB-POL-003, KB-ESC-006 | GR-SEC-R3-01, GR-SEC-R2-01, GR-SEC-R7-01 |
| M-08 | Credential-reset and compromised-credential handling on payment channels | GR-SEC-R5 | Input Guard, Response Generator | KB-REG-008, KB-POL-011, KB-TRB-007, KB-TRB-001 | GR-SEC-R5-01, GR-SEC-R5-03 |

KB-REG-008 states the regulatory requirement only. Claims about NexBank's own encryption implementation are not made in chat; they go to the Compliance Helpdesk (ESC-008, D-34).

### 2.3 PCI DSS v4.0, A4.3

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-09 | Card numbers masked in all display and logging (last 4 digits only) | GR-REG-05, GR-SEC-R1, GR-OUT-02 | Input Guard, Output Safety Layer, Audit Bus | KB-REG-003, KB-POL-002, KB-POL-006 | GR-REG-05-01, GR-REG-05-02, GR-SEC-R1-01, GR-OUT-02-01 |
| M-10 | CVV/CVC never requested, stored or displayed | GR-REG-06, GR-SEC-R5 | Input Guard, Response Generator, Output Safety Layer | KB-REG-003, KB-POL-011, KB-POL-002 | GR-REG-06-01, GR-REG-06-02, GR-SEC-R5-02 |
| M-11 | Enhanced audit logging for all payment-related conversations | GR-REG-07 | Audit Bus, Policy Engine | KB-REG-003, KB-ESC-001, KB-TRB-005 | GR-REG-07-01 |
| M-12 | Payment card data handling in conversational interfaces: masking, encryption, logging requirements (appendix) | GR-SEC-R1, GR-SEC-R5, GR-REG-05 | Input Guard, Audit Bus, Gateway | KB-REG-003, KB-TRB-007, KB-TRB-008, KB-TRB-011 | GR-SEC-R1-02, GR-SEC-R5-04 |

### 2.4 KYC / AML, A4.3

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-13 | Verify customer identity before providing account-specific information | GR-REG-08, GR-SEC-R2 | Policy Engine, Tool Orchestrator, Retrieval | KB-REG-004, KB-POL-003, KB-POL-002 | GR-REG-08-01, GR-REG-08-02, GR-SEC-R2-04 |
| M-14 | Flag suspicious transaction patterns to the AML team | GR-REG-09, GR-SEC-R6 | Policy Engine, Escalation Router | KB-REG-004, KB-ESC-009, KB-ESC-010, KB-ESC-002 | GR-REG-09-01, GR-REG-09-02, GR-SEC-R6-01 |
| M-15 | Never process requests that could facilitate money laundering | GR-REG-10, GR-SEC-R3 | Input Guard, Policy Engine, Tool Orchestrator | KB-REG-004, KB-ESC-016, KB-POL-004 | GR-REG-10-01, GR-REG-10-02, GR-SEC-R3-02 |
| M-16 | PEP flags trigger enhanced due diligence protocols | GR-REG-11 | Policy Engine, Escalation Router (ESC-015) | KB-REG-004, KB-ESC-009, KB-ESC-007 | GR-REG-11-01, GR-REG-11-02 |
| M-17 | KYC mandatory for NexSave and NexInvest; enhanced KYC for the Premium card (A13.1) | GR-REG-08, GR-OUT-01 | Response Generator, Output Safety Layer | KB-PRD-001, KB-PRD-004, KB-PRD-008, KB-POL-005 | GR-REG-08-02, GR-OUT-01-02 |

### 2.5 SEBI Guidelines on Robo-Advisory (2024)

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-18 | SEBI registration required for personalised investment advice | GR-ADV-01, GR-ADV-02, GR-ADV-03, GR-ADV-04, GR-ADV-05, GR-ADV-06, GR-ADV-07, GR-ADV-09, GR-REG-20 | NLU, Policy Engine, Output Safety Layer, prompt layers 0-2 | KB-REG-005, KB-POL-001, KB-PRD-008, KB-FAQ-006, KB-FAQ-008 | GR-ADV-01-01 to GR-ADV-09-03 (all 30), GR-REG-20-01 |
| M-19 | Information-only services are exempt: the agent stays information-only and refers advice to a registered advisor | GR-ADV-08, GR-REG-20 | Policy Engine, Escalation Router (ESC-013) | KB-REG-005, KB-ESC-008, KB-ESC-010, KB-POL-001 | GR-ADV-08-01, GR-ADV-08-02, GR-REG-20-02 |

### 2.6 IRDAI Guidelines on AI in Insurance Distribution (2024)

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-20 | Human oversight required for AI-recommended insurance products above specified thresholds (thresholds not given in the brief, G-02) | GR-REG-12, GR-ADV-03, GR-ADV-06 | Policy Engine, Output Safety Layer, Escalation Router (ESC-013, ESC-008) | KB-REG-006, KB-FAQ-004, KB-PRD-007, KB-ESC-021 | GR-REG-12-01, GR-REG-12-02, GR-ADV-03-02 |

The agent never recommends an insurance product at any value, so its behaviour does not depend on the missing thresholds: every recommendation request goes to a human.

### 2.7 DPDP Act 2023 and IT (Reasonable Security Practices) Rules 2011

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-21 | Data processing requirements, consent management and data localisation for customer-facing AI (mechanics: G-05) | GR-REG-13 | State Tracker, Audit Bus, Learning Pipeline | KB-REG-007, KB-POL-002, KB-POL-003, KB-FAQ-009, KB-FAQ-010 | GR-REG-13-01 |
| M-22 | Sensitive personal data handling applicable to AI systems (credentials, card, Aadhaar, PAN) | GR-SEC-R1, GR-SEC-R5, GR-OUT-02 | Input Guard, Output Safety Layer, Audit Bus | KB-REG-007, KB-POL-002, KB-POL-011 | GR-SEC-R1-03, GR-SEC-R5-01, GR-OUT-02-02 |
| M-23 | Collect only the minimum information to resolve the query; never infer or store sensitive attributes (A11.3) | GR-REG-13, GR-ADV-07 | State Tracker, Policy Engine | KB-REG-007, KB-POL-001, KB-ESC-001 | GR-REG-13-02, GR-ADV-07-01 |
| M-24 | Cross-customer data leakage architecturally impossible (A11.3) | GR-SEC-R4 | Gateway, Tool Orchestrator, State Tracker | KB-POL-010, KB-POL-002, KB-REG-007 | GR-SEC-R4-01, GR-SEC-R4-05 |
| M-25 | Right to deletion within 30 days, including derived and training data (A10) | GR-REG-13 | Learning Pipeline, Audit Bus | KB-REG-007, KB-FAQ-010 | GR-REG-13-02 |

### 2.8 Banking Ombudsman Scheme, 2006 (amended 2017)

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-26 | Grievance redressal mechanism available within 2 turns of any complaint | GR-REG-03 | Policy Engine, State Tracker | KB-REG-002, KB-ESC-005, KB-ESC-019 | GR-REG-03-01, GR-REG-03-03 |
| M-27 | Quarterly customer complaint analysis per Ombudsman requirements (A10, dependency G-04) | GR-REG-19 | Audit Bus, Escalation Router | KB-REG-002, KB-ESC-005 | GR-REG-19-01 |
| M-28 | Ombudsman details and time limits are not in the brief: no figure is stated, the case goes to Compliance | GR-REG-18 | Retrieval, Policy Engine | KB-ESC-019, KB-ESC-008, KB-REG-002 | GR-REG-18-01 |

### 2.9 RBI Circular on Responsible AI in Financial Services (Draft, 2025)

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-29 | Explainability for AI decisions affecting customer outcomes: every decision traceable to inputs, model version and KB entries; a plain reason is given when a request is declined | GR-REG-15, GR-OUT-03, GR-OUT-05 | Audit Bus, Response Generator, Output Safety Layer | KB-REG-009, KB-POL-007, KB-POL-009 | GR-REG-15-02, GR-OUT-03-01, GR-OUT-05-01 |
| M-30 | Prohibits fully automated credit decisions: the agent has no approve or decline function | GR-REG-15 | Policy Engine, Tool Orchestrator | KB-REG-009, KB-ESC-017, KB-ESC-018, KB-FAQ-005 | GR-REG-15-01 |
| M-31 | The circular is a draft: never stated as final; uncertain detail goes to ESC-008 | GR-REG-18 | Retrieval, Output Safety Layer | KB-REG-009, KB-ESC-008, KB-ESC-020 | GR-REG-18-02 |

### 2.10 NIST AI RMF 1.0, EU AI Act (high-risk), OWASP LLM Top 10 (2025)

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-32 | EU AI Act transparency mandate and A11.3: customers are told they talk to an AI, the agent never denies it, human assistance is available on request | GR-REG-16 | prompt layers 0-2, Policy Engine, Output Safety Layer | KB-POL-009, KB-FAQ-009, KB-ESC-003, KB-REG-009 | GR-REG-16-01, GR-REG-16-02 |
| M-33 | EU AI Act risk classification (dependency G-09) and consistent treatment across segments (A11.3) | GR-REG-17 | Policy Engine, Learning Pipeline gate | KB-REG-009 | GR-REG-17-01, GR-REG-17-02 |
| M-34 | NIST AI RMF 1.0: risk identification, assessment, mitigation: severity, false-positive target and fail mode per guardrail in the registry; control change gates | GR-SYS-02, GR-SYS-03, GR-SYS-01 | Learning Pipeline gate, Policy Engine | KB-POL-002 | GR-SYS-01-01, GR-SYS-02-01, GR-SYS-03-01 |
| M-35 | OWASP LLM Top 10 (2025): cross-reference in section 4; attack tests Day 10 | GR-SEC-R1, GR-SEC-R3, GR-SEC-R4, GR-OUT-03 (Day 9); GR-ATK-* (Day 10) | see section 4 | KB-POL-002 | see section 4 |

### 2.11 Product regulatory facts from A13.1

| Ref | Obligation | Guardrails | Components | KB entries | Tests |
|---|---|---|---|---|---|
| M-36 | NexSave deposit cover (DICGC, up to 5L) stated exactly, no extension to other products | GR-OUT-01, GR-OUT-03 | Output Safety Layer | KB-REG-010, KB-FAQ-001, KB-PRD-001 | GR-OUT-01-02, GR-OUT-03-02 |
| M-37 | NexFD: Section 80C benefits and TDS applicable stated as facts, never as tax-planning advice | GR-ADV-05, GR-OUT-01 | Output Safety Layer | KB-REG-011, KB-FAQ-008, KB-PRD-002 | GR-ADV-05-01, GR-ADV-05-03 |
| M-38 | Non-existent product benefit or incorrect interest rate is an AUTO-FAIL (A9.2) | GR-OUT-01, GR-OUT-03, GR-REG-18 | Output Safety Layer, Retrieval | KB-PRD-010, KB-ESC-020, KB-ESC-014 | GR-OUT-01-01, GR-OUT-03-01, GR-REG-18-01 |

## 3. KB tag to regulation index

Every `regulatory_tags` value used in the 77 KB entries maps to a row above.

| KB tag | Regulation | Matrix rows | Count of KB entries tagged |
|---|---|---|---|
| RBI_DIGITAL_LENDING | RBI Digital Lending Guidelines (Sept 2022) | M-01 to M-05 | 20 |
| RBI_DIGITAL_PAYMENT_SECURITY | RBI Master Direction on Digital Payment Security Controls (Apr 2024) | M-06 to M-08 | 13 |
| PCI_DSS | PCI DSS v4.0 | M-09 to M-12 | 12 |
| KYC_AML | KYC / AML | M-13 to M-17 | 19 |
| SEBI_ROBO_ADVISORY | SEBI Robo-Advisory Guidelines (2024) | M-18, M-19 | 5 |
| IRDAI_AI_DISTRIBUTION | IRDAI Guidelines on AI in Insurance Distribution (2024) | M-20 | 5 |
| DPDP_ACT, IT_SPDI_RULES | DPDP Act 2023; IT (Reasonable Security Practices) Rules 2011 | M-21 to M-25 | 9 and 2 |
| RBI_OMBUDSMAN | Banking Ombudsman Scheme 2006 (amended 2017) | M-26 to M-28 | 3 |
| RBI_RESPONSIBLE_AI | RBI Responsible AI circular (Draft, 2025) | M-29 to M-31 | 11 |
| EU_AI_ACT | EU AI Act high-risk requirements | M-32, M-33 | 4 |
| DICGC | DICGC cover (A13.1) | M-36 | 3 |
| TAX_80C, TDS | Section 80C, TDS (A13.1) | M-37 | 4 and 3 |

## 4. OWASP LLM Top 10 (2025) cross-reference

Category names are from the OWASP Top 10 for LLM Applications (2025 edition); the brief names the list as a resource and cross-reference, and the project design uses it in the Day 10 defences. Names and numbering were checked against the OWASP GenAI Security Project list (genai.owasp.org/llm-top-10) on Day 15 and match (D-77). Day 9 guardrails cover the categories as shown in the second column; Day 10 added the GR-ATK guardrails in the third (`adversarial-defences.md` section 12 has the per-vector view). This is a cross-reference, not a certification, and it is not part of the 38 M-rows.

| OWASP category | Day 9 guardrails | Day 10 (GR-ATK, `adversarial-defences.md`) |
|---|---|---|
| LLM01 Prompt Injection (includes jailbreaking) | GR-ADV-07 (prompt layer restatement), GR-SEC-R8 | GR-ATK-01, GR-ATK-02 (injection, indirect injection), GR-ATK-03, GR-ATK-04 (jailbreak, behavioural monitor), GR-ATK-05 (authority claims); 34 reserved tests |
| LLM02 Sensitive Information Disclosure | GR-SEC-R1, GR-SEC-R4, GR-SEC-R5, GR-OUT-02 | GR-ATK-07 (response scanning), GR-ATK-06; exfiltration tests |
| LLM03 Supply Chain | none | none in the chat guardrails: model, library and data supply-chain controls are a platform dependency (Day 14); stated as a gap by scope, not as covered |
| LLM04 Data and Model Poisoning (partial) | GR-SYS-02 (the learning pipeline cannot alter rules, thresholds or prompt layers); KB approval chain for content (`docs/knowledge-base/maintenance-workflow.md`) | GR-ATK-02 (imperative-text scan of KB passages at ingestion and retrieval, quarantine); Day 12 learning-pipeline spec must define data-pipeline quality gates (source validation, PII scrub, human review of training candidates) |
| LLM05 Improper Output Handling | GR-ADV-06, GR-OUT-01 to GR-OUT-05, GR-SYS-01 | GR-ATK-07 (links, images, encoded values, foreign identifiers in drafts); output validation tests |
| LLM06 Excessive Agency | GR-SEC-R3 (no money-movement tool), GR-SEC-R2 | GR-ATK-10, GR-ATK-11 (identity claims, risk signal), GR-ATK-04; agency tests (no model-controlled customer key or auth level) |
| LLM07 System Prompt Leakage | GR-SYS-02 (prompt layers 0-2 are immutable) | GR-ATK-06 (probe lexicon, canary, overlap scan; prompts hold no secrets, D-73); 5 extraction tests |
| LLM08 Vector and Embedding Weaknesses (partial) | Retrieval auth, audience and expiry pre-filter inside both searches (D-44, D-51); KB approval workflow so only published, approved entries are indexed | GR-ATK-02 (retrieval-poisoning and cross-audience probe tests); embedding-store access control and isolation depend on the Day 12 and 13 platform design |
| LLM09 Misinformation | GR-OUT-01, GR-OUT-03, GR-REG-18 | hallucination traps (Day 11 suite); attack replies use the gap statement, never a guess (D-71) |
| LLM10 Unbounded Consumption | none before Day 10 (GR-SEC-R7 is an authentication inactivity timeout, not a consumption limit, and is not mapped here) | **GR-ATK-08 (rate limiting, token budget) and GR-ATK-09 (complexity scoring, tool-call budget, turn cap): gap closed at the application layer** (D-74). Limits are proposals; network-layer DDoS is a platform dependency (Day 14). 8 reserved tests |

Social engineering and identity spoofing (A4.4) have no dedicated OWASP LLM category; they are mapped to LLM01 and LLM06 above and are chiefly bank authentication and process controls.

## 5. Coverage statement

| Measure | Result |
|---|---|
| A4.3 obligations (4 RBI Digital Lending, 3 PCI DSS, 4 KYC/AML) | 11 of 11 mapped to a guardrail, KB entry and test placeholder (M-01 to M-04, M-09 to M-11, M-13 to M-16) |
| Appendix relevance statements (12 listed regulations) | 12 of 12 mapped (M-05 to M-08, M-12, M-18 to M-35) |
| KB regulatory tags | 14 of 14 tags in use mapped (section 3) |
| GR-REG guardrails with a matrix row | 20 of 20 |
| Unmapped obligations | 0 |
| Residual dependencies | 9 (G-01 to G-09, section 6), none leaves an obligation without a guardrail |

The Regulator badge asks for the RBI, PCI DSS and KYC/AML mapping with zero compliance gaps: all three are fully mapped (sections 2.1 to 2.4), with zero unmapped obligations. The residual dependencies are specification details the brief does not give, each with an owner; they do not weaken a guardrail because the guardrail does not depend on them (the default is to say what is not known and route to a human).

## 6. Residual dependencies (stated gaps) and owners

| ID | Dependency | Why it is not closed on Day 9 | Safe default meanwhile | Owner | Due |
|---|---|---|---|---|---|
| G-01 | Length of the cooling-off period | Not in the brief (KB-REG-001 `not_in_brief`, KB-ESC-019) | State the obligation, say the length is not held, offer ESC-008; never a number | Regulatory Compliance Manager | KB update when a source is supplied |
| G-02 | IRDAI "specified thresholds" for human oversight | Not in the brief | Never recommend insurance; every recommendation request goes to a human | Regulatory Compliance Manager | KB update when supplied |
| G-03 | AML suspicious-pattern indicators beyond those in the brief | The brief names the duty, not the indicators | Flag to the AML queue on any customer-stated or structuring cue; do not tell the customer | AML Compliance team | open: indicator list is an AML team input (`docs/escalation/triggers.md`) |
| G-04 | Production of the quarterly Ombudsman complaint analysis and the monthly RBI summary | Reporting pipeline is Day 12 (metrics) and Day 14 (audit logging) | Complaint tickets carry category and timestamps now (GR-REG-19) | Chief Risk Officer | open: AL-D2 (`docs/compliance/audit-logging.md`) |
| G-05 | DPDP mechanics: consent records, data localisation controls, 30-day deletion workflow including training data | Specified in the data pipeline (Day 11) and audit logging (Day 14) | Data minimisation and no sensitive-attribute storage hold now (GR-REG-13) | Data Protection lead with ML team | open: AL-D1 (`docs/compliance/audit-logging.md`) |
| G-06 | PCI DSS enhanced audit logging: field list, retention for payment conversations | Audit logging spec is Day 14 (R-32) | High-risk actions blocked if the audit write fails (GR-REG-07) | Security Operations | specified in `docs/compliance/audit-logging.md`; open: AL-D3 |
| G-07 | NexBank's own channel encryption design | D-34: the brief supports the requirement, not NexBank's implementation | No implementation claims in chat; ESC-008 | Security Operations | open: AL-D3 (`docs/compliance/audit-logging.md`) |
| G-08 | Final text of the RBI Responsible AI circular (draft, 2025) | Draft status | Build to the two stated aims; re-review on publication via fast-track | Regulatory Compliance Manager | On publication |
| G-09 | EU AI Act risk classification of this system and NIST AI RMF function mapping | Day 14 risk matrix (R-33) | Registry carries severity, FP target and fail mode per guardrail | Chief Risk Officer | specified in `docs/risk/risk-matrix.md` |

The registry cites G-01 to G-05 in the `fail_mode` of the guardrails they qualify.

## 7. Regulatory change handling

A new RBI circular or SEBI/IRDAI notice enters through the KB regulatory fast-track (quarantine of affected entries, Compliance review, TTL reset; maintenance-workflow.md). The same ticket reviews this matrix: the changed obligation gets a row or a changed row, a guardrail or a test is added or updated, and the safety suite is re-run before publication. A regulatory obligation may add a guardrail or tighten one; it can never loosen an immutable guardrail through the learning pipeline (GR-SYS-02).

## 8. Reserved test IDs and counts

Reserved IDs follow `<guardrail ID>-<NN>`: GR-REG-01 to GR-REG-20 reserve 2, 2, 3, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2 (total 38); GR-OUT-01 to GR-OUT-05 reserve 2 each (10); GR-SYS-01 reserves 2. Across all families the registry reserves GR-ADV 30, GR-SEC 40, GR-REG 38, GR-OUT 10, GR-SYS 6, a total of 124, from which Day 10 writes at least the 55 guardrail and adversarial cases the project target requires (the brief asks for 50+), and every guardrail gets at least one written case before Day 15. Day 10 adds the adversarial family GR-ATK (11 guardrails, 62 reserved IDs, `adversarial-defences.md` section 15), so the registry reserves 186 IDs in total (124 + 62); the Day 9 figures above are unchanged. The Day 10 audit adds GR-OUT-06 and GR-SYS-04 with 2 reserved IDs each (D-90): 58 guardrails and 190 reserved IDs.
