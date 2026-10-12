"""Validate config/templates/*.yaml, config/parameters.yaml and config/system-prompt/ (Day 13).
Usage: python tests/templates/validate_templates.py            (needs PyYAML)
       python tests/templates/validate_templates.py --rehash   (rewrite the hash fields of config/system-prompt/manifest.yaml)
Exit code 0 = all checks pass. Light harness only: it checks structure, references and wording rules.
It does not execute a template, call a model or measure anything. Check list: tests/templates/README.md.
"""
import glob
import hashlib
import io
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TPL_DIR = os.path.join(ROOT, "config", "templates")
SP_DIR = os.path.join(ROOT, "config", "system-prompt")
errors, warnings, stats = [], [], {}


def err(msg):
    errors.append(msg)


def read(path):
    with io.open(path, encoding="utf8") as fh:
        return fh.read()


def load(path):
    return yaml.safe_load(read(path))


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


# ---------------------------------------------------------------------------------------------- reference sets
INTENTS = load(os.path.join(ROOT, "config", "intents.yaml"))
INTENT_IDS = {i["id"] for i in INTENTS["intents"]}
GUARDRAILS = load(os.path.join(ROOT, "config", "guardrails.yaml"))
GR_IDS = {g["id"] for g in GUARDRAILS["guardrails"]}
ESC_RULES = load(os.path.join(ROOT, "config", "escalation_rules.yaml"))
ESC_IDS = {"ESC-%03d" % n for n in range(1, 16)}
QUEUES = {q["name"] for q in ESC_RULES["queues"]}
KB_IDS = set()
for f in glob.glob(os.path.join(ROOT, "docs", "knowledge-base", "entries", "*.yaml")):
    KB_IDS |= {e["id"] for e in load(f)["entries"]}
TEST_IDS = set()
for f in glob.glob(os.path.join(ROOT, "tests", "**", "*.yaml"), recursive=True):
    TEST_IDS |= set(re.findall(r"^\s*-?\s*id:\s*[\"']?([A-Za-z0-9-]+)", read(f), flags=re.M))
TOOLS = {"get_balance", "get_statement", "get_profile_masked", "get_txn", "search_txn", "create_dispute_ticket",
         "get_card_status", "block_card", "request_replacement", "emi_calculator", "kb_search", "create_complaint",
         "get_complaint_status", "schedule_callback", "flag_fraud", "send_credential_reset_link", "route_to_queue",
         "summarise_conversation"}   # docs/architecture/system-architecture.md tool list

# ---------------------------------------------------------------------------------------------- wording rules
SLOT_RE = re.compile(r"\{\{\s*([a-z0-9_]+)\s*\}\}")
DIGIT_RE = re.compile(r"[0-9\u0966-\u096f]")
DEVANAGARI_RE = re.compile(r"[\u0900-\u097f]")
MODES = {"template", "hybrid", "llm-guided"}
SELECTION = {"single", "condition", "rotate"}
SOURCE_TYPES = {"tool", "kb", "state", "router", "policy", "notice", "llm"}
PATTERNS = {"P1", "P2", "P3", "P4", "P5"}
ANTI = {"AP%d" % n for n in range(1, 9)}
LANGS = ["en", "hi", "hinglish"]
# GR-ADV-07 build-time lint (case GR-ADV-07-01): no slot may hold a personal circumstance.
BANNED_SLOT_NAMES = re.compile(r"(^|_)(income|salary|age|savings|portfolio|goals?|risk_appetite|dependants|net_worth)(_|$)")
# Banned in every template text (English and Hinglish). Each entry: (regex, anti-pattern or rule it protects).
BANNED = [
    (r"as an ai language model", "persona (response-generation.md section 2)"),
    (r"i'?m just a bot|i am just a bot", "persona"),
    (r"\bguarantee", "False Confidence (A9.2); KB-POL-007 is rendered as 'a request and may change'"),
    (r"\bdefinitely\b|\bcertainly will\b|\b100 ?%|\bexactly\b", "False Confidence (A9.2)"),
    (r"\bi promise\b|\bwe promise\b|\bpromise you\b", "False Confidence (A9.2)"),
    (r"will be (credited|refunded|resolved|approved|fixed)", "False Confidence; commitment detection C6"),
    (r"within \d|within (24|two|three|a few) ", "timeline not from a system of record (D-09)"),
    (r"\b(pakka|zaroor mil|ho jayega kal)\b", "False Confidence, Hinglish"),
    (r"deeply apologi[sz]e|sincerely (regret|apologi[sz]e)|so sorry|extremely sorry|profusely", "Sycophantic Recovery (A9.2)"),
    (r"i didn'?t understand|could you (please )?rephrase|please rephrase", "Robotic Loop wording (A9.2 example)"),
    (r"you should have|your fault|your mistake|you failed|you must have|as i (already )?said|galti aapki", "blame"),
    (r"calm down|relax,|don'?t worry about it|not a big deal|shaant ho", "Empathy Bypass / dismissive tone"),
    (r"\bi think\b|\bprobably\b|\bas far as i know\b|\bi believe\b|\bshayad\b", "hedged guess (retrieval-pipeline.md section 10)"),
    (r"act now|limited time|hurry|don'?t miss|last chance|only today|jaldi karo", "pressure selling (A4.3, GR-REG-04)"),
    (r"\bi recommend\b|\bwe recommend\b|you should (invest|buy|choose|take|put)|best option|best choice|right for you|"
     r"suitable for you|lena chahiye\b", "financial advice (A4.1)"),
    (r"no one is available|nobody is available|try (again )?later|baad mein try", "GR-SEC-R6-03 oracle; Graceful Degradation"),
    (r"(?<!don't )(?<!never )(?<!not )share (your|the) (otp|pin|cvv|password)|tell me (your|the) (otp|pin|cvv|password)|otp bata|pin bata", "A4.2 rule 5"),
    (r"stack trace|exception|null pointer|http \d{3}|\bapi\b|backend|database|timeout|latency", "technical jargon (Pattern 4)"),
    (r"\bpep\b|politically exposed|due diligence|\baml\b|money laundering|flagged|suspicious", "no tipping off (layer 2 R4)"),
    (r"\blol\b|\bbro\b|\byaar\b|no worries|chill", "slang near money matters (A9.3 Formality)"),
]
BANNED_HI = [("\u0917\u093e\u0930\u0902\u091f\u0940", "False Confidence"), ("\u092a\u0915\u094d\u0915\u093e", "False Confidence"), ("\u0928\u093f\u0936\u094d\u091a\u093f\u0924 \u0930\u0942\u092a \u0938\u0947 \u092e\u093f\u0932", "False Confidence"),
             ("\u0906\u092a\u0915\u0940 \u0917\u0932\u0924\u0940", "blame"), ("\u0936\u093e\u0902\u0924 \u0939\u094b \u091c\u093e\u0907\u090f", "dismissive"), ("\u091c\u0932\u094d\u0926\u0940 \u0915\u0940\u091c\u093f\u090f", "pressure"),
             ("\u0936\u093e\u092f\u0926", "hedged guess"), ("\u0913\u091f\u0940\u092a\u0940 \u092c\u0924\u093e\u0907\u090f", "A4.2 rule 5"), ("\u092a\u093f\u0928 \u092c\u0924\u093e\u0907\u090f", "A4.2 rule 5")]
# Per-template exemptions from one BANNED entry, each with the reason (kept short and explicit on purpose).
BANNED_EXEMPT = {
    # none needed today; TPL-SRV-NPS uses "recommend NexBank to a friend", which no BANNED pattern matches.
}
REQUIRED_TEMPLATES = [
    "TPL-GEN-GREETING", "TPL-AUTH-OTP-REQUEST", "TPL-ACC-BALANCE", "TPL-TXN-DISPUTE-INTAKE",
    # the 13 advice names of docs/guardrails/financial-advice.md section 6
    "TPL-ADV-BOUNDARY", "TPL-ADV-RATE", "TPL-ADV-LOAN", "TPL-ADV-INVEST", "TPL-ADV-INSURANCE", "TPL-ADV-TAX",
    "TPL-ADV-FOREX", "TPL-ADV-COMPARE", "TPL-ADV-ADVISOR-OFFER", "TPL-ADV-ADVISOR-CONFIRM", "TPL-ADV-ADVISOR-DECLINED",
    "TPL-ADV-ADVISOR-UNAVAILABLE", "TPL-ADV-SAFE-FALLBACK",
    # the 7 attack-response names of docs/guardrails/adversarial-defences.md section 3.3
    "TPL-ATK-NEUTRAL-REDIRECT", "TPL-ATK-CANNOT-SHARE-CONFIG", "TPL-ATK-AUTH-PROMPT", "TPL-ATK-THIRD-PARTY",
    "TPL-ATK-THROTTLE", "TPL-ATK-SHORTEN-OR-SPLIT", "TPL-ATK-SAFE-MODE",
    # the 12 escalation names of docs/escalation/routing-and-handoff.md section 11
    "TPL-ESC-HANDOFF-WARM", "TPL-ESC-HANDOFF-DISCREET", "TPL-ESC-FRAUD-P0", "TPL-ESC-CRISIS", "TPL-ESC-WAIT-UPDATE",
    "TPL-ESC-HUMAN-JOINED", "TPL-ESC-AFTER-HOURS", "TPL-ESC-CALLBACK-OFFER", "TPL-ESC-LANGUAGE-CHOICE",
    "TPL-ESC-HANDOFF-FAILED", "TPL-ESC-DEESCALATION-CHECK", "TPL-ESC-REFERRAL",
    "TPL-CMP-EMPATHY-FIRST", "TPL-CMP-GRIEVANCE-INFO", "TPL-KB-DEGRADE", "TPL-KB-GAP", "TPL-ACT-CONFIRM",
    "TPL-SRV-CSAT", "TPL-GEN-CHECKIN", "TPL-GEN-LANGUAGE-SWITCH", "TPL-AUTH-STEP-UP", "TPL-AUTH-SESSION-TIMEOUT",
    "TPL-GEN-CLARIFY", "TPL-GEN-RECOVERY",
]
LEGACY_NAMES_REQUIRED = {"ask_not_to_share_card", "ask_not_to_share_cvv", "ask_not_to_share_aadhaar",
                         "ask_not_to_share_secret", "use_secure_widget", "use_secure_form", "use_masked_reference",
                         "graceful_degradation"}
# TPL- strings elsewhere in the repo that are not template ids: a test fixture name and two family prefixes used as "TPL-ESC-*".
EXTERNAL_NON_IDS = {"TPL-TEST-INCOME-SLOT"}
TEMPLATE_KEYS = ["id", "title", "version", "customer_facing", "trigger", "mode", "variant_selection", "slots", "variants",
                 "safety", "a9", "kb_refs", "tests"]


def strip_slots(text):
    return SLOT_RE.sub(" ", text)


def words(text):
    return re.findall(r"[a-z']+", text.lower())


# ---------------------------------------------------------------------------------------------- 1. templates
templates = {}
tpl_file = {}
tpl_files = sorted(f for f in glob.glob(os.path.join(TPL_DIR, "*.yaml")) if os.path.basename(f) != "labels.yaml")
for path in tpl_files:
    try:
        doc = load(path)
    except yaml.YAMLError as exc:
        err("%s: YAML parse error: %s" % (rel(path), exc))
        continue
    if (doc.get("review") or {}) != {"hi": "not_native_reviewed", "hinglish": "not_native_reviewed"}:
        err("%s: file-level review block must mark hi and hinglish as not_native_reviewed" % rel(path))
    for t in doc.get("templates") or []:
        tid = t.get("id", "<no id>")
        if tid in templates:
            err("%s: duplicate template id %s" % (rel(path), tid))
        templates[tid] = t
        tpl_file[tid] = rel(path)

for tid, t in templates.items():
    where = "%s %s" % (tpl_file[tid], tid)
    if not re.match(r"^TPL-[A-Z]{2,4}(-[A-Z0-9]+)+$", tid):
        err("%s: id does not match TPL-<FAMILY>-<NAME>" % where)
    for k in TEMPLATE_KEYS:
        if k not in t:
            err("%s: missing field %s" % (where, k))
    if any(k not in t for k in TEMPLATE_KEYS):
        continue
    if t["mode"] not in MODES:
        err("%s: mode %r not in %s" % (where, t["mode"], sorted(MODES)))
    if t["variant_selection"] not in SELECTION:
        err("%s: variant_selection %r invalid" % (where, t["variant_selection"]))
    trig = t["trigger"]
    for k in ("intents", "guardrails", "escalations", "state"):
        if k not in trig:
            err("%s: trigger.%s missing" % (where, k))
    for i in trig.get("intents", []):
        if i not in INTENT_IDS:
            err("%s: unknown intent %s" % (where, i))
    for g in trig.get("guardrails", []) + t["safety"].get("guardrails_enforced", []):
        if g not in GR_IDS:
            err("%s: unknown guardrail %s" % (where, g))
    for e in trig.get("escalations", []):
        if e not in ESC_IDS:
            err("%s: unknown escalation %s" % (where, e))
    if not str(trig.get("state", "")).strip():
        err("%s: trigger.state is empty" % where)
    for k in t["kb_refs"]:
        if k not in KB_IDS:
            err("%s: unknown KB entry %s" % (where, k))
    if not t["tests"]:
        err("%s: no linked test" % where)
    for x in t["tests"]:
        if x not in TEST_IDS:
            err("%s: linked test %s does not exist in tests/" % (where, x))
    for c in t.get("compose_with", []):
        if c not in templates:
            err("%s: compose_with %s is not a template" % (where, c))
    a9 = t["a9"]
    if not a9.get("patterns") or not set(a9["patterns"]) <= PATTERNS:
        err("%s: a9.patterns must be a non-empty subset of P1..P5" % where)
    if not a9.get("anti_patterns_avoided") or not set(a9["anti_patterns_avoided"]) <= ANTI:
        err("%s: a9.anti_patterns_avoided must be a non-empty subset of AP1..AP8" % where)
    if t["customer_facing"] and not t["safety"].get("guardrails_enforced"):
        err("%s: customer-facing template enforces no guardrail" % where)
    if "must_not_contain" not in t["safety"]:
        err("%s: safety.must_not_contain missing" % where)

    # slots
    declared, llm_slots = {}, []
    for s in t["slots"]:
        name = s.get("name", "")
        if name in declared:
            err("%s: slot %s declared twice" % (where, name))
        declared[name] = s
        if BANNED_SLOT_NAMES.search(name):
            err("%s: slot %s holds a personal circumstance (GR-ADV-07 lint)" % (where, name))
        src = s.get("source") or {}
        if src.get("type") not in SOURCE_TYPES:
            err("%s: slot %s source.type %r invalid" % (where, name, src.get("type")))
        if "locked" not in s:
            err("%s: slot %s has no `locked` flag" % (where, name))
        ref = str(src.get("ref", ""))
        for kb in re.findall(r"KB-[A-Z]{3}-\d{3}", ref):
            if kb not in KB_IDS:
                err("%s: slot %s references unknown %s" % (where, name, kb))
        if src.get("type") == "tool":
            named = set(re.findall(r"[a-z]+(?:_[a-z]+)+", ref)) & TOOLS
            if not named and "auth service" not in ref and "executed tool" not in ref:
                err("%s: slot %s tool source names no known tool: %r" % (where, name, ref))
        if src.get("type") == "llm":
            llm_slots.append(name)
            if s.get("locked") is not False:
                err("%s: llm slot %s must be locked: false" % (where, name))
            if not s.get("constraints") or "max_words" not in s["constraints"]:
                err("%s: llm slot %s needs constraints.max_words" % (where, name))
            fb = s.get("fallback") or {}
            for lang in LANGS:
                if not fb.get(lang):
                    err("%s: llm slot %s has no %s fallback" % (where, name, lang))
        elif s.get("locked") is not True:
            err("%s: non-llm slot %s must be locked: true" % (where, name))
    if t["mode"] == "template" and llm_slots:
        err("%s: mode template may not have llm slots %s" % (where, llm_slots))
    if t["mode"] == "llm-guided" and not llm_slots:
        err("%s: mode llm-guided needs at least one llm slot" % where)

    # variants and text
    keys = [v.get("key") for v in t["variants"]]
    if len(keys) != len(set(keys)) or not keys:
        err("%s: variant keys missing or not unique" % where)
    if t["variant_selection"] == "single" and len(keys) != 1:
        err("%s: variant_selection single needs exactly one variant" % where)
    if t["variant_selection"] == "rotate" and len(keys) < 3:
        err("%s: a rotating template needs at least 3 variants (template_variant_min_rotating)" % where)
    allowed_literals = set(t.get("allowed_literals") or [])
    used_anywhere = set()
    texts = []   # (label, lang, text)
    for v in t["variants"]:
        txt = v.get("text") or {}
        per_lang = {}
        for lang in LANGS:
            if not str(txt.get(lang, "")).strip():
                err("%s/%s: missing %s text" % (where, v.get("key"), lang))
                continue
            texts.append(("%s/%s" % (where, v.get("key")), lang, txt[lang]))
            per_lang[lang] = set(SLOT_RE.findall(txt[lang]))
        if len(per_lang) == 3 and not (per_lang["en"] == per_lang["hi"] == per_lang["hinglish"]):
            err("%s/%s: languages use different slot sets %s" % (where, v.get("key"), {k: sorted(x) for k, x in per_lang.items()}))
        for used in per_lang.values():
            used_anywhere |= used
            for u in used - set(declared):
                err("%s/%s: slot {{%s}} used but not declared" % (where, v.get("key"), u))
        if t["variant_selection"] != "single" and not v.get("when"):
            err("%s/%s: variant has no `when` condition" % (where, v.get("key")))
    for d in set(declared) - used_anywhere:
        err("%s: slot %s declared but never used" % (where, d))
    for s in t["slots"]:
        if s.get("source", {}).get("type") == "llm":
            for lang in LANGS:
                if (s.get("fallback") or {}).get(lang):
                    texts.append(("%s/slot %s fallback" % (where, s["name"]), lang, s["fallback"][lang]))

    own_banned = [str(x).lower() for x in t["safety"].get("must_not_contain", [])]
    for label, lang, text in texts:
        bare = strip_slots(text)
        if "{" in bare or "}" in bare:
            err("%s [%s]: malformed slot braces" % (label, lang))
        for d in DIGIT_RE.findall(bare):
            if d not in "".join(allowed_literals):
                err("%s [%s]: digit %r outside a slot (not in allowed_literals)" % (label, lang, d))
        for num in re.findall(r"\d+", bare):
            if num not in allowed_literals:
                err("%s [%s]: number %r outside a slot (not in allowed_literals)" % (label, lang, num))
        low = bare.lower()
        for phrase in own_banned:
            if phrase and phrase in low:
                err("%s [%s]: contains its own must_not_contain phrase %r" % (label, lang, phrase))
        if lang in ("en", "hinglish"):
            if not all(ord(c) < 128 for c in text):
                err("%s [%s]: non-ASCII character in %s text" % (label, lang, lang))
            for rx, why in BANNED:
                if (tid, rx) in BANNED_EXEMPT:
                    continue
                m = re.search(rx, low)
                if m:
                    err("%s [%s]: banned phrase %r (%s)" % (label, lang, m.group(0), why))
        else:
            if bare.strip() and not DEVANAGARI_RE.search(text):
                err("%s [hi]: Hindi text has no Devanagari" % label)
            for phrase, why in BANNED_HI:
                if phrase in text:
                    err("%s [hi]: banned phrase %r (%s)" % (label, phrase, why))
        if re.search(r"[\u2013\u2014\u2018\u2019\u201c\u201d]", text):
            err("%s [%s]: em dash or smart quote" % (label, lang))

stats["templates"] = len(templates)
stats["template_files"] = len(tpl_files)
stats["variants"] = sum(len(t.get("variants", [])) for t in templates.values())
stats["by_mode"] = {m: sum(1 for t in templates.values() if t.get("mode") == m) for m in sorted(MODES)}
stats["by_family"] = {}
for tid in templates:
    fam = tid.split("-")[1]
    stats["by_family"][fam] = stats["by_family"].get(fam, 0) + 1
if len(templates) < 15:
    err("only %d templates; the brief requires 15+" % len(templates))
for r in REQUIRED_TEMPLATES:
    if r not in templates:
        err("required template %s is missing" % r)
legacy = set()
for t in templates.values():
    legacy |= set(t.get("legacy_names") or [])
    for v in t.get("variants", []):
        legacy.add(v.get("key"))
for name in LEGACY_NAMES_REQUIRED - legacy:
    err("legacy template name %s (used by earlier documents) maps to no template" % name)

# labels.yaml
labels_path = os.path.join(TPL_DIR, "labels.yaml")
if os.path.exists(labels_path):
    labels = load(labels_path)
    for q in QUEUES - set(labels.get("queue_plain_names", {})):
        err("labels.yaml: queue %s has no plain name" % q)
    for q, v in labels.get("queue_plain_names", {}).items():
        if q not in QUEUES:
            err("labels.yaml: %s is not a queue in config/escalation_rules.yaml" % q)
        for lang in LANGS:
            if not v.get(lang):
                err("labels.yaml: queue %s lacks %s" % (q, lang))
    for i in labels.get("intent_request_labels", {}):
        if i not in INTENT_IDS:
            err("labels.yaml: unknown intent %s" % i)
    for tid in ("TPL-AUTH-OTP-REQUEST", "TPL-AUTH-STEP-UP"):
        for i in templates.get(tid, {}).get("trigger", {}).get("intents", []):
            if i not in labels.get("intent_request_labels", {}):
                err("labels.yaml: %s is a trigger of %s but has no request label" % (i, tid))
else:
    err("config/templates/labels.yaml missing")

# ---------------------------------------------------------------------------------------------- 2. TPL- references repo-wide
SKIP_DIRS = {".git", "graphify-out", "node_modules", "__pycache__"}
ref_count, ref_files = 0, set()
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if not fn.endswith((".md", ".yaml", ".yml", ".json", ".mmd", ".csv", ".py")):
            continue
        p = os.path.join(dirpath, fn)
        if os.path.abspath(p) == os.path.abspath(__file__):
            continue
        txt = read(p)
        for m in re.finditer(r"TPL-[A-Z0-9]+(?:-[A-Z0-9]+)*", txt):
            tok = m.group(0)
            tail = txt[m.end():m.end() + 2]
            if tok in templates or tok in EXTERNAL_NON_IDS:
                ref_count += 1
                ref_files.add(rel(p))
                continue
            is_prefix = any(t.startswith(tok + "-") for t in templates)
            if is_prefix and (tail.startswith("-*") or tail.startswith("-<") or re.match(r"^TPL-[A-Z]+$", tok)):
                continue   # family prefix such as TPL-ESC-* or TPL-ATK
            err("%s: reference to %s, which is not a template id" % (rel(p), tok))
stats["tpl_references"] = ref_count
stats["files_referencing_templates"] = len(ref_files)

# ---------------------------------------------------------------------------------------------- 3. parameters.yaml
A123 = {  # name: (default, range, owner, change process) copied from the brief p.34
    "intent_confidence_threshold": (0.70, (0.50, 0.95), "NLU Team", "A/B test required"),
    "escalation_sentiment_threshold": (-0.70, (-1.0, -0.3), "CX Team", "CEB approval"),
    "max_conversation_turns": (25, (10, 50), "Product", "Standard change"),
    "session_timeout_minutes": (5, (3, 15), "Security", "RC approval"),
    "knowledge_retrieval_top_k": (5, (3, 10), "NLU Team", "A/B test required"),
    "retrieval_confidence_threshold": (0.65, (0.50, 0.90), "NLU Team", "A/B test required"),
    "guardrail_strictness_level": ("HIGH", ["MEDIUM", "HIGH", "CRITICAL"], "RC", "RC approval required"),
    "model_temperature": (0.3, (0.0, 1.0), "ML Team", "A/B test + RC review"),
}


def dig(doc, path):
    cur = doc
    for part in path.split("."):
        cur = cur[part]
    return cur


def same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(float(a) - float(b)) < 1e-9
    return a == b


params_path = os.path.join(ROOT, "config", "parameters.yaml")
mirror_checked = 0
try:
    P = load(params_path)
    gov = {g["name"]: g for g in P["governed_parameters"]}
    if set(gov) != set(A123):
        err("parameters.yaml: governed_parameters %s differ from the 8 of A12.3" % sorted(set(gov) ^ set(A123)))
    cfg_cache = {}
    for name, (default, rng, owner, process) in A123.items():
        g = gov.get(name)
        if not g:
            continue
        if not same(g["default"], default):
            err("parameters.yaml: %s default %r differs from the brief %r" % (name, g["default"], default))
        if g["owner"] != owner or g["change_process"] != process:
            err("parameters.yaml: %s owner or change process differs from the brief" % name)
        br, eff = g["brief_range"], g["effective_range"]
        if isinstance(rng, list):
            if br["values"] != rng or default not in br["values"] or not set(eff["values"]) <= set(rng) or default not in eff["values"]:
                err("parameters.yaml: %s enum range wrong or default outside it" % name)
        else:
            if not (same(br["min"], rng[0]) and same(br["max"], rng[1])):
                err("parameters.yaml: %s brief_range differs from the brief" % name)
            if not (br["min"] <= g["default"] <= br["max"]):
                err("parameters.yaml: %s default outside brief range" % name)
            if not (br["min"] <= eff["min"] <= g["default"] <= eff["max"] <= br["max"]):
                err("parameters.yaml: %s effective range not inside the brief range or default outside it" % name)
        if g.get("learning") not in ("may_propose", "no"):
            err("parameters.yaml: %s learning flag invalid" % name)
        for m in g.get("mirrors") or []:
            doc = cfg_cache.setdefault(m["file"], load(os.path.join(ROOT, m["file"])))
            mirror_checked += 1
            if not same(dig(doc, m["path"]), g["default"]):
                err("parameters.yaml: %s = %r but %s %s = %r" % (name, g["default"], m["file"], m["path"], dig(doc, m["path"])))
    if gov and gov["session_timeout_minutes"]["effective_range"]["max"] != 5:
        err("parameters.yaml: session_timeout_minutes effective ceiling must be 5 (D-56)")
    seen = set(gov)
    for p in P["project_parameters"]:
        for k in ("name", "value", "unit", "status", "decision", "defined_in", "learning"):
            if k not in p:
                err("parameters.yaml: project parameter %s lacks %s" % (p.get("name"), k))
        if p["name"] in seen:
            err("parameters.yaml: duplicate parameter name %s" % p["name"])
        seen.add(p["name"])
        if p.get("status") not in ("brief_fixed", "decided", "proposal", "default"):
            err("parameters.yaml: %s status invalid" % p["name"])
        if p.get("status") == "brief_fixed" and not p.get("brief_ref"):
            err("parameters.yaml: %s is brief_fixed but has no brief_ref" % p["name"])
        if p.get("decision") is not None and not re.match(r"^D-\d{2,3}$", str(p["decision"])):
            err("parameters.yaml: %s decision id malformed" % p["name"])
        if p.get("learning") not in ("may_propose", "no"):
            err("parameters.yaml: %s learning flag invalid" % p["name"])
        m = p.get("mirror")
        if m:
            doc = cfg_cache.setdefault(m["file"], load(os.path.join(ROOT, m["file"])))
            mirror_checked += 1
            try:
                other = dig(doc, m["path"])
            except (KeyError, TypeError):
                err("parameters.yaml: %s mirror path %s %s not found" % (p["name"], m["file"], m["path"]))
                continue
            if not same(other, p["value"]):
                err("parameters.yaml: %s = %r but %s %s = %r" % (p["name"], p["value"], m["file"], m["path"], other))
    # every parameter of the three config files that carries a scalar must be registered (no orphan threshold)
    for src, block in (("config/guardrails.yaml", GUARDRAILS["parameters"]), ("config/escalation_rules.yaml", ESC_RULES["constants"]),
                       ("config/escalation_rules.yaml", ESC_RULES["proposals"])):
        for k, v in block.items():
            if isinstance(v, (int, float, str)) and not isinstance(v, bool) and k not in seen and k != "turn_unit":
                err("parameters.yaml: %s in %s is not registered" % (k, src))
    stats["governed_parameters"] = len(gov)
    stats["project_parameters"] = len(P["project_parameters"])
    stats["by_reference_families"] = len(P.get("by_reference", []))
    stats["mirrors_checked"] = mirror_checked
    stats["learning_may_propose"] = sum(1 for x in list(gov.values()) + P["project_parameters"] if x.get("learning") == "may_propose")
except (yaml.YAMLError, KeyError, TypeError) as exc:
    err("config/parameters.yaml: cannot validate: %r" % exc)

# ---------------------------------------------------------------------------------------------- 4. system prompt layers
LAYERS = {  # layer: (file, name, purpose, update frequency, immutable) from A12.1 p.33 and A12.2
    0: ("layer0-identity.md", "Identity", "Agent identity", "Quarterly or on rebrand", True),
    1: ("layer1-safety.md", "Safety", "Immutable safety", "Annual (requires RC approval)", True),
    2: ("layer2-regulatory.md", "Regulatory", "Compliance boundaries", "As regulations change (fast-track)", True),
    3: ("layer3-dialogue.md", "Dialogue", "Conversation management", "Monthly", False),
    4: ("layer4-knowledge.md", "Knowledge", "RAG instructions", "Monthly", False),
    5: ("layer5-operational.md", "Operational", "Dynamic context", "Daily or as needed", False),
}
META_KEYS = ["layer", "name", "purpose", "content", "brief_ref", "version", "status", "owner", "mutability", "learning_pipeline",
             "update_frequency", "change_process", "approval_chain", "author", "last_reviewed", "deployment_date",
             "model_version", "token_budget"]
ASSEMBLY_SLOTS = {"turn_boundary", "canary_token", "notices_block"}
prompt_text, layer_hash, layer_words = {}, {}, {}
assertion_ids = set()
for n, (fname, name, purpose, freq, immutable) in LAYERS.items():
    path = os.path.join(SP_DIR, fname)
    if not os.path.exists(path):
        err("config/system-prompt/%s missing" % fname)
        continue
    raw = read(path).replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n", raw, flags=re.S)
    if not m:
        err("%s: no YAML metadata header" % fname)
        continue
    meta = yaml.safe_load(m.group(1))
    for k in META_KEYS:
        if k not in meta:
            err("%s: metadata key %s missing" % (fname, k))
    if meta.get("layer") != n or meta.get("name") != name or meta.get("purpose") != purpose or meta.get("update_frequency") != freq:
        err("%s: layer, name, purpose or update_frequency differs from A12.1" % fname)
    if immutable and meta.get("mutability") != "immutable_to_learning_pipeline":
        err("%s: layers 0-2 must be immutable_to_learning_pipeline (A12.2)" % fname)
    if not immutable and str(meta.get("mutability", "")).startswith("immutable"):
        err("%s: layers 3-5 are modifiable (A12.2)" % fname)
    pm = re.search(r"<!-- PROMPT-BEGIN -->\n```text\n(.*?)\n```\n<!-- PROMPT-END -->", raw, flags=re.S)
    if not pm:
        err("%s: prompt text markers not found" % fname)
        continue
    text = "\n".join(line.rstrip() for line in pm.group(1).split("\n"))
    prompt_text[n] = text
    layer_hash[n] = hashlib.sha256(text.encode("utf8")).hexdigest()
    layer_words[n] = len(text.split())
    if DIGIT_RE.search(re.sub(r"(?m)^[SRDK][0-9]{1,2}[.] ", "", strip_slots(text))):   # section labels such as S1. are not figures
        err("%s: prompt text contains a digit (no figures or thresholds in prompts)" % fname)
    if not all(ord(c) < 128 for c in text):
        err("%s: prompt text is not ASCII" % fname)
    for s in SLOT_RE.findall(text):
        if s not in ASSEMBLY_SLOTS:
            err("%s: unknown assembly slot {{%s}}" % (fname, s))
    if "SHOULD" not in text or "MUST NOT" not in text:
        err("%s: needs both SHOULD and MUST NOT instructions (A12.2)" % fname)
    for secret in (r"api[_ ]?key", r"password\s*[:=]", r"https?://", r"\b[a-z0-9-]+\.internal\b", r"bearer "):
        if re.search(secret, text.lower()):
            err("%s: prompt text matches secret pattern %s" % (fname, secret))
    # assertions
    rows = [ln for ln in raw.split("\n") if re.match(r"^\| PA-L%d-\d\d \|" % n, ln)]
    if not rows:
        err("%s: no testable assertions" % fname)
    for ln in rows:
        aid = ln.split("|")[1].strip()
        if aid in assertion_ids:
            err("%s: duplicate assertion id %s" % (fname, aid))
        assertion_ids.add(aid)
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        for g in re.findall(r"GR-[A-Z]{3}-[A-Z0-9]+", cells[-2]):
            if g not in GR_IDS:
                err("%s %s: unknown guardrail %s" % (fname, aid, g))
        tests = [x.strip() for x in cells[-1].split(",") if x.strip()]
        if not tests:
            err("%s %s: no test mapped" % (fname, aid))
        for x in tests:
            if x not in TEST_IDS:
                err("%s %s: mapped test %s does not exist" % (fname, aid, x))
    budget = meta.get("token_budget", 0)
    est = int(round(layer_words[n] * 1.35))
    if est > budget:
        err("%s: estimated %d tokens (words x 1.35) exceeds token_budget %d" % (fname, est, budget))
stats["layers"] = len(prompt_text)
stats["assertions"] = len(assertion_ids)
stats["layer_words"] = layer_words

# overlap scan: no template text may share atk_prompt_overlap_words consecutive words with layers 0-2 (GR-ATK-06 would block it)
N = GUARDRAILS["parameters"]["atk_prompt_overlap_words"]
grams = set()
for n in (0, 1, 2):
    w = words(strip_slots(prompt_text.get(n, "")))
    grams |= {" ".join(w[i:i + N]) for i in range(len(w) - N + 1)}
overlap_checked = 0
for tid, t in templates.items():
    for v in t.get("variants", []):
        w = words(strip_slots((v.get("text") or {}).get("en", "")))
        overlap_checked += 1
        for i in range(len(w) - N + 1):
            if " ".join(w[i:i + N]) in grams:
                err("%s/%s: shares %d consecutive words with prompt layers 0-2: %r" % (tid, v.get("key"), N, " ".join(w[i:i + N])))
                break
stats["overlap_variants_checked"] = overlap_checked

# manifest
man_path = os.path.join(SP_DIR, "manifest.yaml")
if len(layer_hash) == 6:
    bundle = hashlib.sha256("\n".join("%d:%s" % (n, layer_hash[n]) for n in range(6)).encode("utf8")).hexdigest()
    immut = hashlib.sha256("\n".join("%d:%s" % (n, layer_hash[n]) for n in range(3)).encode("utf8")).hexdigest()
    if "--rehash" in sys.argv:
        raw = read(man_path)
        man = yaml.safe_load(raw)
        ver = man["bundle"]["bundle_version"]
        raw = re.sub(r'prompt_version: "[^"]*"', 'prompt_version: "sp-%s+%s.%s"' % (ver, bundle[:8], man["bundle"]["notice_set"]), raw)
        raw = re.sub(r'bundle_sha256: "[^"]*"', 'bundle_sha256: "%s"' % bundle, raw)
        raw = re.sub(r'immutable_sha256: "[^"]*"', 'immutable_sha256: "%s"' % immut, raw)
        for n in range(6):
            raw = re.sub(r'(\{layer: %d, file: [^,]+, version: "[^"]*", )sha256: "[^"]*", words: \d+\}' % n,
                         lambda mm, n=n: '%ssha256: "%s", words: %d}' % (mm.group(1), layer_hash[n], layer_words[n]), raw)
        with io.open(man_path, "w", encoding="utf8", newline="\n") as fh:
            fh.write(raw)
        print("manifest rehashed")
    if os.path.exists(man_path):
        man = load(man_path)
        b = man["bundle"]
        if b["bundle_sha256"] != bundle or b["immutable_sha256"] != immut:
            err("manifest.yaml: bundle or immutable hash is stale (a layer text changed: bump its version, then --rehash)")
        if b["prompt_version"] != "sp-%s+%s.%s" % (b["bundle_version"], bundle[:8], b["notice_set"]):
            err("manifest.yaml: prompt_version does not match the scheme sp-<version>+<hash8>.<notice set>")
        for k in ("author", "approval_chain", "deployment_date", "model_version"):
            if k not in b:
                err("manifest.yaml: A12.2 metadata %s missing" % k)
        for row in man["layers"]:
            n = row["layer"]
            if row["sha256"] != layer_hash[n]:
                err("manifest.yaml: layer %d hash is stale" % n)
        stats["prompt_version"] = b["prompt_version"]
    else:
        err("config/system-prompt/manifest.yaml missing")

# ---------------------------------------------------------------------------------------------- 5. documents and hygiene
OWNED = tpl_files + [labels_path, params_path, man_path] + [os.path.join(SP_DIR, v[0]) for v in LAYERS.values()] + [
    os.path.join(SP_DIR, "README.md"), os.path.join(TPL_DIR, "README.md"),
    os.path.join(ROOT, "docs", "architecture", "conversation-design.md"),
    os.path.join(ROOT, "tests", "templates", "README.md"), os.path.abspath(__file__)]
docs_checked = 0
for path in OWNED:
    if not os.path.exists(path):
        err("%s missing" % rel(path))
        continue
    docs_checked += 1
    txt = read(path)
    if re.search(r"\bPLAN\b", txt):
        err("%s: references the planning file" % rel(path))
    if "\r\n" in txt:
        warnings.append("%s: CRLF line endings" % rel(path))
    if path.endswith((".md", ".py")) or os.path.basename(path) in ("parameters.yaml", "manifest.yaml"):
        bad = sorted({c for c in txt if ord(c) > 127})
        if bad:
            err("%s: non-ASCII characters %s" % (rel(path), bad[:8]))
    else:   # template YAML: non-ASCII allowed only on Hindi lines
        for i, line in enumerate(txt.split("\n"), 1):
            if any(ord(c) > 127 for c in line) and not re.match(r"^\s*(hi:|fallback:|.*\bhi: )", line):
                err("%s:%d: non-ASCII outside a Hindi field" % (rel(path), i))
    for d in re.findall(r"\bD-(\d{2,3})\b", txt):
        if int(d) > 155:
            err("%s: decision D-%s is outside the allowed range" % (rel(path), d))
for doc in (os.path.join(TPL_DIR, "README.md"), os.path.join(ROOT, "docs", "architecture", "conversation-design.md")):
    if os.path.exists(doc):
        txt = read(doc)
        for tid in templates:
            if tid not in txt:
                err("%s: template %s is not listed" % (rel(doc), tid))
stats["owned_files_checked"] = docs_checked

# ---------------------------------------------------------------------------------------------- report
print("templates: %(templates)d in %(template_files)d files, %(variants)d variants" % stats)
print("  by family: %s" % json.dumps(stats["by_family"], sort_keys=True))
print("  by mode:   %s" % json.dumps(stats["by_mode"], sort_keys=True))
print("TPL references elsewhere in the repo: %(tpl_references)d in %(files_referencing_templates)d files, all resolved" % stats
      if not any("is not a template id" in e for e in errors) else "TPL references: unresolved ids found")
if "governed_parameters" in stats:
    print("parameters: %(governed_parameters)d governed (A12.3), %(project_parameters)d project, %(by_reference_families)d families by "
          "reference, %(mirrors_checked)d mirror values compared, %(learning_may_propose)d open to learning proposals" % stats)
print("system prompt: %(layers)d layers, %(assertions)d assertions, words per layer %(layer_words)s" % stats)
if "prompt_version" in stats:
    print("prompt_version: %s" % stats["prompt_version"])
print("overlap scan: %(overlap_variants_checked)d English variants against layers 0-2; owned files checked: %(owned_files_checked)d" % stats)
for w in warnings:
    print("WARNING %s" % w)
for e in errors:
    print("ERROR %s" % e)
print("RESULT %s (%d errors, %d warnings)" % ("PASS" if not errors else "FAIL", len(errors), len(warnings)))
sys.exit(0 if not errors else 1)
