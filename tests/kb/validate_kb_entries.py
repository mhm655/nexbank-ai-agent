"""Validate docs/knowledge-base/entries/*.yaml against docs/knowledge-base/kb-schema.md.
Usage: python tests/kb/validate_kb_entries.py   (needs PyYAML)
Exit code 0 = all checks pass. Light harness only; the schema doc is the source of truth.
"""
import collections
import glob
import os
import re
import sys
from datetime import date, timedelta

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENTRY_FILES = sorted(glob.glob(os.path.join(ROOT, "docs", "knowledge-base", "entries", "*.yaml")))
INTENTS = yaml.safe_load(open(os.path.join(ROOT, "config", "intents.yaml"), encoding="utf8"))
INTENT_IDS = {i["id"] for i in INTENTS["intents"]}
KB_GAP_INTENTS = {i["id"] for i in INTENTS["intents"] if i.get("kb_gap")}
AUTH = INTENTS["auth_levels"]

REQUIRED = ["id", "category", "format", "title", "body", "structured_fields", "regulatory_tags",
            "auth_level_required", "audience", "version", "effective_from", "ttl_class", "ttl_days",
            "expires_at", "owner", "approval_chain", "source_ref", "languages", "intents", "status"]
CATEGORY_PREFIX = {"product": "PRD", "policy": "POL", "regulatory": "REG", "faq": "FAQ",
                   "troubleshooting": "TRB", "escalation": "ESC"}
FORMATS = {"structured", "semi_structured", "unstructured"}
AUDIENCE = {"customer_facing", "agent_internal"}
STATUS = {"draft", "in_review", "approved", "published", "deprecated", "expired"}
TTL = {"regulatory": 90, "rates": 90, "product_features": 180, "policy": 180,
       "faq_troubleshooting": 120, "escalation_procedure": 365}
LANGS = {"en", "hi", "hinglish", "ta", "te", "bn", "mr", "gu"}
TAGS = {"RBI_DIGITAL_LENDING", "RBI_OMBUDSMAN", "RBI_DIGITAL_PAYMENT_SECURITY", "RBI_RESPONSIBLE_AI",
        "PCI_DSS", "KYC_AML", "SEBI_ROBO_ADVISORY", "IRDAI_AI_DISTRIBUTION", "DPDP_ACT", "IT_SPDI_RULES",
        "DICGC", "TAX_80C", "TDS", "EU_AI_ACT"}
ESC_IDS = {"ESC-%03d" % n for n in range(1, 16)}

# Figures that appear in the brief (A13.1 first, then A4.1 examples, A6 and project decisions).
# Anything outside this list is reported as an error for manual review against the PDF.
ALLOWED_NUMBERS = {
    # A13.1 product catalogue
    "4.5", "6.0", "7.25", "7", "10", "40", "2", "1", "50", "5", "8.25", "30", "90", "700", "650", "10.5",
    "100", "24", "80",
    # A4.1 examples
    "6.5", "20", "8.5", "17356", "17,356", "1.5",
    # A6 triggers, A4.2 rules, A1.2 card-block turns, counts used in prose
    "15", "3", "3.4", "0.7", "50,000", "8", "4", "6",
    # years in the names of the instruments listed in the brief (appendix pp70-71); no other year is allowed
    "2006", "2011", "2017", "2022", "2023", "2024", "2025",
}
# Number + time unit pairs that are in the brief or in a project decision (A13.1 tenures and interest-free days,
# A6 SLAs and turn counts, A4.1 example, A1.2 turns, A4.2 timeout, D-05 window, D-09 example, ACC-002 statement default).
# Any other duration (for example "within 7 working days") is a timeline commitment and is reported (A9.2 False Confidence).
ALLOWED_DURATIONS = {
    ("7", "day"), ("10", "year"), ("30", "year"), ("5", "year"), ("20", "year"), ("1", "year"),
    ("40", "day"), ("50", "day"), ("2", "min"), ("5", "min"), ("10", "min"), ("15", "min"),
    ("2", "turn"), ("15", "turn"), ("3.4", "turn"), ("24", "hour"), ("30", "day"),
}
UNIT = {"day": "day", "days": "day", "hour": "hour", "hours": "hour", "hr": "hour", "hrs": "hour",
        "min": "min", "mins": "min", "minute": "min", "minutes": "min", "week": "week", "weeks": "week",
        "month": "month", "months": "month", "year": "year", "years": "year", "turn": "turn", "turns": "turn"}
DURATION_RE = re.compile(r"(\d[\d,]*\.?\d*)\s*-?\s*((?:working|business|calendar|banking)\s+)?(%s)\b"
                         % "|".join(sorted(UNIT, key=len, reverse=True)), re.I)
GAP_KEYS = {"unknown", "safe_statement", "known_adjacent_facts", "offer", "never"}

errors, warnings = [], []
entries = []
for f in ENTRY_FILES:
    doc = yaml.safe_load(open(f, encoding="utf8"))
    for e in doc["entries"]:
        e["_file"] = os.path.basename(f)
        entries.append(e)

ids = collections.Counter(e.get("id") for e in entries)
for i, n in ids.items():
    if n > 1:
        errors.append("duplicate id %s" % i)
all_ids = set(ids)


def walk_strings(x):
    """Yield every string, and every int or float as a string (a YAML number is a figure too)."""
    if isinstance(x, bool) or x is None:
        return
    if isinstance(x, (str, int, float)):
        yield str(x)
    elif isinstance(x, dict):
        for k, v in x.items():
            yield str(k)
            yield from walk_strings(v)
    elif isinstance(x, (list, tuple)):
        for v in x:
            yield from walk_strings(v)


def check_maps(x, eid, path=""):
    """A stray comma inside an unquoted flow-mapping value silently creates a key with a null value."""
    if isinstance(x, dict):
        for k, val in x.items():
            if not isinstance(k, str) or (val is None and path):
                errors.append("%s suspicious key %r at %s (unquoted comma in a flow map?)" % (eid, k, path))
            check_maps(val, eid, path + "/" + str(k))
    elif isinstance(x, list):
        for n, val in enumerate(x):
            check_maps(val, eid, path + "[%d]" % n)


gap_covered = set()
for e in entries:
    eid = e.get("id", "?")
    missing = [k for k in REQUIRED if k not in e]
    for k in missing:
        errors.append("%s missing field %s" % (eid, k))
    if missing:
        continue
    cat = e["category"]
    if cat not in CATEGORY_PREFIX:
        errors.append("%s bad category %s" % (eid, cat))
    elif not re.fullmatch(r"KB-%s-\d{3}" % CATEGORY_PREFIX[cat], eid):
        errors.append("%s id does not match category %s" % (eid, cat))
    if e["_file"].replace(".yaml", "") != cat:
        errors.append("%s is in %s but category is %s" % (eid, e["_file"], cat))
    if e["format"] not in FORMATS:
        errors.append("%s bad format" % eid)
    if e["auth_level_required"] not in AUTH:
        errors.append("%s bad auth_level_required %s" % (eid, e["auth_level_required"]))
    if e["audience"] not in AUDIENCE:
        errors.append("%s bad audience" % eid)
    if e["status"] not in STATUS:
        errors.append("%s bad status" % eid)
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(e["version"])):
        errors.append("%s bad version" % eid)
    if e["ttl_class"] not in TTL:
        errors.append("%s bad ttl_class" % eid)
    elif type(e["ttl_days"]) is not int:
        errors.append("%s ttl_days must be an integer" % eid)
        continue
    elif e["ttl_days"] != TTL[e["ttl_class"]]:
        errors.append("%s ttl_days %s != class default %s" % (eid, e["ttl_days"], TTL[e["ttl_class"]]))
    ef, ex = e["effective_from"], e["expires_at"]
    if not (isinstance(ef, date) and isinstance(ex, date)):
        errors.append("%s dates must be ISO dates" % eid)
    elif ex != ef + timedelta(days=e["ttl_days"]):
        errors.append("%s expires_at %s != effective_from + ttl_days" % (eid, ex))
    if not e["approval_chain"] or len(e["approval_chain"]) < 2:
        errors.append("%s approval_chain needs >= 2 steps" % eid)
    if cat == "regulatory" and "Regulatory Compliance Manager" not in e["approval_chain"]:
        errors.append("%s regulatory entry needs the Regulatory Compliance Manager in approval_chain" % eid)
    if not str(e["source_ref"]).strip():
        errors.append("%s empty source_ref" % eid)
    if not e["intents"]:
        errors.append("%s has no intent links" % eid)
    for i in e["intents"]:
        if i not in INTENT_IDS:
            errors.append("%s unknown intent %s" % (eid, i))
    for t in e.get("escalation_triggers") or []:
        if t not in ESC_IDS:
            errors.append("%s unknown escalation trigger %s" % (eid, t))
    for t in e["regulatory_tags"]:
        if t not in TAGS:
            errors.append("%s unknown regulatory tag %s" % (eid, t))
    if "en" not in e["languages"] or not set(e["languages"]) <= LANGS:
        errors.append("%s bad languages %s" % (eid, e["languages"]))
    i18n = e.get("body_i18n", {})
    if set(i18n) != set(e["languages"]) - {"en"}:
        errors.append("%s body_i18n keys must equal languages minus en" % eid)
    sf = e["structured_fields"]
    check_maps(sf, eid, "structured_fields")
    words = len(e["body"].split())
    if e["format"] == "unstructured":
        if sf not in ({}, None):
            errors.append("%s unstructured entry must have empty structured_fields" % eid)
        if words < 25:
            errors.append("%s unstructured body too short (%d words)" % (eid, words))
    elif e["format"] == "structured":
        if not isinstance(sf, dict) or len(sf) < 4 or words > 60:
            errors.append("%s structured entry needs >= 4 fields and a short body" % eid)
    else:
        if not isinstance(sf, dict) or not any(isinstance(v, (list, dict)) for v in sf.values()):
            errors.append("%s semi_structured needs nested lists or maps" % eid)
    if e.get("gap_handling"):
        if cat != "escalation":
            errors.append("%s gap entries must have category escalation" % eid)
        if not e.get("gap_for"):
            errors.append("%s gap entry needs a non-empty gap_for" % eid)
        if e["format"] == "semi_structured" and isinstance(sf, dict) and not GAP_KEYS <= set(sf):
            errors.append("%s gap entry missing keys %s" % (eid, sorted(GAP_KEYS - set(sf))))
        for i in e.get("gap_for") or []:
            gap_covered.add(i)
            if i not in INTENT_IDS:
                errors.append("%s gap_for unknown intent %s" % (eid, i))
    elif e.get("gap_for"):
        errors.append("%s has gap_for but gap_handling is not true" % eid)
    for s in list(walk_strings(sf)) + [e["body"], e["title"]] + list(walk_strings(i18n or {})):
        for ref in re.findall(r"KB-[A-Z]{3}-\d{3}", s):
            if ref not in all_ids:
                errors.append("%s references missing entry %s" % (eid, ref))
    if words > 200:
        warnings.append("%s body is long (%d words)" % (eid, words))

for i in sorted(KB_GAP_INTENTS):
    if i not in gap_covered:
        errors.append("kb_gap intent %s has no gap-handling entry" % i)
linked = {i for e in entries for i in e.get("intents", [])}
for i in sorted(INTENT_IDS - linked):
    warnings.append("intent %s has no KB entry" % i)

# figure scan: every number in titles, bodies and structured fields must be on the allow-list
unknown = collections.defaultdict(set)
for e in entries:
    text = " ".join(walk_strings(e["structured_fields"])) + " " + e["body"] + " " + e["title"]
    text += " " + " ".join(walk_strings(e.get("body_i18n") or {}))   # translations must not add figures
    text = re.sub(r"\bKB-[A-Z]{3}-\d{3}\b", " ", text)
    text = re.sub(r"\b[A-Z]{2,4}-\d{3}\b", " ", text)
    text = re.sub(r"\b[AD]\d+(\.\d+)?\b|\b[AD]-\d+\b", " ", text)
    text = re.sub(r"\bP[0-3]\b|\bPCI DSS v4\.0\b", " ", text)
    if e.get("gap_handling"):
        # A gap entry is the fallback when a rates or regulatory entry hard-expires, so it must not restate a figure
        # (kb-schema.md sections 7 and 11); it points to the source entry by ID instead. Titles are labels and exempt.
        gtext = " ".join(walk_strings(e["structured_fields"])) + " " + e["body"]
        gtext = re.sub(r"\bKB-[A-Z]{3}-\d{3}\b|\b[A-Z]{2,4}-\d{3}\b|\b[AD]\d+(\.\d+)?\b|\b[AD]-\d+\b", " ", gtext)
        if re.search(r"\d", gtext):
            errors.append("%s gap entry states a figure: %s" % (e["id"], sorted(set(re.findall(r"\d[\d,.]*", gtext)))))
    for m in DURATION_RE.finditer(text):
        num, qual, unit = m.group(1).rstrip(".,"), m.group(2), UNIT[m.group(3).lower()]
        if qual or (num, unit) not in ALLOWED_DURATIONS:
            unknown["duration '%s'" % m.group(0)].add(e["id"])
    for m in re.findall(r"\d[\d,]*\.?\d*", text):
        m = m.rstrip(".,")
        if m and m not in ALLOWED_NUMBERS:
            unknown[m].add(e["id"])
for n, who in sorted(unknown.items()):
    errors.append("figure %s not in allow-list: %s" % (n, sorted(who)))

by_cat = collections.Counter(e["category"] for e in entries)
by_fmt = collections.Counter(e["format"] for e in entries)
by_auth = collections.Counter(e["auth_level_required"] for e in entries)
print("entries:", len(entries))
print("by category:", dict(by_cat))
print("by format:", dict(by_fmt))
print("by auth:", dict(by_auth))
print("gap entries:", sum(1 for e in entries if e.get("gap_handling")))
print("intents linked: %d of %d" % (len(linked & INTENT_IDS), len(INTENT_IDS)))
if len(entries) < 55:
    errors.append("fewer than 55 entries")
if set(by_cat) != set(CATEGORY_PREFIX) or set(by_fmt) != FORMATS:
    errors.append("category or format spread incomplete")
for w in warnings:
    print("WARN", w)
for er in errors:
    print("ERROR", er)
print("RESULT:", ("FAIL (%d errors)" % len(errors)) if errors else "PASS")
sys.exit(1 if errors else 0)
