# Response and Prompt Template Library

Brief refs: A2.4 (p.7: "template-based generation for safety-critical responses (account balances, transaction details, regulatory information); LLM-based generation for conversational responses (empathy statements, clarifications); hybrid blending approach; persona consistency; response length calibration"), A9 (pp.23-26: patterns, anti-patterns, tone), A12 (p.33), Part D Day 12-13 (p.60: "Create 15+ prompt templates with trigger conditions and safety annotations").

Related: `docs/architecture/response-generation.md` (modes and the hybrid contract), `docs/architecture/conversation-design.md` (pattern and anti-pattern matrix), `config/system-prompt/` (layer 3 D9 tells the model how to treat a template), `config/parameters.yaml`, `docs/guardrails/output-safety-layer.md` (every template still passes the Output Safety Layer). Validator: `python tests/templates/validate_templates.py`.

Status: specification. 63 templates with 131 variants, each in English, Hindi and Hinglish. No template has been rendered by a system or shown to a customer. **Hindi and Hinglish text is not native-reviewed** and must not ship before review (section 8).

## 1. Files

| File | Families | Templates | Origin of the names |
|---|---|---|---|
| `general.yaml` | GEN | 9 | new on Day 13 |
| `auth.yaml` | AUTH, SEC | 5 | new; SEC variants adopt the reply keys of `config/entities.yaml` RED-01 to RED-07 |
| `service.yaml` | ACC, TXN, ACT | 7 | new |
| `support.yaml` | CMP, KB, SRV, SYS | 10 | new; KB adopts `graceful_degradation` from `retrieval-pipeline.md` |
| `advice.yaml` | ADV | 13 | Day 9, `financial-advice.md` section 6 |
| `adversarial.yaml` | ATK | 7 | Day 10, `adversarial-defences.md` section 3.3 |
| `escalation.yaml` | ESC | 12 | Day 12, `routing-and-handoff.md` section 11 |
| `labels.yaml` | n/a | n/a | plain-language label tables for locked slots (queue names, intent labels) |

## 2. ID scheme (D-136)

`TPL-<FAMILY>-<NAME>`, upper case, for example `TPL-ESC-HANDOFF-WARM`. Days 9, 10 and 12 had already published 32 descriptive IDs in documents, the escalation rules file and test cases, so the scheme keeps descriptive names for all templates instead of numbers. An ID never changes once published; wording changes raise `version`. A variant is addressed as `<id>/<variant key>`, and that pair plus the template version is what the turn log records.

Names used by earlier documents that are not IDs:

| Earlier name | Where | Resolves to |
|---|---|---|
| `graceful_degradation` | `retrieval-pipeline.md` sections 9-10 | `TPL-KB-GAP` (decision `gap`), `TPL-KB-DEGRADE` (decision `degrade`) |
| `handoff` | `retrieval-pipeline.md` section 9 | `TPL-ESC-HANDOFF-WARM` variants `regulatory_uncertain` (ESC-008) and `system_error` (ESC-014) |
| `confirmation_before_action` "for the verification step" | `retrieval-pipeline.md` section 9 | `TPL-AUTH-STEP-UP` variant `for_information`; the general pattern is `TPL-ACT-CONFIRM` |
| `ask_not_to_share_card`, `_cvv`, `_aadhaar`, `_secret`, `use_secure_widget`, `use_secure_form`, `use_masked_reference` | `config/entities.yaml`, `account-security.md` | variants of `TPL-SEC-DO-NOT-SHARE` with the same keys |
| "static status message and the human line" | `output-safety-layer.md` section 6 rung 5 | `TPL-SYS-STATUS-STATIC` |
| "the CSAT ask", "check-in templates" | `config/intents.yaml` GEN-006, `csat-signals.md` | `TPL-SRV-CSAT`, `TPL-GEN-CHECKIN` |
| "pre-approved correction messages" | `incident-response-playbook.md` open item 4 | `TPL-SYS-CORRECTION` |
| `TPL-TEST-INCOME-SLOT` | `tests/guardrails/advice.yaml` GR-ADV-07-01 | a deliberately invalid fixture for the build-time lint; not a library template |

## 3. Generation modes (D-144)

| Mode | Meaning | Who writes the words | Count |
|---|---|---|---|
| `template` | Fixed reviewed text. Locked slots are filled by the platform. No model call | authors of this library | 57 |
| `hybrid` | Fixed text carries the facts in locked slots; the model writes only the marked free slot (an acknowledgement) or joins locked facts into sentences | library plus the model inside constraints | 5 |
| `llm-guided` | The model writes one constrained sentence inside a fixed four-step scaffold; all facts and actions are locked | the model inside a scaffold | 1 |

Rules: safety-critical replies are `template` (balances, verification, credential warnings, fraud, crisis, advice refusals, confirmations, failures, surveys). `model_temperature` affects only the free slots. If the model is unavailable, slow or in safe mode, every free slot takes its `fallback` text, so each hybrid template degrades to a pure template (A2.4, `response-generation.md` degradation ladder).

## 4. Template schema

```yaml
- id: TPL-<FAMILY>-<NAME>
  title: "..."
  version: "1.0.0"                 # semantic; logged with the turn
  customer_facing: true
  legacy_names: [...]              # optional: earlier names that resolve here
  trigger:
    intents: [ACC-001]             # config/intents.yaml ids ([] = not intent-driven)
    guardrails: [GR-SEC-R2]        # config/guardrails.yaml ids that select this template
    escalations: [ESC-005]         # A6 triggers it serves
    state: "..."                   # the state condition in words, using state fields and parameter names
  mode: template | hybrid | llm-guided
  compose_with: [TPL-...]          # optional: templates appended by the Policy Engine
  variant_selection: single | condition | rotate
  allowed_literals: ["1", "5"]     # optional: the only digits allowed outside slots, with the reason in safety.notes
  slots:
    - name: balance
      source: {type: tool | kb | state | router | policy | notice | llm, ref: "...", field: "..."}
      locked: true                 # true = injected verbatim; the model cannot alter it. false only for type llm
      required: false              # optional; default true
      constraints: {max_words: 25, sentences: 1, must_not: [...]}   # llm slots only
      fallback: {en: "...", hi: "...", hinglish: "..."}             # llm slots only
  variants:
    - key: default
      when: "..."                  # required unless variant_selection is single
      text: {en: "...", hi: "...", hinglish: "..."}
  safety:
    guardrails_enforced: [...]     # guardrails the wording is designed to satisfy
    must_not_contain: [...]        # phrases the rendered reply must never contain (checked by the validator on the text)
    notes: "..."
  a9: {patterns: [P1..P5], anti_patterns_avoided: [AP1..AP8]}
  kb_refs: [KB-...]
  tests: [...]                     # existing case ids in tests/
```

Slot sources:

| `source.type` | Filled by | Example |
|---|---|---|
| `tool` | a `ToolResult` of the same turn (`source_ts` present) | balance, masked last four digits, reference id, expected date |
| `kb` | a KB entry in the turn's evidence set, by `id@version` | rate range, criteria, safe statement of a gap entry |
| `state` | a `DialogueState` field, masked | pending action, earlier topic |
| `router` | the Escalation Router or queue platform | team label, wait estimate, colleague's first name |
| `policy` | the Policy Engine, from a reviewed label table (`labels.yaml`) | plain action label, clarifying options |
| `notice` | a layer 5 typed notice record | affected service, restoration time |
| `llm` | the generation model, inside `constraints`, with a `fallback` | one acknowledgement sentence |

Slot syntax is `{{name}}` as in the hybrid contract of `response-generation.md`. (Day 9 wrote slot names with single braces in a table; the names are kept, the syntax follows Day 3.) An optional slot that is empty renders as nothing and the renderer collapses the surrounding spaces; a variant exists wherever dropping a slot would leave a broken sentence.

The free slot (D-151): one sentence, at most `llm_ack_slot_max_words` words, no digits, no promise, no blame, no second apology, no product, no reason for a handoff that was not supplied. It passes the Output Safety Layer like any text; two tone failures fall back to the fixed sentence.

## 5. Variants and rotation (D-147)

`rotate` templates have at least `template_variant_min_rotating` variants and never send the same variant twice in a row; each variant must add information or a different next step. This is the template-side control for the Robotic Loop anti-pattern (A9.2, -20 points). Rotating templates: `TPL-ATK-NEUTRAL-REDIRECT`, `TPL-ESC-WAIT-UPDATE`, `TPL-GEN-CLARIFY`, `TPL-KB-DEGRADE`. After the last rotation step the next action is a human offer, not a fourth wording.

## 6. Wording rules enforced by the validator (D-148)

1. No digit outside a slot, in any language, unless listed in `allowed_literals` (only the survey scales: 1 and 5 for CSAT per A5.2, 1 and 7 for CES per A8.2, 0 and 10 for NPS).
2. No timeline or outcome commitment in fixed text. A date or wait estimate appears only as a locked slot from a tool or the router, and the sentence around it says it is an estimate.
3. A global banned-phrase list (guarantees, certainty words, stacked apologies, the Robotic Loop sentence of A9.2, blame, dismissive phrases, hedged guesses, pressure selling, recommendation wording, "no one is available", requests for a credential, technical jargon, flag vocabulary, slang) and each template's own `must_not_contain`.
4. No slot may be named for a personal circumstance (income, age, savings, portfolio, goals, risk appetite): the build-time lint of GR-ADV-07 (case GR-ADV-07-01).
5. No English variant shares `atk_prompt_overlap_words` consecutive words with prompt layers 0 to 2, because the Output Safety Layer would block it (GR-ATK-06).
6. English and Hinglish are ASCII. Hindi is Devanagari. No em dash, smart quote or emoji anywhere.
7. Every variant has all three languages and the three use the same slots.

"A request, not a guarantee" (KB-POL-007) is rendered as "a request and may change", so that the word "guarantee" can be banned outright.

## 7. Index

Columns: variants; slots as locked and free.

| ID | Purpose | Mode | Trigger (intents; escalations) | Variants | Slots | File |
|---|---|---|---|---|---|---|
| `TPL-GEN-GREETING` | Greeting with AI disclosure | template | GEN-001 | 3 | 1 locked, 0 free | `general.yaml` |
| `TPL-GEN-AI-DISCLOSURE` | Asked whether this is a human or a bot | template | GEN-002 | 1 | 0 locked, 0 free | `general.yaml` |
| `TPL-GEN-LANGUAGE-SWITCH` | Language switch and language choice | template | GEN-005 | 3 | 1 locked, 0 free | `general.yaml` |
| `TPL-GEN-CLARIFY` | Clarifying question | template | GEN-004 | 4 | 4 locked, 0 free | `general.yaml` |
| `TPL-GEN-RECOVERY` | Apology and recovery after a misunderstanding or an agent mistake | hybrid | state or guardrail (see file) | 2 | 2 locked, 0 free | `general.yaml` |
| `TPL-GEN-CHECKIN` | In-conversation check-in at a natural breakpoint | template | state or guardrail (see file) | 3 | 0 locked, 0 free | `general.yaml` |
| `TPL-GEN-CARRYOVER` | Context carry-over for a returning customer | template | state or guardrail (see file) | 2 | 2 locked, 0 free | `general.yaml` |
| `TPL-GEN-DISCLOSE-MORE` | Progressive disclosure | hybrid | PRD-001, PRD-003, PRD-004, GEN-008 | 2 | 5 locked, 0 free | `general.yaml` |
| `TPL-GEN-CLOSING` | Anything-else check and closing | template | GEN-006 | 3 | 0 locked, 0 free | `general.yaml` |
| `TPL-AUTH-OTP-REQUEST` | Verification needed | template | ACC-001, ACC-002, ACC-007, TXN-001 ... | 1 | 1 locked, 0 free | `auth.yaml` |
| `TPL-AUTH-STEP-UP` | Step-up to a higher verification level | template | ACC-003, ACC-004, ACC-005, ACC-006 ... | 3 | 1 locked, 0 free | `auth.yaml` |
| `TPL-AUTH-OTP-FAILED` | Wrong code, and lock after repeated failures | template | ESC-009 | 2 | 0 locked, 0 free | `auth.yaml` |
| `TPL-AUTH-SESSION-TIMEOUT` | Session expired after inactivity | template | state or guardrail (see file) | 2 | 1 locked, 0 free | `auth.yaml` |
| `TPL-SEC-DO-NOT-SHARE` | Customer typed a credential or a full identifier in chat | template | state or guardrail (see file) | 7 | 0 locked, 0 free | `auth.yaml` |
| `TPL-ACC-BALANCE` | Account balance | template | ACC-001 | 2 | 4 locked, 0 free | `service.yaml` |
| `TPL-TXN-STATUS` | Transaction or payment status from the system of record | hybrid | TXN-001, TXN-003, TXN-004 | 2 | 3 locked, 1 free | `service.yaml` |
| `TPL-TXN-DISPUTE-INTAKE` | Dispute intake | hybrid | TXN-002; ESC-005, ESC-001 | 3 | 1 locked, 1 free | `service.yaml` |
| `TPL-ACT-CONFIRM` | Confirmation before action | template | CRD-001, CRD-002, TXN-002, TXN-005 ... | 2 | 3 locked, 0 free | `service.yaml` |
| `TPL-ACT-DONE` | Post-action confirmation with reference | template | CRD-001, CRD-002, TXN-002, TXN-005 ... | 1 | 3 locked, 0 free | `service.yaml` |
| `TPL-ACT-FAILED` | Action or lookup did not complete | template | ESC-014 | 2 | 1 locked, 0 free | `service.yaml` |
| `TPL-ACT-CANNOT-DO` | Request outside what the agent may do | template | TXN-005, TXN-006, ACC-005, ACC-006 | 2 | 1 locked, 0 free | `service.yaml` |
| `TPL-CMP-EMPATHY-FIRST` | Empathy-first reply to a complaint or a frustrated customer | llm-guided | CMP-001, CMP-003, CMP-004, TXN-003 | 2 | 2 locked, 1 free | `support.yaml` |
| `TPL-CMP-GRIEVANCE-INFO` | Grievance redressal information | template | CMP-001, CMP-002, CMP-003, CMP-005 | 2 | 1 locked, 0 free | `support.yaml` |
| `TPL-KB-DEGRADE` | Graceful degradation | template | GEN-004 | 3 | 1 locked, 0 free | `support.yaml` |
| `TPL-KB-GAP` | Known knowledge gap | template | PRD-001, PRD-003, PRD-004, CRD-003 ... | 2 | 2 locked, 0 free | `support.yaml` |
| `TPL-SRV-CSAT` | Post-conversation satisfaction rating | template | GEN-006, CMP-004 | 3 | 0 locked, 0 free | `support.yaml` |
| `TPL-SRV-CES` | Customer Effort Score question | template | state or guardrail (see file) | 1 | 0 locked, 0 free | `support.yaml` |
| `TPL-SRV-NPS` | Net Promoter Score question | template | state or guardrail (see file) | 1 | 0 locked, 0 free | `support.yaml` |
| `TPL-SYS-STATUS-STATIC` | Static status message and the human line | template | ESC-014 | 1 | 0 locked, 0 free | `support.yaml` |
| `TPL-SYS-NOTICE` | Customer wording for a layer 5 operational notice | template | TXN-001, TXN-003, TXN-004, GEN-008 ... | 4 | 4 locked, 0 free | `support.yaml` |
| `TPL-SYS-CORRECTION` | Correction of an earlier wrong statement | template | state or guardrail (see file) | 1 | 2 locked, 0 free | `support.yaml` |
| `TPL-ADV-BOUNDARY` | Generic advice decline with facts | template | PRD-005 | 1 | 1 locked, 0 free | `advice.yaml` |
| `TPL-ADV-RATE` | Rates and tenures as facts | template | PRD-003, PRD-005 | 2 | 2 locked, 0 free | `advice.yaml` |
| `TPL-ADV-LOAN` | Published loan criteria and EMI illustration | template | PRD-002, PRD-005 | 2 | 2 locked, 0 free | `advice.yaml` |
| `TPL-ADV-INVEST` | Investment product facts and risk disclosure | template | PRD-005 | 1 | 2 locked, 0 free | `advice.yaml` |
| `TPL-ADV-INSURANCE` | Cover facts without a policy recommendation | template | PRD-004, PRD-005 | 1 | 1 locked, 0 free | `advice.yaml` |
| `TPL-ADV-TAX` | Section 80C and TDS as facts | template | PRD-003, PRD-005 | 1 | 1 locked, 0 free | `advice.yaml` |
| `TPL-ADV-FOREX` | No direction or timing on currency | template | TXN-006, PRD-005 | 1 | 1 locked, 0 free | `advice.yaml` |
| `TPL-ADV-COMPARE` | Factual side-by-side with no verdict | template | PRD-001, PRD-005 | 1 | 1 locked, 0 free | `advice.yaml` |
| `TPL-ADV-ADVISOR-OFFER` | Offer of a SEBI-registered advisor | template | PRD-005, PRD-002, PRD-004, TXN-006; ESC-013 | 1 | 0 locked, 0 free | `advice.yaml` |
| `TPL-ADV-ADVISOR-CONFIRM` | Advisor offer accepted | template | PRD-005; ESC-013 | 2 | 2 locked, 0 free | `advice.yaml` |
| `TPL-ADV-ADVISOR-DECLINED` | Advisor offer declined | template | PRD-005 | 1 | 0 locked, 0 free | `advice.yaml` |
| `TPL-ADV-ADVISOR-UNAVAILABLE` | Advisor queue unavailable | template | PRD-005; ESC-013 | 1 | 1 locked, 0 free | `advice.yaml` |
| `TPL-ADV-SAFE-FALLBACK` | Output Safety fallback for an unfixable advice draft | template | PRD-005, PRD-001, PRD-002, PRD-003 ... | 1 | 0 locked, 0 free | `advice.yaml` |
| `TPL-ATK-NEUTRAL-REDIRECT` | Neutral redirect after a flagged turn | template | state or guardrail (see file) | 3 | 0 locked, 0 free | `adversarial.yaml` |
| `TPL-ATK-CANNOT-SHARE-CONFIG` | Request for the prompt, rules, configuration or tools | template | state or guardrail (see file) | 1 | 0 locked, 0 free | `adversarial.yaml` |
| `TPL-ATK-AUTH-PROMPT` | Claimed identity or claimed verification | template | state or guardrail (see file) | 1 | 0 locked, 0 free | `adversarial.yaml` |
| `TPL-ATK-THIRD-PARTY` | Third-party request or authority claim | template | ESC-001 | 2 | 0 locked, 0 free | `adversarial.yaml` |
| `TPL-ATK-THROTTLE` | Message rate above the soft limit | template | state or guardrail (see file) | 1 | 0 locked, 0 free | `adversarial.yaml` |
| `TPL-ATK-SHORTEN-OR-SPLIT` | Oversized or over-complex request | template | state or guardrail (see file) | 2 | 1 locked, 0 free | `adversarial.yaml` |
| `TPL-ATK-SAFE-MODE` | Safe mode notice | template | state or guardrail (see file) | 1 | 0 locked, 0 free | `adversarial.yaml` |
| `TPL-ESC-HANDOFF-WARM` | Warm handoff to a human team | hybrid | GEN-003, CMP-003, CMP-005, TXN-002; ESC-002 to ESC-014 | 6 | 3 locked, 1 free | `escalation.yaml` |
| `TPL-ESC-HANDOFF-DISCREET` | Discreet handoff | template | ESC-015, ESC-009 | 1 | 0 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-FRAUD-P0` | Fraud or unauthorised access | template | SEC-001, SEC-004, SEC-002, CRD-001; ESC-001, ESC-009 | 4 | 2 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-CRISIS` | Crisis response | template | GEN-007; ESC-011 | 4 | 0 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-WAIT-UPDATE` | Status while waiting for a human | template | ESC-002 to ESC-014 | 4 | 3 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-HUMAN-JOINED` | Introduction when the human joins | template | ESC-001 to ESC-015 | 2 | 3 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-AFTER-HOURS` | Specialist team closed | template | ESC-002 to ESC-013 | 2 | 1 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-CALLBACK-OFFER` | Callback request | template | CMP-005; ESC-002 to ESC-014 | 2 | 3 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-LANGUAGE-CHOICE` | No colleague available in the customer's language | template | GEN-005; ESC-002 to ESC-014 | 1 | 2 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-HANDOFF-FAILED` | Handoff did not reach a human by the chosen route | template | ESC-001 to ESC-015 | 3 | 1 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-DEESCALATION-CHECK` | One check before cancelling a pending escalation | template | ESC-003, ESC-004, ESC-010, ESC-014 | 1 | 0 locked, 0 free | `escalation.yaml` |
| `TPL-ESC-REFERRAL` | Referral to a human process | template | ACC-005, ACC-006, ACC-008 | 2 | 3 locked, 0 free | `escalation.yaml` |

Coverage of the items Part D and earlier days asked for: greeting with AI disclosure (`TPL-GEN-GREETING`), OTP request (`TPL-AUTH-OTP-REQUEST`), balance (`TPL-ACC-BALANCE`), dispute intake (`TPL-TXN-DISPUTE-INTAKE`), advice refusal (13 `TPL-ADV-*`), injection deflection (`TPL-ATK-NEUTRAL-REDIRECT`, `TPL-ATK-CANNOT-SHARE-CONFIG`), impersonation and authority-claim refusal (`TPL-ATK-THIRD-PARTY`), fraud P0 (`TPL-ESC-FRAUD-P0`), empathy-first complaint (`TPL-CMP-EMPATHY-FIRST`), grievance redressal information (`TPL-CMP-GRIEVANCE-INFO`), graceful degradation in English, Hindi and Hinglish (`TPL-KB-DEGRADE`), KB-gap response (`TPL-KB-GAP`), confirmation before action (`TPL-ACT-CONFIRM`, `TPL-ACT-DONE`), warm handoff and the other eleven `TPL-ESC-*`, queue wait (`TPL-ESC-WAIT-UPDATE`), CSAT ask (`TPL-SRV-CSAT`, plus CES and NPS), in-conversation check-in (`TPL-GEN-CHECKIN`), crisis response (`TPL-ESC-CRISIS`), language switch (`TPL-GEN-LANGUAGE-SWITCH`, `TPL-ESC-LANGUAGE-CHOICE`), step-up authentication (`TPL-AUTH-STEP-UP`), session timeout (`TPL-AUTH-SESSION-TIMEOUT`), clarification (`TPL-GEN-CLARIFY`), apology and recovery (`TPL-GEN-RECOVERY`).

## 8. Languages and review (D-145)

1. Every customer-facing template has English, Hindi (Devanagari) and Hinglish (Roman script, code-mixed) text. All Hindi and Hinglish text carries `review: not_native_reviewed` at file level. Release gate: a template may not be enabled for a language until that language's status is `native_reviewed` by a named reviewer; until then Hindi and Hinglish customers would receive English, which is not acceptable for launch. The review is therefore a launch blocker, not a polish item.
2. Known weaknesses to check in review: (a) Hindi first-person verbs are gendered and the drafts use the masculine form ("sakta hoon"); the assistant's grammatical gender is a brand decision; (b) register: the drafts use "aap" throughout; (c) mixed-script terms (OTP, PIN, KYC, EMI, SEBI, RBI, AI) are kept in Latin letters inside Hindi text; (d) Hinglish spellings follow one transliteration but customers use many; (e) slot grammar: a label inserted into a Hindi sentence must fit its postposition, which is why `labels.yaml` states a grammar contract per table.
3. Secondary languages (Tamil, Telugu, Bengali, Marathi, Gujarati): `multilingual.md` requires pre-reviewed translated templates for safety-critical text. None exists yet. Until they do, a secondary-language customer receives the language choice (`TPL-GEN-LANGUAGE-SWITCH` variant `offer_choice`, shown in Hindi and English together) and safety-critical replies in Hindi or English. The first set to translate is listed in the Day 13 handoff: crisis, fraud P0, do-not-share, OTP request, language choice, warm handoff.
4. Locked slot content from the KB is English only today (the KB entries list `languages: [en]`), so a Hindi or Hinglish reply can contain an English fact sentence. Translating `structured_fields` wording is a KB workflow item.

## 9. Deviations from the brief's case studies (deliberate)

| Case study wording | Template behaviour | Reason |
|---|---|---|
| Case Study 1 turn 4 (p.48): "Please share the 6-digit OTP to proceed", and the customer types it in chat | `TPL-AUTH-OTP-REQUEST` sends the customer to the secure widget; `TPL-SEC-DO-NOT-SHARE` handles a typed code | A4.2 rule 5: never accept credentials (Day 9, `auth-flow.mmd`) |
| Case Study 1 turn 2: asks the customer to type the registered mobile number | no template asks for it; verification runs in the widget | data minimisation; a typed number is not proof (D-75) |
| Case Study 1 turn 8: volunteers a minimum payment and due date after a card balance question | `TPL-ACC-BALANCE` gives the balance and one optional next step | A9.2 Information Dump |
| Case Study 3 turn 4 (p.51): "our advisors offer a free 30-minute consultation" | `TPL-ADV-ADVISOR-OFFER` states no duration and no price | neither is in the KB (`financial-advice.md` section 6) |
| Case Study 5: "credited within 24 hours" | a date appears only from a tool result | D-09 |
| Case Study 6: verification reused from the previous day | `TPL-GEN-CARRYOVER` reuses context, never authentication | D-05 |

## 10. Change control

A template is content, not a guardrail, but its wording carries guardrail behaviour. Proposal (D-136): templates whose trigger lists a guardrail of family SEC, ADV, REG, ATK, OUT or SYS, and all `TPL-ESC-*`, change under the layer 3 process (owner approval, Risk Committee review, fixed suite, A/B where the change affects customer-facing behaviour). `TPL-ESC-CRISIS`, `TPL-ESC-FRAUD-P0`, `TPL-SEC-DO-NOT-SHARE` and `TPL-SYS-STATUS-STATIC` change only under safety change control. The remaining GEN and SRV templates follow the layer 3 process without the A/B requirement for PATCH wording. The learning pipeline may propose wording (update class U2); it never applies it. Every change runs this validator (the `template lint` of `safety-invariants.md` section 5.2).

## 11. Open items

1. Native-speaker review of all Hindi and Hinglish text (launch blocker).
2. `TPL-ESC-CRISIS` needs review by the Crisis Response team and a clinical adviser; helpline numbers are absent because the brief and KB hold none (D-146).
3. Label tables for `action_plain`, `result_plain`, `service_plain`, `topic` and the clarifying options are not written yet (`labels.yaml` footer).
4. KB facts and gap statements exist in English only.
5. No secondary-language template text exists.
6. Channel variants (voice read-out, WhatsApp length) are covered by layer 3 rules only, not by separate text.
