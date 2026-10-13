# Response Generation

## 1. Generation strategy

| Mode | Used for | Why |
|---|---|---|
| Template | Account balances, transaction details, fees and rates, regulatory statements, confirmations, escalation notices | Exact, auditable, no hallucination risk. Values are injected from tool results or KB entries |
| LLM | Empathy statements, clarifications, explanations, transitions | Natural and adaptive |
| Hybrid | Most turns | A template carries the facts; the LLM only wraps it in an empathy opener and a next-step line, and cannot change the fact slots |

**Hybrid contract:** facts are passed as locked slots (`{{balance}}`, `{{rate}}`). The Output Safety Layer verifies that every number and rate in the final text matches a locked slot or a cited source.

**Renderer rule for kb slots (D-199):** a kb slot is filled with the served-language body when the entry has a current reviewed one, otherwise with the English body verbatim and untranslated, and the log flag `translation_unavailable` is set; nothing is machine-translated. Slot labels (action verb and noun, result, service, notice effect, topic, option, finish offer) come from the reviewed tables in `config/templates/labels.yaml` (D-198).

## 2. Persona

Brand voice: **friendly, trustworthy, modern**. Plain language, short sentences, no jargon without an explanation, no slang that could read as flippant in a fraud or complaint context. The agent discloses it is an AI at the start and whenever asked. It does not claim human experiences. Tone adapts to emotion: more empathy and fewer words when the customer is frustrated or anxious; no humour near fraud, loss or complaints.

## 3. Length calibration

| Context | Target |
|---|---|
| Simple fact, balance | 1-2 sentences |
| Explanation or how-to | 3-5 short sentences or a numbered list of at most 5 steps |
| Frustrated or anxious customer | Acknowledge first (1 sentence), then 2-3 sentences of action |
| Voice or WhatsApp | Shorter; no tables |

## 4. Conversation patterns (finalised Day 13: `conversation-design.md`)

Five mandatory patterns (A9.1): Empathy-First, Progressive Disclosure, Confirmation-Before-Action, Graceful Degradation, Context Carry-Over; see `docs/architecture/conversation-design.md`. Eight anti-patterns to avoid include robotic loops, empathy bypass, false confidence, and repeating the same fallback message.

## 5. Output Safety Layer

All draft responses pass these checks before delivery:

| Check | Method | On failure |
|---|---|---|
| Financial accuracy | Numbers and rates compared with tool/KB values | Replace with the template version |
| Regulatory compliance | Rule scan plus classifier (no guarantees, no advice, required disclosures) | Block, use the compliant template |
| PII leak | Pattern detection and masking (card, Aadhaar, PAN, phone, full account number) | Mask; if the leak is a credential, block |
| Hallucination / grounding | Every factual claim must map to a source (tool or KB passage) | Remove the claim; clarify or escalate |
| Tone | Classifier for empathy and professionalism; banned phrases | Rewrite once; else template |
| Commitment detection | Flags promises of outcome or timeline not backed by a system of record (D-09) | Rephrase as a hedged range or remove |
| Advice boundary | Detects recommendations, comparisons phrased as advice, suitability judgements | Replace with information-only wording |

**Degradation ladder:** safe template, then clarify, then escalate.
