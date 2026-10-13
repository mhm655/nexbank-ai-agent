# Language Detection, Code-Switching and Translation

Brief refs: A2.4 (multilingual), A2.2 (NLU), A13.2 (personas with Hindi-English mix and Gujarati support). This file expands the Day 3 outline in `docs/architecture/multilingual.md`, which stays the summary and is not contradicted here. Pipeline slots: stages 3.1 (language ID and code-switch tagging) and 3.2 (normalisation) in `docs/architecture/nlu-pipeline-overview.md`. Test data: `utterances.csv` (this folder) and `tests/nlu/README.md`.

All thresholds below are **proposals** (D-20). Like the NLU thresholds they are held in `config/parameters.yaml` and are tuned on the `dev` split.

## 1. Language set and codes

| Tier | Language | Code | Script(s) seen | Notes |
|---|---|---|---|---|
| Primary | English | `en` | Latin | Indian English, includes typos and SMS spelling |
| Primary | Hindi | `hi` | Devanagari | Often with Latin tokens ("statement", "block") |
| Primary | Hinglish | `hinglish` | Latin (Roman) | Hindi-English code-mixed; Roman-script Hindi is treated as Hinglish, per multilingual.md |
| Secondary | Tamil | `ta` | Tamil | |
| Secondary | Telugu | `te` | Telugu | |
| Secondary | Bengali | `bn` | Bengali | |
| Secondary | Marathi | `mr` | Devanagari | Shares a script with Hindi |
| Secondary | Gujarati | `gu` | Gujarati | Persona Rajesh (A13.2) |

The codes match the `language` entity values in `config/entities.yaml`, so the detector output, the GEN-005 slot and the stored `reply_language` use one vocabulary. The NLU frame field is `language.primary` plus `language.code_switching` (nlu-pipeline-overview.md section 2); this spec adds `script`, `confidence` and `mix` to the same object (section 3).

## 2. Order of operations

```
raw message
  -> Input Guard: redaction, injection and crisis screen   (runs on a digit-folded copy, section 4.3)
  -> 3.1 Script detection (per token, Unicode block)
  -> 3.1 Language ID (utterance level, then token tags for mixed text)
  -> 3.2 Normalisation (Unicode, digits, transliteration variants, number words, spelling)
  -> 3.4 Encoder and heads (native for primary, native plus English pivot for secondary)
```

Redaction stays first (RED-01 to RED-07). Language detection never sees a full card, Aadhaar, OTP or PIN, because the Input Guard has replaced them with placeholders.

## 3. Language detection

**Method.** Two cheap signals, then a model. (1) Script by Unicode block per token gives the candidate set: Devanagari (U+0900 to U+097F), Tamil (U+0B80 to U+0BFF), Telugu (U+0C00 to U+0C7F), Bengali (U+0980 to U+09FF), Gujarati (U+0A80 to U+0AFF), Latin. (2) A lightweight language-ID classifier trained on code-mixed text (the same encoder family as the NLU, per nlu-pipeline-overview.md) scores the utterance. The result is the NLU frame's language block:

```json
"language": { "primary": "hinglish", "script": "latin", "confidence": 0.93,
              "code_switching": true, "mix": { "hi": 0.55, "en": 0.45 }, "source": "detected" }
```

`source` is `detected`, `inherited` or `preference` (a set `reply_language`).

**Decision table (proposed thresholds).**

| Condition | Result |
|---|---|
| Customer set a reply-language preference ("reply in Hindi", GEN-005 `explicit_request`) | `reply_language` is stored and overrides detection for the reply. `language.primary` is still detected per turn so the NLU reads the input correctly |
| Detection confidence >= 0.80 (`lang_id_accept`) | Accept the detected language |
| 0.50 to 0.80 | Accept if it equals the previous turn's language; otherwise keep the previous language and set `language.confidence_low` (no reply-language switch yet) |
| < 0.50 (`lang_id_floor`) | Inherit the previous turn's language. On the first turn use Hinglish for Latin-script text and Hindi for Devanagari-only text, and add a language-choice quick reply to the first response |
| Message under 4 tokens, digits only, or a slot answer ("yes", "5000", "ok") | Inherit, as multilingual.md states for short or ambiguous messages |
| Mixed-script message, native script plus Latin | Primary language is the native-script language; Latin tokens count toward `mix` |

**Same-script ambiguity (Hindi and Marathi).** Both are Devanagari. The script alone cannot decide, so the classifier uses function words and verb endings (for example "है" and "मला ... आहे") and returns both scores. If the gap is under 0.15, the previous language wins, and a persistent mismatch triggers the language-choice quick reply.

**Roman-script secondary languages.** A customer may type Tamil or Telugu in Latin letters. This is the weakest case. If the classifier returns a secondary language in Latin script at >= 0.80 it is processed as that language through the pivot (section 6). Below that it is treated as Hinglish for reading and the first reply carries a language-choice quick reply; it is never silently mislabelled as English.

**Per-turn re-check.** Customers switch mid-conversation ("Hindi mein baat karo", then an English reply). Detection runs every turn. This refines multilingual.md's "reply language follows the customer's last message": the reply language changes only on a stable switch (two consecutive turns with confidence >= 0.80) or an explicit request. A one-word borrowed term does not switch the reply language.

## 4. Script handling and normalisation

### 4.1 Unicode

Apply NFC. Remove zero-width joiners and non-joiners except where the script needs them (some conjuncts and Indic scripts need them; the retained ones are whitelisted). Collapse repeated punctuation and elongation ("pleaseeee" becomes "please"). Do not strip diacritics from native-script text: it changes words. Store the original text for audit and the normalised text for the model.

### 4.2 Transliteration normalisation (Roman Hinglish)

Hinglish spelling is free-form, so a canonical-form map is applied before the encoder (the encoder is also trained on the variants; normalisation reduces rather than replaces that). Examples of the map:

| Variants | Canonical |
|---|---|
| nahi, nahin, nhi, nai, nahee | nahi |
| hai, h, hain, he, hei | hai |
| kitna, kitnaa, ketna, kitne | kitna |
| paisa, paise, paisey, pese | paisa |
| balance, blance, balnce, bal | balance |
| bhai, bhaiya, bro | bhai (politeness register feature, not an intent cue) |
| kal (yesterday or tomorrow), parso, aaj | kept, and resolved with the `date` rules in `entities.md` |

Native-script Hindi is **not** transliterated to Roman for intent classification: the multilingual encoder reads Devanagari directly. Roman Hinglish is **not** converted to Devanagari. The only conversions are those listed here, so no information is lost between the stages. Entity values keep their surface form ("kal", "Ramesh Traders") and are normalised by the entity validators (`entities.yaml`).

### 4.3 Digits and number words (also a security control)

- Fold Devanagari, Bengali, Gujarati, Tamil and Telugu digits to ASCII for matching ("५००० " to 5000).
- Number words and shorthand per language and in Hinglish: "paanch hazaar", "ek lakh", "5L", "50k", "5 lakh", "डेढ़ सौ" are resolved by the amount extractor, in the lakh and crore system. A resolved amount keeps its source text.
- **The Input Guard redaction rules (RED-01 to RED-07) match on a digit-folded and space-collapsed copy**, so that a card number, OTP, CVV, PIN or Aadhaar typed in native digits, with separators, or spelled in words cannot slip past redaction. The original text is replaced by the placeholder, never stored (D-21 records this).

### 4.4 Spelling and typos

A language-aware spell and slang pass runs before the heads for `en` and Hinglish (typo rate in the library is about 7%). It is conservative: it never alters tokens inside entity spans (IDs, UPI handles, names) and never rewrites safety cues ("not me", "maine nahi kiya", "block"). Native-script typos are left to the encoder.

## 5. Code-switching

Per multilingual.md, Hinglish is its own language, not noisy English or Hindi. Additional rules:

1. **Token tagging.** Each token is tagged `hi`, `en` or `other`; the tags feed `language.mix` and the code-switching flag (set when both languages exceed 20% of tokens; proposed `code_switch_min_share`).
2. **Intra-sentence switching is neutral.** A switch is not a topic change, an intent change or a sentiment signal. It never counts toward a topic switch in the dialogue state.
3. **Banking terms keep the customer's form.** "statement", "block", "FD", "EMI", "OTP" are not translated back into Hindi; the reply uses the form the customer used (multilingual.md).
4. **Devanagari plus Latin** ("UPI payment fail हो गया but पैसे कट गए") is language `hi` with a high `mix.en`; reply script follows the customer's dominant script.
5. **Intent cues are language-independent where possible.** Safety cues exist in each language's lexicon: not-me ("maine nahi kiya", "मैंने नहीं किया"), scam ("OTP de diya"), loss ("kho gaya", "chori ho gaya"), human request, distress. The rule layer (advice detector, crisis screen, fraud cues) is evaluated on the native text and on the English pivot, and either may trigger.
6. **Sarcasm and tone** are scored by the sentiment head (`sentiment.md`); transliterated slang ("bhai", "yaar") is a register feature, not an intent cue.
7. **Entities first.** Amounts, UPI IDs, transaction and complaint IDs and masked card digits are extracted language-independently before intent fusion (multilingual.md), so a Hindi sentence around an English ID parses the same as an English one.

## 6. Translation pipeline

Aligned with multilingual.md; this section only adds interfaces and checks.

| Step | Primary (`en`, `hi`, `hinglish`) | Secondary (`ta`, `te`, `bn`, `mr`, `gu`) |
|---|---|---|
| Input to NLU | Native text, no translation hop | Native text and an English pivot in parallel |
| Intent and retrieval | Native | **Pivot is the retrieval query**; the intent heads read native and pivot, and the higher-calibrated one wins, with agreement as a confidence bonus and disagreement as a clarify trigger |
| Entities | Native extraction | Native extraction, then language-independent validators; never extracted from the machine translation alone (amounts, names and IDs can be corrupted by MT) |
| Generation | Template or hybrid, native | Pre-reviewed translated **templates** wherever possible; hybrid free text only for non-safety content |
| Safety-critical text | Pre-reviewed templates | Pre-reviewed translated templates only. No machine translation of free text for fraud, block, crisis, legal or advice-boundary wording |
| Output Safety Layer | Checks final text | Checks final text in the target language **and** the English pivot of it for fact match (multilingual.md) |

**Pivot quality gate.** The translator returns a quality estimate. Below 0.60 (`pivot_quality_floor`) the turn is treated as low confidence for retrieval (the retrieval threshold of 0.65 is unchanged) and goes to the fallback ladder in section 7. Numbers, IDs and named entities in the source must appear in the pivot; a mismatch also fails the gate.

**What is translated.** KB answers are authored in English and rendered through reviewed translations for the languages that have them; where a translation does not exist the agent says so and offers Hindi, English or a human, rather than machine-translating a financial fact.

## 7. Secondary-language fallback and thresholds

The intent thresholds in `config/intents.yaml` apply unchanged to secondary-language turns (primary 0.85, secondary 0.70, tertiary 0.65; execution 0.85 plus confirmation for HIGH and CRITICAL writes; safety-flow entry 0.50). Extra rules apply because accuracy is lower and the reply is template-bound.

| Situation | Behaviour |
|---|---|
| Language ID < 0.50 or Roman-script secondary below 0.80 | Language-choice quick reply (the language names in their own script, plus Hindi, English, Hinglish), then continue |
| Intent confidence < 0.70 after the pivot, first time | Ordinary clarification, in the customer's language from a reviewed template |
| Still < 0.70 after the clarification (budget `max_clarification_turns` = 2, so at most one more try) | Offer a switch to Hindi or English, or a human who speaks the language, with buttons. The switch is a customer choice, never automatic |
| A customer-chosen switch | Stored as `reply_language`; the NLU keeps reading both the language the customer types in and the preference |
| Two consecutive turns below 0.40 | `consecutive_low_conf` (ESC-003 rule); a third fires ESC-003 as for any language. Routing prefers a human with the language, falling back to Hindi or English support with a language flag in the handoff package |
| Sentiment on secondary-language turns | Use the EMA route and the confidence gate from D-18; the secondary-language sentiment head is weaker |
| Fraud, scam, distress, human request, legal threat | Never wait for translation quality: the flow-entry gates apply (0.50), the Input Guard screens native text and pivot, replies use reviewed templates, and the human handoff carries the language |

**Per-language gate (from multilingual.md).** Each language has a rolling intent-accuracy target. Proposed: primary languages at the brief's > 92% intent accuracy; secondary languages at >= 85% pooled until native-reviewed data supports per-language targets (D-22). A language that falls below its target for a full evaluation window is put in "escalate on low confidence" mode: the clarification budget drops from 2 turns to 1 and the human offer is made at the first failure, until the fix is verified. The language also shows on the dashboards (`docs/metrics/dashboards.md`).

**Human coverage.** Whether the escalation queue can staff all five secondary languages is open (section 9); the spec routes by a `language` field so the queue design can decide.

## 8. Evaluation and quality assurance

- `utterances.csv` carries a `language` column (`en` 213, `hinglish` 167, `hi` 87, `ta` 26, `te` 15, `bn` 15, `mr` 14, `gu` 13 rows) and the test split is stratified by language class, so every intent has at least one test row and the test split includes rows in all five secondary languages.
- Metrics are reported by language and pooled for the secondary group (`tests/nlu/README.md`). The secondary test split has only 17 rows, so per-language numbers are not stable yet; the Day 14 conversations add no rows to the split; a native-reviewed expansion is pending.
- Language ID itself is evaluated on the same set: accuracy by language, confusion between Hindi and Marathi, and the Roman-script secondary case. Target (proposed): >= 0.95 for primary languages, >= 0.90 for secondary.
- Native-speaker review (CEB concern, multilingual.md): the secondary-language utterances and the translated template set are provisional until a reviewer per language signs them off. Review records the reviewer, date and corrections in the CHANGELOG.
- Monitoring: per-language intent accuracy, clarify rate, fallback offers, human-handoff rate and CSAT, as in multilingual.md.

## 9. Open items

- Whether human support exists for each secondary language and its hours (affects the last step of section 7); Risk and CEB input.
- The detector, translator and encoder are provider-agnostic (A4); candidate model classes are named in the NLU overview, and none is committed.
- Secondary-language rows in the library are machine-drafted and not native-reviewed; treat them as provisional (D-22).
- Thresholds in sections 3, 5, 6 and 7 are proposals to be tuned on `dev` and held in `config/parameters.yaml`.
