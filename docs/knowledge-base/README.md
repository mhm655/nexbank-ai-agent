# Knowledge Base (Day 7)

Sample knowledge base for the NexBank agent: the schema and ER model, and 77 entries across the six A2.3 categories and three representation formats. Retrieval, the maintenance workflow and the access matrix are Day 8.

| File | Contents |
|---|---|
| [`kb-schema.md`](kb-schema.md) | Entry schema, ER model, ID convention, versioning, TTL classes, regulatory tags, auth-level access control, intent links, gap handling |
| [`entries/product.yaml`](entries/product.yaml) | A13.1 catalogue entries, comparisons and one EMI illustration |
| [`entries/policy.yaml`](entries/policy.yaml) | Advice boundary, the 8 security rules, auth levels, protective actions, disclosure |
| [`entries/regulatory.yaml`](entries/regulatory.yaml) | Regulations as stated in the brief (RBI, PCI DSS, KYC/AML, SEBI, IRDAI, DPDP, DICGC, tax) |
| [`entries/faq.yaml`](entries/faq.yaml) | Short customer answers, with Hindi and Hinglish wording for four of them |
| [`entries/troubleshooting.yaml`](entries/troubleshooting.yaml) | UPI, NEFT/RTGS, dispute, credential and statement problems, plus one agent-internal account-takeover check (KB-TRB-011) |
| [`entries/escalation.yaml`](entries/escalation.yaml) | A6 handoff procedures and 11 gap-handling entries for topics A13.1 does not cover |
| `../../diagrams/kb-er-model.mmd` | Mermaid ER diagram of the KB |
| `../../tests/kb/validate_kb_entries.py` | Validator (run from the repo root: `python tests/kb/validate_kb_entries.py`) |

TTL note (D-32): a `rates` entry (90-day hard expiry) is any entry that carries a rate, fee, eligibility criterion, minimum amount or threshold, or a comparison of them, so KB-PRD-007 to KB-PRD-009 and the FAQ entries restating their figures (KB-FAQ-004, KB-FAQ-006) are `rates`, not `product_features`.

Grounding rule (D-26): figures come only from A13.1 and the brief's regulatory text. Where the brief has no data, a gap entry says so and the agent offers a human. All data is synthetic and the approvals in each entry are simulated.

## Coverage counts

**Total: 77 entries** (minimum 55).

| Category | Entries | structured | semi_structured | unstructured |
|---|---|---|---|---|
| product | 12 | 9 | 3 | 0 |
| policy | 11 | 1 | 5 | 5 |
| regulatory | 11 | 4 | 3 | 4 |
| faq | 11 | 1 | 2 | 8 |
| troubleshooting | 11 | 0 | 7 | 4 |
| escalation | 21 | 3 | 15 | 3 |
| **total** | **77** | **18** | **35** | **24** |

| Auth level required | Entries |
|---|---|
| anonymous | 64 |
| otp_verified | 10 |
| biometric_verified | 1 |
| full_kyc | 2 |

| Audience | Entries |
|---|---|
| customer_facing | 58 |
| agent_internal | 19 |

- Gap-handling entries: 11 (KB-ESC-011, KB-ESC-012, KB-ESC-013, KB-ESC-014, KB-ESC-015, KB-ESC-016, KB-ESC-017, KB-ESC-018, KB-ESC-019, KB-ESC-020, KB-ESC-021).
- Intents linked to at least one entry: 38 of 41. No entry (answered by templates): CMP-004, GEN-005, GEN-006.
- `kb_gap` intents and their gap entries: ACC-007: KB-ESC-012; CRD-004: KB-ESC-013; PRD-003: KB-ESC-011, KB-ESC-014; GEN-008: KB-ESC-015.
- Entries with Hindi and Hinglish wording (review simulated; native-speaker check pending): 4 (KB-FAQ-001, KB-FAQ-002, KB-FAQ-008, KB-FAQ-009).
- Regulatory tags in use: DICGC (3), DPDP_ACT (9), EU_AI_ACT (4), IRDAI_AI_DISTRIBUTION (5), IT_SPDI_RULES (2), KYC_AML (19), PCI_DSS (12), RBI_DIGITAL_LENDING (20), RBI_DIGITAL_PAYMENT_SECURITY (13), RBI_OMBUDSMAN (3), RBI_RESPONSIBLE_AI (11), SEBI_ROBO_ADVISORY (5), TAX_80C (4), TDS (3).
- Entries carrying an escalation trigger link: 34.

## Index

Auth: A = anonymous, O = otp_verified, B = biometric_verified, K = full_kyc. Audience: C = customer_facing, I = agent_internal. Format: S = structured, SS = semi_structured, U = unstructured.

| ID | Title | Category | Fmt | Auth | Aud | Intents |
|---|---|---|---|---|---|---|
| KB-PRD-001 | NexSave Savings Account | product | S | A | C | PRD-001, ACC-007 |
| KB-PRD-002 | NexFD Fixed Deposit | product | S | A | C | PRD-001, PRD-003 |
| KB-PRD-003 | NexCredit Card - Classic | product | S | A | C | PRD-001, CRD-005, CRD-003 |
| KB-PRD-004 | NexCredit Card - Premium | product | S | A | C | PRD-001, CRD-005, CRD-003 |
| KB-PRD-005 | NexHome Loan | product | S | A | C | PRD-001, PRD-002 |
| KB-PRD-006 | NexPersonal Loan | product | S | A | C | PRD-001, PRD-002 |
| KB-PRD-007 | NexProtect Term Insurance | product | S | A | C | PRD-004, PRD-001 |
| KB-PRD-008 | NexInvest Mutual Funds | product | S | A | C | PRD-001, PRD-005 |
| KB-PRD-009 | NexGold Digital Gold | product | S | A | C | PRD-001 |
| KB-PRD-010 | NexBank product catalogue overview | product | SS | A | C | PRD-001, GEN-008 |
| KB-PRD-011 | Credit card factual comparison - Classic vs Premium | product | SS | A | C | PRD-001, CRD-005 |
| KB-PRD-012 | Illustrative EMI calculation (brief example) | product | SS | A | C | PRD-002, CRD-004 |
| KB-POL-001 | Information versus advice boundary | policy | SS | A | I | PRD-005, PRD-001, PRD-002, PRD-003, PRD-004, TXN-006 |
| KB-POL-002 | The eight account-security rules | policy | SS | A | I | SEC-001, SEC-002, SEC-003, SEC-004, ACC-003, ACC-004, GEN-004 |
| KB-POL-003 | Authentication levels and session rules | policy | S | A | C | ACC-001, ACC-003, ACC-005, SEC-003 |
| KB-POL-004 | What the agent cannot do (no fund movement, no record changes) | policy | SS | A | I | TXN-003, TXN-005, ACC-005, ACC-006, GEN-004 |
| KB-POL-005 | Account closure and nominee update - branch process | policy | SS | K | C | ACC-005, ACC-006 |
| KB-POL-006 | Card block as a protective action | policy | SS | O | C | CRD-001, CRD-002, SEC-001 |
| KB-POL-007 | Commitments and timelines | policy | U | A | I | TXN-002, TXN-003, TXN-004, CMP-002, CMP-005 |
| KB-POL-008 | No pressure selling and mandatory disclosures | policy | U | A | I | PRD-001, PRD-002, PRD-003, PRD-004 |
| KB-POL-009 | AI disclosure | policy | U | A | C | GEN-002, GEN-001 |
| KB-POL-010 | Third-party requests and authority claims | policy | U | A | I | GEN-004, ACC-001, SEC-002 |
| KB-POL-011 | What to do if credentials are compromised | policy | U | A | C | SEC-001, SEC-003, SEC-002 |
| KB-REG-001 | RBI Digital Lending Guidelines (September 2022) | regulatory | S | A | C | PRD-001, PRD-002, CRD-003, CRD-004 |
| KB-REG-002 | Grievance redressal and the Banking Ombudsman Scheme | regulatory | S | A | C | CMP-001, CMP-003, CMP-002 |
| KB-REG-003 | PCI DSS v4.0 - card data in conversations | regulatory | SS | A | C | CRD-001, CRD-002, SEC-001, SEC-003 |
| KB-REG-004 | KYC, AML and PEP requirements | regulatory | SS | A | I | ACC-008, TXN-006, ACC-001 |
| KB-REG-005 | SEBI robo-advisory guidelines (2024) | regulatory | U | A | C | PRD-005, PRD-001 |
| KB-REG-006 | IRDAI guidelines on AI in insurance distribution (2024) | regulatory | U | A | C | PRD-004, PRD-005 |
| KB-REG-007 | Data protection - DPDP Act 2023 and IT Reasonable Security Practices Rules 2011 | regulatory | S | A | C | GEN-002 |
| KB-REG-008 | RBI Master Direction on Digital Payment Security Controls (April 2024) | regulatory | U | A | C | GEN-002, SEC-003 |
| KB-REG-009 | RBI Responsible AI circular (draft, 2025) and EU AI Act transparency | regulatory | U | A | C | PRD-002, CRD-003, GEN-002 |
| KB-REG-010 | DICGC deposit cover on NexSave | regulatory | S | A | C | PRD-001, ACC-007 |
| KB-REG-011 | Tax treatment of NexFD - Section 80C and TDS | regulatory | SS | A | C | PRD-003, PRD-005, ACC-002 |
| KB-FAQ-001 | Is my NexSave deposit insured? | faq | U | A | C | PRD-001, ACC-007 |
| KB-FAQ-002 | Do I need a minimum balance in NexSave? | faq | U | A | C | PRD-001, ACC-007 |
| KB-FAQ-003 | How long is the interest-free period on NexCredit cards? | faq | U | A | C | PRD-001, CRD-005 |
| KB-FAQ-004 | Is NexProtect regulated, and when is a medical check needed? | faq | U | A | C | PRD-004 |
| KB-FAQ-005 | Loan eligibility quick answers | faq | SS | A | C | PRD-002 |
| KB-FAQ-006 | Smallest amounts for SIP and digital gold | faq | S | A | C | PRD-001, PRD-005 |
| KB-FAQ-007 | Can I take physical gold? | faq | U | A | C | PRD-001 |
| KB-FAQ-008 | What tenure and tax treatment does NexFD have? | faq | U | A | C | PRD-003, PRD-001 |
| KB-FAQ-009 | Am I talking to a human? | faq | U | A | C | GEN-002, GEN-003 |
| KB-FAQ-010 | How do I get my account statement? | faq | SS | O | C | ACC-002 |
| KB-FAQ-011 | What rewards do the NexCredit cards give? | faq | U | A | C | CRD-005, PRD-001 |
| KB-TRB-001 | UPI payment debited but not credited | troubleshooting | SS | O | C | TXN-003, TXN-001 |
| KB-TRB-002 | UPI payment pending or declined | troubleshooting | SS | O | C | TXN-003 |
| KB-TRB-003 | Money sent to the wrong beneficiary | troubleshooting | U | O | C | TXN-003, SEC-001 |
| KB-TRB-004 | NEFT or RTGS status check | troubleshooting | SS | O | C | TXN-004, TXN-001 |
| KB-TRB-005 | Unrecognised or duplicate charge - dispute or fraud? | troubleshooting | SS | O | C | TXN-002, SEC-001, TXN-001 |
| KB-TRB-006 | Refund not received | troubleshooting | U | O | C | TXN-002, TXN-001 |
| KB-TRB-007 | Locked out or forgot the password or PIN | troubleshooting | SS | A | C | SEC-003 |
| KB-TRB-008 | Card was blocked and the customer wants it unblocked | troubleshooting | SS | B | C | CRD-001 |
| KB-TRB-009 | A lookup tool is not responding | troubleshooting | U | A | I | TXN-001, TXN-003, TXN-004, CMP-002 |
| KB-TRB-010 | Statement did not arrive | troubleshooting | U | O | C | ACC-002, ACC-003 |
| KB-TRB-011 | Credential reset after a recent contact-details change (internal check) | troubleshooting | SS | O | I | SEC-003 |
| KB-ESC-001 | Handoff package contents | escalation | SS | A | I | GEN-003, CMP-003, SEC-001, ACC-005 |
| KB-ESC-002 | Fraud report handling (P0) | escalation | SS | A | I | SEC-001, SEC-004, SEC-002, CRD-001 |
| KB-ESC-003 | Customer asks for a human agent | escalation | SS | A | I | GEN-003, CMP-005 |
| KB-ESC-004 | Distress, self-harm or emergency disclosure | escalation | U | A | I | GEN-007 |
| KB-ESC-005 | Legal threats and unresolved complaints | escalation | SS | A | I | CMP-001, CMP-003, CMP-005 |
| KB-ESC-006 | Dispute above INR 50,000 | escalation | S | A | I | TXN-002 |
| KB-ESC-007 | Account closure for a high-value customer | escalation | S | K | I | ACC-005 |
| KB-ESC-008 | Regulatory question with an uncertain answer, and advisory requests | escalation | SS | A | I | PRD-001, PRD-004, PRD-005, CMP-003 |
| KB-ESC-009 | AML indicators and PEP customers | escalation | U | A | I | TXN-006, ACC-008 |
| KB-ESC-010 | Escalation trigger and queue table (A6) | escalation | S | A | I | GEN-003, SEC-001, CMP-003, TXN-002, ACC-005, PRD-005, GEN-007 |
| KB-ESC-011 | GAP - Recurring deposit (RD) is not in the catalogue | escalation | SS | A | C | PRD-003 |
| KB-ESC-012 | GAP - Savings account variants and upgrade paths | escalation | SS | A | C | ACC-007 |
| KB-ESC-013 | GAP - EMI conversion fees and rates | escalation | SS | A | C | CRD-004 |
| KB-ESC-014 | GAP - FD rates for a specific tenure | escalation | SS | A | C | PRD-003, PRD-001 |
| KB-ESC-015 | GAP - Branches, ATMs, working hours and contact channels | escalation | SS | A | C | GEN-008, ACC-005, ACC-006 |
| KB-ESC-016 | GAP - International transfer charges, limits and forex rates | escalation | SS | A | C | TXN-006, PRD-005 |
| KB-ESC-017 | GAP - Card fees after year 1, credit limits and revolving interest | escalation | SS | A | C | CRD-003, CRD-005, PRD-001 |
| KB-ESC-018 | GAP - Loan fees, charges and decisions | escalation | SS | A | C | PRD-002, PRD-001 |
| KB-ESC-019 | GAP - Ombudsman details and cooling-off period length | escalation | SS | A | C | CMP-003, CMP-001, PRD-001, PRD-002 |
| KB-ESC-020 | GAP - Unknown or unsupported question (graceful degradation) | escalation | U | A | C | GEN-004, PRD-001, GEN-008, PRD-003, ACC-007, CRD-004 |
| KB-ESC-021 | GAP - Insurance premiums, policy terms and claims | escalation | SS | A | C | PRD-004 |
