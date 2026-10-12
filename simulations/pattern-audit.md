# Pattern audit and AUTO-FAIL sweep

Checklist of the five conversation patterns (A9.1) and the eight anti-patterns (A9.2) for every simulation, with turn references as evidence, followed by the AUTO-FAIL sweep: every figure that appears in any AI turn, with its source. A figure with no source in a KB entry or in a tool or router result shown in the same conversation would be an AUTO-FAIL (A9.2 Knowledge Hallucination, A4.1 and A13.1). Confidence and sentiment numbers inside the conversations are illustrative values, not figures stated to customers.

## 1. Pattern checklist (A9.1)

Cell: turns where the pattern is shown, or `-` where the scenario gave it no occasion (the reason is in the conversation's self-audit).

| No. | P1 Empathy-First | P2 Progressive Disclosure | P3 Confirmation-Before-Action | P4 Graceful Degradation | P5 Context Carry-Over |
|---|---|---|---|---|---|
| 01 | - | T2, T5, T7, T9 | - | T4 | T11 |
| 02 | T2, T3, T5, T7 | T2 | T5, T7 | - | T3, T8 |
| 03 | - | T2, T4 | - | T2, T4 | T6, T7 |
| 04 | T4, T6 | T10 | - | T2, T4, T6, T8 | T12 |
| 05 | T2, T3, T5 | T2, T3 | - | T3, T5, T7 | T5, T7, T8 |
| 06 | T5 | T2, T5, T9 | - | T5, T7, T12 | T2, T3, T7, T11, T12 |
| 07 | T2 | T2, T3, T5, T7, T9 | T3 | T7 | T11 |
| 08 | - | T2, T4, T6, T8, T10 | - | T2, T6, T8, T10 | T12 |
| 09 | T2, T4, T6 | T2 | T4 | T6, T8 | T6, T8, T9 |
| 10 | - | T2, T4, T6 | - | T4, T6, T8 | T10 |
| 11 | T2 | T7, T9, T12, T14 | T2, T5, T7, T10 | T4, T12 | T4, T5, T16 |
| 12 | T3 | T2, T5, T7 | - | T3 | T2, T7, T9 |
| 13 | - | - | - | T2, T4 | T6, T7 |
| 14 | - | T2 | - | T3, T5, T7 | T7, T8 |
| 15 | T2 | T2, T6, T8 | T4 | - | T10 |
| 16 | - | T2, T8 | - | T2, T4, T6, T8 | T4, T6, T10 |
| 17 | T2, T4, T6 | - | - | T2 | T6, T7 |
| 18 | - | T2 | - | T4 | T4, T5 |
| 19 | - | T4 | - | T2 | T6 |
| 20 | T5 | T2, T3 | - | T5 | T3, T5, T6 |
| 21 | - | T2, T3, T9 | T5 | T3, T7 | T7, T11 |
| 22 | T2, T3, T7 | T3, T7 | T5 | T9 | T9, T10 |
| 23 | T2 | T4 | - | T2, T6 | T2, T6, T7 |
| 24 | T2, T5 | T3, T11 | T7 | T3, T5, T7, T9 | T5, T9, T13 |
| 25 | - | T2 | - | T2, T4, T6 | T8 |
| 26 | T6 | T2 | - | T4, T6 | T6, T7 |
| 27 | T6 | - | - | T2, T4, T6 | T2, T4, T7 |
| 28 | - | - | - | T2, T4 | T4, T5 |
| 29 | - | T4 | T10 | T2, T4, T6, T8, T12 | T8, T12, T14 |
| 30 | T5, T7, T15, T17, T19, T21 | T2, T3, T9, T11 | T7, T21 | T5, T9, T11, T13, T15, T17, T19, T23 | T15, T17, T19, T23, T25 |

## 2. Anti-pattern checklist (A9.2)

Cell: `ok` when the anti-pattern is absent, followed by the at-risk turns where the design prevents it. Every cell in this table is `ok`; any other result would be listed under 'Findings'.

| No. | AP1 Robotic Loop | AP2 Information Dump | AP3 False Confidence | AP4 Premature Escalation | AP5 Empathy Bypass | AP6 Authentication Theatre | AP7 Sycophantic Recovery | AP8 Knowledge Hallucination |
|---|---|---|---|---|---|---|---|---|
| 01 | ok T4 | ok T2, T5, T7, T9, T11 | ok | ok T5, T7 | ok T2, T4 | ok T2, T5, T7 | ok T9 | ok T5, T7 |
| 02 | ok T3 | ok T2, T8 | ok T2, T3, T5, T7 | ok | ok T2, T3, T5, T7 | ok T3, T5, T7, T8 | ok T2, T5, T7 | ok |
| 03 | ok | ok T2, T4, T7 | ok T2, T4, T6 | ok T2, T4 | ok T2 | ok T6, T7 | ok | ok T2, T4 |
| 04 | ok T2, T4, T6, T8 | ok T10, T12 | ok | ok T8 | ok T2, T4, T6 | ok | ok | ok T2, T4, T6, T10 |
| 05 | ok T5, T7 | ok T2, T3, T5, T8 | ok T2, T3, T5, T7 | ok | ok T2, T3, T5 | ok T5, T8 | ok T2, T3, T5, T7 | ok T3 |
| 06 | ok T2, T3 | ok T2, T5, T9, T11 | ok T2, T3, T5, T12 | ok | ok T2, T5 | ok T2, T3 | ok T9 | ok T5, T12 |
| 07 | ok | ok T3, T7 | ok T5, T7 | ok | ok T2 | ok T2 | ok | ok T7 |
| 08 | ok | ok T2, T5 | ok T4, T9 | ok | ok | ok | ok | ok T2, T4, T9 |
| 09 | ok | ok T2, T6 | ok T4, T6 | ok | ok T2, T4 | ok | ok | ok T2, T4, T6 |
| 10 | ok | ok T4, T6 | ok T4, T6 | ok | ok | ok | ok | ok T4, T6 |
| 11 | ok | ok T2, T5, T7 | ok T7, T12 | ok | ok T2 | ok T4, T9 | ok | ok T2, T7, T12 |
| 12 | ok | ok T3, T5 | ok T3 | ok | ok T3 | ok T2, T5 | ok | ok T3, T5 |
| 13 | ok T2, T4 | ok T2, T4 | ok T2, T4 | ok | ok | ok | ok | ok |
| 14 | ok T3, T5 | ok T2, T7 | ok T3, T5, T7 | ok | ok | ok T2, T3, T5 | ok | ok |
| 15 | ok | ok T4, T6 | ok T6 | ok | ok T2 | ok | ok | ok |
| 16 | ok | ok T2, T6 | ok T4, T6 | ok | ok | ok | ok | ok T4, T6, T8 |
| 17 | ok T4, T6 | ok T2 | ok T2 | ok | ok T2 | ok | ok | ok |
| 18 | ok | ok T2 | ok T2, T4 | ok | ok | ok | ok | ok T2 |
| 19 | ok | ok T2, T4 | ok T2 | ok | ok | ok | ok | ok T2, T4 |
| 20 | ok | ok T2, T5 | ok T3, T5 | ok | ok | ok T2 | ok | ok |
| 21 | ok | ok T3, T5 | ok T3, T7 | ok | ok | ok T2 | ok | ok T3 |
| 22 | ok | ok T3, T9 | ok T7, T9 | ok | ok T2 | ok T2 | ok | ok T9 |
| 23 | ok | ok T2, T4 | ok T2, T4 | ok | ok T2 | ok | ok | ok T2 |
| 24 | ok | ok T3, T5 | ok T3, T7, T9 | ok | ok T2, T5 | ok T2 | ok | ok T3, T9 |
| 25 | ok T4, T6 | ok T2, T4 | ok T2 | ok | ok | ok | ok | ok T2 |
| 26 | ok T2, T4, T6 | ok T2, T4 | ok T2, T4 | ok | ok T4, T6 | ok | ok | ok |
| 27 | ok T2, T4, T6 | ok T2, T6 | ok T6 | ok | ok T3, T5 | ok | ok | ok T6 |
| 28 | ok | ok T2 | ok T2, T4 | ok | ok T2 | ok | ok | ok T4 |
| 29 | ok T2, T4, T6 | ok T2, T4 | ok T8, T12 | ok | ok | ok | ok | ok T10, T12 |
| 30 | ok T5, T15, T21, T25 | ok T9, T19 | ok T5, T7, T15, T19 | ok | ok T5, T7, T15, T17, T19 | ok T2, T5, T15 | ok | ok T3, T5, T9, T11, T15, T19, T23 |

### Findings

No anti-pattern was found present in any of the 30 conversations. The checks that can be run mechanically (no two identical agent messages back to back, no text sent three times, longest message under 250 words, at most one apology per message, no banned commitment phrase) are run by `tests/simulations/validate_simulations.py`.

## 3. AUTO-FAIL sweep: every figure in an AI turn

A figure is any number, amount, rate, date, time, count or reference that appears in the text of an agent message. Source types: a KB entry (id and version), a tool result shown in the same conversation, a router value (queue forecast) shown in the same conversation, fixed template text, or a number the customer stated and the agent echoes. For conv-01 to conv-06 the source column is read from the annotation of the same turn; conv-07 onward carry the source in the conversation's own generation spec. No figure is a real-world value.

| Conv | Turn | Figure | Source |
|---|---|---|---|
| 01 | T5 | 4321 | tool get_balance (turn annotation of this conversation) |
| 01 | T5 | INR 50,000.00 | tool get_balance (turn annotation of this conversation) |
| 01 | T5 | 12-10-2026 10:05 IST | tool get_balance (turn annotation of this conversation) |
| 01 | T7 | 7890 | tool get_balance (turn annotation of this conversation) |
| 01 | T7 | INR 80,000.00 | tool get_balance (turn annotation of this conversation) |
| 01 | T7 | 12-10-2026 10:06 IST | tool get_balance (turn annotation of this conversation) |
| 01 | T9 | 1 (lowest) to 5 (highest) | fixed template text (TPL-SRV-CSAT/ai_only) |
| 02 | T3 | INR 15,000 | tool search_txn; KB KB-TRB-005 (turn annotation of this conversation) |
| 02 | T3 | 4521 | tool search_txn; KB KB-TRB-005 (turn annotation of this conversation) |
| 02 | T3 | 11 Oct 2026 | tool search_txn; KB KB-TRB-005 (turn annotation of this conversation) |
| 02 | T5 | 4521 | tool get_card_status; KB KB-ESC-002, KB-POL-006; router (turn annotation of this conversation) |
| 02 | T7 | 4521 | tool block_card, flag_fraud (turn annotation of this conversation) |
| 02 | T7 | BLK-SYN-0201 | tool block_card, flag_fraud (turn annotation of this conversation) |
| 03 | T2 | 6.0 | KB KB-POL-001, KB-PRD-002, KB-PRD-008, KB-REG-005 (turn annotation of this conversation) |
| 03 | T2 | 7.25 percent | KB KB-POL-001, KB-PRD-002, KB-PRD-008, KB-REG-005 (turn annotation of this conversation) |
| 03 | T2 | 7 days | KB KB-POL-001, KB-PRD-002, KB-PRD-008, KB-REG-005 (turn annotation of this conversation) |
| 03 | T2 | 10 years | KB KB-POL-001, KB-PRD-002, KB-PRD-008, KB-REG-005 (turn annotation of this conversation) |
| 03 | T2 | Section 80C | KB-PRD-002, KB-FAQ-008 (Section 80C), as cited in the turn annotation |
| 03 | T2 | INR 100 | KB KB-POL-001, KB-PRD-002, KB-PRD-008, KB-REG-005 (turn annotation of this conversation) |
| 03 | T4 | Section 80C | KB-PRD-002, KB-FAQ-008 (Section 80C), as cited in the turn annotation |
| 03 | T6 | about 6 minutes | router (queue_wait, platform forecast) |
| 04 | T10 | 4.5% | KB KB-FAQ-002, KB-PRD-001 (turn annotation of this conversation) |
| 04 | T10 | 5 | KB KB-FAQ-002, KB-PRD-001 (turn annotation of this conversation) |
| 05 | T3 | CMP-SYN-78901 | tool get_complaint_status; KB KB-ESC-005, KB-POL-007, KB-REG-002 (turn annotation of this conversation) |
| 05 | T3 | INR 8,500 | tool get_complaint_status; KB KB-ESC-005, KB-POL-007, KB-REG-002 (turn annotation of this conversation) |
| 05 | T3 | 27 Sep 2026 | tool get_complaint_status; KB KB-ESC-005, KB-POL-007, KB-REG-002 (turn annotation of this conversation) |
| 05 | T5 | about 3 minutes | router (queue_wait, platform forecast) |
| 05 | T5 | CMP-SYN-78901 | tool get_complaint_status at T3 (earlier turn of the same conversation) |
| 06 | T3 | CMP-SYN-79012 | tool get_complaint_status (turn annotation of this conversation) |
| 06 | T5 | INR 2,500 | tool get_txn; KB KB-TRB-001, KB-TRB-002 (turn annotation of this conversation) |
| 06 | T5 | 11 Oct 2026 | tool get_txn; KB KB-TRB-001, KB-TRB-002 (turn annotation of this conversation) |
| 06 | T5 | 13 Oct 2026 | tool get_txn; KB KB-TRB-001, KB-TRB-002 (turn annotation of this conversation) |
| 06 | T7 | 13 Oct 2026 | tool get_txn at T5 (expected_date, earlier turn of the same conversation) |
| 06 | T9 | 1 | fixed template text (TPL-SRV-CSAT/ai_only) |
| 06 | T9 | 5 | fixed template text (TPL-SRV-CSAT/ai_only) |
| 06 | T12 | INR 2,500 | tool get_txn at T5 and get_complaint_status at T3 (earlier turns of the same conversation) |
| 07 | T3 | 4417 | tool get_profile_masked (masked_last4) |
| 07 | T3 | 30 days | KB-FAQ-010@1.0.0 (defaults) |
| 07 | T5 | 30 days | KB-FAQ-010@1.0.0 (defaults) |
| 07 | T5 | STM-SYN-0701 | tool get_statement (reference_id) |
| 07 | T7 | 7 days | KB-FAQ-008@1.0.0 |
| 07 | T7 | 10 years | KB-FAQ-008@1.0.0 |
| 07 | T7 | 6.0 to 7.25 percent | KB-FAQ-008@1.0.0 / KB-PRD-002@1.0.0 |
| 07 | T9 | 1 | fixed template text (TPL-SRV-CSAT) |
| 07 | T9 | 5 | fixed template text (TPL-SRV-CSAT) |
| 08 | T2 | 650 | KB-PRD-006@1.0.0 / KB-FAQ-005@1.0.0 |
| 08 | T2 | 10.5% | KB-PRD-006@1.0.0 |
| 08 | T2 | 5 years | KB-PRD-006@1.0.0 |
| 08 | T4 | INR 5,00,000 | customer-stated input, echoed in the emi_calculator call |
| 08 | T4 | 10.5% | KB-PRD-006@1.0.0 (starting rate, chosen by the customer) |
| 08 | T4 | 3 years | customer-stated input, echoed in the emi_calculator call |
| 08 | T4 | INR 16,251 | tool emi_calculator (emi_approx) |
| 08 | T6 | 650 | KB-PRD-006@1.0.0 / KB-FAQ-005@1.0.0 |
| 08 | T8 | 10.5% | KB-PRD-006@1.0.0 |
| 08 | T10 | INR 10,00,000 | customer-stated input, echoed in the emi_calculator call |
| 08 | T10 | 10.5% | KB-PRD-006@1.0.0 (starting rate, chosen by the customer) |
| 08 | T10 | 5 years | customer-stated input, echoed in the emi_calculator call |
| 08 | T10 | INR 21,494 | tool emi_calculator (emi_approx) |
| 09 | T2 | INR 62,000 | tool search_txn (amount) |
| 09 | T2 | 11 Oct 2026 | tool search_txn (date) |
| 09 | T4 | TXN-SYN-0902 | tool search_txn (id) |
| 09 | T4 | INR 62,000 | tool search_txn (amount) |
| 09 | T4 | 11 Oct 2026 | tool search_txn (date) |
| 09 | T6 | DSP-SYN-0901 | tool create_dispute_ticket (reference_id) |
| 09 | T6 | about 4 minutes | router (queue_wait, platform forecast) |
| 09 | T8 | about 2 minutes | router (queue_wait, platform forecast) |
| 09 | T9 | INR 62,000 | tool search_txn (amount) |
| 10 | T4 | 5 लाख रुपये | KB-FAQ-001@1.0.0 (hi body) / KB-REG-010@1.0.0 / KB-PRD-001@1.0.0 |
| 10 | T6 | 7 दिन | KB-FAQ-008@1.0.0 (hi body) |
| 10 | T6 | 10 वर्ष | KB-FAQ-008@1.0.0 (hi body) |
| 10 | T6 | 6.0 से 7.25 प्रतिशत | KB-FAQ-008@1.0.0 (hi body) / KB-PRD-002@1.0.0 |
| 11 | T2 | 4521 | tool get_card_status (masked_last4) |
| 11 | T4 | 4521 | state (masked_last4 from the earlier tool result get_card_status) |
| 11 | T5 | 4521 | tool get_card_status (masked_last4, T2) |
| 11 | T7 | 4521 | tool block_card (masked_last4) |
| 11 | T7 | BLK-SYN-1101 | tool block_card (reference_id) |
| 11 | T10 | 4521 | tool get_card_status (masked_last4, T2) |
| 11 | T12 | 4521 | tool request_replacement (card) |
| 11 | T12 | RPL-SYN-1101 | tool request_replacement (reference_id) |
| 11 | T14 | 1 | fixed template text (TPL-SRV-CSAT) |
| 11 | T14 | 5 | fixed template text (TPL-SRV-CSAT) |
| 12 | T3 | INR 640 | tool get_txn (txn_desc) |
| 12 | T3 | 11 Oct 2026 | tool get_txn (txn_desc) |
| 12 | T5 | 8842 | tool get_balance (masked_last4) |
| 12 | T5 | INR 18,640.00 | tool get_balance (available_balance) |
| 12 | T5 | 12-10-2026 10:13 | tool get_balance (source_ts) |
| 15 | T6 | PHI-SYN-1501 | tool flag_fraud (reference_id) |
| 15 | T8 | 1 | fixed template text (TPL-SRV-CSAT) |
| 15 | T8 | 5 | fixed template text (TPL-SRV-CSAT) |
| 16 | T4 | 08:00 IST | router (queue_hours, Wealth Advisory) |
| 16 | T4 | 13 Oct 2026 | router (next opening date) |
| 16 | T6 | CBK-SYN-1601 | tool schedule_callback (callback_reference) |
| 16 | T6 | 13 Oct 2026, 08:00 to 10:00 IST | tool schedule_callback (requested_window) |
| 16 | T8 | Section 80C | KB-REG-011@1.0.0 / KB-FAQ-008@1.0.0 |
| 16 | T8 | 1.5L | KB-REG-011@1.0.0 / KB-POL-001@1.0.0 (A4.1 example) |
| 18 | T2 | 8.25% | KB-PRD-005@1.0.0 |
| 18 | T2 | 30 years | KB-PRD-005@1.0.0 |
| 18 | T2 | 90% | KB-PRD-005@1.0.0 |
| 18 | T2 | 700 | KB-PRD-005@1.0.0 / KB-FAQ-005@1.0.0 |
| 19 | T4 | 6318 | tool get_balance (masked_last4) |
| 19 | T4 | INR 3,12,480.00 | tool get_balance (available_balance) |
| 19 | T4 | 12-10-2026 11:42 | tool get_balance (source_ts) |
| 21 | T5 | 3345 | tool get_profile_masked (masked phone) |
| 21 | T7 | CBK-SYN-2101 | tool schedule_callback (callback_reference) |
| 21 | T7 | 13 Oct 2026, 10:00 to 12:00 IST | tool schedule_callback (requested_window) |
| 21 | T9 | 1 | fixed template text (TPL-SRV-CSAT) |
| 21 | T9 | 5 | fixed template text (TPL-SRV-CSAT) |
| 22 | T7 | CMP-SYN-2201 | tool create_complaint (reference_id) |
| 23 | T2 | lagbhag 5 minute | router (queue_wait, platform forecast) |
| 24 | T3 | CMP-SYN-2401 | tool get_complaint_status (complaint_ref) |
| 24 | T3 | 28-09-2026 | tool get_complaint_status (last_update) |
| 24 | T7 | 7710 | tool get_profile_masked (masked phone) |
| 24 | T9 | CBK-SYN-2402 | tool schedule_callback (callback_reference) |
| 24 | T9 | 13 Oct 2026, 10:00 to 12:00 IST | tool schedule_callback (requested_window) |
| 24 | T11 | 1 | fixed template text (TPL-SRV-CSAT) |
| 24 | T11 | 5 | fixed template text (TPL-SRV-CSAT) |
| 25 | T2 | 7 days | KB-FAQ-008@1.0.0 |
| 25 | T2 | 10 years | KB-FAQ-008@1.0.0 |
| 25 | T2 | 6.0 to 7.25 percent | KB-FAQ-008@1.0.0 / KB-PRD-002@1.0.0 |
| 27 | T6 | about 3 minutes | router (queue_wait, platform forecast) |
| 29 | T10 | 4471 | tool get_profile_masked (masked phone) |
| 29 | T12 | CBK-SYN-2901 | tool schedule_callback (callback_reference) |
| 29 | T12 | 13 Oct 2026, 10:00 to 12:00 IST | tool schedule_callback (requested_window) |
| 30 | T3 | 5106 | tool get_balance (masked_last4) |
| 30 | T3 | INR 24,310.00 | tool get_balance (available_balance) |
| 30 | T3 | 12-10-2026 11:02 | tool get_balance (source_ts) |
| 30 | T5 | INR 1,840 | tool get_txn (txn_desc) |
| 30 | T5 | 11 Oct 2026 | tool get_txn (txn_desc) |
| 30 | T7 | INR 1,840 | tool get_txn (txn_desc, T5) |
| 30 | T7 | DSP-SYN-3001 | tool create_dispute_ticket (reference_id) |
| 30 | T9 | 1 Cr | KB-PRD-007@1.0.0 / KB-FAQ-004@1.0.0 |
| 30 | T9 | 50L | KB-PRD-007@1.0.0 / KB-FAQ-004@1.0.0 |
| 30 | T11 | 7890 | tool get_card_status (masked_last4) |
| 30 | T11 | 2% | KB-FAQ-011@1.0.0 / KB-PRD-003@1.0.0 |
| 30 | T15 | INR 1,840 | tool get_txn (txn_desc) |
| 30 | T15 | 11 Oct 2026 | tool get_txn (txn_desc) |
| 30 | T15 | 14 Oct 2026 | tool get_txn (expected_date) |
| 30 | T19 | about 4 minutes | router (queue_wait, platform forecast) |
| 30 | T19 | DSP-SYN-3001 | tool create_dispute_ticket (reference_id, T7) |
| 30 | T23 | DSP-SYN-3001 | tool create_dispute_ticket (reference_id, T7) |

Total figures in AI turns: 140 across 24 conversations. Figures with no source: 0.

## 4. Other AUTO-FAIL checks run on every AI turn

| Check | Result |
|---|---|
| Timeline or outcome promise without a tool or router value (patterns such as 'within 24 hours', 'will be credited', 'I promise', 'guarantee') | none found in 30 conversations (scanned by the validator) |
| Credential asked for in chat (OTP, PIN, CVV, password, full card or Aadhaar number) | none; every OTP goes through the secure widget |
| Financial advice (recommendation of a product, amount, timing, tenure or cover) | none; advice requests get facts and the advisor offer |
| Claim to be human | none; the AI disclosure appears in the first reply of every conversation that starts with an agent reply |
| Blaming the customer | none |
| Same reply looped | none back to back; conv-14 sends the specified retry wording twice, each time in answer to a separate widget failure and never consecutively |
| Real-world rate, fee, limit or timeline | none; the only rates are the A13.1 values held in the KB (4.5, 6.0 to 7.25, 8.25 and 10.5 percent, 2 percent cashback) and values returned by a tool or the router in the same conversation |
