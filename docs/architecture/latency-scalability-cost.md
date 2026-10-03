# Latency, Scalability and Cost

Response-time tiers (D-07): < 3 s p95 per turn is the engineering budget, < 5 s the SLO, < 30 s the business ceiling for the first reply.

## 1. Per-turn latency budget (p95)

| Stage | Budget (ms) | Notes |
|---|---|---|
| Gateway & session | 50 | |
| Input Guard | 100 | Rules plus a small classifier, in parallel |
| NLU | 250 | Small encoder; LLM fallback only on low confidence |
| State update and policy | 50 | |
| Retrieval | 200 | embed 20 + ANN 30 + BM25 20 (parallel) + re-rank 80 + overhead 30 = about 160-180 |
| Tool calls | 400 | Run in parallel with retrieval where independent |
| Generation | 1,500 | Streamed: first token earlier, so perceived latency is lower. Template turns take < 50 |
| Output safety | 300 | |
| **Total** | **about 2,850** | Under 3 s; audit logging is async |

Levers if over budget: cache frequent FAQ answers, skip retrieval for pure-tool intents, run Input Guard and NLU in parallel, use template mode for factual turns, stream the reply.

## 2. Scalability

Assumptions: average 7 turns per interaction (the A1.2 table implies 3-11), a 3x peak-to-average ratio. 18,000 interactions/day is about 126,000 turns/day, averaging about 1.5 turns/s and peaking at about 5 turns/s. The brief requires >= 10,000 concurrent conversations, which is the real sizing driver (mostly idle sessions; state is small).

| Scale | Interactions/day | Turns/day | Peak turns/s | Architecture notes |
|---|---|---|---|---|
| 1x | 18,000 | 126,000 | ~5 | Stateless services behind a load balancer, 2+ replicas per service, managed hot store |
| 10x | 180,000 | 1.26M | ~50 | Horizontal autoscale; sharded session store; dedicated retrieval cluster; batched async logging |
| 100x | 1.8M | 12.6M | ~500 | Multi-region active-active in India; partitioned vector index; model tiering and heavier template/cache use; separate analytics plane |

Concurrency target (10,000 conversations) is met at 1x by session-store sizing (about 10-20 KB state each, so about 100-200 MB hot), not by compute. Uptime target >= 99.9%: multi-AZ, health-based failover, graceful degradation to templates.

## 3. Cost model (illustrative)

All unit prices below are **placeholder assumptions**, not quotes. Replace with real vendor pricing before use. Assumptions: about 3,000 input and 300 output tokens per LLM turn; illustrative blended price of 1 USD per million input tokens and 4 USD per million output tokens; 60% of turns use the LLM (the rest are template or cache hits).

| Item | 1x | 10x | 100x |
|---|---|---|---|
| LLM turns/month | ~2.3M | ~23M | ~230M |
| LLM cost/month (USD) | ~9.7k | ~97k | ~0.97M (before discounts; tiering/caching assumed to cut 30-50%) |
| Infra (compute, stores, search, logging; USD/month) | ~8k | ~45k | ~300k |
| Human supervisor review (50 reviews/supervisor/day) | 3-5 supervisors | 15-25 | 100+ (sampling rate falls; automated triage) |
| Cost per interaction (rough, USD, excl. human staff) | ~0.03 | ~0.03 | ~0.02 (with discounts) |

Context: the brief cites projected annual savings of INR 42 crore from replacing 60% of first-line support with AI; this model is offered to show unit economics are sensitive mainly to LLM token volume, which template and cache usage reduce.

## 4. Capacity guardrails

Autoscale on queue depth and p95 latency; shed load by degrading to template-only mode before refusing; alert at 70% of budget at each stage.
