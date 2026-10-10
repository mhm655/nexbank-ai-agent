# Customer Satisfaction Signals

Brief refs: A5.2 (p.15: "in-conversation sentiment check at natural breakpoints; post-conversation CSAT rating (1-5) with optional free-text; implicit signals (resolution without escalation, return visits, time to resolution); dissatisfaction detection without explicit feedback; feedback bias correction; and feedback attribution to specific agent actions"), A8.1 (p.19: Sentiment Trajectory Slope), A8.2 (p.20: CSAT 4.5, FCR 70%, CES 5.5, NPS 50), A8.5 (p.22: rolling 1-hour CSAT), A10.1 (p.27: `csat_score` Float 1-5, retention 3 years), A1.1 and A1.2 (pp.3-4: current CSAT 3.2, target 4.5, per-category CSAT), A11.3 (pp.31-32: no differential treatment; no sensitive-attribute inference). Related: `docs/intent-taxonomy/sentiment.md` (scoring, resignation, silent dissatisfaction), `config/intents.yaml` (CMP-004, GEN-006), `outcome-tracking.md`, `ab-testing.md`.

**Status.** The brief fixes the six design items above and the CSAT scale. The response-rate assumption, the check-in limits, the detector thresholds, the weighting scheme and the attribution method are proposals (D-99 to D-102). Worked figures are illustrative.

## 1. Purpose and the three layers of signal

CSAT is the Customer Experience Board's headline metric (A1.3), but an explicit rating exists for a minority of conversations and that minority is not representative. The design therefore uses three layers and never treats one as the whole truth.

| Layer | Signal | Coverage | Strength | Weakness |
|---|---|---|---|---|
| Explicit | post-chat CSAT 1-5 with optional comment; in-conversation check-in answers | planning assumption: 15% of conversations (section 3.3) | the customer's own judgement | non-response bias; one number for a whole conversation |
| Implicit | resolution without escalation, return visits, time to resolution, abandonment, sentiment trajectory | 100% | no survey needed | indirect; needs outcome maturity (7 days for return visits) |
| Predicted | silent-dissatisfaction score and predicted CSAT (pCSAT) | 100% | fills the gap for non-responders | a model output, not a measurement; used for triage and monitoring only |

## 2. In-conversation sentiment check at natural breakpoints

A check-in is a short question that confirms the customer is being helped. It is a dialogue act, not a survey.

| Rule | Specification (proposal unless stated) |
|---|---|
| Natural breakpoints | (a) after a task completes and before closing (the "anything else" point); (b) after the agent delivers a multi-step explanation (Progressive Disclosure, A9); (c) after a failed lookup or a gap statement; (d) when `sentiment.slope` is negative for 2 turns but ESC-004 has not fired; (e) on resignation cues (`sentiment.md` section 3: "chalo theek hai", "forget it") |
| Never at | mid slot-filling or with a `pending_confirmation` open; inside the fraud, crisis or credential-compromise flows before containment (SEC-001, SEC-004, GEN-007); in the same turn as a refusal or a disclosure; after the customer has asked for a human |
| Frequency | at most 1 check-in per task and 2 per conversation; none in conversations of 3 turns or fewer |
| Form | a template (Day 13 library), in the customer's reply language, for example "Is this helping so far?" or "Before we stop, can I try one more thing?" (`sentiment.md`); never a 1-5 scale mid-conversation |
| Reading the answer | NLU classifies the reply as positive, negative or neutral with the normal sentiment model; a negative reply raises `escalation_proximity`, triggers one recovery attempt and offers a human. It does not by itself create an ESC record: ESC-004 keeps the brief's rule (2 or more turns below -0.7, D-18) |
| Record | `checkin` event on the turn log: breakpoint type, template id, reply polarity, turn id. A rating typed in reply is captured as a dialogue act, not a topic switch (`config/intents.yaml`, CMP-004 note) |
| Guardrails | the check-in text passes the Output Safety Layer like any reply; it never offers a product, a promise or an incentive for a good rating |

Check-in answers are explicit signals at turn level. They are the main input to attribution (section 7) because they are tied to a point in the conversation.

## 3. Post-conversation CSAT

### 3.1 Survey

| Aspect | Specification |
|---|---|
| Question | one rating, 1 to 5 (brief), with an optional free-text comment (brief). Wording is a Day 13 template; the scale direction is stated every time (1 lowest, 5 highest) |
| When | when the conversation reaches `CLOSING` after GEN-006 (thanks or closure) or a completed task; for an escalated conversation, after the human agent closes it, with a separate question about the AI part and the human part (proposal) so that the handoff is not scored against the wrong party |
| Not asked | conversations that ended in ESC-011 (crisis); fraud and security conversations still open with a human team (asked after the case closes); sessions that timed out with no customer message after the greeting; a customer already surveyed in the last 7 days (proposal, survey fatigue); a customer who opted out of surveys |
| Channel | the same channel as the conversation; one prompt, no reminder |
| Storage | `csat_score` on the conversation record (A10.1: Float 1-5, retention 3 years); the comment after RED-01 to RED-07 redaction (case SS-PII-10), also 3 years |
| Other A8.2 metrics | CES (1-7) and NPS are sampled on separate, less frequent surveys so the post-chat prompt stays at one question (proposal; detail in `docs/metrics/`, Day 12) |

### 3.2 Use

A rating is evidence about the conversation as handled by one version tuple (prompt, model, KB epoch). It feeds: the rolling CSAT panels (A8.5), the A/B primary metric (`ab-testing.md`), the complaint-triggered review stream for ratings of 1 or 2 (`supervisor-corrections.md`), and attribution (section 7). It is never a training label by itself: a low rating does not say what was wrong.

### 3.3 Response-rate assumption

The brief gives no response rate. Planning assumption (D-99): **15% of closed conversations return a rating**, that is 18,000 x 0.15 = 2,700 ratings per day, with sensitivity cases of 10% (1,800) and 25% (4,500). Sample-size and staffing arithmetic in the other documents uses 15% and shows the sensitivity. The first weeks of operation replace the assumption with the observed rate, per channel and per outcome.

## 4. Implicit signals

The brief names three: "resolution without escalation, return visits, time to resolution". The table adds the others the logs already hold.

| Signal | Definition | Source | Reads as |
|---|---|---|---|
| Resolution without escalation (brief) | conversation closed with `resolution_status = resolved_ai` | A10.1 | positive |
| Return visits (brief) | a new contact by the same customer on the same issue within 7, 14 or 30 days (`outcome-tracking.md` section 4) | conversation records, human-channel records | negative: the issue was not really resolved |
| Time to resolution (brief) | first customer message to resolution; A8.3 Average Handle Time target below 8 minutes | timestamps | long for the intent's norm: negative |
| Turn count against the intent's norm | `turn_count` compared with the category's typical length (A1.2 gives legacy averages) | A10.1 | long: effort |
| Abandonment | customer stops replying while a question or an auth step is pending; session closes by timeout | state machine, `last_activity_at` | negative, weakly (people also get interrupted) |
| Repetition | the customer restates the same request; `clarification_attempts` at 2; agent repeats itself (A9.2 Robotic Loop) | state, turn log | negative |
| Human request | `human_request_count` above 0 | state | negative for containment, neutral for safety flows |
| Sentiment trajectory | `sentiment.slope` and the last-turn score (A8.1 Sentiment Trajectory Slope: positive or stable) | state `sentiment` | falling: negative |
| Closing tone | thanks with a positive emotion against thanks after resignation (`sentiment.md` section 3) | NLU emotions | resignation: negative |
| Channel switch | a call to the human line or a branch contact within 24 hours of an AI conversation on the same issue | cross-channel join | negative |
| Acceptance of the next step | the customer follows the self-service link or completes the secure step | secure widget events | positive |

Implicit signals are reported for 100% of conversations and are the denominators that make the explicit minority interpretable.

## 5. Dissatisfaction detection without explicit feedback

Most dissatisfied customers do not fill in a survey. `sentiment.md` section 5.5 already flags the pattern: a "thanks" after a falling trajectory with resignation is likely silent dissatisfaction.

### 5.1 Detector

Two stages (D-100):

1. **Rule score (transparent, always on).** One point each for: resignation emotion in the last 2 customer turns; negative `sentiment.slope` over the conversation with a last-turn score below 0; abandonment with a pending step; 2 or more clarification attempts on one ambiguity; the customer repeating the request 2 or more times; a negative check-in answer; conversation longer than twice the intent's norm; a gap statement or failed lookup as the final agent turn; repeat contact inside 7 days (added when it matures). A score of 3 or more flags the conversation (proposal).
2. **Predicted CSAT (pCSAT).** A small supervised model trained on conversations that did return a rating, with the implicit signals and conversation features as inputs and the 1-5 rating as the target, corrected for non-response with the weights of section 6. Output: predicted rating and the probability of a rating of 2 or less.

### 5.2 Allowed and forbidden uses

| Use | Allowed |
|---|---|
| Send the 30 highest-scoring conversations of each day to supervisor review (`supervisor-corrections.md` section 2.2) | yes |
| Trigger one in-conversation check-in when the rule score reaches 2 during the conversation | yes, within the limits of section 2 |
| Monitor predicted dissatisfaction per intent, language, channel and version as an early-warning panel | yes, labelled "predicted" |
| Use as a secondary, labelled metric in experiments | yes |
| Use as the primary metric of an experiment, or report it as CSAT | no: it is a model of the survey, and a candidate could improve the prediction without improving the experience |
| Change how an individual customer is treated later (priority, offers, routing) | no: A11.3 forbids differential treatment based on history |
| Use features about who the customer is (demographics, balance band, inferred sensitive attributes) | no: only what happened in the conversation (A11.3) |

Validation: pCSAT is checked monthly on fresh rated conversations (mean absolute error, calibration by decile, and the same per language), and against supervisor verdicts on the random review stream, which is the only label source unaffected by survey non-response. If calibration differs across languages by more than the agreed tolerance it is reported as a fairness finding, not silently corrected.

## 6. Feedback bias correction

### 6.1 The biases

| Bias | Mechanism | Correction |
|---|---|---|
| Non-response | customers whose issue was resolved answer more often than those who gave up, so the raw mean is too high | weighting (6.2) |
| Extremity | very happy and very angry customers answer more than the middle | weighting on outcome and sentiment strata reduces it; report the distribution, not only the mean |
| Channel and language | response rates differ by channel and language | strata include both |
| Survey timing | escalated conversations are surveyed later, after a human fixed the issue | separate AI-part and human-part questions (section 3.1) |
| Acquiescence and politeness | Indian-English politeness norms compress ratings upward (`sentiment.md` cultural notes) | none claimed; compare trends and arms, not absolute levels across groups |
| Differential response in an experiment | a candidate that changes who answers changes the raw mean without changing satisfaction | pre-registered check on response rates and weighted primary analysis (`ab-testing.md` section 9) |

### 6.2 Method (D-101)

1. **Strata.** Every closed conversation, rated or not, is assigned to a cell of: outcome class (three groups: resolved by AI; escalated or resolved by human; unresolved or dropped) x intent category (the ten A1.2 categories) x channel x language class. Cells with fewer than 30 ratings in the window are merged with their neighbour along language, then channel.
2. **Post-stratification weight.** A rating in cell h gets weight `w_h = N_h / n_h`, where `N_h` is the number of conversations in the cell and `n_h` the number of ratings. The weighted mean is `sum(N_h x mean_h) / sum(N_h)`.
3. **Response-propensity refinement.** Inside a cell, a logistic model of "answered the survey" on conversation features (turn count, last sentiment, check-in polarity, time of day) gives a propensity `p_i`; the weight is multiplied by `mean(p) / p_i` within the cell. This step is optional and is switched on only if it changes the weighted mean by more than its standard error.
4. **Weight cap.** Weights are capped at 25 (proposal). A cap trades variance for bias and is reported whenever it binds.
5. **Variance.** The weighted mean is reported with a standard error from the stratified formula, and with Kish's effective sample size `n_eff = (sum w)^2 / sum(w^2)`.
6. **Reporting.** Raw CSAT, weighted CSAT, response rate and `n_eff` are always shown together. The 4.5 target (A8.2) is tracked on the weighted figure; the raw figure is kept because A8.2 defines CSAT as the "average post-conversation rating".

### 6.3 Worked example (illustrative numbers, one day)

| Stratum | Conversations `N_h` | Response rate | Ratings `n_h` | Mean rating | Weight `N_h / n_h` | Share of ratings | Share of conversations |
|---|---|---|---|---|---|---|---|
| Resolved by AI | 12,600 | 18% | 2,268 | 4.4 | 5.56 | 81.3% | 70% |
| Escalated or resolved by human | 3,600 | 12% | 432 | 3.6 | 8.33 | 15.5% | 20% |
| Unresolved or dropped | 1,800 | 5% | 90 | 2.1 | 20.00 | 3.2% | 10% |
| Total | 18,000 | 15.5% | 2,790 | | | 100% | 100% |

- Raw mean: `(2,268 x 4.4 + 432 x 3.6 + 90 x 2.1) / 2,790 = 11,723.4 / 2,790 = 4.20`.
- Weighted mean: `0.70 x 4.4 + 0.20 x 3.6 + 0.10 x 2.1 = 3.08 + 0.72 + 0.21 = 4.01`.
- The raw figure overstates satisfaction by 0.19 points, because the unresolved tenth of conversations supplies only 3.2% of the ratings.
- Effective sample size: `18,000^2 / (2,268 x 5.56^2 + 432 x 8.33^2 + 90 x 20^2) = 324,000,000 / 136,000 = 2,382`, a design effect of 1.17: weighting costs about 15% of the precision.
- Effect of a tight cap: capping weights at 10 would give 4.11, removing only half of the correction. That is why the proposed cap is 25, above the largest weight here.

What weighting cannot fix: it assumes that, inside a cell, those who answered resemble those who did not. That is untestable from survey data alone. Two checks bound the error: the supervisor random stream gives an independent quality rate per cell, and a periodic follow-up of a small random sample of non-responders by a different channel (proposal, with consent) measures the gap directly.

## 7. Attribution of feedback to specific agent actions

A 1-5 rating belongs to a conversation; improvement needs to know which action earned it. Attribution is done at four levels of evidence, weakest to strongest (D-102).

| Level | Method | Output | Trust |
|---|---|---|---|
| 1. Comment aspects | the redacted free text is tagged with aspects (wrong answer, slow, repeated questions, could not reach a human, tone, auth friction, unclear next step) by a classifier and checked on a reviewed sample | aspect counts per intent and version | direct but sparse: few ratings carry a comment |
| 2. Turn-level signals | for each agent action, the change in customer sentiment over the next customer turn, and any check-in answer that follows it; aggregated per action type (template id, KB entry id, clarification, auth step-up, gap statement, refusal, escalation offer) | mean sentiment change per action type, with intervals and counts | observational; confounded by the customer's situation |
| 3. Conversation-level model | a regression of the weighted rating on the presence and count of action types, with intent, channel, language and outcome as controls; reported as adjusted differences, for example "conversations where the auth step-up came before the empathy line rate 0.3 lower, other things equal" | ranked list of action types associated with low ratings | observational; gives hypotheses, not causes |
| 4. Experiment | change the action in an A/B test and read the primary metrics (`ab-testing.md`) | a causal estimate | the only level allowed to justify a release |

Rules:

1. Levels 1 to 3 produce the DESIGN hypotheses of the improvement cycle (A8.4). Only level 4 can confirm one.
2. Attribution joins on ids: every rating carries `conversation_id`; every turn carries `turn_id`, `kb_entry_ids` with versions, the template id, `response_generation_method` and the version tuple (A10.2, A12.2 version control). Without those joins a rating cannot be attributed, so their completeness is a data quality gate (QG-01).
3. Credit is never assigned to a guardrail as "the guardrail lowered CSAT, relax it". A refusal that earns a low rating is first a wording and next-step question (layer 3, the safe-response template), and the finding goes to the template owner. Case SS-LRN-03 fixes this in the suite.
4. Attribution reports are aggregated: minimum 30 conversations per row, no per-customer or per-reviewer view.
5. Simpson's paradox check: any aggregate attribution finding is re-computed inside each intent category before it becomes a hypothesis, because the ten A1.2 categories start from very different levels (2.4 for complaints to 4.3 for card blocking).

## 8. From signal to change

| Signal pattern | Diagnosis route | Usual update class |
|---|---|---|
| Low weighted CSAT on one intent with high retrieval confidence and correct intent | answer content or clarity | U1 KB change request |
| Low ratings with comment aspect "repeated questions" | context carry-over or slot logic | policy flow fix; U5 only if the ranker is the cause |
| Falling sentiment after a refusal or auth step | empathy and next-step wording | U2 layer 3 |
| High silent-dissatisfaction rate after gap statements on one topic | missing knowledge | U1 new entry through the KB chain; no invented content |
| CSAT differs by language with equal resolution | language quality | U4 NLU data for that language; native review (D-22) |
| Low CSAT concentrated in one KB epoch or prompt version | regression | rollback candidate; incident if a hard-zero is involved |

## 9. Monitoring and alerts (proposals)

Rolling 1-hour CSAT (A8.5) is shown only when the hour holds at least 30 ratings; otherwise the panel shows the count and "insufficient sample". Alerts: weighted daily CSAT below its 28-day mean by more than 3 standard errors; response rate down by more than a quarter against the 28-day mean (a survey fault); predicted-dissatisfaction share above its baseline by 3 sigma for an intent; a gap of more than 0.3 between raw and weighted CSAT (non-response is growing).

## 10. Decisions and open items

D-99 (survey rules and the 15% response-rate assumption), D-100 (two-stage silent-dissatisfaction detector and its allowed uses), D-101 (post-stratification weighting with a cap), D-102 (four attribution levels; only experiments justify a release).

1. Survey wording and check-in templates are written on Day 13 with the template library.
2. The non-responder follow-up needs a consent basis and a channel decision from the CX Team and the Data Protection lead.
3. CES and NPS collection is specified with the metrics framework in `docs/metrics/` (Day 12).
