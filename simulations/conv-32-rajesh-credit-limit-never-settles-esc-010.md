# conv-32: Rajesh: a credit limit request that never settles, and the ESC-010 handoff at the 16th message

Designed, illustrative conversation. It shows how the specified system must behave; it is not a transcript of a real run, and nothing here was executed. Confidence, sentiment and retrieval scores are illustrative values chosen to exercise thresholds. Account data, references and dates are synthetic tool results; identifiers appear only in masked form.

## Header

| Field | Value |
|---|---|
| Scenario | Rajesh, signed in to the app, asks for a higher credit limit on his NexCredit card. The assistant can only take a request and cannot say what limit he would get or whether it would be approved, and every answer it can give is a stated gap or a boundary. He keeps asking, compares the Premium card, names an amount and changes it. No topic is ever resolved, and on the 16th message the conversation exceeds 15 messages without a resolved topic (ESC-010): a warm handoff to Supervisor Review follows, with the open question carried over. |
| Persona | Rajesh (Business Owner) |
| Channel | app |
| Language | en |
| Starting auth level | otp_verified |
| Intents covered | CRD-003 |
| Guardrails exercised | GR-ADV-06, GR-OUT-01, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-REG-15, GR-REG-16, GR-REG-19, GR-SEC-R1, GR-SEC-R2, GR-SEC-R3 |
| Escalation outcome | ESC-010 fired at T16 (P2, Supervisor Review): ESC-010.a, turns_since_resolution 16 with CRD-003 still active; warm handoff announced at T17 and accepted at E2 |
| Escalation IDs | ESC-010 |
| Priority | P2 |
| Adversarial vectors | none |
| Security rules exercised | R1, R2, R3 |
| Patterns shown | P1, P2, P3, P4, P5 |
| Anti-patterns designed against | AP1, AP2, AP3, AP4, AP6, AP8 |
| Coverage tags | ESC-010 fires on the 16th message (turns_since_resolution 16 above 15, open topic), boundary at message 15 (not yet), CRD-003 credit limit intake with KB-ESC-017 gap, no credit decision or approval promised (GR-REG-15), step-up to biometric_verified (R2), repeated gap answers worded differently, full state at every turn |
| Case study | none (new scenario, not a brief case study) |
| Templates used | TPL-GEN-GREETING, TPL-AUTH-STEP-UP, TPL-KB-GAP, TPL-ACT-CANNOT-DO, TPL-ESC-HANDOFF-WARM, TPL-ESC-HUMAN-JOINED |
| KB entries cited | KB-POL-003, KB-PRD-003, KB-ESC-017, KB-REG-009, KB-PRD-004, KB-ESC-010 |
| Tools called | get_card_status |
| prompt_version | sp-1.1.0+1527a050.n000000 (template versions as listed in config/templates, shown with each Generation row; model_version unbound) |
| What this conversation proves | ESC-010 fires only when more than 15 messages pass with no resolved topic and a topic is open, not before (message 15 does not fire it), the assistant never invents a limit or promises an approval while it waits, answers a repeated question in new words instead of looping, and hands the open request to a person with every figure carried over and nothing asked again. |

Setup: Rajesh, Surat, is signed in to the app at 14:10 IST on 12 Oct 2026 (otp_verified). His NexCredit Classic card is masked ending 6642 in the synthetic card record. Supervisor Review runs 08:00 to 22:00 IST (open).

## Turns

Turn unit: one customer or agent message (D-119). System events (E) are not counted. Each block lists the annotation after the message has been processed.

### T1 | Customer

> I want my credit limit increased on my NexCredit card.

| Field | Value |
|---|---|
| NLU | intent `CRD-003` 0.88 (tertiary increase_request); runner-up `CRD-005` 0.30; entities: card_type=credit (stated); language: en 0.99 |
| Sentiment | raw 0.00, smoothed 0.00, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: GR-SEC-R2 (CRD-003 needs biometric_verified; the session holds otp_verified) |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase INIT > INTENT_DETECT > AUTH_REQUIRED; auth otp_verified; turn_count 1; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 1; escalation_proximity 0.00 |
| Decision point | A credit limit change is an intake request: the bank decides, the agent never does (intents.yaml CRD-003). The step-up comes first. |

### T2 | Agent

> Hello, I'm NexBank's AI assistant. You're verified for everyday requests. To request a credit limit change I need one more check: please confirm with your fingerprint or face in the app prompt I've opened. I won't ask you to verify again for this once it's done.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-16 (AI disclosure), GR-SEC-R2 (step-up to biometric_verified before the request is taken) |
| KB / tools | KB: KB-POL-003@1.0.0 (0.86); retrieval confidence 0.86; decision step_up |
| Action | transfer: step-up to biometric_verified in the app prompt |
| Generation | template `TPL-GEN-GREETING/with_request@1.1.0` + `TPL-AUTH-STEP-UP/biometric@1.0.0` (language en); patterns: P2; anti-pattern check: none |
| State | phase AUTH_REQUIRED; auth otp_verified; turn_count 2; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### E1 | System event

> Secure widget reports: fingerprint or face check passed in the app prompt. The Gateway raises the session claim to biometric_verified. Nothing biometric passed through the chat, the state or the logs.

| Field | Value |
|---|---|
| State | phase AUTH_REQUIRED > EXECUTE; auth biometric_verified; turn_count 2; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled)}; pending_confirmation none; counters: all 0; turns_since_resolution 2; escalation_proximity 0.00 |

### T3 | Agent

> Thank you, that's done. I can see your NexCredit Classic card ending 6642. What limit would you like to ask for?

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.00 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-SEC-R1 (last four digits only), GR-OUT-01 (card from the tool), GR-OUT-03 (no limit stated) |
| KB / tools | KB: KB-PRD-003@1.0.0 (0.80), KB-ESC-017@1.0.0 (0.70); retrieval confidence 0.80; decision answer<br>tool: `get_card_status`() -> ok: {cards: [credit NexCredit Classic ending 6642, status active]} |
| Action | respond: the card is named from the tool and the one missing entity (the amount to request) is asked for |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on the get_card_status result and KB-PRD-003; no figure beyond the masked card ending; language en); patterns: P2, P5; anti-pattern check: none |
| State | phase EXECUTE; auth biometric_verified; turn_count 3; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 3; escalation_proximity 0.00 |
| Decision point | No template asks for the amount of a limit request, so the question is short free text checked by the Output Safety Layer (D-172), grounded on the get_card_status result and KB-ESC-017. |

### T4 | Customer

> Make it as high as you can. What limit can I get?

| Field | Value |
|---|---|
| NLU | intent `CRD-003` 0.86 (tertiary limit_info); runner-up `PRD-001` 0.35; entities: none |
| Sentiment | raw 0.05, smoothed 0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth biometric_verified; turn_count 4; topic_stack [CRD-003 (limit_info): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 4; escalation_proximity 0.00 |

### T5 | Agent

> I don't have that fee or limit in the information I hold. I can share the card features and eligibility, or connect you with a team member. Credit limit decisions are made by the bank, not by me, so I can only take your request.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays 0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-01 (no limit stated), GR-OUT-03 (the gap is stated), GR-OUT-05 (no outcome promised) |
| KB / tools | KB: KB-ESC-017@1.0.0 (0.90), KB-PRD-003@1.0.0 (0.62); retrieval confidence 0.90; decision gap |
| Action | respond: gap statement for the limit value; the intake route is named |
| Generation | hybrid `TPL-KB-GAP/statement_only@1.0.0` + free text (grounded on KB-ESC-017; no figure; language en); patterns: P4; anti-pattern check: none |
| State | phase RESPOND; auth biometric_verified; turn_count 5; topic_stack [CRD-003 (limit_info): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 5; escalation_proximity 0.00 |
| Decision point | A gap answer states what is not known; it does not resolve the topic, so turns_since_resolution keeps counting. The second sentence restates KB-ESC-017 ("credit limit decisions are made by the bank, not the agent") as free text. |

### T6 | Customer

> Fine, take the request then. Will it be approved?

| Field | Value |
|---|---|
| NLU | intent `CRD-003` 0.84 (tertiary increase_request); runner-up `CRD-003` limit_info 0.40; entities: none |
| Sentiment | raw -0.05, smoothed -0.01, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth biometric_verified; turn_count 6; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 6; escalation_proximity 0.00 |

### T7 | Agent

> That isn't something I can decide or promise in chat. I can note your request once you tell me the limit you would like to ask for.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.01 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-REG-15 (no credit verdict), GR-OUT-05 (no outcome promised), GR-SEC-R3 |
| KB / tools | KB: KB-ESC-017@1.0.0 (0.80), KB-REG-009@1.0.0 (0.60); retrieval confidence 0.80; decision answer |
| Action | respond: no approval is promised (credit decisions are the bank's); the next step is named |
| Generation | template `TPL-ACT-CANNOT-DO/decision_or_waiver@1.0.0` (language en); patterns: P4; anti-pattern check: none |
| State | phase RESPOND; auth biometric_verified; turn_count 7; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 7; escalation_proximity 0.00 |

### T8 | Customer

> I don't know what to ask for. What do other customers usually get?

| Field | Value |
|---|---|
| NLU | intent `CRD-003` 0.80 (tertiary limit_info); runner-up `PRD-001` 0.32; entities: none |
| Sentiment | raw -0.10, smoothed -0.06, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth biometric_verified; turn_count 8; topic_stack [CRD-003 (limit_info): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 8; escalation_proximity 0.10 |

### T9 | Agent

> I don't have typical limits to share, and I'd rather not guess. The limit is set by the bank for each customer. You can name a figure to include in your request, or I can bring in a colleague to talk it through.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.06 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-01 (no limit stated), GR-OUT-03, GR-OUT-05, GR-ADV-06 (no recommendation of an amount) |
| KB / tools | KB: KB-ESC-017@1.0.0 (0.88); retrieval confidence 0.88; decision gap |
| Action | respond: a second gap answer in different words that adds a choice: name a figure, or have a person help |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on KB-ESC-017; no figure; language en); patterns: P4; anti-pattern check: none |
| State | phase RESPOND; auth biometric_verified; turn_count 9; topic_stack [CRD-003 (limit_info): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 9; escalation_proximity 0.10 |
| Decision point | KB-ESC-017 lists credit limit values as unknown and forbids stating one. The reply differs from T5 on purpose (A9.2 Robotic Loop): it explains why no typical figure is given and offers the two next steps. Free text checked by the Output Safety Layer (D-172). |

### T10 | Customer

> Is income proof needed for a limit increase?

| Field | Value |
|---|---|
| NLU | intent `CRD-003` 0.78 (tertiary limit_info); runner-up `PRD-001` 0.40; entities: none |
| Sentiment | raw 0.00, smoothed -0.03, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth biometric_verified; turn_count 10; topic_stack [CRD-003 (limit_info): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 10; escalation_proximity 0.10 |

### T11 | Agent

> For the card itself, the catalogue lists income proof and a credit score check. It doesn't say what a limit change needs, so I can't tell you that.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.03 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-01 (only what the catalogue states), GR-OUT-03 (the unknown is named), GR-OUT-05 |
| KB / tools | KB: KB-PRD-003@1.0.0 (0.84), KB-ESC-017@1.0.0 (0.76); retrieval confidence 0.84; decision gap |
| Action | respond: the catalogue requirement for the card is separated from the unknown requirement for a limit change |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on KB-PRD-003 and KB-ESC-017; no figure; language en); patterns: P4; anti-pattern check: none |
| State | phase RESPOND; auth biometric_verified; turn_count 11; topic_stack [CRD-003 (limit_info): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool)}; pending_confirmation none; counters: all 0; turns_since_resolution 11; escalation_proximity 0.10 |
| Decision point | No template renders a partial answer with a stated unknown, so this is short free text (D-172). The answer is still not a resolution of the topic. |

### T12 | Customer

> What about the Premium card? Would its limit be higher?

| Field | Value |
|---|---|
| NLU | intent `CRD-003` 0.76 (tertiary limit_info); runner-up `PRD-001` 0.55; entities: card_type=premium (stated) |
| Sentiment | raw -0.05, smoothed -0.04, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > RESPOND; auth biometric_verified; turn_count 12; topic_stack [CRD-003 (limit_info): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool); card_type_considered=premium (stated)}; pending_confirmation none; counters: all 0; turns_since_resolution 12; escalation_proximity 0.10 |

### T13 | Agent

> The catalogue doesn't list a credit limit for either card, so I can't compare them. For the Premium card it lists a minimum income of 10 LPA and enhanced KYC.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.04 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-01 (10 LPA equals the KB value), GR-OUT-03, GR-ADV-06 (facts only, no recommendation of a card), GR-OUT-05 |
| KB / tools | KB: KB-PRD-004@1.0.0 (0.88), KB-ESC-017@1.0.0 (0.72); retrieval confidence 0.88; decision gap |
| Action | respond: the Premium entry's requirements are stated as the catalogue holds them; the limit comparison is declined as unknown |
| Generation | llm (free text inside prompt layers 0 to 5; grounded on KB-PRD-004 and KB-ESC-017; one figure from the KB entry; language en); patterns: P4; anti-pattern check: none |
| State | phase RESPOND; auth biometric_verified; turn_count 13; topic_stack [CRD-003 (limit_info): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool); card_type_considered=premium (stated)}; pending_confirmation none; counters: all 0; turns_since_resolution 13; escalation_proximity 0.10 |
| Decision point | The two cards are not compared and neither is recommended. Free text checked by the Output Safety Layer (D-172). |

### T14 | Customer

> So just raise it by 20,000 rupees and let us see.

| Field | Value |
|---|---|
| NLU | intent `CRD-003` 0.87 (tertiary increase_request); runner-up `CRD-003` limit_info 0.30; entities: amount=INR 20,000 (stated) |
| Sentiment | raw -0.15, smoothed -0.09, confidence 0.85; emotions: frustration 0.30 |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: none |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase RESPOND > INTENT_DETECT > CONFIRM; auth biometric_verified; turn_count 14; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool); amount=INR 20,000 (stated)}; pending_confirmation none; counters: all 0; turns_since_resolution 14; escalation_proximity 0.20 |
| Decision point | The amount is the customer's own figure. It is a request to be taken, not a limit the agent grants. |

### T15 | Agent

> To be sure I note this correctly: you would like to ask for an increase of INR 20,000 on the card ending 6642. Shall I take that request? Please reply yes or no.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.09 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (no outcome promised), GR-SEC-R1, GR-REG-15 (no approval implied) |
| KB / tools | KB: KB-ESC-017@1.0.0 (0.84); retrieval confidence 0.84; decision answer |
| Action | confirm: explicit confirmation before the intake request is taken; nothing is submitted until the customer says yes |
| Generation | llm (free text inside prompt layers 0 to 5; the INR 20,000 is the customer's own figure; the masked card ending is from the get_card_status result; language en); patterns: P3; anti-pattern check: none |
| State | phase CONFIRM; auth biometric_verified; turn_count 15; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool); amount=INR 20,000 (stated)}; pending_confirmation take_limit_request, offered; counters: all 0; turns_since_resolution 15; escalation_proximity 0.20 |
| Decision point | No tool or confirmation template exists for a credit limit intake (the action labels of TPL-ACT-CONFIRM name tools, and CRD-003 has none), so the confirmation is short free text with the amount echoed from the customer (D-172). turns_since_resolution is 15 here: ESC-010 needs more than 15, so it does not fire yet. |

### T16 | Customer

> Hold on, let me think about the amount again. Can we make it 30,000 instead?

| Field | Value |
|---|---|
| NLU | intent `CRD-003` 0.74 (tertiary increase_request); runner-up `CRD-003` limit_info 0.30; entities: amount=INR 30,000 (stated, replaces INR 20,000) |
| Sentiment | raw 0.00, smoothed -0.05, confidence 0.85; emotions: none |
| Guardrails | checked: Input Guard: GR-ATK-01, GR-ATK-03, GR-ATK-08, GR-SEC-R5 redaction, crisis screen; triggered: ESC-010.a evaluated and met: turns_since_resolution 16 is above esc010_turns (15) and CRD-003 is still active (open_topic); no topic has reached resolved since the start of the conversation |
| KB / tools | none on the customer message (retrieval and tools run for the reply) |
| Action | n/a (customer message; the policy decision is on the next agent message) |
| Generation | n/a (customer message) |
| State | phase CONFIRM > ESCALATING; auth biometric_verified; turn_count 16; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool); amount=INR 30,000 (stated)}; pending_confirmation take_limit_request, not answered; counters: all 0; turns_since_resolution 16; escalation_proximity 0.60 |
| Decision point | This is message 16 with no topic resolved (D-119): ESC-010.a fires on the customer message, and the next agent message announces it. Nothing in the customer's tone fires another trigger (raw 0.00). The cause is not the customer: five gap or boundary answers and an open confirmation cannot resolve the topic, and the one question left is a person's decision. |

### T17 | Agent

> We've covered a lot of ground on this request. A colleague from our senior support team is the right person for this, and I'm bringing them into this chat. They'll have the full details, so you won't need to repeat yourself. The current estimate is about 6 minutes; it is an estimate, and I'll stay here until they join. I've noted your credit limit request on the card ending 6642 for them.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 (the wait is a router estimate), GR-REG-19, GR-OUT-04 (one acknowledgement, no apology) |
| KB / tools | KB: KB-ESC-010@1.0.0 (0.86), KB-ESC-017@1.0.0 (0.70); retrieval confidence 0.86; decision answer<br>router: queue=Supervisor Review (open, 08:00-22:00 IST); team_plain=senior support team; queue_wait=about 6 minutes (platform forecast, stated as an estimate) |
| Action | escalate: ESC-010 warm handoff to Supervisor Review; the package is built from state (nothing re-typed); the agent stays; the open confirmation is not taken |
| Generation | template `TPL-ESC-HANDOFF-WARM/standard_with_wait@1.0.0` (language en); patterns: P1, P5; anti-pattern check: none |
| State | phase ESCALATING; auth biometric_verified; turn_count 17; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool); amount=INR 30,000 (stated)}; pending_confirmation take_limit_request, not answered; counters: all 0; turns_since_resolution 17; escalation_proximity 0.60 |
| Decision point | The pending confirmation is not answered by the agent: a request to raise a limit by INR 30,000 was never confirmed, so none is submitted. The colleague receives both figures and the unanswered question. |

### E2 | System event

> A Supervisor Review colleague accepts the conversation.

| Field | Value |
|---|---|
| State | phase ESCALATING > HANDOFF; auth biometric_verified; turn_count 17; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool); amount=INR 30,000 (stated)}; pending_confirmation take_limit_request, not answered; counters: all 0; turns_since_resolution 17; escalation_proximity 0.60 |

### T18 | Agent

> This is Kavita from our senior support team. They have the details of your credit limit request and will take it from here.

| Field | Value |
|---|---|
| NLU | n/a (agent message) |
| Sentiment | n/a (agent messages are not scored); smoothed stays -0.05 |
| Guardrails | checked: Output Safety Layer: GR-OUT-01, GR-OUT-02, GR-OUT-03, GR-OUT-04, GR-OUT-05, GR-OUT-06; triggered: GR-OUT-05 |
| KB / tools | router: agent_first_name=Kavita (synthetic); team_plain=senior support team |
| Action | escalate: handoff complete; the agent posts one line and stops replying |
| Generation | template `TPL-ESC-HUMAN-JOINED/standard@1.1.0` (language en); patterns: P5; anti-pattern check: none |
| State | phase HANDOFF; auth biometric_verified; turn_count 18; topic_stack [CRD-003 (increase_request): active]; slots {card_type=credit (filled); card_last4=6642 (from the tool); amount=INR 30,000 (stated)}; pending_confirmation take_limit_request, not answered; counters: all 0; turns_since_resolution 18; escalation_proximity 0.60 |

## Closing

| Item | Value |
|---|---|
| Outcome class | resolved-with-escalation once the human closes (A5.3); resolution_status escalated at handoff (A10.1) |
| Messages | 18 (customer and agent); system events excluded |
| Sentiment trajectory (raw) | [0.00, 0.05, -0.05, -0.10, 0.00, -0.05, -0.15, 0.00]; final smoothed -0.05 |
| Escalation record | ESC-010, sub-rule ESC-010.a, fired at T16 (turns_since_resolution 16 above esc010_turns 15, CRD-003 active); priority P2, queue Supervisor Review, SLA under 15 min, handoff mode warm, cancellable customer_or_recovery (recovery would need the topic to reach resolved, which it did not); secondary triggers: none; result: warm handoff announced at T17 and accepted at E2 |
| CSAT / check-in | Asked after the human conversation ends (two-part CSAT). No in-chat check-in: none is sent after an escalation has fired. |

### Design notes (each one deliberate)

| Topic | This specification | Why |
|---|---|---|
| Where the count reaches 16 | T1 and T2 are customer and agent; the step-up (T2, E1, T3) puts two agent messages in a row, so every later customer message has an even number and message 16 is a customer message | ESC-010 evaluates on the 16th message (D-119); a customer message at that point is evaluated before the agent replies |
| Why nothing resolves | T5, T7, T9, T11 and T13 are gap or boundary answers; T15 is a confirmation that is never answered | A gap answer does not resolve a topic, so turns_since_resolution keeps counting from the first message |
| Boundary shown | turns_since_resolution is 15 at T15 and 16 at T16 | The rule is "more than 15" (A6: exceeds 15 turns); 15 does not fire |
| No limit, no approval | No figure for a limit appears except the customer's own INR 20,000 and INR 30,000 and the KB entry's 10 LPA | KB-ESC-017 lists credit limit values as unknown and forbids saying "you will be approved"; credit decisions belong to the bank (GR-REG-15) |

### Handoff package (8 elements, D-04 and KB-ESC-001; built from state, nothing re-typed by the customer)

| No. | Element | Content |
|---|---|---|
| 1 | Customer ID (pseudonymised) | cust_ref_syn_32 |
| 2 | Auth level | level biometric_verified; level_at_trigger biometric_verified |
| 3 | Intent history | CRD-003 > increase_request 0.88 first at T1; CRD-003 > limit_info 0.86 first at T4; CRD-003 > increase_request 0.84 first at T6; CRD-003 > limit_info 0.80 first at T8; CRD-003 > limit_info 0.78 first at T10; CRD-003 > limit_info 0.76 first at T12; CRD-003 > increase_request 0.87 first at T14; CRD-003 > increase_request 0.74 first at T16 |
| 4 | Entities collected (masked) | card_type=credit (filled); card_last4=6642 (from the tool); card_type_considered=premium (stated); amount=INR 30,000 (stated, replaces INR 20,000) |
| 5 | Conversation summary | Customer asked to raise the credit limit on his NexCredit Classic card ending 6642. The limit he could get and whether it would be approved are not known to the assistant and were not guessed. He asked what others usually get, whether income proof is needed for a limit change, and whether the Premium card has a higher limit; each was answered as a stated gap with the catalogue facts that exist. He proposed INR 20,000, was asked to confirm, and changed it to INR 30,000 before answering. No request was submitted. |
| 6 | Sentiment trajectory | raw [0.00, 0.05, -0.05, -0.10, 0.00, -0.05, -0.15, 0.00]; current -0.05; emotions: mild frustration at T14; sarcasm_suspected false |
| 7 | Actions already taken | step-up to biometric_verified at T2; card status read at T3; no credit limit request taken or submitted |
| 8 | Escalation trigger and reason | trigger_id ESC-010; rule_id ESC-010.a; priority P2; source system; secondary []; reason_text: More than 15 messages without a resolved topic on a credit limit request that is still open.; evidence_turns [T16] |

Envelope: priority P2; queue Supervisor Review; handoff_mode warm; language en; channel app; complete true; missing_fields []; versions.prompt_version sp-1.1.0+1527a050.n000000. The open confirmation (take the request: yes or no) is flagged for the colleague. Never in the package: full card number, CVV, PIN, full Aadhaar, password, OTP.

## Self-audit

### Patterns (A9.1)

| Code | Pattern | Evidence |
|---|---|---|
| P1 | Empathy-First | shown at T17 (one acknowledgement, then the action) |
| P2 | Progressive Disclosure | shown at T2, T3 |
| P3 | Confirmation-Before-Action | shown at T15. the request was offered for confirmation and never taken without a yes |
| P4 | Graceful Degradation | shown at T5, T7, T9, T11, T13 |
| P5 | Context Carry-Over | shown at T3, T17, T18. the card and both amounts travel in the package |

### Anti-patterns (A9.2)

| Code | Anti-pattern | Result | At-risk turns where the design prevents it |
|---|---|---|---|
| AP1 | Robotic Loop | absent: 10 agent messages, no two identical; the gap answers at T5, T9 and T11 are in different words and add a different next step each time | T5, T9, T11 |
| AP2 | Information Dump | absent: longest agent message is 72 words (cap `atk_output_max_words`); one concept per message | T17 |
| AP3 | False Confidence | absent: no limit, approval, timeline or outcome is stated except values returned by a tool or the router on that turn, a KB entry cited on it, or the customer's own figure | T5, T7, T9, T13, T15, T17 |
| AP4 | Premature Escalation | absent: ESC-010 fired only on the 16th message; at message 15 the rule was evaluated and did not fire | T15, T16 |
| AP5 | Empathy Bypass | not at risk: no negative emotion above mild frustration in the scenario | none at risk |
| AP6 | Authentication Theatre | absent: verification requested 1 time(s) at T2; every later account step was served with no second verification | T2, T3 |
| AP7 | Sycophantic Recovery | absent: no apology is given | none at risk |
| AP8 | Knowledge Hallucination | absent: 6 figure(s) in agent text, each traced to a cited KB entry, a tool or router value, or the customer's own words (see pattern-audit.md) | T3, T13, T15, T17 |
