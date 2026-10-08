# Access-Control Matrix

Brief refs: A2.3 (access control by authentication level), A4.2 (security rules, session timeout), A4.3 (KYC/AML, PCI DSS), A3.3 (intent auth levels). Plan refs: section 4 Phase 3 item 6. Decisions: D-29 to D-31 (earlier), D-44 and D-47 (this day). Schema and rule summary: `kb-schema.md` section 9. How the filter runs: `retrieval-pipeline.md` section 5. Level definitions: `KB-POL-003`, `config/dialogue_state.schema.json`. Intent levels: `config/intents.yaml`.

Levels, lowest to highest: `anonymous` (A) < `otp_verified` (O) < `biometric_verified` (B) < `full_kyc` (K). Audience: `customer_facing` (C) or `agent_internal` (I).

## 1. Where access is enforced

| # | Control point | What it does |
|---|---|---|
| 1 | Policy Engine, before any agent or retrieval call | Compares session `auth_level` with the intent's `auth` in `config/intents.yaml`. Account-specific work above the level goes to `AUTH_REQUIRED` (step-up), except fraud intake (D-16) |
| 2 | Retrieval pre-filter | Hard clause `rank(session) >= rank(entry.auth_level_required)` inside both searches, so ineligible entries never enter a candidate list (`retrieval-pipeline.md` section 5) |
| 3 | Retrieval post-assertion | Every returned passage is re-checked against the session level, status and expiry. A failure drops the passage and raises a P0 incident |
| 4 | Tool Orchestrator | Re-checks the level independently for every tool call (`component-interfaces.md` cross-cutting rules) |
| 5 | Output Safety Layer | Rejects a reply that copies an `agent_internal` body; checks that cited IDs are evidence-lane IDs |
| 6 | Cache | Keyed by auth class and `index_epoch`; re-checks level and expiry at serve time |

The session level comes only from the Gateway and the auth state machine (`diagrams/auth-flow.mmd`). Text typed by the customer, a claim of identity, or an instruction inside a message never changes it (security rule 2, KB-POL-002). A session idle for 5 minutes drops to `anonymous`; elevated entries leave retrieval on the next turn, while conversation context is kept for 24 hours (D-05, KB-POL-003).

The KB holds no personal data. Balances, transactions, profile and complaint status come from tools gated by points 1 and 4; the KB only holds procedures, product facts and rules.

## 2. Matrix: level by category and audience (sample KB, 77 entries)

Each cell is the number of entries that **first become retrievable at that level**. Retrieval is cumulative: a session at a level sees its own column and all columns to the left.

| Category | Audience | A | O | B | K | Total |
|---|---|---|---|---|---|---|
| product | C | 12 | 0 | 0 | 0 | 12 |
| policy | C | 3 | 1 (KB-POL-006) | 0 | 1 (KB-POL-005) | 5 |
| policy | I | 6 | 0 | 0 | 0 | 6 |
| regulatory | C | 10 | 0 | 0 | 0 | 10 |
| regulatory | I | 1 (KB-REG-004) | 0 | 0 | 0 | 1 |
| faq | C | 10 | 1 (KB-FAQ-010) | 0 | 0 | 11 |
| troubleshooting | C | 1 (KB-TRB-007) | 7 | 1 (KB-TRB-008) | 0 | 9 |
| troubleshooting | I | 1 (KB-TRB-009) | 1 (KB-TRB-011) | 0 | 0 | 2 |
| escalation | C (gap entries) | 11 | 0 | 0 | 0 | 11 |
| escalation | I | 9 | 0 | 0 | 1 (KB-ESC-007) | 10 |
| **Entries first visible at level** | | **64** | **10** | **1** | **2** | **77** |
| **Cumulative retrievable** | | 64 (C 47, I 17) | 74 (C 56, I 18) | 75 (C 57, I 18) | 77 (C 58, I 19) | |

The seven `otp_verified` customer-facing troubleshooting entries are KB-TRB-001 to KB-TRB-006 and KB-TRB-010.

## 3. Rules that decide an entry's level

| Content class | Level | Audience | Reason | Examples |
|---|---|---|---|---|
| Catalogue facts, comparisons, regulation statements, generic FAQs | A | C | Public information; the brief's own catalogue (A13.1) | KB-PRD-002, KB-REG-001, KB-FAQ-008 |
| Gap entries (known absences) | A | C | Hold no data, no figure; must stay reachable so the agent says "I can't confirm" instead of stepping up (D-31) | KB-ESC-011, KB-ESC-019 |
| Rules that steer the agent | A | I | Retrievable in any session because they shape behaviour; never quoted, never shown | KB-POL-001, KB-POL-007, KB-ESC-008, KB-ESC-010 |
| Generic credential and fraud guidance | A | C or I | Safe for anyone; fraud intake is accepted at any level (D-16) | KB-TRB-007, KB-POL-011, KB-ESC-002 (I) |
| Procedures for acting on the customer's own account | O | C | Describes a personal action; needs an identity check | KB-TRB-001, KB-TRB-005, KB-FAQ-010, KB-POL-006 |
| Detection logic and how a check is applied | O (the level at which it is applied) | I | Must not be reachable anonymously (D-30) | KB-TRB-011 |
| Step-up actions | B | C | Sensitive or hard to reverse | KB-TRB-008 (card unblock) |
| Closure, nominee, high-value handling | K | C or I | Highest-risk account changes, handled by humans or at the branch | KB-POL-005, KB-ESC-007 |

Changing `auth_level_required` or `audience` of an entry is a MAJOR change through the full approval chain (`maintenance-workflow.md`), with the Chief Risk Officer in the chain (D-47). Lowering a level needs an explicit confirmation that the entry holds no personal or detection information.

## 4. Matrix: intent by level by KB entries

`auth` is the level needed for account-specific data or action. `generic_info_auth` is the level at which the intent's generic KB content is available (`-` means it is the same as `auth`). The last two columns list the entries linked to the intent in `entries/*.yaml` (`intents` field), split into those retrievable at `anonymous` and those that need a step-up, with the required level in brackets. Entry IDs drop the `KB-` prefix. Entries serve several intents, so the same ID can appear in many rows.

| Intent | Name | `auth` | `generic_info_auth` | Entries at anonymous | Entries needing step-up |
|---|---|---|---|---|---|
| ACC-001 | Check Account Balance | otp_verified | anonymous | POL-003, POL-010, REG-004 | none |
| ACC-002 | Request Account Statement | otp_verified | - | REG-011 | FAQ-010 (O), TRB-010 (O) |
| ACC-003 | Update Contact Details | biometric_verified | - | POL-002, POL-003 | TRB-010 (O) |
| ACC-004 | Update Mailing Address | biometric_verified | - | POL-002 | none |
| ACC-005 | Account Closure Request | full_kyc | - | ESC-001, ESC-010, ESC-015, POL-003, POL-004 | ESC-007 (K), POL-005 (K) |
| ACC-006 | Nominee Update | full_kyc | - | ESC-015, POL-004 | POL-005 (K) |
| ACC-007 | Account Upgrade / Downgrade | otp_verified | anonymous | ESC-012, ESC-020, FAQ-001, FAQ-002, PRD-001, REG-010 | none |
| ACC-008 | KYC Update and Documents | biometric_verified | anonymous | ESC-009, REG-004 | none |
| TXN-001 | Transaction Status Enquiry | otp_verified | - | TRB-009 | TRB-001 (O), TRB-004 (O), TRB-005 (O), TRB-006 (O) |
| TXN-002 | Raise Transaction Dispute | otp_verified | - | ESC-006, ESC-010, POL-007 | TRB-005 (O), TRB-006 (O) |
| TXN-003 | UPI Payment Failure | otp_verified | - | POL-004, POL-007, TRB-009 | TRB-001 (O), TRB-002 (O), TRB-003 (O) |
| TXN-004 | NEFT/RTGS Status Check | otp_verified | - | POL-007, TRB-009 | TRB-004 (O) |
| TXN-005 | Recurring Payment Setup/Cancel | biometric_verified | - | POL-004 | none |
| TXN-006 | International Transfer Enquiry | full_kyc | anonymous | ESC-009, ESC-016, POL-001, REG-004 | none |
| CRD-001 | Block / Unblock Card | otp_verified | - | ESC-002, REG-003 | POL-006 (O), TRB-008 (B) |
| CRD-002 | Card Replacement | biometric_verified | - | REG-003 | POL-006 (O) |
| CRD-003 | Credit Limit Change | biometric_verified | - | ESC-017, PRD-003, PRD-004, REG-001, REG-009 | none |
| CRD-004 | EMI Conversion | otp_verified | anonymous | ESC-013, ESC-020, PRD-012, REG-001 | none |
| CRD-005 | Reward Points Enquiry | otp_verified | anonymous | ESC-017, FAQ-003, FAQ-011, PRD-003, PRD-004, PRD-011 | none |
| PRD-001 | Product Information | anonymous | - | ESC-008, ESC-014, ESC-017, ESC-018, ESC-019, ESC-020, FAQ-001, FAQ-002, FAQ-003, FAQ-006, FAQ-007, FAQ-008, FAQ-011, POL-001, POL-008, PRD-001, PRD-002, PRD-003, PRD-004, PRD-005, PRD-006, PRD-007, PRD-008, PRD-009, PRD-010, PRD-011, REG-001, REG-005, REG-010 | none |
| PRD-002 | Loan Eligibility and EMI | anonymous | - | ESC-018, ESC-019, FAQ-005, POL-001, POL-008, PRD-005, PRD-006, PRD-012, REG-001, REG-009 | none |
| PRD-003 | FD/RD Rate Enquiry | anonymous | - | ESC-011, ESC-014, ESC-020, FAQ-008, POL-001, POL-008, PRD-002, REG-011 | none |
| PRD-004 | Insurance Enquiry | anonymous | - | ESC-008, ESC-021, FAQ-004, POL-001, POL-008, PRD-007, REG-006 | none |
| PRD-005 | Investment Advisory Request | anonymous | - | ESC-008, ESC-010, ESC-016, FAQ-006, POL-001, PRD-008, REG-005, REG-006, REG-011 | none |
| CMP-001 | Register Complaint | otp_verified | anonymous | ESC-005, ESC-019, REG-002 | none |
| CMP-002 | Check Complaint Status | otp_verified | - | POL-007, REG-002, TRB-009 | none |
| CMP-003 | Escalate Complaint | otp_verified | anonymous | ESC-001, ESC-005, ESC-008, ESC-010, ESC-019, REG-002 | none |
| CMP-004 | Provide Feedback | anonymous | - | none | none |
| CMP-005 | Request Supervisor Callback | otp_verified | - | ESC-003, ESC-005, POL-007 | none |
| SEC-001 | Report Fraud | anonymous | - | ESC-001, ESC-002, ESC-010, POL-002, POL-011, REG-003 | POL-006 (O), TRB-003 (O), TRB-005 (O) |
| SEC-002 | Report Phishing | anonymous | - | ESC-002, POL-002, POL-010, POL-011 | none |
| SEC-003 | Reset Credentials | otp_verified | anonymous | POL-002, POL-003, POL-011, REG-003, REG-008, TRB-007 | TRB-011 (O) |
| SEC-004 | Suspicious Activity Response | otp_verified | - | ESC-002, POL-002 | none |
| GEN-001 | Greeting | anonymous | - | POL-009 | none |
| GEN-002 | AI Disclosure Question | anonymous | - | FAQ-009, POL-009, REG-007, REG-008, REG-009 | none |
| GEN-003 | Human Agent Request | anonymous | - | ESC-001, ESC-003, ESC-010, FAQ-009 | none |
| GEN-004 | Out of Scope | anonymous | - | ESC-020, POL-002, POL-004, POL-010 | none |
| GEN-005 | Language Switch | anonymous | - | none | none |
| GEN-006 | Thanks / Closure | anonymous | - | none | none |
| GEN-007 | Distress or Emergency Disclosure | anonymous | - | ESC-004, ESC-010 | none |
| GEN-008 | Bank Service Information | anonymous | - | ESC-015, ESC-020, PRD-010 | none |

Reading the table: when `generic_info_auth` is `anonymous`, the intent's generic answers come from the anonymous entries without a step-up, and nothing account-specific is unlocked (for example ACC-001 answers "how do I check my balance" from KB-POL-003, then needs OTP before any balance is read by a tool). When the flag is `-` and `auth` is above `anonymous`, the Policy Engine asks for the step-up before answering (for example ACC-002, TXN-001), and the elevated entries are retrievable only after it.

## 5. Step-up behaviour when a query needs a higher level

| # | Scenario | Session | What happens | Entries involved |
|---|---|---|---|---|
| S1 | Public product question ("What is the NexFD rate?") | A | Answered at A; no step-up | KB-PRD-002, KB-ESC-014 |
| S2 | Statement request | A | Intent ACC-002 needs O: `AUTH_REQUIRED` before retrieval, OTP step-up, then retrieval at O, then the tool | KB-FAQ-010 (O), KB-TRB-010 (O) |
| S3 | "Money was debited but not credited" | A | TXN-003 needs O: step-up. A fraud-flavoured variant is handled as a fraud report at A (D-16) | KB-TRB-001 (O); KB-ESC-002 (A, I) |
| S4 | Unblock a blocked card | O | CRD-001 tertiary `unblock` needs B: biometric step-up with a summary and explicit yes. If the card was blocked after a fraud report, no unblock: human | KB-POL-006 (O), KB-TRB-008 (B) |
| S5 | Close the account | O | ACC-005 needs K: step-up; the agent records the reason and hands off to the branch process; ESC-007 above 5L | KB-POL-005 (K), KB-ESC-007 (K, I) |
| S6 | Known gap ("What is the RD rate?") | A | Answered by the gap entry at A. A step-up would not help, so none is requested | KB-ESC-011, KB-PRD-002 |
| S7 | Question whose best entry is above the level, intent unclear | A or O | Retrieval confidence is low; the step-up probe finds a qualifying higher-level entry and returns only the required level; the Policy Engine asks for that step-up. Nothing about the guarded entry is revealed | any elevated entry |
| S8 | Session timeout mid-chat | A (dropped) | Elevated entries leave retrieval on the next turn; the next elevated need triggers re-authentication; context is kept for 24 hours (D-05) | KB-POL-003 |
| S9 | Step-up fails | A | The agent stays at A. Generic information continues. For a fraud report, a failed OTP leads to a P0 human handoff (D-16, KB-ESC-002). Otherwise the agent offers a human | KB-ESC-002, KB-ESC-003 |
| S10 | Customer claims to be verified or asks to skip verification | any | Ignored: the level comes from the session only. Third-party and authority claims follow KB-POL-010 | KB-POL-002, KB-POL-010 |
| S11 | Chain of intents ("balance, then change my phone number") | O then B | Least privilege: authenticate for the first intent, step up only when the chain reaches the higher requirement (nlu-pipeline-overview section 4) | KB-POL-003, KB-POL-002 |
| S12 | Credential reset shortly after a contact-detail change | O | Internal check applies after verification; the agent does not send the link and hands off to Security Operations (ESC-009); the customer text stays neutral | KB-TRB-011 (O, I), KB-TRB-007 (A) |

Principles:

1. **Empty after filtering is not "no information"** (D-29). The probe in `retrieval-pipeline.md` section 5.4 turns it into a step-up.
2. **Ask once, for the level actually needed.** The step-up asks for the lowest level that opens the action, not the highest the session could reach.
3. **Never reveal existence.** The reply to an under-privileged session does not name or describe the guarded entry; it says verification is needed for what the customer asked. The probe-driven prompt uses one fixed wording and is capped per session (`retrieval-pipeline.md` section 5.4, D-51).
4. **Generic stays open.** Where the intent carries `generic_info_auth: anonymous`, generic content is answered before any step-up.
5. **Fraud first.** Reporting fraud and the empathy and containment steps are available at any level; protective actions need O and an explicit yes (KB-POL-006, KB-ESC-002).

## 6. Audience rules

| Question | `customer_facing` | `agent_internal` |
|---|---|---|
| May the Generator quote or paraphrase the text? | Yes, template-first for figures | No: it steers the action; wording is the agent's own or a template |
| Retrieval lane | Evidence | Guidance |
| Shown as a citation to the customer? | Yes, by title | Never |
| Output Safety Layer | Checks figures against the passage | Rejects verbatim copying |
| Cached FAQ path | Allowed (anonymous only) | Not cached for customers |
| Appears in logs | `id@version` | `id@version` |

## 7. Worked examples tied to entries

| Example | Session | Query (short) | Result |
|---|---|---|---|
| E1 | A | "NexCredit Premium: minimum income?" | KB-PRD-004 returned (A, C) |
| E2 | A | "What is the procedure for an unrecognised charge on my account?" | KB-TRB-005 (O) filtered. The probe may hint O. The agent asks for OTP; it does not describe the entry |
| E3 | O | "How do I unblock my card?" | KB-POL-006 (O) returned; KB-TRB-008 (B) filtered; the answer says unblocking needs biometric verification (from KB-POL-006) and offers the step-up |
| E4 | A | "I forgot my password, can the link go to a new number?" | KB-TRB-007 (A) returned; KB-TRB-011 (O, I) absent. The reply gives generic guidance only |
| E5 | O | Same as E4 after a recent contact-detail change | KB-TRB-011 returned in the guidance lane; reply neutral; handoff to Security Operations |
| E6 | O | "Close my account" | KB-POL-005 (K) and KB-ESC-007 (K) filtered; KB-POL-004 (A, I) steers; step-up to K or handoff |
| E7 | A | "Is the RD rate high?" | KB-ESC-011 (A) gap entry; no figure confirmed |
| E8 | K | "Which gold scheme should I buy?" | All entries visible; the advice boundary (KB-POL-001, KB-REG-005) still applies: a higher level never lifts the advice rule |

E8 matters: authentication gates **data and actions**. It never relaxes the advice boundary, the 8 security rules, or the no-fund-movement rule (KB-POL-004).

## 8. Tests and checks

- Gold set auth traps: every query whose best entry is above the session level lists it in `forbidden_ids` and passes only if it is absent from the result (`retrieval-pipeline.md` section 15). Counter: auth leaks, target 0.
- `tests/kb/boss-level3.yaml`: each gold ID must be permitted at the stated `auth_level`; each `forbidden_ids` entry must be above it. The Day 8 checker enforces this.
- Matrix drift: the counts in section 2 are reproduced from `entries/*.yaml` by the checker; a mismatch with the `README.md` coverage counts fails the Day 15 cross-reference lint.
- Mutation test (proposal): lower one entry's level in a copy of the KB and confirm the auth-trap queries fail.
