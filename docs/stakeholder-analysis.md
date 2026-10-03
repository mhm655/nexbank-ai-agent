# Stakeholder Analysis: CEB vs Risk Committee

Source: brief sections A1.1 and A1.3. The architect reports to the CTO and works with Product Engineering (platform APIs), Risk & Compliance, and Customer Experience.

## Stakeholders

| Body | Members | Primary concerns |
|---|---|---|
| Customer Experience Board (CEB) | Head of Customer Experience, UX Research Lead, Brand Communications Director | Naturalness and empathy; first-contact resolution; fewer unnecessary escalations; "friendly, trustworthy, modern" brand voice; accessibility across literacy and language; proactive service |
| Risk Committee (RC) | Chief Risk Officer, Regulatory Compliance Manager, Information Security Officer | No incorrect financial advice; no unauthorised account changes, fund transfers or data disclosure; RBI digital lending, PCI DSS, KYC/AML; tamper-proof audit trail; fail-safe default to human escalation under low confidence; adversarial robustness |
| Product Engineering | Platform/API owners | Feasible integrations, latency, scalability |
| CTO (sponsor) | | Cost, delivery, 60% first-line replacement within 18 months |

## Tension map

| Topic | CEB wants | RC wants | Resolution in design |
|---|---|---|---|
| Escalation | Fewer escalations (containment >= 70%) | Escalate whenever confidence is low | Tiered thresholds (D-06); escalate on safety triggers always, resolve low-risk intents autonomously |
| Product recommendation | Proactive suggestions | No advice or unsolicited investment guidance | Information-only framing from the catalogue, with no suitability judgement; proactive hints limited to factual features |
| Verification | Low-friction, quick answers | Strong authentication, short timeouts | Auth tiers by intent risk; low-risk FAQs need no OTP (D-05) |
| Tone | Warm, conversational, LLM-generated | Deterministic, auditable wording | Hybrid generation: templates for safety-critical facts, LLM for empathy |
| Response commitments | Reassuring timelines | No unfulfillable promises | Commit only to system-of-record timelines (D-09) |
| Learning loop | Rapid improvement from CSAT | Immutable safety invariants | Layers 0-2 immutable; fixed 200-case safety suite; HITL gate; staged rollout |
| Language | Hindi/Hinglish and regional fluency | Verified compliance in every language | Safety checks run on the normalised intent plus the output in the user's language; native-speaker review |

## Resolution principle

1. Where the two conflict on a safety matter, **RC wins** (it is the Safety level, 180 points, and an AUTO-FAIL domain).
2. CEB goals are met by design inside the safe envelope rather than by relaxing guardrails.
3. Each documented trade-off cites the config parameter that governs it, so either body can audit and tune it through the change process.
