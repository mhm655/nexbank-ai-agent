"""Validate config/escalation_rules.yaml, tests/escalation/*.yaml and the Day 12 docs against the rest of the repo.
Usage: python tests/escalation/validate_escalation.py   (needs PyYAML)
Exit code 0 = all checks pass. Light harness only: it checks structure and cross-references of the specification.
It does not run any agent and proves nothing about runtime behaviour.
"""
import collections
import glob
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _max_decision():
    """Highest D- row of docs/assumptions-and-decisions.md: upper bound for cited decision IDs."""
    ids = []
    with open(os.path.join(ROOT, "docs", "assumptions-and-decisions.md"), encoding="utf8") as fh:
        for line in fh:
            m = re.match(r"\|\s*D-(\d+)\s*\|", line)
            if m:
                ids.append(int(m.group(1)))
    return max(ids)


MAX_DECISION = _max_decision()


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf8") as fh:
        return yaml.safe_load(fh)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf8") as fh:
        return fh.read()


errors, warnings = [], []


def err(msg):
    errors.append(msg)


# ------------------------------------------------------------------ sources
RULES = load("config", "escalation_rules.yaml")
INTENTS = load("config", "intents.yaml")
GUARDS = load("config", "guardrails.yaml")
INTENT_IDS = {i["id"] for i in INTENTS["intents"]}
INTENT_TERTIARY = {i["id"]: set(i.get("tertiary") or []) for i in INTENTS["intents"]}
AUTH = set(INTENTS["auth_levels"])
GR_IDS = {g["id"] for g in GUARDS["guardrails"]}
KB = {}
for f in sorted(glob.glob(os.path.join(ROOT, "docs", "knowledge-base", "entries", "*.yaml"))):
    with open(f, encoding="utf8") as fh:
        for e in yaml.safe_load(fh)["entries"]:
            KB[e["id"]] = e
ESC_IDS = ["ESC-%03d" % n for n in range(1, 16)]
PERSONAS = {"Priya", "Rajesh", "Meera", "Arjun", "Sunita", "Vikram"}
ACTIONS = {"block", "redirect", "escalate", "mask", "allow"}
BEHAVIOUR = {"empathy_present", "no_hallucination", "no_repeated_reply", "human_offered", "serves_benign_remainder",
             "no_clarifying_question", "disclosures_present", "cooling_off_stated", "grievance_info_within_2_turns",
             "credential_change_instruction", "complaint_record_created", "same_treatment_across_pair"}
LANGS = {"en", "hi", "hinglish", "ta", "te", "bn", "mr", "gu"}

# A6 as transcribed from the brief PDF (pp.16-17): priority, target queue, SLA. Second witness beside KB-ESC-010.
BRIEF_A6 = {
    "ESC-001": ("P0", "Fraud Investigation", "<2 min"),
    "ESC-002": ("P1", "Senior Resolution Mgr", "<5 min"),
    "ESC-003": ("P2", "General Support", "<10 min"),
    "ESC-004": ("P1", "Customer Retention", "<5 min"),
    "ESC-005": ("P1", "Dispute Resolution", "<5 min"),
    "ESC-006": ("P2", "Next Available Agent", "<10 min"),
    "ESC-007": ("P1", "Relationship Manager", "<5 min"),
    "ESC-008": ("P1", "Compliance Helpdesk", "<10 min"),
    "ESC-009": ("P0", "Security Operations", "<2 min"),
    "ESC-010": ("P2", "Supervisor Review", "<15 min"),
    "ESC-011": ("P0", "Crisis Response", "IMMEDIATE"),
    "ESC-012": ("P0", "AML Compliance", "<2 min"),
    "ESC-013": ("P1", "Wealth Advisory", "<10 min"),
    "ESC-014": ("P2", "Technical Support", "<10 min"),
    "ESC-015": ("P1", "Enhanced Due Diligence", "<5 min"),
}


def norm_sla(s):
    s = str(s).strip()
    m = re.match(r"^(?:<|under)\s*(\d+)\s*min$", s)
    return ("min", int(m.group(1))) if m else ("raw", s.upper())


# ------------------------------------------------------------------ 1. triggers present, agree with the brief and KB-ESC-010
triggers = {t["id"]: t for t in RULES["triggers"]}
if list(triggers) != ESC_IDS:
    err("rules: trigger ids are %s, expected ESC-001..ESC-015 in order" % list(triggers))
kb010 = {t["id"]: t for t in KB["KB-ESC-010"]["structured_fields"]["triggers"]}
for k in ESC_IDS:
    t = triggers.get(k)
    if not t:
        err("rules: %s missing" % k)
        continue
    kb = kb010.get(k)
    if not kb:
        err("KB-ESC-010 has no row for %s" % k)
    else:
        for field, kbf in (("priority", "priority"), ("queue", "queue"), ("sla", "sla"), ("condition_text", "condition")):
            if str(t[field]) != str(kb[kbf]):
                err("%s: rules %s=%r differs from KB-ESC-010 %r" % (k, field, t[field], kb[kbf]))
    bp, bq, bs = BRIEF_A6[k]
    b = t.get("brief") or {}
    if (b.get("priority"), b.get("queue"), b.get("sla")) != (bp, bq, bs):
        err("%s: brief block %r differs from the A6 transcription %r" % (k, b, BRIEF_A6[k]))
    if t["priority"] != bp or t["queue"] != bq or norm_sla(t["sla"]) != norm_sla(bs):
        err("%s: priority, queue or sla differs from A6" % k)
    if kb and (kb["priority"] != bp or kb["queue"] != bq or norm_sla(kb["sla"]) != norm_sla(bs)):
        err("KB-ESC-010 %s differs from A6 (report to the coordinator; do not edit here)" % k)
    kind, val = norm_sla(t["sla"])
    if kind == "min" and t.get("sla_seconds") != val * 60:
        err("%s: sla_seconds %r does not equal %d" % (k, t.get("sla_seconds"), val * 60))
    if kind == "raw" and t.get("sla_seconds") is not None:
        err("%s: IMMEDIATE must have sla_seconds null" % k)
    if t.get("origin") != "brief":
        err("%s: origin must be brief" % k)
    if t["priority"] == "P0" and t.get("cancellable") != "never":
        err("%s: a P0 trigger must have cancellable: never" % k)
    if t.get("cancellable") not in ("never", "customer_only", "customer_or_recovery"):
        err("%s: bad cancellable value" % k)
    if t.get("handoff_mode") not in ("warm", "discreet", "silent_case"):
        err("%s: bad handoff_mode" % k)
    for req in ("fire_when", "sub_rules", "precedence_rank", "state_fields", "intents", "guardrails", "kb_entries",
                "tests", "owner_component", "detectors", "intent_scope"):
        if req not in t:
            err("%s: missing field %s" % (k, req))

# ------------------------------------------------------------------ 2. links agree with intents.yaml, guardrails.yaml and the KB
by_intent, by_guard, by_kb = (collections.defaultdict(set) for _ in range(3))
for i in INTENTS["intents"]:
    for e in i.get("escalation") or []:
        if e not in triggers:
            err("config/intents.yaml %s links %s, which is not a defined trigger" % (i["id"], e))
        by_intent[e].add(i["id"])
for g in GUARDS["guardrails"]:
    for e in g.get("escalation") or []:
        if e not in triggers:
            err("config/guardrails.yaml %s escalation %s is not a defined trigger" % (g["id"], e))
        by_guard[e].add(g["id"])
for kid, e in KB.items():
    for x in e.get("escalation_triggers") or []:
        if x not in triggers:
            err("KB %s escalation_triggers %s is not a defined trigger" % (kid, x))
        by_kb[x].add(kid)
components = set(GUARDS["components"])
for k, t in triggers.items():
    if set(t["intents"]) != by_intent[k]:
        err("%s: rules intents %s != intents.yaml links %s" % (k, sorted(t["intents"]), sorted(by_intent[k])))
    if set(t["guardrails"]) != by_guard[k]:
        err("%s: rules guardrails %s != guardrails.yaml links %s" % (k, sorted(t["guardrails"]), sorted(by_guard[k])))
    if set(t["kb_entries"]) != by_kb[k]:
        err("%s: rules kb_entries %s != KB escalation_triggers %s" % (k, sorted(t["kb_entries"]), sorted(by_kb[k])))
    for c in [t["owner_component"]] + list(t["detectors"]):
        if c not in components:
            err("%s: component %s is not in config/guardrails.yaml components" % (k, c))

extras = {x["id"]: x for x in RULES.get("extra_rules") or []}
queue_names = [q["name"] for q in RULES["queues"]]
for xid, x in extras.items():
    if not re.match(r"^XTR-\d{2}$", xid) or x.get("origin") != "addition":
        err("%s: extra rules need an XTR-nn id and origin: addition" % xid)
    for i in x.get("intents") or []:
        if i not in INTENT_IDS:
            err("%s: unknown intent %s" % (xid, i))
    for g in x.get("guardrails") or []:
        if g not in GR_IDS:
            err("%s: unknown guardrail %s" % (xid, g))
    for kb in x.get("kb_entries") or []:
        if kb not in KB:
            err("%s: unknown KB entry %s" % (xid, kb))
    if x.get("raises"):
        if x["raises"] not in triggers:
            err("%s: raises unknown trigger %s" % (xid, x["raises"]))
        if x.get("route"):
            err("%s: a rule that raises a brief trigger must not define its own route" % xid)
    else:
        r = x.get("route") or {}
        if r.get("queue") not in queue_names:
            err("%s: route queue %r is not one of the brief's queues" % (xid, r.get("queue")))
        else:
            own = next(t for t in triggers.values() if t["queue"] == r["queue"])
            if r.get("sla") != "referral" and (r.get("sla") != own["sla"] or r.get("priority") != own["priority"]):
                err("%s: route must use the queue's own priority and SLA (%s, %s)" % (xid, own["priority"], own["sla"]))
    if x.get("cancellable") not in ("never", "customer_only", "customer_or_recovery"):
        err("%s: bad cancellable value" % xid)

# ------------------------------------------------------------------ 3. queues and precedence
if sorted(queue_names) != sorted(t["queue"] for t in triggers.values()) or len(set(queue_names)) != 15:
    err("queues: must be exactly the 15 A6 target queues")
for q in RULES["queues"]:
    own = triggers.get(q["trigger"])
    if not own or own["queue"] != q["name"]:
        err("queue %s: trigger %s does not target it" % (q["name"], q["trigger"]))
    for o in q["overflow"]:
        if o != "callback" and o not in queue_names:
            err("queue %s: overflow target %s is not a brief queue" % (q["name"], o))
        if o == q["name"]:
            err("queue %s overflows to itself" % q["name"])
    if q["hours"] not in RULES["queue_hours"]:
        err("queue %s: unknown hours %s" % (q["name"], q["hours"]))
    if own and own["priority"] == "P0" and q["hours"] != "24x7":
        err("queue %s: a P0 queue must be 24x7" % q["name"])

ranks = sorted((t["precedence_rank"], k) for k, t in triggers.items())
if [r for r, _ in ranks] != list(range(1, 16)):
    err("precedence_rank must be 1..15 with no duplicates")
if [k for _, k in ranks] != RULES["precedence"]["ranked"]:
    err("precedence.ranked does not match the precedence_rank values")
PRANK = {"P0": 0, "P1": 1, "P2": 2}


def sla_key(t):
    kind, val = norm_sla(t["sla"])
    return 0 if kind == "raw" else val


prev = None
for _, k in ranks:
    cur = (PRANK[triggers[k]["priority"]], sla_key(triggers[k]))
    if prev and cur < prev:
        err("precedence: %s breaks the order priority first, then shorter SLA" % k)
    prev = cur

# ------------------------------------------------------------------ 4. expressions use defined signals only
signals = set(RULES["signals"])
ns = {"const": set(RULES["constants"]), "prop": set(RULES["proposals"]), "param": set(RULES["parameters_ref"])}
KEYWORDS = {"in"}


def check_expr(owner, expr):
    stripped = re.sub(r"'[^']*'", "", expr)
    for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", stripped):
        if tok in KEYWORDS:
            continue
        if "." in tok:
            space, name = tok.split(".", 1)
            if space not in ns or name not in ns[space]:
                err("%s: expression uses undefined name %s" % (owner, tok))
        elif tok not in signals:
            err("%s: expression uses undefined signal %s" % (owner, tok))


sub_rule_ids = set()
for k, t in triggers.items():
    check_expr(k, t["fire_when"])
    for s in t["sub_rules"]:
        if not s["id"].startswith(k + "."):
            err("%s: sub-rule id %s must start with the trigger id" % (k, s["id"]))
        sub_rule_ids.add(s["id"])
for xid, x in extras.items():
    check_expr(xid, x["fire_when"])
for name, sig in RULES["signals"].items():
    if "in_schema" not in sig or "source" not in sig:
        err("signal %s needs source and in_schema" % name)

# ------------------------------------------------------------------ 5. handoff package equals KB-ESC-001 (D-04)
kb_elems = KB["KB-ESC-001"]["structured_fields"]["elements"]
rule_elems = [e["name"] for e in RULES["handoff_package"]["elements"]]
if rule_elems != kb_elems or len(rule_elems) != 8:
    err("handoff package elements %s differ from KB-ESC-001 %s" % (rule_elems, kb_elems))

# ------------------------------------------------------------------ 6. test cases
TEST_DIR = os.path.join(ROOT, "tests", "escalation")
cases, per_trigger = [], collections.defaultdict(lambda: collections.Counter())
seen = set()
files = sorted(glob.glob(os.path.join(TEST_DIR, "*.yaml")))
for f in files:
    name = os.path.basename(f)
    with open(f, encoding="utf8") as fh:
        raw = fh.read()
    try:
        raw.encode("ascii")
    except UnicodeEncodeError:
        err("%s: non-ASCII character" % name)
    doc = yaml.safe_load(raw)
    cs = doc.get("cases") or []
    if doc.get("case_count") != len(cs):
        err("%s: case_count %r but %d cases" % (name, doc.get("case_count"), len(cs)))
    for c in cs:
        c["_file"] = name
        cases.append(c)

REQUIRED = ["id", "category", "vector", "persona", "input_turns", "preconditions", "expected_action",
            "expected_guardrails", "must_not_contain", "severity"]
for c in cases:
    cid = c.get("id", "?")
    if cid in seen:
        err("duplicate case id %s" % cid)
    seen.add(cid)
    boss = c["_file"] == "boss-level6.yaml"
    for r in REQUIRED:
        if r not in c:
            err("%s: missing %s" % (cid, r))
    if c.get("category") != "escalation":
        err("%s: category must be escalation" % cid)
    if c.get("persona") not in PERSONAS:
        err("%s: persona %r is not an A13.2 persona" % (cid, c.get("persona")))
    if (c.get("preconditions") or {}).get("auth_level") not in AUTH:
        err("%s: bad auth_level" % cid)
    if c.get("expected_action") not in ACTIONS:
        err("%s: bad expected_action %r" % (cid, c.get("expected_action")))
    if c.get("severity") not in ("CRITICAL", "HIGH", "MEDIUM"):
        err("%s: bad severity" % cid)
    if c.get("language", "en") not in LANGS:
        err("%s: bad language" % cid)
    if not isinstance(c.get("input_turns"), list) or not c["input_turns"]:
        err("%s: input_turns must be a non-empty list" % cid)
    for g in c.get("expected_guardrails") or []:
        if g not in GR_IDS:
            err("%s: unknown guardrail %s" % (cid, g))
    for b in c.get("behaviour_checks") or []:
        if b not in BEHAVIOUR:
            err("%s: unknown behaviour check %s" % (cid, b))
    for e in (c.get("expected_escalation") or []) + (c.get("must_not_escalate") or []) + (c.get("expected_secondary") or []):
        if e not in triggers:
            err("%s: unknown ESC id %s" % (cid, e))
    if set(c.get("expected_escalation") or []) & set(c.get("must_not_escalate") or []):
        err("%s: a trigger is both expected and forbidden" % cid)
    for x in c.get("expected_extra_rules") or []:
        if x not in extras:
            err("%s: unknown extra rule %s" % (cid, x))
    if c.get("expected_rule") and c["expected_rule"] not in sub_rule_ids:
        err("%s: expected_rule %s is not a sub-rule in the rules file" % (cid, c["expected_rule"]))
    for tr in ((c.get("fixture") or {}).get("nlu_trace") or []):
        if tr.get("intent") not in INTENT_IDS:
            err("%s: nlu_trace intent %r unknown" % (cid, tr.get("intent")))
        elif tr.get("tertiary") and tr["tertiary"] not in INTENT_TERTIARY[tr["intent"]]:
            err("%s: tertiary %s is not defined for %s" % (cid, tr["tertiary"], tr["intent"]))
        for alt in (tr.get("alternatives") or {}):
            if alt not in INTENT_IDS:
                err("%s: nlu_trace alternative %r unknown" % (cid, alt))
    trace = (c.get("fixture") or {}).get("nlu_trace")
    if trace and len(trace) != len(c["input_turns"]):
        err("%s: nlu_trace has %d entries for %d turns" % (cid, len(trace), len(c["input_turns"])))
    blob = yaml.safe_dump(c)
    if re.search(r"\d{9,}", blob) or re.search(r"\b\d{4}[ -]\d{4}[ -]\d{4}\b", blob):
        err("%s: sensitive-looking digit run" % cid)
    for ref in re.findall(r"\b(?:GR-[A-Z]{3}-R?\d+|KB-[A-Z]{3}-\d{3}|ESC-0\d\d|XTR-\d\d)\b(?!-)", str(c.get("notes", "")) + str(c.get("reasoning", ""))):
        if ref not in GR_IDS and ref not in KB and ref not in triggers and ref not in extras:
            err("%s: note mentions unknown id %s" % (cid, ref))

    if boss:
        if not re.match(r"^ESC-BOSS-L6-\d{2}$", cid):
            err("%s: boss ids are ESC-BOSS-L6-nn" % cid)
        for r in ("ambiguity", "reasoning", "expected_owner", "expected_secondary", "expected_priority", "expected_queue"):
            if r not in c:
                err("%s: boss case missing %s" % (cid, r))
        owner = c.get("expected_owner")
        if owner:
            t = triggers.get(owner)
            if not t:
                err("%s: unknown owner %s" % (cid, owner))
            else:
                if (c.get("expected_priority"), c.get("expected_queue"), c.get("expected_sla")) != (t["priority"], t["queue"], t["sla"]):
                    err("%s: priority, queue or SLA does not match the owner %s" % (cid, owner))
                if c.get("expected_escalation") != [owner]:
                    err("%s: expected_escalation must be the owner" % cid)
                for s in c.get("expected_secondary") or []:
                    if triggers[s]["precedence_rank"] < t["precedence_rank"]:
                        err("%s: secondary %s outranks the owner %s" % (cid, s, owner))
                if c.get("expected_handoff_mode") not in ("warm", "discreet", "silent_case"):
                    err("%s: boss case needs expected_handoff_mode" % cid)
        elif c.get("expected_escalation") or c.get("expected_queue") or c.get("expected_priority"):
            err("%s: no owner but an escalation is expected" % cid)
        continue

    trig = c.get("trigger")
    exp = c.get("expect")
    if exp not in ("fire", "no_fire"):
        err("%s: expect must be fire or no_fire" % cid)
    if trig in triggers:
        m = re.match(r"^ESC-T-(\d{3})-(\d{2})$", cid)
        if not m or "ESC-" + m.group(1) != trig:
            err("%s: id must be ESC-T-<nnn>-<nn> matching trigger %s" % (cid, trig))
        per_trigger[trig][exp] += 1
        t = triggers[trig]
        if exp == "fire":
            if trig not in (c.get("expected_escalation") or []):
                err("%s: fire case must expect %s" % (cid, trig))
            if (c.get("expected_priority"), c.get("expected_queue"), c.get("expected_sla")) != (t["priority"], t["queue"], t["sla"]):
                err("%s: expected priority, queue or SLA differs from the rules file" % cid)
            if not c.get("expected_rule", "").startswith(trig + "."):
                err("%s: fire case needs an expected_rule of %s" % (cid, trig))
        else:
            if trig in (c.get("expected_escalation") or []):
                err("%s: near-miss must not expect %s" % (cid, trig))
            if trig not in (c.get("must_not_escalate") or []):
                err("%s: near-miss must list %s in must_not_escalate" % (cid, trig))
        if cid not in t["tests"]:
            err("%s: not listed under tests of %s in the rules file" % (cid, trig))
    elif trig in extras:
        m = re.match(r"^XTR-T-(\d{2})-(\d{2})$", cid)
        if not m or "XTR-" + m.group(1) != trig:
            err("%s: id must be XTR-T-<nn>-<nn> matching %s" % (cid, trig))
        per_trigger[trig][exp] += 1
        x = extras[trig]
        if exp == "fire":
            if trig not in (c.get("expected_extra_rules") or []):
                err("%s: fire case must list %s in expected_extra_rules" % (cid, trig))
            if x.get("raises"):
                t = triggers[x["raises"]]
                want = (t["priority"], t["queue"], t["sla"])
                if x["raises"] not in (c.get("expected_escalation") or []):
                    err("%s: must expect the raised trigger %s" % (cid, x["raises"]))
            else:
                want = (x["route"]["priority"], x["route"]["queue"], x["route"]["sla"])
            if (c.get("expected_priority"), c.get("expected_queue"), c.get("expected_sla")) != want:
                err("%s: expected priority, queue or SLA differs from the rules file %r" % (cid, want))
        elif trig in (c.get("expected_extra_rules") or []):
            err("%s: near-miss must not expect %s" % (cid, trig))
        if cid not in x["tests"]:
            err("%s: not listed under tests of %s in the rules file" % (cid, trig))
    else:
        err("%s: trigger %r is neither a brief trigger nor an extra rule" % (cid, trig))

for k in ESC_IDS:
    n = per_trigger[k]
    if n["fire"] < 1 or n["no_fire"] < 1:
        err("%s: needs at least one fire and one near-miss case (has %d and %d)" % (k, n["fire"], n["no_fire"]))
    for tid in triggers[k]["tests"]:
        if tid not in seen:
            err("%s: rules file lists test %s, which is not written" % (k, tid))
for xid, x in extras.items():
    if per_trigger[xid]["fire"] < 1:
        err("%s: needs at least one fire case" % xid)
    for tid in x["tests"]:
        if tid not in seen:
            err("%s: rules file lists test %s, which is not written" % (xid, tid))
boss_cases = [c for c in cases if c["_file"] == "boss-level6.yaml"]
if len(boss_cases) != 10:
    err("boss set must have exactly 10 cases, has %d" % len(boss_cases))
esc_cases = [c for c in cases if str(c.get("id", "")).startswith("ESC-T-")]
if len(esc_cases) < 30:
    err("need at least 30 ESC-T cases, have %d" % len(esc_cases))

# ------------------------------------------------------------------ 7. documents and diagram: every ID mentioned exists
DOCS = [("docs", "escalation", "triggers.md"), ("docs", "escalation", "routing-and-handoff.md"),
        ("docs", "escalation", "queue-management.md"), ("docs", "metrics", "kpi-framework.md"),
        ("docs", "metrics", "improvement-cycle.md"), ("docs", "metrics", "dashboards.md"),
        ("tests", "escalation", "README.md"), ("diagrams", "escalation-routing.mmd"),
        ("config", "escalation_rules.yaml")]
DM_IDS = {"DM-%02d" % n for n in range(1, 17)}
kpi_ids = set()
kpi_path = os.path.join(ROOT, "docs", "metrics", "kpi-framework.md")
if os.path.exists(kpi_path):
    kpi_ids = set(re.findall(r"^\| (KPI-[A-Z]\d+|EQ-\d\d) \|", read("docs", "metrics", "kpi-framework.md"), re.M))
    eq_path = os.path.join(ROOT, "docs", "escalation", "queue-management.md")
    if os.path.exists(eq_path):
        kpi_ids |= set(re.findall(r"^\| (EQ-\d\d) \|", read("docs", "escalation", "queue-management.md"), re.M))
doc_count = 0
for parts in DOCS:
    path = os.path.join(ROOT, *parts)
    label = "/".join(parts)
    if not os.path.exists(path):
        err("missing deliverable %s" % label)
        continue
    doc_count += 1
    text = read(*parts)
    try:
        text.encode("ascii")
    except UnicodeEncodeError as ex:
        err("%s: non-ASCII character at offset %d" % (label, ex.start))
    for ref in set(re.findall(r"(?<!KB-)\bESC-\d{3}\b", text)):
        if ref not in triggers:
            err("%s: unknown trigger %s" % (label, ref))
    for ref in set(re.findall(r"\bXTR-\d{2}\b", text)):
        if ref not in extras:
            err("%s: unknown extra rule %s" % (label, ref))
    for ref in set(re.findall(r"\bGR-[A-Z]{3}-R?\d{1,2}\b", text)):
        if ref not in GR_IDS:
            err("%s: unknown guardrail %s" % (label, ref))
    for ref in set(re.findall(r"\bKB-[A-Z]{3}-\d{3}\b", text)):
        if ref not in KB:
            err("%s: unknown KB entry %s" % (label, ref))
    for ref in set(re.findall(r"\b(?:ACC|TXN|CRD|PRD|CMP|SEC|GEN)-\d{3}\b", text)):
        if ref not in INTENT_IDS:
            err("%s: unknown intent %s" % (label, ref))
    for ref in set(re.findall(r"\bDM-\d{2}\b", text)):
        if ref not in DM_IDS:
            err("%s: unknown dashboard metric %s" % (label, ref))
    for ref in set(re.findall(r"\bD-(\d{1,3})\b", text)):
        if not 1 <= int(ref) <= MAX_DECISION:
            err("%s: decision D-%s is outside D-01..D-%d" % (label, ref, MAX_DECISION))
    for ref in set(re.findall(r"\b(?:ESC-T-\d{3}-\d{2}|XTR-T-\d{2}-\d{2}|ESC-BOSS-L6-\d{2})\b", text)):
        if ref not in seen:
            err("%s: unknown test id %s" % (label, ref))
    if kpi_ids:
        for ref in set(re.findall(r"\b(?:KPI-[A-Z]\d+|EQ-\d\d)\b", text)):
            if ref not in kpi_ids:
                err("%s: unknown KPI id %s" % (label, ref))
    planning_word = "PL" + "AN"   # the planning file lives outside the repository and is never cited
    if re.search(r"\b" + planning_word + r"(\.md| \d)", text):
        err("%s: must not reference the planning file" % label)
    if parts[-1] in ("triggers.md", "escalation-routing.mmd"):
        for k in ESC_IDS:
            if k not in text:
                err("%s: does not mention %s" % (label, k))

# ------------------------------------------------------------------ 8. A6 constants, comparison operators, overflow floor
A6_CONSTANTS = {"esc003_confidence_floor": 0.40, "esc003_consecutive_turns": 3, "esc004_consecutive_turns": 2,
                "esc005_dispute_amount_inr": 50000, "esc006_human_requests": 3, "esc007_high_value_inr": 500000,
                "esc010_turns": 15}
for name, val in A6_CONSTANTS.items():
    if RULES["constants"].get(name) != val:
        err("constants: %s is %r, A6 says %r" % (name, RULES["constants"].get(name), val))
if set(RULES["constants"]) != set(A6_CONSTANTS):
    err("constants: keys differ from the A6 set")
# The comparison each brief trigger must use (strict or not, as A6 writes it). A fragment must appear verbatim.
OPERATORS = {
    "ESC-003": "low_conf_streak >= const.esc003_consecutive_turns",
    "ESC-004": "neg_sentiment_streak >= const.esc004_consecutive_turns",
    "ESC-005": "dispute_amount_inr > const.esc005_dispute_amount_inr",
    "ESC-006": "human_requests >= const.esc006_human_requests",
    "ESC-007": "closure_requested && high_value",
    "ESC-010": "turns_since_resolution > const.esc010_turns",
    "ESC-015": "customer_identified && pep_flag",
}
for k, frag in OPERATORS.items():
    fw = " ".join(triggers[k]["fire_when"].split())
    if frag not in fw:
        err("%s: fire_when must contain %r (A6 comparison)" % (k, frag))
    if frag not in " ".join(str(triggers[k]["sub_rules"][0]["when"]).split()):
        err("%s: first sub-rule must contain %r" % (k, frag))
if triggers["ESC-015"]["fire_when"].strip() != "customer_identified && pep_flag":
    err("ESC-015: fire_when must be the literal status condition (D-164)")
xtr06 = extras.get("XTR-06", {}).get("fire_when", "")
if "turn_count > const.esc010_turns" not in xtr06:
    err("XTR-06: must not raise ESC-010 at or below 15 turns")
for q in RULES["queues"]:
    own = triggers.get(q["trigger"])
    if own and own["priority"] == "P0":
        humans = [o for o in q["overflow"] if o != "callback"]
        if not humans or q["overflow"][0] == "callback":
            err("queue %s: a P0 queue needs a human queue before callback in its overflow chain" % q["name"])
        if q["mode"] == "live" and len(humans) < 2:
            err("queue %s: a live P0 queue needs at least two human overflow queues" % q["name"])
        if q["mode"] == "live" and humans and next(t for t in triggers.values() if t["queue"] == humans[0])["priority"] != "P0":
            err("queue %s: the first overflow of a live P0 queue must be a P0 queue" % q["name"])

# ------------------------------------------------------------------ 9. tables in the documents against the rules file and the brief
trig_doc = os.path.join(ROOT, "docs", "escalation", "triggers.md")
if os.path.exists(trig_doc):
    rows = re.findall(r'^\| (ESC-\d{3}) \| "([^"]*)" \| (P\d) \| ([^|]+?) \| ([^|]+?) \| (\d+) \|$', read("docs", "escalation", "triggers.md"), re.M)
    if [r[0] for r in rows] != ESC_IDS:
        err("triggers.md: the A6 table must have one quoted row per trigger, in order")
    for tid, cond, pri, queue, sla, page in rows:
        if (pri, queue, sla) != BRIEF_A6.get(tid):
            err("triggers.md: A6 table row %s (%s, %s, %s) differs from the brief" % (tid, pri, queue, sla))
        if tid in triggers and cond != triggers[tid]["brief"]["condition"]:
            err("triggers.md: A6 table condition for %s differs from the rules file brief block" % tid)
qm_doc = os.path.join(ROOT, "docs", "escalation", "queue-management.md")
if os.path.exists(qm_doc):
    qrows = re.findall(r"^\| ([A-Za-z ]+?) \| (ESC-\d{3}) \| (P\d) \| ([^|]+?) \| [^|]+ \| (24x7|extended) \|", read("docs", "escalation", "queue-management.md"), re.M)
    seen_q = {}
    for name, tid, pri, sla, hrs in qrows:
        seen_q[name] = (tid, pri, sla, hrs)
    for q in RULES["queues"]:
        got = seen_q.get(q["name"])
        want = (q["trigger"],) + BRIEF_A6[q["trigger"]][0:1] + (BRIEF_A6[q["trigger"]][2], q["hours"])
        if got != want:
            err("queue-management.md: queue table row for %s is %r, expected %r" % (q["name"], got, want))
# A8 and A1.4 as transcribed from the brief PDF (pp.5, 19-21): target and frequency per metric.
BRIEF_A8 = {
    "First Response Time": ("<5 seconds", "Real-time"), "Intent Recognition Accuracy": (">92%", "Daily"),
    "Entity Extraction Accuracy": (">95%", "Daily"), "Sentiment Trajectory Slope": ("Positive or stable", "Daily"),
    "Knowledge Retrieval Relevance": (">0.85", "Daily"), "Guardrail False Positive Rate": ("<3%", "Daily"),
    "Agent Confidence Distribution": (">80% above 0.7", "Weekly"), "CSAT Score": ("at least 4.5 (1-5 scale)", "Weekly"),
    "Net Promoter Score": ("at least 50", "Monthly"), "First Contact Resolution": ("at least 70%", "Weekly"),
    "Containment Rate": ("at least 70%", "Weekly"), "Customer Effort Score": ("at least 5.5 (1-7 scale)", "Monthly"),
    "Incorrect Advice Rate": ("0%", "Daily"), "Customer Retention Impact": ("Positive", "Quarterly"),
    "Average Handle Time": ("<8 minutes", "Daily"), "Escalation Rate": ("<30%", "Daily"),
    "System Uptime": ("at least 99.9%", "Real-time"), "Concurrent Capacity": ("at least 10,000", "Weekly load test"),
    "Knowledge Base Coverage": ("at least 90%", "Monthly"), "Model Drift Score": ("<0.05", "Weekly"),
    "First reply (business ceiling)": ("<30 seconds", "not stated"),
    "KB retrieval latency, 95th percentile": ("maximum 200 ms", "not stated"),
}
if os.path.exists(kpi_path):
    ktext = read("docs", "metrics", "kpi-framework.md")
    sec2 = ktext[ktext.index("## 2. Brief targets at a glance"):ktext.index("## 3. Leading indicators")]
    krows = {m[0]: (m[1], m[2]) for m in re.findall(r"^\| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| [^|]+ \| [^|]+ \|$", sec2, re.M)}
    for metric, want in BRIEF_A8.items():
        if krows.get(metric) != want:
            err("kpi-framework.md section 2: %s is %r, the brief says %r" % (metric, krows.get(metric), want))
    if 'fully resolved by AI without human intervention' not in ktext:
        err("kpi-framework.md: the glossary definition of containment (p.68) must be quoted")

# ------------------------------------------------------------------ 10. oracles computed from injected values
THR = -0.70          # A6 value of escalation_sentiment_threshold; strict less-than
SECONDARY_LANGS = {"ta", "te", "bn", "mr", "gu"}


def computed_expectation(c):
    """Return True/False when the case's fixture fully determines the rule, else None."""
    fx = c.get("fixture") or {}
    trace = fx.get("nlu_trace") or []
    st = fx.get("state") or {}
    trig = c.get("trigger")
    if trig == "ESC-003" and trace and all("confidence" in t for t in trace):
        streak = best = 0
        for t in trace:
            streak = streak + 1 if t["confidence"] < 0.40 else 0
            best = max(best, streak)
        return best >= 3
    if trig == "ESC-004" and trace and all("sentiment" in t for t in trace):
        streak = best = 0
        for t in trace:
            if t.get("sentiment_confidence", 1.0) < 0.70:
                continue                      # uncertain: neither adds nor resets
            streak = streak + 1 if t["sentiment"] < THR else 0
            best = max(best, streak)
        fire = best >= 2
        if c.get("language") in SECONDARY_LANGS:
            raw = [t["sentiment"] for t in trace]
            run = rb = 0
            for s in raw:
                run = run + 1 if s < THR else 0
                rb = max(rb, run)
            m = raw[0]
            for s in raw[1:]:
                m = 0.5 * s + 0.5 * m
            fire = fire or (rb >= 2 and m < THR)
        return fire
    if trig == "ESC-005":
        amt = ((st.get("slots") or {}).get("amount") or {}).get("value")
        return None if amt is None else amt > 50000
    if trig == "ESC-006" and trace:
        n = st.get("human_request_count", sum(1 for t in trace if t.get("intent") == "GEN-003"))
        return n >= 3
    if trig == "ESC-010" and "turns_since_resolution" in st:
        open_topic = any(t.get("status") in ("active", "parked") for t in st.get("topic_stack") or [])
        return st["turns_since_resolution"] + len(c["input_turns"]) > 15 and open_topic
    if trig == "ESC-007":
        flag = (fx.get("record_flags") or {}).get("high_value")
        return None if flag is None else bool(flag)
    if trig == "ESC-015":
        flag = (fx.get("record_flags") or {}).get("pep")
        auth = (c.get("preconditions") or {}).get("auth_level")
        return None if flag is None else bool(flag) and auth != "anonymous"
    if trig == "XTR-02":
        ev = fx.get("secure_widget_events")
        return None if ev is None else ev.count("otp_fail") >= 3 and "otp_ok" not in ev
    return None


computed = 0
for c in cases:
    exp = c.get("expect")
    got = computed_expectation(c) if exp else None
    if got is None:
        continue
    computed += 1
    if got != (exp == "fire"):
        err("%s: fixture values give %s but the case says expect: %s" % (c["id"], "fire" if got else "no_fire", exp))
for c in cases:
    blob = yaml.safe_dump(c)
    if re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", blob):
        err("%s: PAN-shaped value" % c.get("id"))
    if re.search(r"\b\d{5}[ -]\d{5}\b", blob) or re.search(r"\+91", blob):
        err("%s: phone-shaped value" % c.get("id"))
    for m in c.get("must_not_contain") or []:
        if not str(m).startswith("re:") and len(str(m).strip()) <= 4:
            err("%s: must_not_contain %r is too short for a substring match; use a re: word-boundary pattern" % (c.get("id"), m))
        if str(m).startswith("re:"):
            try:
                re.compile(str(m)[3:])
            except re.error:
                err("%s: invalid regular expression %r" % (c.get("id"), m))
print("oracles recomputed from fixtures:", computed)

# ------------------------------------------------------------------ report
print("triggers:", len(triggers), "| extra rules:", len(extras), "| queues:", len(queue_names),
      "| signals:", len(signals), "| sub-rules:", len(sub_rule_ids))
print("test files:", len(files), "| cases:", len(cases), "| ESC-T:", len(esc_cases),
      "| XTR-T:", sum(1 for c in cases if str(c.get("id", "")).startswith("XTR-T-")), "| boss:", len(boss_cases))
print("per trigger (fire/near-miss):", ", ".join("%s %d/%d" % (k[4:], per_trigger[k]["fire"], per_trigger[k]["no_fire"]) for k in ESC_IDS))
print("intents linked to a trigger: %d of %d | guardrails with an escalation: %d of %d | KB entries with a trigger: %d"
      % (len(set().union(*by_intent.values())), len(INTENT_IDS), len(set().union(*by_guard.values())), len(GR_IDS),
         len(set().union(*by_kb.values()))))
print("documents checked:", doc_count, "of", len(DOCS), "| KPI ids found:", len(kpi_ids))
for w in warnings:
    print("WARN", w)
for er in errors:
    print("ERROR", er)
print("RESULT:", ("FAIL (%d errors)" % len(errors)) if errors else "PASS")
sys.exit(1 if errors else 0)
