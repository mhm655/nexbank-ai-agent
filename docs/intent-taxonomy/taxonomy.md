# Intent Taxonomy

Source of truth: `config/intents.yaml` (41 intents, 145 tertiary labels). Entities: `config/entities.yaml`, see `entities.md`. Brief refs: A2.2, A3.1-A3.4, A4.1, A4.2, A6. Thresholds and multi-intent handling: `docs/architecture/nlu-pipeline-overview.md`. Disambiguation: `disambiguation.md`.

## 1. Structure

Three layers, as A2.2 requires:

| Layer | What it decides | Example |
|---|---|---|
| Primary (6) | `account`, `transaction`, `product`, `complaint`, `security`, `general` | `transaction` |
| Secondary (intent ID level) | The actionable intent; one row per ID below | `transaction > dispute` (TXN-002) |
| Tertiary | The variant that changes the action, entities or template | `dispute > duplicate_charge` |

`layer_path` in the dialogue state is `[primary, secondary, tertiary]`. Intent IDs are stable keys; the secondary label is the human-readable name. The A12.3 `intent_confidence_threshold` applies to the secondary layer.

**Decision D-13 (card intents).** The brief's CRD-001 to CRD-005 sit under the primary class `account`, with secondary labels `card_block`, `card_replacement`, `credit_limit_change`, `emi_conversion` and `reward_points`. This keeps the primary layer at the six classes named in A2.2. The IDs keep the `CRD-` prefix so every A3 reference still resolves.

## 2. Coverage

| Measure | Count | Requirement |
|---|---|---|
| Intents | 41 | 25 minimum, 30+ target (Linguist badge) |
| Brief intents (A3.1 to A3.3) | 32 (ACC 7, TXN 6, CRD 5, PRD 5, CMP 5, SEC 4) | all |
| Added intents | 9 (ACC-008, GEN-001 to GEN-008) | n/a |
| Tertiary labels | 145 | tertiary layer present |
| Safety ratings | LOW 12, MEDIUM 13, HIGH 10, CRITICAL 6 | all assigned |

Added intents and why:

- **ACC-008 KYC Update and Documents.** The A1.2 data package has a "KYC Update & Documents" category (45 transcripts, 81% resolution) that A3 does not cover.
- **GEN-001 to GEN-008.** A2.2 names a `general` primary class but A3 lists no general intents. These are conversation-management intents: greeting, AI disclosure, human request, out of scope, language switch, closure, distress or emergency (needed to carry the ESC-011 label) and bank service information.

## 3. Intent register

`Auth` is the level needed for account-specific data or actions. Generic, non-personal information is served at the knowledge-base entry's own level (usually anonymous). Auth levels use the state-schema names: Anonymous, OTP (`otp_verified`), Biometric (`biometric_verified`), Full KYC (`full_kyc`).

| ID | Name | Path | Tert. | Required entities | Auth | Safety | Action | ESC links |
|---|---|---|---|---|---|---|---|---|
| ACC-001 | Check Account Balance | account > balance_check | 3 | account_id or account_type | OTP | LOW | read | - |
| ACC-002 | Request Account Statement | account > statement_request | 4 | account_id, date_range, statement_format | OTP | LOW | read | - |
| ACC-003 | Update Contact Details | account > update_contact | 2 | field_to_update, new_value | Biometric | HIGH | write | - |
| ACC-004 | Update Mailing Address | account > update_mailing_address | 2 | new_address, proof_document | Biometric | HIGH | self_service_link | - |
| ACC-005 | Account Closure Request | account > account_closure | 2 | account_id, close_reason, confirmation | Full KYC | CRITICAL | handoff | ESC-007 |
| ACC-006 | Nominee Update | account > nominee_update | 4 | nominee_name, relationship, id_proof_type | Full KYC | CRITICAL | handoff | - |
| ACC-007 | Account Upgrade / Downgrade | account > account_type_change | 3 | current_account_type, desired_account_type | OTP | MEDIUM | self_service_link | - |
| ACC-008 | KYC Update and Documents | account > kyc_update | 3 | kyc_document_type | Biometric | HIGH | self_service_link | - |
| TXN-001 | Transaction Status Enquiry | transaction > status_enquiry | 3 | transaction_id or txn_description | OTP | LOW | read | ESC-014 |
| TXN-002 | Raise Transaction Dispute | transaction > dispute | 6 | transaction_id, dispute_reason, amount | OTP | HIGH | ticket | ESC-005, ESC-001 |
| TXN-003 | UPI Payment Failure | transaction > upi_failure | 4 | upi_ref, beneficiary_name, amount, date | OTP | MEDIUM | read | ESC-014 |
| TXN-004 | NEFT/RTGS Status Check | transaction > neft_rtgs_status | 2 | neft_ref, beneficiary_bank | OTP | LOW | read | ESC-014 |
| TXN-005 | Recurring Payment Setup/Cancel | transaction > recurring_payment | 4 | beneficiary_name, amount, frequency | Biometric | HIGH | write | - |
| TXN-006 | International Transfer Enquiry | transaction > international_transfer_enquiry | 4 | amount, currency, destination_country | Full KYC | HIGH | info | ESC-012, ESC-013 |
| CRD-001 | Block / Unblock Card | account > card_block | 5 | card_last4, block_reason | OTP (unblock: Biometric) | HIGH | protective_write | ESC-001 |
| CRD-002 | Card Replacement | account > card_replacement | 3 | card_last4, block_reason | Biometric | MEDIUM | write | - |
| CRD-003 | Credit Limit Change | account > credit_limit_change | 3 | card_last4, amount | Biometric | HIGH | ticket | - |
| CRD-004 | EMI Conversion | account > emi_conversion | 3 | transaction_id, tenure | OTP | MEDIUM | self_service_link | - |
| CRD-005 | Reward Points Enquiry | account > reward_points | 3 | card_last4 | OTP | LOW | read | - |
| PRD-001 | Product Information | product > product_information | 4 | product_name | Anonymous | LOW | info | ESC-008 |
| PRD-002 | Loan Eligibility and EMI | product > loan_enquiry | 5 | loan_type | Anonymous | MEDIUM | info | ESC-013 |
| PRD-003 | FD/RD Rate Enquiry | product > deposit_rates | 4 | product_name, tenure | Anonymous | MEDIUM | info | - |
| PRD-004 | Insurance Enquiry | product > insurance_enquiry | 3 | product_name | Anonymous | MEDIUM | info | ESC-008, ESC-013 |
| PRD-005 | Investment Advisory Request | product > investment_advisory | 6 | (none) | Anonymous | CRITICAL | handoff | ESC-013 |
| CMP-001 | Register Complaint | complaint > register_complaint | 7 | complaint_category, complaint_text | OTP | MEDIUM | ticket | ESC-004, ESC-002 |
| CMP-002 | Check Complaint Status | complaint > complaint_status | 2 | complaint_id | OTP | LOW | read | ESC-010 |
| CMP-003 | Escalate Complaint | complaint > escalate_complaint | 4 | complaint_id | OTP | MEDIUM | handoff | ESC-002, ESC-004, ESC-010 |
| CMP-004 | Provide Feedback | complaint > feedback | 3 | (none) | Anonymous | LOW | ticket | - |
| CMP-005 | Request Supervisor Callback | complaint > supervisor_callback | 3 | callback_time | OTP | MEDIUM | ticket | ESC-006, ESC-004 |
| SEC-001 | Report Fraud | security > report_fraud | 5 | (none) | Anonymous (protective acts: OTP) | CRITICAL | protective_write | ESC-001, ESC-009, ESC-012 |
| SEC-002 | Report Phishing | security > report_phishing | 4 | scam_channel | Anonymous | HIGH | ticket | ESC-001 |
| SEC-003 | Reset Credentials | security > reset_credentials | 4 | credential_type | OTP | CRITICAL | protective_write | ESC-009 |
| SEC-004 | Suspicious Activity Response | security > suspicious_activity_response | 3 | alert_reference | OTP | HIGH | protective_write | ESC-001, ESC-009 |
| GEN-001 | Greeting | general > greeting | 2 | (none) | Anonymous | LOW | info | - |
| GEN-002 | AI Disclosure Question | general > ai_disclosure | 3 | (none) | Anonymous | MEDIUM | info | - |
| GEN-003 | Human Agent Request | general > human_request | 3 | (none) | Anonymous | MEDIUM | handoff | ESC-006 |
| GEN-004 | Out of Scope | general > out_of_scope | 4 | (none) | Anonymous | MEDIUM | info | ESC-003 |
| GEN-005 | Language Switch | general > language_switch | 2 | language | Anonymous | LOW | info | - |
| GEN-006 | Thanks / Closure | general > closure | 3 | (none) | Anonymous | LOW | info | - |
| GEN-007 | Distress or Emergency Disclosure | general > distress_emergency | 4 | (none) | Anonymous | CRITICAL | handoff | ESC-011 |
| GEN-008 | Bank Service Information | general > service_information | 4 | (none) | Anonymous | LOW | info | - |

Auth and safety levels for the 32 brief intents follow the brief's A3.1 and A3.2 tables where given. A3.3 gives no levels for CRD, PRD, CMP and SEC, so those, and ACC-008 and the GEN intents, are my assignments (rationale in section 5).

## 4. Tertiary labels

| ID | Tertiary labels |
|---|---|
| ACC-001 | current_balance, available_balance, all_accounts_summary |
| ACC-002 | in_app_download, email_statement, mini_statement_last_n, interest_certificate |
| ACC-003 | phone_number, email_address |
| ACC-004 | communication_address, residential_address_change |
| ACC-005 | closure_request, closure_process_enquiry |
| ACC-006 | add_nominee, change_nominee, remove_nominee, nominee_status_enquiry |
| ACC-007 | upgrade, downgrade, eligibility_info |
| ACC-008 | document_update, rekyc_status, kyc_requirements_info |
| TXN-001 | by_transaction_id, by_description, recent_transactions |
| TXN-002 | merchant_error, duplicate_charge, unrecognised_charge, wrong_amount, refund_not_received, cash_not_dispensed |
| TXN-003 | debited_not_credited, payment_pending, payment_declined, wrong_beneficiary_payment |
| TXN-004 | neft, rtgs |
| TXN-005 | setup_info, cancel, modify_info, status |
| TXN-006 | process_info, charges_and_limits_info, existing_transfer_status, forex_rate_info |
| CRD-001 | block_lost, block_stolen, block_temporary, unblock, block_after_fraud |
| CRD-002 | lost_or_damaged, expired_card, replacement_status |
| CRD-003 | increase_request, decrease_request, limit_info |
| CRD-004 | transaction_to_emi, eligibility_info, charges_info |
| CRD-005 | points_balance, redemption_info, earning_rules |
| PRD-001 | features, eligibility_criteria, fees_and_charges, factual_comparison |
| PRD-002 | home_loan_criteria, personal_loan_criteria, emi_calculation, documents_required, emi_restructuring_request |
| PRD-003 | fd_rate_by_tenure, fd_features, rd_rate_enquiry, maturity_calculation |
| PRD-004 | cover_info, medical_check_requirements, claim_process_info |
| PRD-005 | interest_rate_advice, loan_affordability_advice, investment_product_advice, insurance_suitability_advice, tax_planning_advice, forex_timing_advice |
| CMP-001 | service_quality, transaction_issue, card_issue, staff_conduct, app_technical, charges_and_fees, other |
| CMP-002 | by_complaint_id, latest_open_complaint |
| CMP-003 | repeat_unresolved, escalate_existing, legal_threat, ombudsman_info |
| CMP-004 | compliment, suggestion, rating_response |
| CMP-005 | schedule_callback, callback_status, reschedule_callback |
| SEC-001 | unauthorised_transaction, account_takeover, card_misuse, scam_victim, identity_theft |
| SEC-002 | sms_or_email, vishing_call, fake_app_or_website, impersonation |
| SEC-003 | password_reset, login_unlock, device_rebind, pin_reset_info |
| SEC-004 | confirm_legitimate, deny_not_me, request_details |
| GEN-001 | hello, returning_customer |
| GEN-002 | are_you_human, how_do_you_work, data_handling_question |
| GEN-003 | first_request, repeated_request, implicit_request |
| GEN-004 | off_topic, chit_chat, unsupported_banking_request, adversarial_or_harmful |
| GEN-005 | explicit_request, detected_code_switch |
| GEN-006 | thanks, goodbye, nothing_more |
| GEN-007 | self_harm, threat_to_others, medical_emergency, coercion_or_duress |
| GEN-008 | branch_or_atm_locator, working_hours, contact_channels, app_how_to |

The tertiary layer is used where it changes what the agent does. Examples: `unblock` raises the auth requirement from OTP to Biometric (CRD-001); `legal_threat` fires ESC-002 (CMP-003); `setup_info` and `cancel` take different paths (TXN-005); `rd_rate_enquiry` has no catalogue data and so uses graceful degradation (PRD-003). When tertiary confidence is below its threshold, the agent proceeds at the secondary level and asks the tertiary question only if the answer changes the action.

## 5. Design decisions behind auth and safety ratings

1. **No intent can move money.** TXN-005 setup, CRD-004 EMI conversion and TXN-006 stop at information or a self-service link. No tool exists for fund movement (system-architecture hard rule, A4.2 rule 3).
2. **Protective actions are not gated like changes (D-08, D-16).** CRD-001 block works at OTP; unblock steps up to Biometric. SEC-001 accepts a fraud report at any auth level, because delay costs money, but any protective action still needs OTP. An anonymous reporter gets a fast OTP step, then a P0 human handoff if OTP fails.
3. **Write actions need explicit confirmation.** Every intent with a `write` or `protective_write` action, and every HIGH or CRITICAL intent that changes state, has `confirmation: explicit` (A9 Pattern 3).
4. **CRITICAL means handoff or Guardian control.** The six CRITICAL intents are ACC-005 and ACC-006 (branch or human only), PRD-005 (advice boundary), SEC-001, SEC-003 (agent never touches credentials) and GEN-007 (crisis).
5. **KB gaps are labelled.** Intents marked `kb_gap: true` (ACC-007, CRD-004, PRD-003, GEN-008) touch data that A13.1 does not contain: named account variants, EMI conversion fees, RD products, branch details. The agent must answer from KB entries or say it cannot confirm; it must never fill the gap. These are hallucination traps for the Day 10 tests.
6. **Information is not advice.** PRD-001 to PRD-004 are information. PRD-005 captures every request for a recommendation, with six tertiary classes mapped to the six A4.1 categories. PRD-002 states published criteria and runs the deterministic EMI calculator but never judges affordability.
7. **Where the brief is silent, the safer reading wins.** For example, SEC-003 is OTP-level because the agent only sends a reset link to the registered channel, but it is rated CRITICAL because a reset right after a contact change is an account-takeover pattern (ESC-009).

## 6. Mapping from the provisional Day 3 labels

`docs/architecture/boss-trace.md` used provisional labels. They map as follows (the trace is updated in place):

| Provisional | Final |
|---|---|
| ACC.balance_check | ACC-001 |
| TXN.unrecognised_charge | TXN-002 > unrecognised_charge |
| SEC.unauthorised_txn | SEC-001 > unauthorised_transaction |
| PRD.fd_info | PRD-003 > fd_rate_by_tenure |
| PRD.compare_advice | PRD-005 > investment_product_advice |
| UPI.failed_payment | TXN-003 |
| KYC.address_update | ACC-004 (an address change that alters KYC records is ACC-008) |
| CMP.general | CMP-001 |
| PRD.emi_calc | PRD-002 > emi_calculation |
| GEN.human_request | GEN-003 |

## 7. Open items

- A3.3 gives CRD, PRD, CMP and SEC no auth levels or safety ratings; the assignments here are mine and are logged as D-17 in `assumptions-and-decisions.md` for Risk Committee review.
- The tertiary labels for the brief's intents are my design; the only labels the brief itself names are `merchant_error` and `duplicate_charge`.
- Sample utterances: `utterances.csv` (Day 6, 551 rows, 13 to 17 per intent, all 41 intents and 145 tertiary labels). Language handling: `language-detection.md`. NLU tests: `tests/nlu/`.
