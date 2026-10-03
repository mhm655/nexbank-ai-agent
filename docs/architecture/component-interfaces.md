# Component Interface Contracts

Each contract lists input, output, errors and the p95 latency budget (sums to the per-turn budget in `latency-scalability-cost.md`). All messages carry `conversation_id`, `turn_index`, `trace_id`. Error behaviour always degrades toward safety (fail closed).

| # | Component | Input | Output | Errors and fallback | p95 SLA |
|---|---|---|---|---|---|
| 1 | Gateway & Session Manager | Raw channel message, channel metadata, auth token | Normalised `TurnRequest` (text, channel, session, auth_level, timestamp) | Rate limit exceeded: 429 with polite retry text. Session expired (> 5 min idle): downgrade to anonymous, keep context, require re-auth | 50 ms |
| 2 | Input Guard | `TurnRequest` | `GuardVerdict` {allow, block, sanitise, flags[], crisis} | Classifier timeout: fall back to rules only and tag the turn for review. Block: safe template reply | 100 ms |
| 3 | Language & NLU | Sanitised text, dialogue state summary | `NLUResult` {language, code_switch, intents[{label, conf}], entities[], sentiment, emotions[], multi_intent, out_of_scope} | Model failure: use the rule/regex tier plus LLM fallback; if still unavailable, treat as low confidence (clarify, then escalate) | 250 ms |
| 4 | Dialogue State Tracker | `NLUResult`, `GuardVerdict`, system events | Updated `DialogueState` (schema in `config/`) | Store unavailable: serve from replica; if both fail, restart with a re-greeting and flag for human takeover. State writes are versioned and idempotent | 20 ms |
| 5 | Dialogue Policy Engine | `DialogueState` | `PolicyDecision` {action, agent, tool_calls[], template_id?, reason_codes[]} | Learned ranker unavailable: rules-only policy. No rule matches: clarify, then escalate | 30 ms |
| 6 | Knowledge Retrieval | Rewritten query, auth_level, language, filters | `RetrievalResult` {passages[{id, version, score}], confidence, latency} | Confidence below threshold (0.65): "uncertain" flag; regulatory topic with low confidence: ESC-008. Index down: cached FAQ then escalate | 200 ms |
| 7 | Tool/Action Orchestrator | `ToolCall` {name, args, idempotency_key, auth_proof} | `ToolResult` {ok, data, error_code, source_ts} | Timeout (400 ms hard cap): one retry for reads, none for writes. Write failures are reported honestly with no promise of outcome. Unconfirmed protective actions are never executed | 400 ms |
| 8 | Escalation Router | `DialogueState`, trigger signals | `EscalationDecision` {trigger_id, priority, queue, handoff_package, sla} | Queue unavailable: next queue by priority, then callback scheduling. Handoff package missing fields: fill from state, flag incomplete | 50 ms |
| 9 | Response Generator | `PolicyDecision`, passages, tool data, persona, language | `DraftResponse` {text, mode (template|llm|hybrid), citations[]} | LLM timeout or error: use template. No template: clarification/escalation template | 1,500 ms (streamed) |
| 10 | Output Safety Layer | `DraftResponse`, state, sources | `SafetyVerdict` {pass, rewrite, block, checks[]} and the final text | Check timeout: block the LLM text, send the template version. Any "block": safe template, then clarify, then escalate | 300 ms |
| 11 | Audit & Telemetry Bus | Turn/conversation events, guard flags, versions | Immutable, encrypted log records; metric streams | Async with local buffer; when the bus is down, buffer to disk and alert. Never block the customer turn. Audit write failure on a high-risk action blocks that action | async |
| 12 | Continuous Learning Pipeline | Supervisor labels, CSAT, outcomes, logs | Candidate updates (KB edits, prompt layers 3-5, thresholds, model versions) with eval reports | Any gate failure: reject the candidate. Circuit breaker breach: auto-rollback and page the owner. Layers 0-2 and rule layer are read-only to this component | offline |

## Cross-cutting rules

- **Versioning:** every output records prompt_version, model_version and KB entry versions.
- **Idempotency:** write tools require an idempotency key; a retry never repeats a block or ticket.
- **Timeouts:** each hop has a hard timeout and a defined fallback; no unbounded waits.
- **PII:** components exchange tokens or masked values where possible; full card numbers, CVV, PIN and full Aadhaar never enter state or logs.
- **Auth:** the Policy Engine checks `auth_level` against the intent's required level before calling any agent; the Tool Orchestrator re-checks independently.
