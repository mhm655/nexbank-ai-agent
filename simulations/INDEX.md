# Simulations index

Designed, illustrative conversations. They show how the specified system must behave; none is a transcript of a real run and nothing here was executed. Confidence, sentiment and retrieval numbers in every conversation are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form. Hindi, Hinglish and Gujarati text is not native-reviewed.

The format of every conversation is that of `conv-06-case-study-6-hinglish-upi-carry-over.md` (conv-01 to conv-06 are the brief's six case studies re-run; they share one table format; conv-06 is canonical. Differences found: a `Setup:` line exists only in conv-05 and conv-06, and a deviations table exists only in the re-runs; neither is a defect, and conv-07 onward carry a `Setup:` line and, where useful, a design-notes table). Conv-07 onward were rendered from a compact spec so that template turns carry the verbatim template wording from `config/templates/`.

## 1. All conversations

| No. | File | Scenario in one line | Persona | Channel | Language | Messages | ESC and XTR IDs | Priority |
|---|---|---|---|---|---|---|---|---|
| 01 | `conv-01-case-study-1-balance-with-otp.md` | Case Study 1 re-run: balance enquiry with authentication | Priya | app | en | 11 | none | none |
| 02 | `conv-02-case-study-2-dispute-escalating-to-fraud.md` | Case Study 2 re-run: transaction dispute escalating to fraud | Sunita | app | en | 8 | ESC-001 | P0 |
| 03 | `conv-03-case-study-3-fd-or-mutual-funds-advice.md` | Case Study 3 re-run: product question that asks for advice | Arjun | chat | en | 7 | ESC-013 | P1 |
| 04 | `conv-04-case-study-4-injection-then-authority-claim.md` | Case Study 4 re-run: prompt injection, authority claim and what follows | Vikram | chat | en | 12 | ESC-001 | P0 |
| 05 | `conv-05-case-study-5-complaint-esc-004.md` | Case Study 5 re-run: long-running complaint and the ESC-004 decision | Rajesh | app | en | 8 | ESC-004 | P1 |
| 06 | `conv-06-case-study-6-hinglish-upi-carry-over.md` | Case Study 6 re-run: Hinglish UPI follow-up across sessions | Priya | WhatsApp | hinglish | 12 | XTR-05 | none |
| 07 | `conv-07-meera-statement-and-fd-rate-gap.md` | Meera: statement request and an FD tenure the KB does not hold | Meera | app | en | 11 | XTR-03 | none |
| 08 | `conv-08-rajesh-loan-affordability-advice.md` | Rajesh: loan facts and illustration, affordability declined | Rajesh | chat | en | 12 | ESC-013 (offered, declined) | none |
| 09 | `conv-09-rajesh-duplicate-charge-esc-005.md` | Rajesh: duplicate charge above INR 50,000 and the ESC-005 handoff | Rajesh | app | en | 9 | ESC-005 | P1 |
| 10 | `conv-10-meera-hindi-disclosure-cover-and-rate-advice.md` | Meera (Hindi): AI disclosure, deposit cover, and an FD-or-savings question declined | Meera | app | hi | 10 | ESC-013 (offered, declined) | none |
| 11 | `conv-11-priya-lost-card-timeout-and-step-up.md` | Priya: lost card, a timeout that voids the confirmation, and a step-up for the replacement | Priya | app | en | 16 | none | none |
| 12 | `conv-12-priya-hinglish-multi-intent-and-parked-topic.md` | Priya (Hinglish): two requests in one message, a declined ticket and a parked topic | Priya | WhatsApp | hinglish | 9 | none | none |
| 13 | `conv-13-vikram-flooding-and-oversize-dos.md` | Vikram: oversized input and flooding, and a human request that is not throttled | Vikram | chat | en | 7 | XTR-01 | P2 |
| 14 | `conv-14-vikram-identity-spoofing-and-otp-lock.md` | Vikram: identity claim with typed facts, three failed codes, and the ESC-009 lock | Vikram | WhatsApp | en | 8 | ESC-001, ESC-009, XTR-02 | P0 |
| 15 | `conv-15-sunita-phishing-report-no-action.md` | Sunita: phishing SMS reported, nothing clicked, so a ticket and no escalation | Sunita | app | en | 10 | none | none |
| 16 | `conv-16-arjun-forex-and-tax-advice-after-hours.md` | Arjun: forex timing and tax-planning questions, and an after-hours advisor callback | Arjun | app | en | 10 | ESC-013 | P1 |
| 17 | `conv-17-sunita-hinglish-crisis-esc-011.md` | Sunita (Hinglish): crisis disclosure and the ESC-011 handoff | Sunita | chat | hinglish | 7 | ESC-011 | P0 |
| 18 | `conv-18-rajesh-pep-flag-esc-015.md` | Rajesh: a flagged customer, a generic answer, and a discreet handoff that never says why | Rajesh | chat | en | 5 | ESC-015 | P1 |
| 19 | `conv-19-rajesh-structuring-cue-esc-012.md` | Rajesh: a structuring cue, a plain refusal, and a silent AML case | Rajesh | app | en | 6 | ESC-012 | P0 |
| 20 | `conv-20-arjun-high-value-closure-esc-007.md` | Arjun: closing a high-value account, the full_kyc step, and the ESC-007 handoff | Arjun | app | en | 6 | ESC-007 | P1 |
| 21 | `conv-21-meera-nominee-referral-xtr-07.md` | Meera: nominee request, a step-up before the answer, and an honest referral with a callback | Meera | app | en | 11 | XTR-07 | P2 |
| 22 | `conv-22-priya-fee-complaint-ombudsman-esc-008.md` | Priya: a fee complaint, an ombudsman question that is not a legal threat, and an ESC-008 handoff | Priya | chat | en | 10 | ESC-008 | P1 |
| 23 | `conv-23-rajesh-hinglish-legal-threat-esc-002.md` | Rajesh (Hinglish): a legal threat and the ESC-002 handoff | Rajesh | WhatsApp | hinglish | 7 | ESC-002 | P1 |
| 24 | `conv-24-priya-hinglish-sentiment-recovery.md` | Priya (Hinglish): one very negative message, recovery without escalation | Priya | WhatsApp | hinglish | 13 | none | none |
| 25 | `conv-25-sunita-gap-and-degrade-hallucination-traps.md` | Sunita: a product the catalogue lacks, a product that does not exist, and two graceful degradations | Sunita | chat | en | 8 | none | none |
| 26 | `conv-26-sunita-low-confidence-esc-003.md` | Sunita: three vague messages and the ESC-003 handoff | Sunita | chat | en | 7 | ESC-003 | P2 |
| 27 | `conv-27-priya-human-requests-xtr-01-esc-006.md` | Priya: the first, second and third request for a human | Priya | app | en | 7 | XTR-01, ESC-006 | P2 |
| 28 | `conv-28-priya-tool-failure-esc-014.md` | Priya: a status lookup that fails twice and the ESC-014 handoff | Priya | app | en | 5 | ESC-014 | P2 |
| 29 | `conv-29-rajesh-gujarati-fallback-ladder.md` | Rajesh (Gujarati): the secondary-language fallback ladder | Rajesh | app | gu (secondary), replies in hi | 14 | XTR-01 | P2 |
| 30 | `conv-30-level-7-integration-journey.md` | LEVEL 7 INTEGRATION JOURNEY: Priya, 25 messages, five intents, one escalation decision | Priya | app | en (one Hinglish message at T14) | 25 | ESC-004, ESC-013 (offered, declined), XTR-01, XTR-06 | P1 |
| 31 | `conv-31-priya-contact-vs-address-update.md` | Priya: "update my address" is ambiguous, an email is not a postal address, and each change finishes in its secure flow | Priya | app | en | 9 | none | none |
| 32 | `conv-32-rajesh-credit-limit-never-settles-esc-010.md` | Rajesh: a credit limit request that never settles, and the ESC-010 handoff at the 16th message | Rajesh | app | en | 18 | ESC-010 | P2 |

## 2. Totals

| Measure | Value |
|---|---|
| Conversations | 32 (conv-01 to conv-06 re-run the brief's case studies; conv-07 to conv-32 are new) |
| Customer and agent messages | 318 |
| Distinct intents covered | 34 of 41 (ACC-001, ACC-002, ACC-003, ACC-004, ACC-005, ACC-006, CMP-001, CMP-002, CMP-003, CMP-004, CMP-005, CRD-001, CRD-002, CRD-003, CRD-004, CRD-005, GEN-002, GEN-003, GEN-004, GEN-006, GEN-007, GEN-008, PRD-001, PRD-002, PRD-003, PRD-005, SEC-001, SEC-002, SEC-003, TXN-001, TXN-002, TXN-003, TXN-004, TXN-006) |
| Intent families covered | ACC, TXN, CRD, PRD, CMP, SEC, GEN (all 7: ACC, TXN, CRD, PRD, CMP, SEC, GEN) |
| Personas | Priya, Rajesh, Meera, Arjun, Sunita, Vikram (all 6) |
| Adversarial vectors | prompt injection, jailbreak, social engineering, data exfiltration, denial of service, identity spoofing (all 6) |
| Brief ESC triggers fired in at least one conversation | 15: ESC-001, ESC-002, ESC-003, ESC-004, ESC-005, ESC-006, ESC-007, ESC-008, ESC-009, ESC-010, ESC-011, ESC-012, ESC-013, ESC-014, ESC-015 |
| Priorities | P0 (02, 04, 14, 17, 19), P1 (03, 05, 09, 16, 18, 20, 22, 23, 30), P2 (13, 21, 26, 27, 28, 29, 32) |
| Conversation lengths | shortest 5 messages, longest 25 (conv-30), the Level 7 journey is 25 |

## 3. What conv-01 to conv-06 already covered, and what conv-07 onward adds

| Dimension | Covered by conv-01 to conv-06 | Added by conv-07 onward |
|---|---|---|
| Intents | 9: ACC-001, CMP-003, GEN-004, GEN-006, PRD-001, PRD-005, SEC-001, TXN-002, TXN-003 | 24 more: ACC-002, ACC-003, ACC-004, ACC-005, ACC-006, CMP-001, CMP-002, CMP-005, CRD-001, CRD-002, CRD-003, CRD-004, CRD-005, GEN-002, GEN-003, GEN-007, GEN-008, PRD-002, PRD-003, SEC-002, SEC-003, TXN-001, TXN-004, TXN-006 |
| Intent families | ACC, TXN, PRD, CMP, SEC, GEN | CRD (card intents) |
| Personas | Arjun, Priya, Rajesh, Sunita, Vikram | Meera |
| Adversarial vectors | prompt injection, jailbreak, social engineering, data exfiltration | denial of service, identity spoofing |
| Escalation IDs fired | ESC-001, ESC-004, ESC-013, XTR-05 | ESC-002, ESC-003, ESC-005, ESC-006, ESC-007, ESC-008, ESC-009, ESC-010, ESC-011, ESC-012, ESC-014, ESC-015, XTR-01, XTR-02, XTR-03, XTR-06, XTR-07 |
| Priorities | P0 (conv-02, conv-04), P1 (conv-03, conv-05) | P2 as a brief trigger (ESC-003, ESC-006, ESC-014) and more P0 and P1 |
| Languages | en, hinglish | hi (Devanagari), more hinglish, gu (secondary, fallback ladder) |

## 4. Coverage matrices

Marks: `x` shown or fired, `o` offered and declined (no record), `e` evaluated and closed without a record, `s` secondary trigger only. A blank cell means not covered.

### 4.1 Conversation by intent family

| No. | ACC | TXN | CRD | PRD | CMP | SEC | GEN |
|---|---|---|---|---|---|---|---|
| 01 | x |  |  |  |  |  | x |
| 02 |  | x |  |  |  | x |  |
| 03 |  |  |  | x |  |  |  |
| 04 |  |  |  | x |  |  | x |
| 05 |  |  |  |  | x |  |  |
| 06 |  | x |  |  |  |  | x |
| 07 | x |  |  | x |  |  | x |
| 08 |  |  |  | x |  |  | x |
| 09 |  | x |  |  |  |  | x |
| 10 |  |  |  | x |  |  | x |
| 11 |  |  | x |  |  |  | x |
| 12 | x | x |  |  |  |  | x |
| 13 | x |  |  |  |  |  | x |
| 14 | x |  |  |  |  | x |  |
| 15 |  |  |  |  |  | x | x |
| 16 |  | x |  | x | x |  | x |
| 17 |  |  |  |  |  |  | x |
| 18 |  | x |  | x |  |  |  |
| 19 | x |  |  |  |  |  | x |
| 20 | x |  |  |  |  |  |  |
| 21 | x |  |  |  | x |  | x |
| 22 |  |  |  |  | x |  |  |
| 23 |  |  |  |  | x |  |  |
| 24 |  |  |  |  | x |  | x |
| 25 |  |  |  | x |  |  | x |
| 26 |  |  |  |  |  |  | x |
| 27 | x |  |  |  |  |  | x |
| 28 |  | x |  |  |  |  | x |
| 29 | x | x |  |  | x |  | x |
| 30 | x | x | x | x |  |  | x |
| 31 | x |  |  |  |  |  | x |
| 32 |  |  | x |  |  |  |  |
| Total | 12 | 9 | 3 | 9 | 7 | 3 | 23 |

### 4.2 Conversation by persona

| No. | Priya | Rajesh | Meera | Arjun | Sunita | Vikram |
|---|---|---|---|---|---|---|
| 01 | x |  |  |  |  |  |
| 02 |  |  |  |  | x |  |
| 03 |  |  |  | x |  |  |
| 04 |  |  |  |  |  | x |
| 05 |  | x |  |  |  |  |
| 06 | x |  |  |  |  |  |
| 07 |  |  | x |  |  |  |
| 08 |  | x |  |  |  |  |
| 09 |  | x |  |  |  |  |
| 10 |  |  | x |  |  |  |
| 11 | x |  |  |  |  |  |
| 12 | x |  |  |  |  |  |
| 13 |  |  |  |  |  | x |
| 14 |  |  |  |  |  | x |
| 15 |  |  |  |  | x |  |
| 16 |  |  |  | x |  |  |
| 17 |  |  |  |  | x |  |
| 18 |  | x |  |  |  |  |
| 19 |  | x |  |  |  |  |
| 20 |  |  |  | x |  |  |
| 21 |  |  | x |  |  |  |
| 22 | x |  |  |  |  |  |
| 23 |  | x |  |  |  |  |
| 24 | x |  |  |  |  |  |
| 25 |  |  |  |  | x |  |
| 26 |  |  |  |  | x |  |
| 27 | x |  |  |  |  |  |
| 28 | x |  |  |  |  |  |
| 29 |  | x |  |  |  |  |
| 30 | x |  |  |  |  |  |
| 31 | x |  |  |  |  |  |
| 32 |  | x |  |  |  |  |
| Total | 10 | 8 | 3 | 3 | 5 | 3 |

### 4.3 Conversation by guardrail group (a group counts when a guardrail of the group is listed as exercised)

| No. | ADV | SEC | REG | OUT | SYS | ATK |
|---|---|---|---|---|---|---|
| 01 |  | x | x | x |  |  |
| 02 |  | x | x | x |  |  |
| 03 | x |  | x | x |  |  |
| 04 |  | x | x | x | x | x |
| 05 |  | x | x | x |  |  |
| 06 |  | x | x | x |  |  |
| 07 | x | x | x | x |  |  |
| 08 | x |  | x | x |  |  |
| 09 |  | x | x | x |  |  |
| 10 | x |  | x | x |  |  |
| 11 |  | x | x | x |  |  |
| 12 |  | x | x | x |  |  |
| 13 |  |  | x |  |  | x |
| 14 |  | x | x |  |  | x |
| 15 |  | x | x | x |  |  |
| 16 | x | x | x | x |  |  |
| 17 |  | x | x |  |  |  |
| 18 |  | x | x | x |  |  |
| 19 |  | x | x | x |  |  |
| 20 |  | x | x | x |  |  |
| 21 |  | x | x | x |  |  |
| 22 |  | x | x | x |  |  |
| 23 |  |  | x | x |  |  |
| 24 |  | x | x | x |  |  |
| 25 |  |  | x | x |  | x |
| 26 |  |  | x | x | x |  |
| 27 |  |  | x | x |  |  |
| 28 |  |  | x | x | x |  |
| 29 |  | x | x | x | x |  |
| 30 | x | x | x | x |  | x |
| 31 |  | x | x | x | x |  |
| 32 | x | x | x | x |  |  |
| Total | 7 | 23 | 32 | 29 | 5 | 5 |

### 4.4 Conversation by ESC trigger

Columns are ESC-001 to ESC-015, shown by number.

| No. | 001 | 002 | 003 | 004 | 005 | 006 | 007 | 008 | 009 | 010 | 011 | 012 | 013 | 014 | 015 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 02 | x |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 03 |  |  |  |  |  |  |  |  |  |  |  |  | x |  |  |
| 04 | x |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 05 |  |  |  | x |  |  |  |  |  |  |  |  |  |  |  |
| 06 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 07 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 08 |  |  |  |  |  |  |  |  |  |  |  |  | o |  |  |
| 09 |  |  |  |  | x |  |  |  |  |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |  |  |  |  |  |  | o |  |  |
| 11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 13 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 14 | x |  |  |  |  |  |  |  | x |  |  |  |  |  |  |
| 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 16 |  |  |  |  |  |  |  |  |  |  |  |  | x |  |  |
| 17 |  |  |  |  |  |  |  |  |  |  | x |  |  |  |  |
| 18 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | x |
| 19 |  |  |  |  |  |  |  |  |  |  |  | x |  |  |  |
| 20 |  |  |  |  |  |  | x |  |  |  |  |  |  |  |  |
| 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 22 |  |  |  |  |  |  |  | x |  |  |  |  |  |  |  |
| 23 |  | x |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 24 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 25 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 26 |  |  | x |  |  |  |  |  |  |  |  |  |  |  |  |
| 27 |  |  |  |  |  | x |  |  |  |  |  |  |  |  |  |
| 28 |  |  |  |  |  |  |  |  |  |  |  |  |  | x |  |
| 29 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 30 |  |  |  | x |  |  |  |  |  |  |  |  | o |  |  |
| 31 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 32 |  |  |  |  |  |  |  |  |  | x |  |  |  |  |  |
| Total | 3 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 5 | 1 | 1 |

### 4.5 Conversation by extra rule (XTR)

| No. | XTR-01 | XTR-02 | XTR-03 | XTR-04 | XTR-05 | XTR-06 | XTR-07 |
|---|---|---|---|---|---|---|---|
| 01 |  |  |  |  |  |  |  |
| 02 |  |  |  |  |  |  |  |
| 03 |  |  |  |  |  |  |  |
| 04 |  |  |  |  |  |  |  |
| 05 |  |  |  |  |  |  |  |
| 06 |  |  |  |  | x |  |  |
| 07 |  |  | x |  |  |  |  |
| 08 |  |  |  |  |  |  |  |
| 09 |  |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |  |
| 11 |  |  |  |  |  |  |  |
| 12 |  |  |  |  |  |  |  |
| 13 | x |  |  |  |  |  |  |
| 14 |  | x |  |  |  |  |  |
| 15 |  |  |  |  |  |  |  |
| 16 |  |  |  |  |  |  |  |
| 17 |  |  |  |  |  |  |  |
| 18 |  |  |  |  |  |  |  |
| 19 |  |  |  |  |  |  |  |
| 20 |  |  |  |  |  |  |  |
| 21 |  |  |  |  |  |  | x |
| 22 |  |  |  |  |  |  |  |
| 23 |  |  |  |  |  |  |  |
| 24 |  |  |  |  |  |  |  |
| 25 |  |  |  |  |  |  |  |
| 26 |  |  |  |  |  |  |  |
| 27 | x |  |  |  |  |  |  |
| 28 |  |  |  |  |  |  |  |
| 29 | x |  |  |  |  |  |  |
| 30 | s |  |  |  |  | e |  |
| 31 |  |  |  |  |  |  |  |
| 32 |  |  |  |  |  |  |  |
| Total | 4 | 1 | 1 | 0 | 1 | 1 | 1 |

### 4.6 Conversation by language

| No. | en | hi | hinglish | gu (secondary) |
|---|---|---|---|---|
| 01 | x |  |  |  |
| 02 | x |  |  |  |
| 03 | x |  |  |  |
| 04 | x |  |  |  |
| 05 | x |  |  |  |
| 06 |  |  | x |  |
| 07 | x |  |  |  |
| 08 | x |  |  |  |
| 09 | x |  |  |  |
| 10 |  | x |  |  |
| 11 | x |  |  |  |
| 12 |  |  | x |  |
| 13 | x |  |  |  |
| 14 | x |  |  |  |
| 15 | x |  |  |  |
| 16 | x |  |  |  |
| 17 |  |  | x |  |
| 18 | x |  |  |  |
| 19 | x |  |  |  |
| 20 | x |  |  |  |
| 21 | x |  |  |  |
| 22 | x |  |  |  |
| 23 |  |  | x |  |
| 24 |  |  | x |  |
| 25 | x |  |  |  |
| 26 | x |  |  |  |
| 27 | x |  |  |  |
| 28 | x |  |  |  |
| 29 |  | x |  | x |
| 30 | x |  | x |  |
| 31 | x |  |  |  |
| 32 | x |  |  |  |
| Total | 25 | 2 | 6 | 1 |

### 4.7 Conversation by pattern (A9.1)

| No. | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| 01 |  | x |  | x | x |
| 02 | x | x | x |  | x |
| 03 |  | x |  | x | x |
| 04 | x | x |  | x | x |
| 05 | x | x |  | x | x |
| 06 | x | x |  | x | x |
| 07 | x | x | x | x | x |
| 08 |  | x |  | x | x |
| 09 | x | x | x | x | x |
| 10 |  | x |  | x | x |
| 11 | x | x | x | x | x |
| 12 | x | x |  | x | x |
| 13 |  |  |  | x | x |
| 14 |  | x |  | x | x |
| 15 | x | x | x |  | x |
| 16 |  | x |  | x | x |
| 17 | x |  |  | x | x |
| 18 |  | x |  | x | x |
| 19 |  | x |  | x | x |
| 20 | x | x |  | x | x |
| 21 |  | x | x | x | x |
| 22 | x | x | x | x | x |
| 23 | x | x |  | x | x |
| 24 | x | x | x | x | x |
| 25 |  | x |  | x | x |
| 26 | x | x |  | x | x |
| 27 | x |  |  | x | x |
| 28 |  |  |  | x | x |
| 29 |  | x | x | x | x |
| 30 | x | x | x | x | x |
| 31 |  | x |  |  | x |
| 32 | x | x | x | x | x |
| Total | 18 | 28 | 11 | 29 | 32 |

### 4.8 Conversation by anti-pattern designed against (A9.2)

| No. | AP1 | AP2 | AP3 | AP4 | AP5 | AP6 | AP7 | AP8 |
|---|---|---|---|---|---|---|---|---|
| 01 | x | x |  | x | x | x | x | x |
| 02 | x | x | x |  | x | x | x |  |
| 03 |  | x | x | x | x | x |  | x |
| 04 | x | x |  | x | x |  |  | x |
| 05 | x | x | x |  | x | x | x | x |
| 06 | x | x | x |  | x | x | x | x |
| 07 | x | x | x |  | x | x | x | x |
| 08 | x | x | x | x |  |  | x | x |
| 09 | x | x | x | x | x |  | x | x |
| 10 | x | x | x | x |  |  | x | x |
| 11 | x | x | x | x | x | x | x | x |
| 12 | x | x | x | x | x | x | x | x |
| 13 | x | x | x | x |  |  | x | x |
| 14 | x | x | x | x |  | x | x | x |
| 15 | x | x | x | x | x | x | x | x |
| 16 | x | x | x | x | x |  | x | x |
| 17 | x | x | x | x | x |  | x | x |
| 18 | x | x | x | x |  | x | x | x |
| 19 | x | x | x | x |  | x | x | x |
| 20 | x | x | x | x |  | x | x | x |
| 21 | x | x | x | x | x | x | x | x |
| 22 | x | x | x | x | x | x | x | x |
| 23 | x | x | x | x | x |  | x | x |
| 24 | x | x | x | x | x | x | x | x |
| 25 | x | x | x | x |  |  | x | x |
| 26 | x | x | x | x | x |  | x | x |
| 27 | x | x | x | x | x |  | x | x |
| 28 | x | x | x | x |  |  | x | x |
| 29 | x | x | x | x | x |  | x | x |
| 30 | x | x | x | x | x | x | x | x |
| 31 | x | x | x |  |  | x |  | x |
| 32 | x | x | x | x |  | x |  | x |
| Total | 31 | 32 | 30 | 27 | 21 | 19 | 28 | 31 |

### 4.9 Conversation by adversarial vector

| No. | prompt injection | jailbreak | social engineering | data exfiltration | denial of service | identity spoofing |
|---|---|---|---|---|---|---|
| 01 |  |  |  |  |  |  |
| 02 |  |  |  |  |  |  |
| 03 |  |  |  |  |  |  |
| 04 | x | x | x | x |  |  |
| 05 |  |  |  |  |  |  |
| 06 |  |  |  |  |  |  |
| 07 |  |  |  |  |  |  |
| 08 |  |  |  |  |  |  |
| 09 |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |
| 11 |  |  |  |  |  |  |
| 12 |  |  |  |  |  |  |
| 13 |  |  |  |  | x |  |
| 14 |  |  |  |  |  | x |
| 15 |  |  |  |  |  |  |
| 16 |  |  |  |  |  |  |
| 17 |  |  |  |  |  |  |
| 18 |  |  |  |  |  |  |
| 19 |  |  |  |  |  |  |
| 20 |  |  |  |  |  |  |
| 21 |  |  |  |  |  |  |
| 22 |  |  |  |  |  |  |
| 23 |  |  |  |  |  |  |
| 24 |  |  |  |  |  |  |
| 25 |  |  |  |  |  |  |
| 26 |  |  |  |  |  |  |
| 27 |  |  |  |  |  |  |
| 28 |  |  |  |  |  |  |
| 29 |  |  |  |  |  |  |
| 30 |  |  |  |  |  |  |
| 31 |  |  |  |  |  |  |
| 32 |  |  |  |  |  |  |
| Total | 1 | 1 | 1 | 1 | 1 | 1 |

### 4.10 Conversation by account-security rule (docs/guardrails/account-security.md)

| No. | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 |
|---|---|---|---|---|---|---|---|---|
| 01 | x | x |  |  | x |  |  |  |
| 02 | x | x |  |  | x | x |  |  |
| 03 |  |  |  |  |  |  |  |  |
| 04 |  |  |  | x |  |  |  | x |
| 05 |  | x |  |  |  |  |  |  |
| 06 |  | x | x |  |  |  | x |  |
| 07 | x | x | x |  | x |  |  |  |
| 08 |  |  |  |  |  |  |  |  |
| 09 |  | x |  |  |  | x |  |  |
| 10 |  |  |  |  |  |  |  |  |
| 11 | x | x |  |  |  |  | x |  |
| 12 | x | x | x |  | x |  |  |  |
| 13 |  |  |  |  |  |  |  |  |
| 14 | x | x |  |  | x | x |  |  |
| 15 |  |  |  |  | x | x |  |  |
| 16 |  |  | x |  |  |  |  |  |
| 17 |  | x |  |  |  |  |  |  |
| 18 |  |  |  |  |  | x |  |  |
| 19 | x |  | x |  |  |  |  |  |
| 20 | x | x |  |  |  | x |  |  |
| 21 | x | x |  |  |  |  |  |  |
| 22 |  | x |  |  | x |  |  |  |
| 23 |  |  |  |  |  |  |  |  |
| 24 | x | x |  |  | x |  |  |  |
| 25 |  |  |  |  |  |  |  |  |
| 26 |  |  |  |  |  |  |  |  |
| 27 |  |  |  |  |  |  |  |  |
| 28 |  |  |  |  |  |  |  |  |
| 29 | x |  |  |  |  |  |  |  |
| 30 | x | x | x |  | x |  |  |  |
| 31 | x | x |  |  | x |  |  |  |
| 32 | x | x | x |  |  |  |  |  |
| Total | 14 | 17 | 7 | 1 | 10 | 6 | 2 | 1 |

### 4.11 Conversation by priority

| No. | P0 | P1 | P2 |
|---|---|---|---|
| 01 |  |  |  |
| 02 | x |  |  |
| 03 |  | x |  |
| 04 | x |  |  |
| 05 |  | x |  |
| 06 |  |  |  |
| 07 |  |  |  |
| 08 |  |  |  |
| 09 |  | x |  |
| 10 |  |  |  |
| 11 |  |  |  |
| 12 |  |  |  |
| 13 |  |  | x |
| 14 | x |  |  |
| 15 |  |  |  |
| 16 |  | x |  |
| 17 | x |  |  |
| 18 |  | x |  |
| 19 | x |  |  |
| 20 |  | x |  |
| 21 |  |  | x |
| 22 |  | x |  |
| 23 |  | x |  |
| 24 |  |  |  |
| 25 |  |  |  |
| 26 |  |  | x |
| 27 |  |  | x |
| 28 |  |  | x |
| 29 |  |  | x |
| 30 |  | x |  |
| 31 |  |  |  |
| 32 |  |  | x |
| Total | 5 | 9 | 7 |

## 5. Intent coverage

| Intent | Name | Conversations |
|---|---|---|
| ACC-001 | Check Account Balance | 01, 12, 13, 14, 19, 29, 30 |
| ACC-002 | Request Account Statement | 07, 27 |
| ACC-003 | Update Contact Details | 31 |
| ACC-004 | Update Mailing Address | 31 |
| ACC-005 | Account Closure Request | 20 |
| ACC-006 | Nominee Update | 21 |
| ACC-007 | Account Upgrade / Downgrade | not covered |
| ACC-008 | KYC Update and Documents | not covered |
| TXN-001 | Transaction Status Enquiry | 18 |
| TXN-002 | Raise Transaction Dispute | 02, 09 |
| TXN-003 | UPI Payment Failure | 06, 12, 29, 30 |
| TXN-004 | NEFT/RTGS Status Check | 28 |
| TXN-005 | Recurring Payment Setup/Cancel | not covered |
| TXN-006 | International Transfer Enquiry | 16 |
| CRD-001 | Block / Unblock Card | 11 |
| CRD-002 | Card Replacement | 11 |
| CRD-003 | Credit Limit Change | 32 |
| CRD-004 | EMI Conversion | 30 |
| CRD-005 | Reward Points Enquiry | 30 |
| PRD-001 | Product Information | 04, 10, 25 |
| PRD-002 | Loan Eligibility and EMI | 08, 18 |
| PRD-003 | FD/RD Rate Enquiry | 07, 25 |
| PRD-004 | Insurance Enquiry | not covered |
| PRD-005 | Investment Advisory Request | 03, 08, 10, 16, 30 |
| CMP-001 | Register Complaint | 22 |
| CMP-002 | Check Complaint Status | 24 |
| CMP-003 | Escalate Complaint | 05, 22, 23 |
| CMP-004 | Provide Feedback | 24 |
| CMP-005 | Request Supervisor Callback | 16, 21, 24, 29 |
| SEC-001 | Report Fraud | 02 |
| SEC-002 | Report Phishing | 15 |
| SEC-003 | Reset Credentials | 14 |
| SEC-004 | Suspicious Activity Response | not covered |
| GEN-001 | Greeting | not covered |
| GEN-002 | AI Disclosure Question | 10 |
| GEN-003 | Human Agent Request | 09, 13, 27, 28, 29, 30 |
| GEN-004 | Out of Scope | 04, 19, 26 |
| GEN-005 | Language Switch | not covered |
| GEN-006 | Thanks / Closure | 01, 04, 06, 07, 08, 10, 11, 12, 15, 16, 19, 21, 24, 25, 29, 30, 31 |
| GEN-007 | Distress or Emergency Disclosure | 17 |
| GEN-008 | Bank Service Information | 26 |

Distinct intents covered: 34 of 41. Not covered: ACC-007, ACC-008, TXN-005, PRD-004, SEC-004, GEN-001, GEN-005.

## 6. Required scenarios and where they are shown

| Required scenario | Conversations |
|---|---|
| Information-versus-advice boundary: investment (A4.1) | 03 |
| Information-versus-advice boundary: loan products (A4.1) | 08 |
| Information-versus-advice boundary: interest rates (A4.1) | 10 |
| Information-versus-advice boundary: forex (A4.1) | 16 |
| Information-versus-advice boundary: tax planning (A4.1) | 16 |
| Information-versus-advice boundary: insurance (A4.1) | 30 |
| Sentiment recovery without escalation | 24 (and 30, where a pending escalation is cancelled after recovery) |
| Correct non-escalation near-miss | 15 (ESC-001.e not met), 22 (ombudsman question is not ESC-002), 24 (one score below -0.70), 08 and 10 (advisor offer declined), 30 (dips at T6 and T14), 32 (ESC-010 evaluated at message 15 and not fired) |
| Hindi (Devanagari) | 10, 29 |
| Hinglish | 06, 12, 17, 23, 24 (and one message in 30) |
| Secondary language with the fallback ladder | 29 |
| Multi-session carry-over with re-authentication | 06 |
| Multi-intent turn | 12, 14, 16, 31 |
| Topic switch and return | 12, 30 |
| KB gap or hallucination trap answered with the gap response | 07, 08, 16, 25, 30, 32 |
| Low-confidence retrieval with graceful degradation | 25 (retrieval), 26 (NLU confidence) |
| Tool failure (ESC-014 path) | 28 |
| Step-up authentication | 11, 20, 21, 31, 32 |
| Session timeout | 11 |
| First-request human handoff (XTR-01) | 13, 27, 29 |
| ESC-006 third-request backstop | 27 |
| Level 7 integration journey (25 messages) | 30 |
| Disambiguation pair 3: contact details or mailing address (ACC-003 vs ACC-004) | 31 |
| ESC-010 fires: more than 15 messages without a resolved topic | 32 |
| Crisis handled with care (ESC-011) | 17 |
| PEP record on every identified flagged contact, discreet live handoff only when account-specific (ESC-015) | 18 |

## 7. Gaps, stated honestly

- Intents not covered by any conversation: ACC-007, ACC-008, TXN-005, PRD-004, SEC-004, GEN-001, GEN-005.
- The information-versus-advice boundary is shown for all six A4.1 categories, but insurance appears only once (conv-30, inside the Level 7 journey) and no category is shown in more than one language other than English except interest rates in Hindi (conv-10).
- ESC-010 fires once, in conv-32, on the 16th message; conv-30 shows it as a condition that is not reached. XTR-04 (clarification budget exhausted) never fires, because a below-floor turn does not count as a clarification (D-169); conv-29 reaches two clarifications and ends in a human request instead. XTR-06 is evaluated at the ceiling in conv-30 and creates no record.
- Confidence, sentiment and retrieval numbers are illustrative values chosen to exercise thresholds. They are not measurements and no model was run.
- Hindi, Hinglish and Gujarati wording is authored and not native-reviewed (D-22). Only four KB entries have Hindi and Hinglish bodies (KB-FAQ-001, 002, 008, 009), so conversations in those languages keep to those facts, tool values and templates.
- Conv-07 to conv-30 were written when several short replies had no template (the XTR-03 offer, the XTR-01 offer, the multi-request acknowledgement, the phishing triage question, the closure-reason question, a complaint status, a cancelled-handoff line, the turn-ceiling close), so those turns are free text checked by the Output Safety Layer. The library now holds templates for most of them (TPL-ESC-CARE-OFFER, TPL-ESC-HUMAN-REQUEST-FIRST, TPL-GEN-TWO-REQUESTS, TPL-SEC-PHISHING-TRIAGE, TPL-ACC-CLOSURE-REASON, TPL-CMP-STATUS, TPL-ESC-HANDOFF-CANCELLED, TPL-GEN-LIMIT-CLOSE); those conversations have not been re-rendered with them yet. Conv-31 and conv-32 use the library as it stands.
- `config/templates/labels.yaml` still lacks the `action_plain`, `result_plain`, `service_plain`, `topic` and `option_a..c` label tables; these conversations use plain phrases for them, and the tables remain an open item for the template owners.

## 8. State-row names (D-212)

The `State` row of every conversation uses working counter names for readability. They are not a second schema. The table maps each name to a property of `config/dialogue_state.schema.json` or marks it "derived, not stored" with the rule that derives it. Neither the schema nor the conversations are changed by this mapping.

| Name in the State row | Maps to | Rule or note |
|---|---|---|
| `human_requests` | `human_request_count` | Same value; `human_requests` is the signal name in `config/escalation_rules.yaml` |
| `low_conf_streak`, `low_confidence_turns` | `consecutive_low_conf` | Same value; `low_conf_streak` is the signal name |
| `clarify_attempts` | `clarification_attempts` | Same value |
| `flagged_turns` | `guardrails.injection_attempts` | Same value; the name used by `config/templates/adversarial.yaml` |
| `neg_sentiment_streak` | `escalation.neg_sentiment_streak` | Same value |
| `turns_since_resolution` | `escalation.turns_since_resolution` | Same value |
| `otp_failures` | `escalation.otp_failures` | Same value |
| `multi_intent` | `intent.multi_intent` | Count of intents in the last message when more than one |
| `advice_deflections` | `guardrails.advice_deflections` | Same value |
| `escalation_proximity` | `escalation_proximity` | Same value |
| `dispute_open` | derived, not stored | True while a TXN-002 topic is active or parked and not resolved (the signal of the same name in `config/escalation_rules.yaml`), read from `topic_stack` |
| `pep_case_open` | derived, not stored | True when `escalation.fired` holds an ESC-015 record for the conversation (the silent case of ESC-015.a) |
| `aml_cue` | derived, not stored | Number of turns for which `guardrails.triggered` holds GR-REG-09 or GR-REG-10 (the signal `aml_indicator`) |
| `grievance_info_due_turn` | derived, not stored | The turn by which grievance information must have been given: the complaint turn plus 2 messages (GR-REG-03, D-119, D-205), computed from `history` |
| `care_flag` | derived, not stored | True once the customer has stated bereavement, serious illness, disability or hardship in the session (the signal `care_disclosure`), read from `history` |
| `degrade_count` | derived, not stored | Number of turns whose retrieval decision was `degrade`, counted from the per-turn records (`last_response` and the audit log); the dialogue state holds no such counter |
| `advisor_offers` | derived, not stored | Number of GR-ADV-08 advisor offers made in the session, counted from `guardrails.triggered` and `history` |
| `oversize_inputs` | derived, not stored | Number of messages refused by the input length limit (GR-ATK-08), counted from `guardrails.triggered` |
| `throttle_events` | derived, not stored | Number of messages refused by the rate limit (GR-ATK-08), counted from `guardrails.triggered` |
| `lang_choice_offered` | derived, not stored | 1 once the language-choice message has been sent in the session (`language.reply_language` records the outcome), counted from `history` |
| `deadline`, `awaited` (conv-06) | derived, not stored | The follow-up timer of Case Study 6; its signal is `followup_deadline_missed` in `config/escalation_rules.yaml` |
