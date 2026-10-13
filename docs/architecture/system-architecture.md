# System Architecture

Design is LLM-provider-agnostic (A4). It specifies interfaces and behaviour, not vendors. See `diagrams/architecture.mmd` and `diagrams/agents-and-tools.mmd`.

## 1. Principles

1. **Safety is structural, not prompted.** Hard rules live in a deterministic Guardian that no LLM output or learning update can override.
2. **Fail closed.** If a check fails or confidence is low, degrade to safe template, then clarify, then human escalation.
3. **Least privilege.** Each agent only gets the tools it needs. No tool moves money, changes nominee or KYC, or closes accounts.
4. **Facts from systems of record.** Balances, rates, fees and timelines come from tools or the KB, never from model memory.
5. **Everything is auditable.** Each turn emits a structured event with versions of prompt, model and KB entries used.

## 2. Components (12; the brief requires at least 8)

| # | Component | Responsibility |
|---|---|---|
| 1 | Gateway & Session Manager | Channel adapters, rate limits, session lifecycle, 5-minute inactivity timeout, DoS defence |
| 2 | Input Guard | Prompt-injection and jailbreak detection, credential/PII capture blocking (full Aadhaar, CVV, PIN, OTP-sharing), crisis detection |
| 3 | Language & NLU Service | Language detection and code-switching, hierarchical intent, entities, sentiment/emotion |
| 4 | Dialogue State Tracker | Authoritative per-conversation state (`config/dialogue_state.schema.json`) |
| 5 | Dialogue Policy Engine | Hybrid decision logic: deterministic rules first, learned ranking second; owns the orchestrator role |
| 6 | Knowledge Retrieval | Hybrid dense+BM25 retrieval with re-ranking, auth-filtered |
| 7 | Tool/Action Orchestrator | Calls banking APIs (read-only plus protective actions with confirmation); idempotency and timeouts |
| 8 | Escalation Router | Evaluates triggers, picks queue and priority, builds the handoff package |
| 9 | Response Generator | Template, LLM or hybrid generation with persona and length calibration |
| 10 | Output Safety Layer | Accuracy, compliance, PII, grounding, tone, commitment and advice-boundary checks |
| 11 | Audit & Telemetry Bus | Encrypted conversation/turn logs, metrics, dashboards, regulatory reports |
| 12 | Continuous Learning Pipeline | Supervisor corrections, CSAT and outcomes, evaluation gates, staged rollout |

## 3. Agents and tool scope

The Dialogue Policy Engine acts as orchestrator and hands the turn to a specialised agent. The Guardian can veto any action or response and is not controllable by an LLM.

| Agent | Scope | Tools (least privilege) |
|---|---|---|
| Orchestrator / Policy | Selects next action; enforces auth gates and confirm-before-act | Sub-agents only |
| Account Agent | Balance, statements, masked profile (read-only) | `get_balance`, `get_statement`, `get_profile_masked` |
| Transaction Agent | Lookup, dispute intake | `get_txn`, `search_txn`, `create_dispute_ticket` |
| Card Agent | Card status, protective block, replacement | `get_card_status`, `block_card` (confirm), `request_replacement` (confirm) |
| Product Info Agent | Information only, no suitability advice | `kb_search`, `emi_calculator` (deterministic) |
| Complaint Agent | Grievance intake and tracking | `create_complaint`, `get_complaint_status`, `schedule_callback` |
| Security Agent | Fraud and phishing handling | `block_card`, `flag_fraud`, `send_credential_reset_link` |
| Escalation Agent | Handoff package, queue choice | `route_to_queue`, `summarise_conversation` |
| Guardian | Immutable input/output checks | Veto only |

**Hard rule:** no agent has a tool for fund transfers, nominee or KYC changes, or account closure. Those go to humans or the branch (decision D-08).

## 4. Request flow (one turn)

1. Channel adapter delivers the message to Gateway; session loaded or created, timeout checked (D-05).
2. Input Guard screens; a block short-circuits to a safe reply (and possibly an escalation).
3. NLU returns language, intent hypotheses with confidence, entities, sentiment.
4. State Tracker merges NLU output into state (slots, topic stack, sentiment trajectory, escalation proximity).
5. Policy Engine picks an action. Order of precedence: safety and auth rules, escalation triggers, deterministic flows, learned ranking.
6. If needed, Retrieval and/or Tool Orchestrator are called (auth filtering happens before retrieval).
7. Response Generator produces text; Output Safety Layer verifies it; on failure, fall back to a template, then clarify, then escalate.
8. Reply is sent; the Audit Bus records the turn asynchronously.

## 5. Safety architecture (defence in depth)

1. Immutable rule layer: regex, validators, allow/deny lists, auth matrix. Excluded from the learning pipeline.
2. Model-based classifiers: injection, jailbreak, social engineering, advice detection, crisis, toxicity.
3. Prompt layers 0-2 (identity, safety invariants, compliance) are immutable; user and RAG content are separated from instructions.
4. Output verification: numeric claims checked against KB or tool results, grounding check, PII masking, commitment detection, advice boundary.
5. Fail-closed degradation ladder (above).

## 6. Data and state

- Hot session state in a low-latency store; durable state and audit in encrypted storage in an India region.
- Simulated sources: customer profile, interaction history, transaction ledger, product catalogue, regulatory registry, agent performance.
- Full state schema: `config/dialogue_state.schema.json`. Behaviour: `dialogue-management.md`.

## 7. Reference stack (options, not commitments)

| Layer | Options |
|---|---|
| Orchestration | LangGraph or a custom state machine |
| LLM | Any, behind an abstraction interface; low temperature (0.3) for generation |
| NLU | Fine-tuned multilingual encoder (e.g. MuRIL, IndicBERT, XLM-R) with LLM fallback |
| Retrieval | Vector DB (Qdrant, pgvector, etc.) plus BM25 (OpenSearch) plus multilingual cross-encoder |
| State | Redis (hot), Postgres (durable) |
| Events | Kafka to encrypted object store/SIEM; AES-256 at rest, TLS 1.3 |
| Experiments | MLflow or equivalent; feature flags for traffic split |

## 8. Related documents

`component-interfaces.md` (contracts and message shapes), `dialogue-management.md`, `response-generation.md`, `multilingual.md`, `failure-modes.md`, `latency-scalability-cost.md`, `boss-trace.md`. Later documents that specify components in detail: `nlu-pipeline-overview.md` (Language & NLU), `docs/guardrails/` (Input Guard, Output Safety Layer), `docs/knowledge-base/retrieval-pipeline.md` (Knowledge Retrieval), `docs/escalation/` (Escalation Router), `docs/compliance/audit-logging.md` (Audit & Telemetry Bus), `docs/learning-pipeline/` (Continuous Learning Pipeline).
