# System Prompt Specification (6 layers)

Brief refs: A12.1 (p.33: six layers with purpose, content and update frequency), A12.2 (pp.33-34: Layered Immutability, Explicit Over Implicit, Positive and Negative Instruction, Testable Assertions, Context-Aware Activation, Version Control), A12.3 (p.34: configuration parameters), A4.4 (p.14: instruction-data separation, system prompt protection), A10.2 (turn log), Part D Day 12-13 (p.60: "Design layered system prompt architecture (6 layers with immutability rules)").

Related: `config/parameters.yaml` (governed parameters), `config/templates/` (template library), `docs/architecture/conversation-design.md` (A9 patterns), `docs/guardrails/adversarial-defences.md` sections 3.2 and 7 (instruction-data separation, leak tolerance), `docs/learning-pipeline/overview.md` section 3 and `safety-invariants.md` (who may change what). Validator: `tests/templates/validate_templates.py`.

Status: specification. No model has been run with this prompt. Every statement about model behaviour is a requirement with a mapped test, not a result. The Hindi and Hinglish wording it points to is not native-reviewed.

## 1. Files

| File | Layer | Brief name | Purpose (brief) | Update frequency (brief) |
|---|---|---|---|---|
| `layer0-identity.md` | 0 | Identity | Agent identity | Quarterly or on rebrand |
| `layer1-safety.md` | 1 | Safety | Immutable safety | Annual (requires RC approval) |
| `layer2-regulatory.md` | 2 | Regulatory | Compliance boundaries | As regulations change (fast-track) |
| `layer3-dialogue.md` | 3 | Dialogue | Conversation management | Monthly |
| `layer4-knowledge.md` | 4 | Knowledge | RAG instructions | Monthly |
| `layer5-operational.md` | 5 | Operational | Dynamic context | Daily or as needed |
| `manifest.yaml` | all | n/a | Version, hashes and A12.2 metadata of the bundle | every change |

Each layer file has a YAML metadata header (layer, version, owner, mutability, change process, approval chain, author, last reviewed, deployment date, model version, token budget), the prompt text between `<!-- PROMPT-BEGIN -->` and `<!-- PROMPT-END -->`, a table of testable assertions and notes. Only the text between the markers is sent to a model.

## 2. Mutability and ownership

A12.2: "Layers 0-2 immutable by learning pipeline. Only Layers 3-5 modifiable through continuous improvement; only Layer 5 without RC review."

| Layer | Learning pipeline | Owner (proposal where the brief is silent) | Change path | Risk Committee |
|---|---|---|---|---|
| 0 Identity | excluded (X1); may only file an observation | Product, brand | safety change control (`safety-invariants.md` section 9) | approval |
| 1 Safety | excluded (X1) | Risk Committee (brief: "requires RC approval") | safety change control | approval |
| 2 Regulatory | excluded (X1) | Regulatory Compliance Manager | regulatory fast-track under safety change control, released with the affected KB entries | approval |
| 3 Dialogue | may draft a version (U2) | CX Team | gates G0 to G9 with an A/B test | review (A12.2) |
| 4 Knowledge | may draft a version (U2) | NLU Team | gates G0 to G9 with an A/B test | review (A12.2) |
| 5 Operational, frame text | as layer 3 | CX Team | as layer 3 | review |
| 5 Operational, notice values | may propose values (U2) | Operations owner with Product | G0 slot check, lint, fixed suite, straight to 100 percent with flag rollback | none (A12.2) |

Enforcement is by permission, not by instruction: the pipeline's service identity has no write access to layers 0 to 2 (invariant INV-01, cases SS-LRN-01, SS-LRN-02, GR-SYS-02-02), and the hash of layers 0 to 2 (`immutable_sha256` in `manifest.yaml`) is compared with the approved value at load; a mismatch is SEV0 (`safety-invariants.md` mechanism M7). The brief names the owner for layer 1 only; the other owners are proposals (D-137).

## 3. Assembly order

One system message, then typed data blocks. Decision D-137.

```text
SYSTEM MESSAGE (instructions; the only instructions)
  Layer 0 Identity        fixed text
  Layer 1 Safety          fixed text; assembler fills {{turn_boundary}} and {{canary_token}}
  Layer 2 Regulatory      fixed text
  Layer 3 Dialogue        base text + the ACTIVE WHEN blocks whose condition holds this turn
  Layer 4 Knowledge       fixed text
  Layer 5 Operational     frame text; assembler fills {{notices_block}} with rendered typed notices

DATA BLOCKS (never instructions; each wrapped in markers that carry the turn boundary code)
  session_facts           from the Policy Engine: auth level, reply language, dialogue phase, flow, mode, selected
                          template id and variant, locked slot values, allowed next actions, retrieval decision,
                          candidates for a clarifying question, handoff wording inputs
  knowledge_passages      top-k entries (id@version, title, served-language body, stale flag); empty when not needed
  tool_results            ToolResult objects of this turn, masked server-side
  conversation            summary.text, pinned_facts, and the last turns (masked)
  customer_message        the current customer text, neutralised by the Input Guard (injection span replaced by a typed marker)
```

Rules:

1. The system message is built by concatenation only. No customer text, passage, tool string or notice summary is ever interpolated into a layer. The three assembly slots are filled by the assembler from platform values.
2. Data-block markers have the form `<<nb-data kind=... code={{turn_boundary}}>> ... <<nb-end code={{turn_boundary}}>>`. The code is a fresh random value per turn, so text inside a customer message that imitates a marker cannot match it (attack pattern P6 in `adversarial-defences.md` section 4.1). The exact marker syntax is a platform choice; the requirement is an unguessable per-turn code.
3. The model never selects the template, the tool, the auth level or the escalation. It receives them as session facts. This is why the prompt can be leaked without loss: no decision of consequence is made from prompt text alone (assumption 1 of `adversarial-defences.md`).
4. Template-only turns (mode `template`, about nine in ten templates in the library) do not call the model at all: the Response Generator renders the template and the Output Safety Layer checks it. The prompt matters for `hybrid` and `llm-guided` turns and for free conversational turns.

## 4. Precedence

1. A lower-numbered layer wins over a higher-numbered one. Layer 0 states this to the model; gate G0 enforces it at authoring time by running the assertion sets of all layers against any candidate for layers 3 to 5.
2. Instructions (the six layers) win over all data. Data cannot add, remove or suspend an instruction (layer 1 S1).
3. Within layer 1, S11 gives the order when rules collide: safety of life, then security of money and data, then the rules, then helpfulness.
4. Platform controls win over the prompt. Where the prompt and a rule disagree (they should not), the rule layer, Policy Engine, Tool Orchestrator and Output Safety Layer decide; the prompt is a restatement (system-architecture.md principle 1).
5. A template marked fixed (mode `template`) wins over layer 3 wording preferences: the model does not reword it (layer 3 D9).

## 5. Context-aware activation (A12.2)

Layer 3 carries eight conditional blocks. The assembler includes a block only when the Policy Engine sets its condition; the model never evaluates the condition.

| Block | Condition (set by) | Source of the condition |
|---|---|---|
| fraud_or_security | active intent SEC-001, SEC-002, SEC-004 or CRD-001 with a fraud cue; ESC-001 or ESC-009 pending | Policy Engine, Escalation Router |
| crisis | Input Guard crisis screen or GEN-007 at `flow_entry_confidence` | Input Guard, NLU |
| complaint | CMP-001 to CMP-005 active | NLU |
| safe_mode | `atk_adversarial_flags_safe_mode` reached, or the template-only lever is on | Policy Engine (GR-ATK-04), incident commander (GR-SYS-04) |
| waiting_for_human | dialogue_phase ESCALATING with a pending record | Escalation Router |
| reply language hi or hinglish | `language.reply_language` | State Tracker |
| reply language secondary | `language.reply_language` in ta, te, bn, mr, gu | State Tracker |
| channel voice or messaging app | A10.1 `channel` | Gateway |

Blocks only add restrictions or style. None can relax a layer 0 to 2 rule, so a wrongly activated block fails safe.

## 6. Token budget (proposal, D-139)

The brief gives no budget. Budgets below are ceilings per layer; the validator estimates tokens as words x 1.35 (a rough ratio for English prose, not a tokenizer measurement) and fails a layer that exceeds its ceiling.

| Part | Words now | Estimated tokens now | Ceiling |
|---|---|---|---|
| Layer 0 | 550 | 742 | 800 |
| Layer 1 | 1392 | 1879 | 2,000 |
| Layer 2 | 773 | 1044 | 1,150 |
| Layer 3 (all blocks active; a real turn activates a subset) | 1127 | 1521 | 1,650 |
| Layer 4 | 641 | 865 | 950 |
| Layer 5 frame plus at most `layer5_notice_max_active` notices | 250 frame | 338 frame | 750 |
| **System message total** | 4733 | 6389 | **7,300** (`prompt_token_budget_total`) |
| Data blocks: session facts 400, passages 1,500 (`knowledge_retrieval_top_k` entries), tool results 400, conversation 2,500, customer message 1,400 (`atk_input_max_chars` is 4,000 characters) | n/a | n/a | 6,200 |

Layers 0 to 2 are identical on every turn, so they are the natural prefix for provider-side prompt caching; that is a cost lever, not a requirement, and is not counted in `latency-scalability-cost.md`. The layer 1 slots `{{turn_boundary}}` and `{{canary_token}}` would defeat a cache of layer 1 if filled per turn; the implementation may place the per-turn code in a short uncached preamble instead. Open item.

## 7. Versioning, hashing and `prompt_version` (D-138)

A12.2: "Every prompt version stored with metadata (author, approval chain, deployment date, model version)."

1. **Layer version.** Each layer has a semantic version in its header: MAJOR for a change of meaning of any instruction, MINOR for an added or removed instruction that does not change others, PATCH for wording with no change of meaning. Versions are immutable once approved; a change is a new version.
2. **Layer hash.** SHA-256 of the prompt text between the markers, UTF-8, LF line endings, trailing spaces removed, assembly slots left unfilled.
3. **Bundle hash.** SHA-256 of the six lines `<layer>:<layer hash>`. **Immutable hash.** The same over layers 0 to 2 only; this is the value the dashboard and the load check compare (`safety-invariants.md` M7).
4. **Notice set id.** `n` plus the first six hex characters of the SHA-256 of the canonical JSON of the active notice records; `n000000` when there is none.
5. **`prompt_version`** (the string logged on every turn, `versions.prompt_version` in `config/dialogue_state.schema.json`, A10.2 turn record, `component-interfaces.md` versioning rule):

```text
sp-<bundle semantic version>+<first 8 hex of the bundle hash>.<notice set id>
current draft: sp-1.0.0+518d5a1e.n000000
```

6. **Manifest.** `manifest.yaml` stores the bundle version, the three hashes, the per-layer version and hash, the author, the approval chain, the deployment date (null: nothing is deployed), the model version (unbound: the design is provider-agnostic) and the `model_temperature` the bundle was approved with. `python tests/templates/validate_templates.py --rehash` writes the hash fields; every validator run verifies them, so an edit to any layer text without a rehash fails the build.
7. **What else the turn log records.** Template id, template version and variant key (attribution, D-102), the ids of the notices rendered, KB `id@version` for citations, and `model_version`. Together with `prompt_version` these make a turn replayable (A11.3).
8. **Rollback.** A flag flip to the previous bundle; it takes effect on the next turn and a conversation in progress finishes its current turn on the version it started (`safety-invariants.md` section 7).

## 8. Layer 5 typed notice slots

Specified in `layer5-operational.md` section 2. Summary: the frame text is fixed; daily changes are records with a closed schema (`system_status`, `known_issue`, `promotion`, `temporary_policy`); a record is validated at gate G0 (types, length, no digits, no link, no imperative text addressed to the assistant, expiry at most 7 days out) and is rendered inside data markers; the customer never sees the notice summary, only `TPL-SYS-NOTICE`; a promotion or policy notice carries a KB entry id and no figure.

## 9. Testable assertions

Every layer ends with an assertion table. IDs are `PA-L<layer>-<nn>` (D-155). An assertion states a pass condition on replies or on the change process, the guardrails that enforce it outside the prompt, and existing test cases that exercise it.

| Layer | Assertions | Notes |
|---|---|---|
| 0 | 8 | identity, disclosure, capability limits |
| 1 | 25 | the eight A4.2 rules, the advice boundary, instruction-data separation, prompt protection, truthfulness |
| 2 | 15 | A4.3 and A11.3 behaviours |
| 3 | 17 | the five A9.1 patterns and the eight A9.2 anti-patterns |
| 4 | 12 | grounding, citation, retrieval decisions |
| 5 | 7 | typed slots, no instruction in data |
| **Total** | **84** | all map to at least one existing case; none has been executed |

Known coverage gaps (reported in the Day 13 handoff): layer 5 assertions PA-L5-03 to PA-L5-07 map to the nearest existing case rather than a dedicated one; PA-L0-07 (reply language) and PA-L3-08 (context carry-over) have no dedicated case either.

## 10. What the prompt deliberately does not contain

| Not in any layer | Why | Where it lives |
|---|---|---|
| Product rates, fees, limits, tenures | a figure in a prompt goes stale and bypasses the KB (A9.2 Knowledge Hallucination is an AUTO-FAIL) | KB entries, locked slots |
| Thresholds and limits (confidence, sentiment, timeout, rate limits) | they are governed parameters; an immutable layer must not need an edit when one moves; and they would be an oracle if leaked | `config/parameters.yaml` |
| Secrets: keys, host names, customer data | leak tolerance (D-73) | nowhere in a prompt |
| Tool names and schemas | the model does not choose tools; listing them invites probing (GR-ATK-06-05) | Tool Orchestrator |
| Queue names, SLAs, trigger conditions | router-side; a customer must not learn routing reasons | `config/escalation_rules.yaml` |
| PEP, AML or risk flags | never enter a prompt (`prompt_visible: false`, D-120) | Escalation Router |
| Customer-facing sentences from templates | a reply that repeats eight consecutive words of layers 0 to 2 is blocked by the overlap scan (GR-ATK-06); the validator checks that no template does | `config/templates/` |
| Any digit | enforced by the validator as a cheap proxy for the first two rows | n/a |

## 11. Open items

1. No committee has reviewed any layer; every approval chain entry reads "pending".
2. The token figures are word-count estimates. A tokenizer measurement on the chosen model is needed before the ceilings are fixed.
3. The assistant has no personal name; a brand name is a Product and CEB decision.
4. Marker syntax, canary generation and the cache placement of the per-turn code are platform choices.
5. Secondary-language instructions exist (layer 3 block) but no reviewed secondary-language template text exists yet.
6. Layer 2 has had no legal review.
