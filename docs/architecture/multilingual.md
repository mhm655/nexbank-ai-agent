# Multilingual Support

## Languages

| Tier | Languages |
|---|---|
| Primary | English, Hindi, Hinglish (Hindi-English code-mixed, Roman script) |
| Secondary | Tamil, Telugu, Bengali, Marathi, Gujarati |

## Language detection

Run on the first message and re-checked each turn (customers switch). Output: primary language, script, and a code-switching flag. A short or ambiguous message inherits the previous language. A confirmed customer preference (set by an explicit request such as "reply in Hindi") overrides detection and is stored as `reply_language`.

## Code-switching

Hinglish is treated as its own language, not as noisy English or Hindi. NLU uses an encoder trained on code-mixed text; entities (amounts, UPI IDs, card digits) are extracted language-independently first. Reply language follows the customer's last message unless a preference is set. The agent mirrors the register (formal vs casual) but keeps banking terms in the form the customer used.

## Translation pipeline

1. **Primary languages:** NLU and generation operate natively; no translation hop.
2. **Secondary languages:** detect, normalise to an English pivot for intent and retrieval, then generate the reply in the target language from templates where possible. Safety-critical text uses pre-reviewed translated templates, not machine translation of free text.
3. The Output Safety Layer checks the final text in the target language and also checks the English pivot to ensure the facts match.

## Cultural adaptation

Formal address forms in Hindi, Marathi and Tamil by default ("aap", respectful suffixes). Currency in INR with the lakh/crore grouping where natural. Date format DD/MM/YYYY. Avoid idioms that don't translate. Sensitive topics (fraud, bereavement-related account queries) use gentler register.

## Quality assurance

- Native-speaker review of the template set and a sample of utterances per language (CEB concern).
- Per-language intent accuracy and CSAT monitored on dashboards; a language below target triggers a fallback to escalation for that language until fixed.
- Secondary-language fallback: if confidence is low, offer Hindi or English or a human who speaks the language.

## Detailed specification

Language ID thresholds, script handling, transliteration normalisation, the English-pivot interfaces, the secondary-language fallback ladder and per-language gates are specified in `docs/intent-taxonomy/language-detection.md` (Day 6). This file stays the summary; the two are consistent.
