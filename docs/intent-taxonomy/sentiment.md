# Sentiment and Emotion Specification

Brief refs: A2.2 (real-time continuous scoring, seven emotions, trajectory tracking, Indian-English cultural sensitivity, sarcasm and irony), A6 (ESC-004), A9 (Empathy-First, Pattern 1), A12.3 (`escalation_sentiment_threshold`), A8 (CSAT). State fields: `sentiment` in `config/dialogue_state.schema.json`. NLU context: `docs/architecture/nlu-pipeline-overview.md`. Customer-effort and CSAT use of these signals: Day 11 and Day 12.

## 1. Outputs per customer turn

| Output | Type | Notes |
|---|---|---|
| `score` | number in [-1, 1] | Continuous polarity of the customer's turn after sarcasm adjustment. -1 very negative, 0 neutral, +1 very positive |
| `emotions` | up to 7 labels with intensity 0 to 1 | frustration, anger, confusion, satisfaction, urgency, anxiety, resignation. Multi-label; a label is "active" at >= 0.50 |
| `sarcasm` | probability 0 to 1 | `sarcasm_suspected` in state is true at >= 0.60 |
| `confidence` | 0 to 1 | Model certainty in the score; used by the escalation rule |
| `trajectory` | raw scores of all customer turns so far | The state schema's `trajectory` array |
| `slope` | number | Least-squares slope of the last 5 customer turns |

State mapping: `sentiment.current` = smoothed score (section 4), `trajectory` = raw per-turn scores, `slope`, `emotions` = active labels, `sarcasm_suspected`.

## 2. Model design

- **Shared encoder with extra heads.** Polarity regression, 7-way multi-label emotion, sarcasm binary. They share the NLU encoder (nlu-pipeline-overview.md section 1, stage 3.4), so there is no extra encoder pass and the budget impact is small.
- **Context features.** The previous agent act (apology, failure, clarification, handoff offer), whether the same intent has been open for several turns, the clarification count, and the previous sentiment. These matter because the same words carry different meanings after a failure (see sarcasm).
- **Lexicon features.** A curated Indian-English, Hindi and Hinglish lexicon (Devanagari and Romanised) is a feature set and a rule-layer fallback, not the main model.
- **Language coverage.** Primary: English, Hindi, Hinglish. Secondary: Tamil, Telugu, Bengali, Marathi, Gujarati; coverage for these relies on the multilingual encoder with a smaller lexicon, and has lower confidence, which the escalation rule respects (section 5).
- **Fallbacks.** Sentiment head unavailable: score is *unknown*, not neutral (nlu-pipeline-overview.md section 7); the lexicon rule layer still marks strong signals (swearing, capitals with several exclamation marks, explicit "worst service").
- **Privacy.** Scores and labels are stored; the raw text goes through the normal redaction (entities.md section 2). No emotion data is used for customer profiling or pricing.

## 3. Seven emotions

| Emotion | Typical signals (English / Hinglish) | Agent response style |
|---|---|---|
| frustration | repeated asks, "again", "still", "kitni baar", "bahut time lag raha hai", "this is ridiculous", "kya bakwas hai" | Acknowledge, own the delay, give the next concrete step, shorten turns |
| anger | caps, "!!!", abuse, threats, "worst", "bekaar bank", "I will report", "bakwaas" | Calm, brief, no defensiveness, no policy lecture; legal words go to ESC-002 |
| confusion | "I don't understand", "samajh nahi aaya", "what does that mean", repeated "?" | Simplify, one idea per message, example, offer a different channel (Progressive Disclosure layer 1 only) |
| satisfaction | "thanks", "great", "perfect", "bahut accha", "mil gaya" | Close the task, then the CSAT ask; no new offers while a task is open |
| urgency | "urgent", "jaldi", "right now", "abhi", "ASAP", "emergency" | Shortest path, skip optional steps, surface the human option early; urgency plus fraud words is P0 |
| anxiety | "worried", "tension", "pata nahi kya hoga", "paise kat gaye", "is my money safe" | Reassure with facts first (what is already protected, what the agent is doing), avoid speculative reassurance |
| resignation | "chalo theek hai", "forget it", "rehne do", "koi fayda nahi", "whatever", short flat answers after a long exchange | Do not close. Check in once ("Before we stop, can I try one more thing?") and offer a human; log silent dissatisfaction |

Intensity and negative-polarity mapping: frustration, anger, anxiety and resignation lower the score; confusion is neutral to mildly negative; urgency is neutral (it increases priority, not negativity); satisfaction is positive.

## 4. Continuous scoring and trajectory

1. **Raw score** `s_t` for every customer turn (not agent turns).
2. **Smoothed score** with an exponential moving average, `m_t = 0.5 * s_t + 0.5 * m_(t-1)`, so that one blunt message does not dominate. `sentiment.current` is `m_t`.
3. **Slope** is the least-squares slope of the last 5 raw scores (fewer if the conversation is shorter; reported only from 3 turns).
4. **Volatility** is the standard deviation of the last 5 scores, used by the supervisor view.
5. **Recovery** is detected when slope >= +0.15 per turn over 3 turns and `m_t` >= -0.2. A recovery is a positive learning signal and is attributed to the agent action that preceded the rise (apology, a concrete fix, a human offer) in the learning pipeline.
6. **Spike versus drift.** A single drop of 0.6 or more is a spike (often a misunderstanding); a falling slope across turns is a drift. The policy treats a spike with a repair attempt, and a drift with proximity and handoff preparation.

## 5. Policy use

### 5.1 ESC-004 (hard trigger, A6)

ESC-004 fires when the *raw* sentiment score is below `escalation_sentiment_threshold` (default -0.70, range -1.0 to -0.3, CX Team, CEB approval) on **2 or more consecutive customer turns**. It routes to Customer Retention at P1 (< 5 min).

Safeguards, so that a noisy score does not cause a false escalation, or a missed one:

- Both turns must have `confidence` >= 0.70. Below that, the turn is counted as "uncertain" and neither adds to nor breaks the streak.
- A turn flagged `sarcasm_suspected` is scored using the sarcasm-adjusted polarity (section 7), not the literal one.
- For the secondary languages the model confidence is usually lower, so the rule also accepts the EMA: 2 consecutive raw scores strictly below the threshold, with the sentiment-confidence gate waived and the smoothed score `m_t` strictly below the threshold, trigger the same route (D-165: the route waives only the confidence gate). This removes the language disparity that a confidence gate alone would create; the fairness test on this (counterfactual language swap) is in the Day 14 risk matrix.
- The default threshold is the brief's. It is a CEB-owned parameter; changing it is outside this specification's authority (D-18).

### 5.2 Escalation proximity

Sentiment slope and level are two of the inputs to the 0 to 1 escalation-proximity score (dialogue-management.md section 6). Slope < -0.15 per turn raises it; any active anger or resignation emotion raises it. This is advisory: proximity >= 0.6 prepares a handoff package, >= 0.8 offers a human.

### 5.3 Empathy-First trigger (A9 Pattern 1)

The Empathy-First pattern (Acknowledge, Assure, Act, Affirm) applies when any of: `m_t` <= -0.30, an active frustration, anger, anxiety or resignation label, a problem or complaint intent (TXN-002, TXN-003, CMP-*, SEC-*), or a recovery from a drop. The acknowledgement is one sentence, specific to the situation, not a repeated apology (apologise once, specifically, then act, per A9.3; an over-apology with no resolution steps is the Sycophantic Recovery anti-pattern, and skipping the acknowledgement entirely is Empathy Bypass).

### 5.4 Tone and length

| State | Behaviour |
|---|---|
| `m_t` <= -0.40 | No proactive recommendations or cross-sell (consistent with the Day 3 trace), shorter replies, no marketing phrases |
| Active confusion | Simpler wording, one idea, an example; offer another language or a human |
| Active urgency | Fewest steps; skip optional slots; do not interleave information |
| Positive and task complete | CSAT ask; a proactive, relevant, non-advice offer is allowed once |
| Unknown sentiment | Neutral polite tone; rely on lexicon hits for empathy |

### 5.5 Other consumers

- **Supervisor review sampling (Day 11).** Conversations with a large negative drift, sarcasm flags or recovery are oversampled.
- **CSAT prediction and silent-dissatisfaction detection.** A "thanks" after a falling trajectory with resignation is flagged as likely silent dissatisfaction.
- **Metrics (Day 12).** Share of conversations with a recovery, mean sentiment change from first to last turn, ESC-004 volume and false-positive rate.

## 6. Indian-English and Hinglish cultural sensitivity

A direct English-trained sentiment model misreads Indian customers in predictable ways. The spec handles these cases explicitly:

| Pattern | Example | Handling |
|---|---|---|
| Politeness inflation covers anger | "Kindly do the needful at the earliest", "I request you to look into it", "Sir, I have already informed three times" | Formal register plus a repeat cue ("already", "three times") scores as frustration. Formality is not satisfaction |
| "Sir/Madam" and "please" | "Please sir please help" | Marks urgency and anxiety, not satisfaction |
| Emphasis by repetition or reduplication | "fast fast", "jaldi jaldi", "pls pls pls", "bahut bahut" | Raises intensity of the emotion, not the polarity |
| Emphatic "only" and "na" | "I will come to branch only", "kar do na" | Marks firmness (frustration or urgency); not a hedge |
| Indirect complaint | "It would be nice if someone replied", "I was expecting a better service" | Read as mild to moderate dissatisfaction when preceded by a failure, not as neutral |
| Understated hardship | "Thoda problem ho gaya hai" after money is deducted | Reads as anxiety. Amount and loss context raise intensity |
| Code-mixed negation | "problem nahi hai" vs "problem hai nahi solve hua" | The negation scope is handled across languages; "nahi" and "na" flip only the nearest predicate |
| Romanised spellings | "bakwas", "bakwaas", "bekar", "fraud hai", "chor" | Variants listed in the lexicon with phonetic matching |
| Religious or cultural greeting | "Namaste", "Jai Hind" | Neutral politeness, no polarity |
| Emoji | 🙏 (plea or thanks, read with the words), 😂 or 🙂 after a complaint (possible sarcasm), 😡 | Interpreted with context, not as fixed polarity |
| Regional-language courtesy | Tamil, Telugu, Bengali, Marathi, Gujarati honorifics | The encoder handles them; the lexicon is small, so confidence is reduced and the EMA route (section 5.1) is used |
| Resignation in quiet speech | "Theek hai, chalo", "koi baat nahi", "rehne do" | Resignation label, not satisfaction, especially after unresolved turns |

Indian customers may also not express anger overtly with a bank they depend on. The model therefore treats *behaviour* (repeats, clipped replies, asking for a person, long silence after a failure) as signal alongside words.

## 7. Sarcasm and irony

**Definition.** A positive-sounding message that expresses negative sentiment, almost always about the agent or bank.

**Examples.** "Wow, great service, third time asking the same thing", "Thanks for nothing", "Bahut accha service hai aapki, 3 din se wait kar raha hu", "Excellent, now it's even worse" with 🙂 or 😂.

**Detection (combined, no single cue decides).**

1. **Incongruity.** A positive lexicon hit (great, wonderful, excellent, bahut accha, shabash, thanks) within a context that is negative: an open unresolved problem, the previous agent act was a failure or a repeat clarification, or the topic is a loss.
2. **Surface cues.** Quotation marks around a positive word, ellipses, "yeah right", "kya baat hai", mock thanks, an emoji of the opposite polarity, exaggeration ("best bank ever" after an error).
3. **Model head.** The sarcasm head output, using the context features above.
4. **Interaction with trajectory.** A positive literal score right after two or more negative turns, with no resolving agent action, is suspicious.

**Handling.**

| Sarcasm probability | Score used | Agent behaviour |
|---|---|---|
| < 0.40 | Literal | None |
| 0.40 to 0.60 | Literal, with a -0.15 caution | Do not assume. The reply can include a light check: "Did that help, or is something still not right?" |
| >= 0.60 | Polarity inverted to the negative reading, `sarcasm_suspected` = true | Empathy-First reply that acknowledges the underlying problem without accusing the customer of sarcasm: "It sounds like this has been frustrating, and I'm sorry. Let me see what I can fix." |
| >= 0.60 and the customer replies that they were sincere | Flag reset, next turn re-scored | Short apology for the misread, continue |

A wrong sarcasm call costs one unnecessary empathy sentence; a missed sarcasm may let ESC-004 pass unseen, so the inversion is the safer error. The sarcasm head's precision and recall are tracked separately (section 9).

## 8. Interaction with other components

| Component | Interaction |
|---|---|
| Input Guard | Crisis wording (self-harm, threats) is a separate classifier and ESC-011 path; sentiment never downgrades it |
| Dialogue policy | Empathy-First, tone, no proactive offers, handoff preparation (section 5) |
| Response generator | Receives `emotions` and a tone directive; templates for safety-critical facts are unchanged |
| Output safety layer | Tone verification checks for empathy where required and flags dismissiveness |
| Escalation router | ESC-004 payload includes the trajectory and the active emotions in the handoff package (element 6 of the 8, D-04) |
| Learning pipeline | Sentiment recovery and drift per action; reward-hacking is prevented by keeping the escalation and safety rules outside what the pipeline can change |

## 9. Evaluation (proposed targets, to be confirmed on the Day 6 data)

The brief gives no sentiment accuracy target; these are proposals I set so the model is testable.

| Measure | Proposed target |
|---|---|
| Polarity: agreement with human labels (Cohen's kappa) | >= 0.70 |
| Emotion macro-F1, primary languages | >= 0.75 |
| ESC-004 precision at the default threshold | >= 0.85 (false escalations are the Premature Escalation anti-pattern, -10) |
| ESC-004 recall on labelled very-negative pairs | >= 0.90 |
| Sarcasm recall | >= 0.60, with precision >= 0.60 |
| Fairness: counterfactual language, region and name swap on ESC-004 | Escalation rates equal within 2 percentage points; method in `docs/risk/fairness-testing.md` section 6 |

The evaluation set is built from the Day 6 utterance library plus 100 synthetic multi-turn trajectories (sentiment curves, sarcasm cases, recovery cases).

## 10. Open items

- D-18: ESC-004 uses raw consecutive scores per the brief, with the confidence and EMA safeguards above. Awaiting CEB view on the EMA route for secondary languages.
- The exact lexicon and emoji table are data artefacts, built with native-speaker review on Day 6 (plan risk table: Hinglish and Indic quality).
- Voice channel prosody features (tone, speech rate) are out of scope for this text spec.
