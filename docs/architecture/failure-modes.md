# Failure Mode Analysis (FMEA)

Severity (S), Likelihood (L), Detectability (D) on 1-5; RPN = S x L x D. Principle: fail closed toward safety.

| # | Component | Failure mode | Effect | S | L | D | RPN | Detection | Fallback / mitigation |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Gateway | Session store outage | Lost auth/context | 4 | 2 | 1 | 8 | Health checks, error rate | Replica; else restart conversation and require re-auth |
| 2 | Gateway | Traffic spike or DoS | Slow replies, drops | 3 | 3 | 1 | 9 | Rate metrics | Rate limit, autoscale, queue with honest wait message |
| 3 | Input Guard | False negative (injection passes) | Policy bypass | 5 | 2 | 4 | 40 | Red-team suite, output checks, audit sampling | Defence in depth: immutable rules, Output Safety Layer, tool-level auth re-check |
| 4 | Input Guard | False positive | Frustrated legitimate user | 2 | 3 | 3 | 18 | FP rate metric (< 3%) | Soft-block with rephrase prompt; human review of samples |
| 5 | NLU | Misclassified intent | Wrong flow | 3 | 3 | 3 | 27 | Confidence, confusion matrix | Thresholds, clarification, confirm before side effects |
| 6 | NLU | Service down | No understanding | 4 | 2 | 1 | 8 | Health | Rule/regex tier, then low-confidence path to escalation |
| 7 | NLU | Entity extraction error (amount, card) | Wrong action | 5 | 2 | 3 | 30 | Validation rules, echo-back | Validators; explicit confirmation of exact values before execution |
| 8 | State Tracker | Corrupt or stale state | Wrong context | 4 | 2 | 3 | 24 | Versioned writes, checksum | Rebuild from history; else clarify; else escalate |
| 9 | Policy | Learned ranker misbehaves | Poor action choice | 3 | 2 | 3 | 18 | A/B and shadow metrics | Ranker restricted to safe candidates; rules-only fallback |
| 10 | Policy | Rule conflict | Deadlock or unsafe path | 4 | 1 | 4 | 16 | Rule tests, precedence order | Strict precedence; unresolved: escalate |
| 11 | Retrieval | Wrong or stale passage | Incorrect info | 5 | 3 | 3 | 45 | TTL, version checks, relevance score | Confidence threshold 0.65, TTL expiry, grounding check, template-first for facts |
| 12 | Retrieval | Latency > budget | Slow turn | 2 | 3 | 1 | 6 | p95 metric | FAQ cache, timeout, answer without KB or clarify |
| 13 | Tool Orchestrator | Banking API timeout | No data/action | 3 | 3 | 1 | 9 | Timeouts, error codes | Retry reads once; honest status; offer human |
| 14 | Tool Orchestrator | Duplicate action (retry) | Double block/ticket | 3 | 2 | 3 | 18 | Idempotency keys | Idempotent writes; no automatic write retry |
| 15 | Escalation Router | Queue unavailable | Customer stuck | 4 | 2 | 1 | 8 | Queue health | Next queue, callback scheduling, notify the customer |
| 16 | Escalation Router | Missed trigger | Unsafe or frustrated customer | 5 | 2 | 4 | 40 | Trigger audits, supervisor sampling | Proximity score as a backstop; periodic replay tests |
| 17 | Generator | LLM hallucination | False claim | 5 | 3 | 3 | 45 | Grounding check | Locked fact slots; Output Safety Layer; template fallback |
| 18 | Generator | LLM outage/latency | No reply | 3 | 2 | 1 | 6 | Timeout | Template replies; failover model |
| 19 | Output Safety | False negative | Unsafe text delivered | 5 | 2 | 4 | 40 | Eval sets, audit sampling | Multiple independent checks; fact-slot comparison |
| 20 | Output Safety | Over-blocking | Robotic replies | 2 | 3 | 2 | 12 | Block rate, CSAT | Tune thresholds via the change process; review samples |
| 21 | Audit Bus | Log loss | Compliance gap | 5 | 1 | 2 | 10 | Sequence gaps | Local buffering; block high-risk actions if audit write fails |
| 22 | Learning Pipeline | Bad update degrades safety | Regression | 5 | 2 | 2 | 20 | Safety suite, canary metrics | Safety suite 100% pass; staged rollout; circuit breaker auto-rollback |
| 23 | Learning Pipeline | Feedback poisoning | Skewed behaviour | 4 | 2 | 3 | 24 | Anomaly detection, supervisor audit | Reviewer diversity, outlier filters, HITL gate |
| 24 | Whole system | Regional/provider outage | Total outage | 5 | 1 | 1 | 5 | Synthetic probes | Multi-AZ, provider failover; static status message and human line |

Highest RPN items (11, 17, 3, 16, 19) drive the Day 9-11 guardrail and testing priorities.
