"""Validate the Day 14 compliance and risk artefacts.

Usage: python tests/compliance/validate_compliance.py   (needs PyYAML; uses jsonschema when importable)
Exit code 0 = all checks pass. Light harness only: the documents and the brief are the source of truth.

Checks
  1  config/audit_log.schema.json is a valid JSON Schema and the three examples validate against it
  2  the examples hold no full identifier pattern (card, Aadhaar, PAN, phone, OTP) and carry only the brief's top-level fields
  3  every A10.1 and A10.2 field of the brief (transcribed below from the brief text) is in the schema, with its type,
     values and retention, and no other top-level field exists
  4  the same fields are in docs/compliance/audit-logging.md, with the brief's retention for A10.1
  5  every GR- ESC- KB- D- DM- KPI- RISK- (and EQ- FT- AQ- RPT- QG- INV- RED- XTR- TPL- case) ID cited in the owned files exists
     where it is defined
  6  risk register: columns, scales, score arithmetic, residual <= inherent, severity rule, brief rows, counts, heat maps, top 10
  7  fairness pairs: parse, one differing attribute per pair, identical expected outcomes, at least 12 pairs
  8  numbers: volume and cost model, fairness sample sizes, repository counts quoted in the owned documents
  9  docs/compliance/submission-checklist.md counts equal counts recomputed from the repository
"""
import csv
import glob
import json
import math
import os
import re
import sys
from statistics import NormalDist

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
# Mutation testing points these at a scratch copy of the owned files. Default: the repository.
OWN = os.environ.get("COMPLIANCE_OWN_ROOT", ROOT)


def P(*a):
    return os.path.join(ROOT, *a)


def O(*a):
    return os.path.join(OWN, *a)


def read(path):
    with open(path, encoding="utf8") as f:
        return f.read()


ERR, WARN, INFO = [], [], []


def err(check, msg):
    ERR.append("[%s] %s" % (check, msg))


def warn(check, msg):
    WARN.append("[%s] %s" % (check, msg))


# --------------------------------------------------------------------------------------------------
# Transcription of the brief (ZeTheta PDF, A10.1 p.27, A10.2 p.28, A11.1 p.30, A11.2 p.31, A11.3 pp.31-32)
# --------------------------------------------------------------------------------------------------
A101 = [  # field, type as the brief writes it, retention as the brief writes it
    ("conversation_id", "UUID", "7 years"),
    ("customer_id", "UUID (hashed)", "7 years"),
    ("channel", "Enum", "7 years"),
    ("authentication_level", "Enum", "7 years"),
    ("primary_intent", "String", "7 years"),
    ("resolution_status", "Enum", "7 years"),
    ("guardrails_activated", "Array[String]", "7 years"),
    ("csat_score", "Float (1-5)", "3 years"),
    ("model_version", "String", "7 years"),
    ("turn_count", "Integer", "7 years"),
    ("pii_detected", "Boolean", "7 years"),
]
A102 = ["turn_id", "speaker", "raw_message", "intent_classification", "entities_extracted", "sentiment_score",
        "knowledge_items_retrieved", "retrieval_confidence", "agent_response", "response_generation_method",
        "guardrails_checked", "guardrails_triggered", "response_latency_ms", "action_taken"]
A102_SUB = {  # sub-fields and value sets the brief names
    "intent_classification": ["label", "confidence", "alternatives"],
    "entities_extracted": ["type", "value", "confidence", "validation"],
}
CHANNELS = {"chat", "voice", "whatsapp", "app"}
RESOLUTION = {"resolved_ai", "resolved_human", "unresolved", "escalated"}
SPEAKERS = {"customer", "agent", "system"}
METHODS = {"template", "llm", "hybrid"}
ACTIONS = {"respond", "clarify", "confirm", "escalate", "authenticate"}
# A11.1 and A11.2 (the PDF table text is interleaved; this is the reading by row order): risk, prob, impact, severity
BRIEF_RISKS = {
    "RISK-T-01": ("Medium", "Critical", "P0"), "RISK-T-02": ("High", "High", "P1"),
    "RISK-T-03": ("Medium", "Medium", "P2"), "RISK-T-04": ("Medium", "Critical", "P0"),
    "RISK-T-05": ("Low", "Critical", "P1"), "RISK-T-06": ("Medium", "Medium", "P2"),
    "RISK-B-01": ("Medium", "High", "P1"), "RISK-B-02": ("Low", "Critical", "P0"),
    "RISK-B-03": ("Low", "Critical", "P1"), "RISK-B-04": ("Low", "Critical", "P0"),
}
# A11.1 (p.30) and A11.2 (p.31) as the brief prints them: risk, probability, impact, severity, mitigation required.
# The PDF text is interleaved; this is the reading by row order, checked against the page images on Day 14 (audit).
A111_ROWS = [
    ("LLM hallucination producing incorrect financial info", "Medium", "Critical", "P0", "Response grounding, KB cross-check, financial figure validation"),
    ("Model drift degrading performance", "High", "High", "P1", "Continuous monitoring, drift detection, retraining triggers"),
    ("Context window overflow in complex conversations", "Medium", "Medium", "P2", "Summarisation, sliding window, priority retention"),
    ("KB staleness from delayed regulatory updates", "Medium", "Critical", "P0", "Regulatory fast-track, staleness alerts, version-tagged KB with expiry"),
    ("Cascading failures across components", "Low", "Critical", "P1", "Circuit breaker, bulkhead isolation, rule-based fallback"),
    ("Latency spikes during peak hours", "Medium", "Medium", "P2", "Auto-scaling, request queuing, response caching, CDN for static KB"),
]
A112_ROWS = [
    ("Customer churn from poor AI experience", "Medium", "High", "P1", "Real-time CSAT, auto-escalation on negative sentiment, A/B testing"),
    ("Regulatory penalty for non-compliant AI", "Low", "Critical", "P0", "Compliance layer, mandatory testing, quarterly regulatory audit"),
    ("Reputational damage from viral negative interaction", "Low", "Critical", "P1", "Quality monitoring, crisis response, detect potentially viral conversations"),
    ("Legal liability from AI-caused customer loss", "Low", "Critical", "P0", "Comprehensive guardrails, legal review, insurance, audit trail"),
]
# A10.3 (pp.28-29), the sixteen requirement lines exactly as the brief prints them. audit-logging.md quotes them in sections 8.1, 11.1 and 12.1.
A103_QUOTES = [
    "All log data encrypted at rest using AES-256 encryption",
    "All log data encrypted in transit using TLS 1.3",
    "PII fields additionally encrypted with separate key (double encryption)",
    "Encryption keys rotated quarterly through hardware security module (HSM)",
    "Customer right-to-deletion requests processed within 30 days",
    "Deletion includes all copies, backups, and derived data including model training data",
    "Deletion certificates generated and stored for regulatory proof",
    "Monthly AI interaction summary for RBI (volume, escalation rates, complaint categories)",
    "Quarterly customer complaint analysis per Banking Ombudsman requirements",
    "Annual AI system audit report covering accuracy, fairness, and safety metrics",
    "Ad-hoc regulatory query responses within 48 hours of receipt",
]
BRIEF_ETHICAL = 15  # A11.3: 4 fairness + 4 transparency + 3 accountability + 4 privacy statements
LIK = {1: "Low", 2: "Medium", 3: "High"}
IMP = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
LIK_R = {v: k for k, v in LIK.items()}
IMP_R = {v: k for k, v in IMP.items()}


def band(score):
    return "red" if score >= 8 else ("amber" if score >= 4 else "green")


def severity_by_rule(l, i, regulatory_or_legal):
    if i == 4:
        return "P0" if (l >= 2 or regulatory_or_legal) else "P1"
    return "P1" if i == 3 else "P2"


# --------------------------------------------------------------------------------------------------
# Repository counters (shared by check 9 and by the checklist generator)
# --------------------------------------------------------------------------------------------------
def _yaml(path):
    with open(path, encoding="utf8") as f:
        return yaml.safe_load(f)


def repo_counts():
    c = {}
    intents = _yaml(P("config", "intents.yaml"))["intents"]
    c["intents"] = len(intents)
    c["primary_classes"] = len(_yaml(P("config", "intents.yaml"))["primary_classes"])
    c["intents_with_3_levels"] = sum(1 for i in intents if i.get("primary") and i.get("secondary") and i.get("tertiary"))
    rows = list(csv.DictReader(open(P("docs", "intent-taxonomy", "utterances.csv"), encoding="utf8")))
    per = {}
    for r in rows:
        per[r["intent_id"]] = per.get(r["intent_id"], 0) + 1
    c["utterances_total"] = len(rows)
    c["utterances_min_per_intent"] = min(per.values()) if len(per) == len(intents) else 0
    c["disambiguation_diagrams"] = len(glob.glob(P("diagrams", "disambiguation-*.mmd")))
    kb = 0
    for f in glob.glob(P("docs", "knowledge-base", "entries", "*.yaml")):
        kb += len(_yaml(f)["entries"])
    c["kb_entries"] = kb
    adv, boss, vectors = 0, 0, set()
    for f in glob.glob(P("tests", "adversarial", "*.yaml")):
        d = _yaml(f)
        adv += len(d["cases"])
        boss += sum(1 for x in d["cases"] if x.get("boss"))
        vectors.add(d["vector"])
    c["adversarial_cases"], c["adversarial_boss"], c["attack_vectors"] = adv, boss, len(vectors)
    c["guardrail_cases"] = sum(len(_yaml(f)["cases"]) for f in glob.glob(P("tests", "guardrails", "*.yaml")))
    g = _yaml(P("config", "guardrails.yaml"))["guardrails"]
    c["guardrails"] = len(g)
    c["security_rules"] = len({x["id"] for x in g if re.fullmatch(r"GR-SEC-R[1-8]", x["id"])})
    esc = _yaml(P("config", "escalation_rules.yaml"))
    c["escalation_triggers"] = len(esc["triggers"])
    c["extra_rules"] = len(esc["extra_rules"])
    c["handoff_elements"] = len(esc["handoff_package"]["elements"])
    tpl = 0
    for f in glob.glob(P("config", "templates", "*.yaml")):
        d = _yaml(f)
        if isinstance(d, dict) and "templates" in d:
            tpl += len(d["templates"])
    c["templates"] = tpl
    m = _yaml(P("tests", "safety-suite", "manifest.yaml"))
    c["safety_cases"] = len(m["cases"])
    c["prompt_layers"] = len(glob.glob(P("config", "system-prompt", "layer[0-5]-*.md")))
    ci = read(P("docs", "architecture", "component-interfaces.md"))
    c["components"] = len(re.findall(r"^\| (\d+) \| ", ci.split("## Cross-cutting")[0], re.M))
    c["fmea_rows"] = len(re.findall(r"^\| \d+ \|", read(P("docs", "architecture", "failure-modes.md")), re.M))
    c["simulations"] = len(glob.glob(P("simulations", "conv-*.md")))
    cl = read(P("CHANGELOG.md"))
    c["changelog_days"] = len(re.findall(r"^## Day \d+", cl, re.M))
    c["changelog_days_complete"] = 0
    for blk in re.split(r"^## Day ", cl, flags=re.M)[1:]:
        if all(h in blk for h in ("**Tasks completed**", "**Decisions", "**Challenges**", "**Open questions**", "**Next")):
            c["changelog_days_complete"] += 1
    need = ["README.md", "docs/architecture", "docs/intent-taxonomy", "docs/knowledge-base", "docs/guardrails",
            "docs/learning-pipeline", "docs/escalation", "docs/metrics", "diagrams", "simulations", "tests", "config",
            "CHANGELOG.md"]
    c["structure_present"] = sum(1 for n in need if os.path.exists(P(*n.split("/"))))
    c["structure_required"] = len(need)
    cd = read(P("docs", "architecture", "conversation-design.md"))
    c["patterns"] = len(set(re.findall(r"^### \d\.\d (P[1-5]) ", cd, re.M)))
    c["anti_patterns"] = len(set(re.findall(r"^\| (AP[1-8]) \|", cd, re.M)))
    dash = read(P("docs", "metrics", "dashboards.md"))
    c["dashboards"] = len(re.findall(r"^## \d\. (Real-Time Operations|Daily Performance|Weekly Strategic) dashboard", dash, re.M))
    ic = read(P("docs", "metrics", "improvement-cycle.md"))
    c["cycle_stages"] = len([s for s in ("DETECT", "DIAGNOSE", "DESIGN", "DEPLOY", "VALIDATE", "DOCUMENT")
                             if re.search(r"^\| %s \|" % s, ic, re.M)])
    lsc = read(P("docs", "architecture", "latency-scalability-cost.md"))
    c["scale_rows"] = len(re.findall(r"^\| (1x|10x|100x) \|", lsc, re.M))
    c["latency_budget_3s"] = 1 if re.search(r"\b3 s\b|\b3 seconds\b|< ?3 ?s", lsc) else 0
    c["retrieval_200ms"] = 1 if "200 ms" in read(P("docs", "knowledge-base", "retrieval-pipeline.md")) else 0
    personas = set()
    for f in glob.glob(P("tests", "adversarial", "*.yaml")) + glob.glob(P("tests", "guardrails", "*.yaml")):
        for x in _yaml(f)["cases"]:
            personas.add(x.get("persona"))
    c["personas"] = len(personas & {"Priya", "Rajesh", "Meera", "Arjun", "Sunita", "Vikram"})
    c["boss_l2"] = len(_yaml(P("tests", "nlu", "boss-level2.yaml"))["cases"])
    c["boss_l3"] = len(_yaml(P("tests", "kb", "boss-level3.yaml"))["cases"])
    c["boss_l6"] = len(_yaml(P("tests", "escalation", "boss-level6.yaml"))["cases"])
    c["boss_l1_doc"] = 1 if os.path.exists(P("docs", "architecture", "boss-trace.md")) else 0
    c["boss_l5_doc"] = 1 if os.path.exists(P("docs", "learning-pipeline", "boss-level5.md")) else 0
    c["feedback_sources"] = len([s for s in ("supervisor-corrections.md", "csat-signals.md", "outcome-tracking.md")
                                 if os.path.exists(P("docs", "learning-pipeline", s))])
    c["state_machine"] = len([p for p in (P("diagrams", "dialogue-state-machine.mmd"), P("docs", "architecture", "dialogue-management.md"))
                              if os.path.exists(p)])
    c["regulatory_obligations"] = len(re.findall(r"^\| M-\d+ \|", read(P("docs", "guardrails", "regulatory-mapping.md")), re.M))
    c["diagrams"] = len(glob.glob(P("diagrams", "*.mmd")))
    c["hallucination_traps"] = sum(1 for x in m["cases"] if x.get("suite_category") == "hallucination_trap")
    for k in range(1, 9):
        c["ap%d" % k] = 1 if re.search(r"^\| AP%d \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]*\S" % k, cd, re.M) else 0
    for lvl, files in DR_FILES.items():
        c["dr%d" % lvl] = sum(1 for f in files if os.path.exists(P(*f.split("/"))))
    return c


# Deliverable files per campaign level (D-02: the 7 deliverable requirements are read as the 7 levels)
DR_FILES = {
    1: ["docs/architecture/system-architecture.md", "docs/architecture/component-interfaces.md", "docs/architecture/dialogue-management.md",
        "docs/architecture/failure-modes.md", "docs/architecture/latency-scalability-cost.md", "docs/architecture/boss-trace.md",
        "diagrams/architecture.mmd", "diagrams/dialogue-state-machine.mmd", "config/dialogue_state.schema.json"],
    2: ["config/intents.yaml", "config/entities.yaml", "docs/intent-taxonomy/taxonomy.md", "docs/intent-taxonomy/entities.md",
        "docs/intent-taxonomy/disambiguation.md", "docs/intent-taxonomy/sentiment.md", "docs/intent-taxonomy/language-detection.md",
        "docs/intent-taxonomy/utterances.csv", "docs/architecture/nlu-pipeline-overview.md", "tests/nlu/boss-level2.yaml"],
    3: ["docs/knowledge-base/kb-schema.md", "docs/knowledge-base/retrieval-pipeline.md", "docs/knowledge-base/maintenance-workflow.md",
        "docs/knowledge-base/access-control-matrix.md", "docs/knowledge-base/README.md", "diagrams/kb-er-model.mmd",
        "diagrams/retrieval-pipeline.mmd", "tests/kb/boss-level3.yaml", "tests/kb/validate_kb_entries.py"],
    4: ["docs/guardrails/account-security.md", "docs/guardrails/adversarial-defences.md", "docs/guardrails/financial-advice.md",
        "docs/guardrails/incident-response-playbook.md", "docs/guardrails/monitoring-dashboard.md", "docs/guardrails/output-safety-layer.md",
        "docs/guardrails/regulatory-mapping.md", "config/guardrails.yaml", "diagrams/guardrail-layers.mmd", "tests/README.md",
        "tests/adversarial/data-exfiltration.yaml", "tests/adversarial/denial-of-service.yaml", "tests/adversarial/identity-spoofing.yaml",
        "tests/adversarial/jailbreak.yaml", "tests/adversarial/prompt-injection.yaml", "tests/adversarial/social-engineering.yaml",
        "tests/guardrails/account-security.yaml", "tests/guardrails/advice.yaml", "tests/guardrails/output-safety-system.yaml",
        "tests/guardrails/regulatory.yaml"],
    5: ["docs/learning-pipeline/overview.md", "docs/learning-pipeline/supervisor-corrections.md", "docs/learning-pipeline/csat-signals.md",
        "docs/learning-pipeline/outcome-tracking.md", "docs/learning-pipeline/data-pipeline.md", "docs/learning-pipeline/ab-testing.md",
        "docs/learning-pipeline/safety-invariants.md", "docs/learning-pipeline/boss-level5.md", "diagrams/learning-loop.mmd",
        "tests/safety-suite/manifest.yaml", "tests/safety-suite/validate_manifest.py"],
    6: ["docs/escalation/triggers.md", "docs/escalation/routing-and-handoff.md", "docs/escalation/queue-management.md",
        "config/escalation_rules.yaml", "diagrams/escalation-routing.mmd", "docs/metrics/kpi-framework.md", "docs/metrics/improvement-cycle.md",
        "docs/metrics/dashboards.md", "tests/escalation/boss-level6.yaml", "tests/escalation/validate_escalation.py",
        "config/system-prompt/manifest.yaml", "config/parameters.yaml", "config/templates/README.md", "tests/templates/validate_templates.py"],
    7: ["docs/compliance/audit-logging.md", "config/audit_log.schema.json", "diagrams/audit-log-flow.mmd", "docs/risk/risk-matrix.md",
        "docs/risk/fairness-testing.md", "tests/compliance/fairness-pairs.yaml", "tests/compliance/validate_compliance.py",
        "docs/compliance/submission-checklist.md", "README.md", "CHANGELOG.md", "docs/requirements-traceability.md"],
}


# --------------------------------------------------------------------------------------------------
# Check 1 and 2: schema and examples
# --------------------------------------------------------------------------------------------------
def load_schema():
    return json.load(open(O("config", "audit_log.schema.json"), encoding="utf8"))


def check_schema_and_examples():
    schema = load_schema()
    try:
        import jsonschema
        mode = "jsonschema %s" % __import__("importlib.metadata", fromlist=["version"]).version("jsonschema")
        cls = jsonschema.validators.validator_for(schema)
        try:
            cls.check_schema(schema)
        except Exception as e:
            err(1, "schema is not a valid JSON Schema: %s" % str(e)[:200])
            return mode
        if "2020-12" not in schema.get("$schema", ""):
            err(1, "schema declares %s, the documents say 2020-12" % schema.get("$schema"))
        v = cls(schema, format_checker=jsonschema.FormatChecker())
        for f in sorted(glob.glob(O("tests", "compliance", "examples", "*.json"))):
            errs = list(v.iter_errors(json.load(open(f, encoding="utf8"))))
            if errs:
                err(1, "%s does not validate: %s at %s" % (os.path.basename(f), errs[0].message[:160],
                                                           "/".join(str(p) for p in errs[0].absolute_path)))
    except ImportError:
        mode = "structural fallback (jsonschema not importable)"
        for f in sorted(glob.glob(O("tests", "compliance", "examples", "*.json"))):
            rec = json.load(open(f, encoding="utf8"))
            rt = rec.get("ext", {}).get("record_type")
            d = schema["$defs"]["conversation_record" if rt == "conversation" else "turn_record"]
            missing = [k for k in d["required"] if k not in rec]
            extra = [k for k in rec if k not in d["properties"]]
            if missing or extra:
                err(1, "%s: missing %s extra %s" % (os.path.basename(f), missing, extra))
    return mode


SECRET_PATTERNS = {
    "card number": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "Aadhaar": re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"),
    "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "phone": re.compile(r"(?<!\d)(?:\+91[ -]?)?[6-9]\d{9}(?!\d)"),
    "OTP-like 6 digits near 'otp'": re.compile(r"(?i)otp\D{0,12}\d{6}\b"),
}


SEALED_OK = re.compile(r"^(?:SYNTHETIC-CIPHERTEXT[-A-Z0-9_]*|(?:v\d+:)?[A-Za-z0-9+/_-]{24,}={0,2})$")


def check_sealed_fields(fname, node, path=""):
    """A field the schema types as ciphertext must hold a sealed or synthetic-ciphertext marker, never readable text."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "ciphertext" and isinstance(v, str):
                erased = bool(node.get("erased"))
                if v == "" and erased:
                    continue
                if not SEALED_OK.match(v):
                    err(2, "%s: %s.ciphertext holds readable text, not a sealed value: %r" % (fname, path or "/", v[:40]))
            else:
                check_sealed_fields(fname, v, path + "/" + k)
    elif isinstance(node, list):
        for k, v in enumerate(node):
            check_sealed_fields(fname, v, "%s[%d]" % (path, k))


def check_examples_hygiene():
    files = sorted(glob.glob(O("tests", "compliance", "examples", "*.json")))
    if len(files) < 3:
        err(2, "expected 3 example records, found %d" % len(files))
    kinds = set()
    for f in files:
        text = read(f)
        for name, rx in SECRET_PATTERNS.items():
            for m in rx.finditer(text):
                s = m.group(0)
                if re.fullmatch(r"[0-9a-f]{8}-[0-9a-f-]+", s) or (re.fullmatch(r"[0-9a-f]{20,}", s) and re.search(r"[a-f]", s)):
                    continue                      # a UUID or a hex digest, never a bare run of digits
                err(2, "%s: looks like a full %s: %r" % (os.path.basename(f), name, s[:30]))
        rec = json.loads(text)
        kinds.add((rec["ext"]["record_type"], rec.get("speaker")))
        check_sealed_fields(os.path.basename(f), rec)
    if files and not ({("conversation", None), ("turn", "customer"), ("turn", "agent")} <= kinds):
        err(2, "examples must cover a conversation record, a customer turn and an agent turn; found %s" % sorted(kinds, key=str))


# --------------------------------------------------------------------------------------------------
# Check 3 and 4: brief fields in schema and document
# --------------------------------------------------------------------------------------------------
def resolve(schema, node):
    seen = 0
    while isinstance(node, dict) and "$ref" in node and seen < 10:
        cur = schema
        for part in node["$ref"].lstrip("#/").split("/"):
            cur = cur[part]
        node = cur
        seen += 1
    return node


def check_brief_fields_in_schema():
    schema = load_schema()
    d = schema["$defs"]
    conv, turn = d["conversation_record"], d["turn_record"]
    cp, tp = conv["properties"], turn["properties"]
    for name, typ, ret in A101:
        if name not in cp:
            err(3, "A10.1 field %s missing from conversation_record" % name)
            continue
        desc = cp[name].get("description", "")
        if ret not in desc:
            err(3, "A10.1 field %s: retention %r not stated in its description" % (name, ret))
        node = resolve(schema, cp[name])
        t = node.get("type")
        want = {"UUID": "string", "UUID (hashed)": None, "Enum": "string", "String": "string", "Array[String]": "array",
                "Float (1-5)": "number", "Integer": "integer", "Boolean": "boolean"}[typ]
        if want and want not in (t if isinstance(t, list) else [t]):
            err(3, "A10.1 field %s: brief type %s but schema type %s" % (name, typ, t))
    extra = sorted(set(cp) - {n for n, _, _ in A101} - {"ext"})
    if extra:
        err(3, "conversation_record has top-level fields that are not in A10.1: %s" % extra)
    if conv.get("additionalProperties") is not False:
        err(3, "conversation_record must set additionalProperties false")
    ch = resolve(schema, cp["channel"])
    if set(ch.get("enum", [])) != CHANNELS:
        err(3, "channel enum %s differs from the brief's four channels" % ch.get("enum"))
    rs = resolve(schema, cp["resolution_status"])
    if set(rs.get("enum", [])) != RESOLUTION:
        err(3, "resolution_status enum %s differs from the brief" % rs.get("enum"))
    cs = resolve(schema, cp["csat_score"])
    if cs.get("minimum") != 1 or cs.get("maximum") != 5:
        err(3, "csat_score range must be 1 to 5")
    for name in A102:
        if name not in tp:
            err(3, "A10.2 field %s missing from turn_record" % name)
    extra = sorted(set(tp) - set(A102) - {"ext"})
    if extra:
        err(3, "turn_record has top-level fields that are not in A10.2: %s" % extra)
    if turn.get("additionalProperties") is not False:
        err(3, "turn_record must set additionalProperties false")
    for fld in A102:
        if fld in tp and tp[fld].get("x-brief") != "A10.2":
            err(3, "turn field %s lacks the x-brief marker" % fld)
    for fld, subs in A102_SUB.items():
        node = resolve(schema, tp.get(fld, {}))
        flat = json.dumps(node)
        for s in subs:
            if '"%s"' % s not in flat:
                err(3, "A10.2 %s: sub-field %s missing from the schema" % (fld, s))
    sp = resolve(schema, tp["speaker"])
    if set(sp.get("enum", [])) != SPEAKERS:
        err(3, "speaker enum differs from customer/agent/system")
    me = resolve(schema, tp["response_generation_method"])
    if {x for x in me.get("enum", []) if x} != METHODS:
        err(3, "response_generation_method enum differs from template/llm/hybrid")
    ac = resolve(schema, tp["action_taken"])
    if {x for x in ac.get("enum", []) if x} != ACTIONS:
        err(3, "action_taken enum differs from respond/clarify/confirm/escalate/authenticate")
    ss = resolve(schema, tp["sentiment_score"])
    if ss.get("minimum") != -1 or ss.get("maximum") != 1:
        err(3, "sentiment_score range must be -1 to 1")
    return len(A101), len(A102)


def check_brief_fields_in_doc():
    doc = read(O("docs", "compliance", "audit-logging.md"))
    for name, typ, ret in A101:
        rows = [ln for ln in doc.split("\n") if ln.startswith("| `%s` |" % name)]
        okrow = [ln for ln in rows if typ in ln and ret in ln.split("|")[-2]]
        if not okrow:
            err(4, "audit-logging.md section 2.1 has no row `%s` | %s | ... | %s" % (name, typ, ret))
    sec3 = doc.split("### 3.1")[1].split("### 3.2")[0] if "### 3.1" in doc and "### 3.2" in doc else ""
    for name in A102:
        if "| `%s` |" % name not in sec3:
            err(4, "audit-logging.md section 3.1 has no row for `%s`" % name)
    quote = "turn_id, speaker (customer/agent/system), encrypted raw_message with PII redacted"
    if quote not in doc:
        err(4, "audit-logging.md no longer quotes the A10.2 sentence")
    for phrase in ("AES-256", "TLS 1.3", "quarterly", "30 days", "within 48 hours", "Monthly AI interaction summary for RBI",
                   "Banking Ombudsman", "Annual AI system audit report", "meta-audit trail", "Deletion certificates"):
        if phrase not in doc:
            err(4, "audit-logging.md lacks the brief's phrase %r" % phrase)
    for q in A103_QUOTES:
        if '"%s"' % q not in doc:
            err(4, "audit-logging.md does not quote the brief's A10.3 line exactly: %r" % q)
    nq = len(re.findall(r"^\*\*AQ-\d+\.", doc, re.M))
    if nq < 10:
        err(4, "audit-logging.md has %d worked audit queries, at least 10 are required" % nq)
    for sec in ("## 2. ", "## 3. ", "## 5. ", "## 7. ", "## 8. ", "## 9. ", "## 10. ", "## 11. ", "## 12. ", "## 13. ", "## 14. ",
                "## 15. ", "## 16. "):
        if sec not in doc:
            err(4, "audit-logging.md lacks section %s" % sec.strip())
    return nq


# --------------------------------------------------------------------------------------------------
# Check 5: cited IDs exist
# --------------------------------------------------------------------------------------------------
CITE = re.compile(
    r"(?<![A-Za-z0-9-])("
    r"GR-[A-Z]+-R?\d+(?:-\d+)?|ESC-\d{3}|ESC-T-\d+-\d+|KB-[A-Z]+-\d+|D-\d+|DM-\d+|KPI-[A-Z]\d+|RISK-[TBE]-\d+|"
    r"EQ-\d+|FT-\d+|AQ-\d+|RPT-\d+|QG-\d+|INV-\d+|RED-\d+|XTR-\d+|TPL-[A-Z]+(?:-[A-Z0-9]+)+|FAIR-\d+(?:-[ab])?|SS-[A-Z]+-\d+"
    r")(?![A-Za-z0-9\[])")
PENDING_DECISIONS = {"D-%d" % n for n in range(181, 191)}  # in the Day 14 handoff, not yet merged into the decisions log
AUDIT_FIX_DECISIONS = {"D-%d" % n for n in range(200, 208)}  # Day 14 audit fixes, same status


def collect_definitions():
    defs = set()
    files = []
    for pat in ("docs/**/*.md", "config/**/*.yaml", "config/**/*.md", "tests/**/*.yaml", "tests/**/*.md", "config/*.json"):
        files += glob.glob(P(*pat.split("/")), recursive=True)
    row = re.compile(r"^\|\s*\**`?([A-Z][A-Za-z]*(?:-[A-Za-z0-9]+)+)`?\**(?:\s|\|)", re.M)
    yid = re.compile(r"^\s*-?\s*(?:id|rule_id|trigger_id|set_id):\s*['\"]?([A-Z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+)['\"]?\s*$", re.M)
    bold = re.compile(r"^\*\*([A-Z][A-Za-z]*-[A-Za-z0-9-]+)[\.\*]", re.M)
    head = re.compile(r"^#+ .*?\b([A-Z]{2,4}-[0-9A-Z]+(?:-[0-9]+)?)\b", re.M)
    for f in files:
        try:
            t = read(f)
        except UnicodeDecodeError:
            continue
        for rx in (row, yid, bold):
            defs.update(rx.findall(t))
        if f.endswith(".md"):
            defs.update(head.findall(t))
    return defs


def check_cited_ids():
    defs = collect_definitions()
    # IDs the owned documents define themselves
    own_docs = [O("docs", "compliance", "audit-logging.md"), O("docs", "risk", "risk-matrix.md"), O("docs", "risk", "fairness-testing.md")]
    for f in own_docs:
        t = read(f)
        defs.update(re.findall(r"^\|\s*\**`?([A-Z]+-[A-Z0-9-]+)`?\**\s*\|", t, re.M))
        defs.update(re.findall(r"^\*\*([A-Z]+-[0-9]+)\.", t, re.M))
    defs.update(c["id"] for c in _yaml(O("tests", "compliance", "fairness-pairs.yaml"))["cases"])
    files = own_docs + [O("config", "audit_log.schema.json"), O("tests", "compliance", "fairness-pairs.yaml"),
                        O("diagrams", "audit-log-flow.mmd")] + sorted(glob.glob(O("tests", "compliance", "examples", "*.json")))
    # decisions log rows
    dec = read(P("docs", "assumptions-and-decisions.md"))
    decisions = set(re.findall(r"^\| (D-\d+) \|", dec, re.M))
    defs |= decisions
    seen, missing, pending = {}, {}, set()
    for f in files:
        t = read(f)
        for m in CITE.findall(t):
            seen.setdefault(m, set()).add(os.path.basename(f))
    for ident, where in seen.items():
        if ident in defs:
            continue
        if ident in PENDING_DECISIONS or ident in AUDIT_FIX_DECISIONS:
            pending.add(ident)
            continue
        # a range written as "GR-REG-01 to GR-REG-20" cites both ends; a case ID is checked as a case ID
        missing[ident] = where
    for ident, where in sorted(missing.items()):
        err(5, "%s is cited in %s and is not defined anywhere" % (ident, ", ".join(sorted(where))))
    for p in sorted(pending):
        warn(5, "%s is defined only in the Day 14 handoff (not merged into the decisions log yet)" % p)
    # decisions the owned files claim: each of D-181..D-190 must be cited at least once
    cited_new = sorted(PENDING_DECISIONS & set(seen))
    for d in sorted(PENDING_DECISIONS):
        if d not in seen:
            warn(5, "%s is reserved for this work but not cited in any owned file" % d)
    return len(seen), len(cited_new)


# --------------------------------------------------------------------------------------------------
# Check 6: risk register
# --------------------------------------------------------------------------------------------------
def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def parse_risk_doc():
    text = read(O("docs", "risk", "risk-matrix.md"))
    assess, control = {}, {}
    for line in text.split("\n"):
        if not line.startswith("| RISK-"):
            continue
        cells = split_row(line)
        if len(cells) == 9 and re.fullmatch(r"\d [A-Z][a-z]+", cells[4]):
            assess[cells[0]] = cells
        elif len(cells) == 9:
            control[cells[0]] = cells
    return text, assess, control


def lv(cell):
    m = re.fullmatch(r"(\d) ([A-Z][a-z]+)", cell)
    return (int(m.group(1)), m.group(2)) if m else (None, None)


def heat_map(register, residual):
    cells = {}
    for rid, r in register.items():
        l, i = (r["rl"], r["ri"]) if residual else (r["l"], r["i"])
        cells.setdefault((i, l), []).append(rid)
    return cells


def check_risk_register():
    text, assess, control = parse_risk_doc()
    required_ctl = ["controls", "rl", "ri", "residual", "band", "owner", "metric", "contingency"]
    if set(assess) != set(control):
        err(6, "risk IDs differ between assessment and control tables: %s" % sorted(set(assess) ^ set(control)))
    reg = {}
    for rid, a in assess.items():
        c = control.get(rid)
        if not c:
            continue
        for k, name in enumerate(["ID", "Risk", "Origin", "Cause", "L", "I", "Inherent", "Severity", "Rationale"]):
            if not a[k]:
                err(6, "%s: empty column %s in the assessment table" % (rid, name))
        for k, name in enumerate(["ID", "Controls", "Residual L", "Residual I", "Residual", "Band", "Owner", "Monitoring metric",
                                  "Contingency"]):
            if not c[k]:
                err(6, "%s: empty column %s in the control table" % (rid, name))
        l, ln = lv(a[4]); i, inn = lv(a[5]); rl, rln = lv(c[2]); ri, rin = lv(c[3])
        if None in (l, i, rl, ri):
            err(6, "%s: a likelihood or impact cell is not '<number> <label>'" % rid)
            continue
        if not (1 <= l <= 3 and 1 <= rl <= 3):
            err(6, "%s: likelihood outside 1..3" % rid)
        if not (1 <= i <= 4 and 1 <= ri <= 4):
            err(6, "%s: impact outside 1..4" % rid)
        if ln != LIK.get(l) or rln != LIK.get(rl) or inn != IMP.get(i) or rin != IMP.get(ri):
            err(6, "%s: label does not match number (%s %s %s %s)" % (rid, a[4], a[5], c[2], c[3]))
        try:
            inh, res = int(a[6]), int(c[4])
        except ValueError:
            err(6, "%s: score is not an integer" % rid)
            continue
        if inh != l * i:
            err(6, "%s: inherent %d but %d x %d = %d" % (rid, inh, l, i, l * i))
        if res != rl * ri:
            err(6, "%s: residual %d but %d x %d = %d" % (rid, res, rl, ri, rl * ri))
        if res > inh:
            err(6, "%s: residual %d is above inherent %d" % (rid, res, inh))
        if rl > l or ri > i:
            err(6, "%s: residual likelihood or impact is above the inherent one" % rid)
        if c[5] != band(res):
            err(6, "%s: band %s but residual %d is %s" % (rid, c[5], res, band(res)))
        if a[7] not in ("P0", "P1", "P2"):
            err(6, "%s: severity %r" % (rid, a[7]))
        # controls must carry at least one concrete reference: a backticked path or an ID
        if not (re.search(r"`[^`]+`", c[1]) or CITE.search(c[1])):
            err(6, "%s: the controls column holds no repository reference" % rid)
        for ref in re.findall(r"`([^`]+\.(?:md|yaml|json|py|mmd|csv))`", c[1]):
            ref0 = ref.split(" ")[0]
            if not (os.path.exists(P(*ref0.split("/"))) or os.path.exists(O(*ref0.split("/")))):
                err(6, "%s: control reference %s does not exist" % (rid, ref0))
        if not re.search(r"(KPI|DM|EQ|FT|AQ|QG)-", c[7]):
            err(6, "%s: monitoring metric %r names no metric ID" % (rid, c[7]))
        reg[rid] = dict(l=l, i=i, rl=rl, ri=ri, inh=inh, res=res, sev=a[7], origin=a[2], band=c[5], risk=a[1])
    # the brief's rows
    for rid, (pb, ib, sb) in BRIEF_RISKS.items():
        r = reg.get(rid)
        if not r:
            err(6, "brief risk %s missing" % rid)
            continue
        if (LIK[r["l"]], IMP[r["i"]], r["sev"]) != (pb, ib, sb):
            err(6, "%s: (%s, %s, %s) differs from the brief (%s, %s, %s)" % (rid, LIK[r["l"]], IMP[r["i"]], r["sev"], pb, ib, sb))
        if not r["origin"].startswith("brief"):
            err(6, "%s: origin should be the brief" % rid)
    # severity rule reproduces the brief's ten rows
    regulatory_legal = {"RISK-B-02", "RISK-B-04"}
    for rid in BRIEF_RISKS:
        if rid in reg and severity_by_rule(reg[rid]["l"], reg[rid]["i"], rid in regulatory_legal) != BRIEF_RISKS[rid][2]:
            err(6, "%s: the severity rule of section 2.4 does not reproduce the brief's severity" % rid)
    # the brief's matrices as reproduced in sections 3.1 and 4.1 must equal the transcription above, cell by cell
    for sec_a, sec_b, rows, label in (("### 3.1", "### 3.2", A111_ROWS, "A11.1 (section 3.1)"), ("### 4.1", "### 4.2", A112_ROWS, "A11.2 (section 4.1)")):
        part = text.split(sec_a)[1].split(sec_b)[0] if sec_a in text and sec_b in text else ""
        got = []
        for ln in part.split("\n"):
            if ln.startswith("|") and not ln.startswith("| Risk") and not ln.startswith("|---"):
                got.append(tuple(split_row(ln)))
        if got != [tuple(r) for r in rows]:
            for k, (g, w) in enumerate(zip(got + [None] * len(rows), rows)):
                if g != tuple(w):
                    err(6, "%s row %d differs from the brief: document %s, brief %s" % (label, k + 1, g, w))
            if len(got) != len(rows):
                err(6, "%s has %d rows, the brief has %d" % (label, len(got), len(rows)))
    # section 2.4 table agrees with the brief rows
    for m in re.finditer(r"^\| (RISK-[TB]-\d+) \| (\w+) \| (\w+) \| (P\d) \| (P\d) \| (yes|no) \|", text, re.M):
        rid, pb, ib, sb, sr, match = m.groups()
        if BRIEF_RISKS.get(rid) != (pb, ib, sb):
            err(6, "section 2.4 row %s disagrees with the brief transcription" % rid)
        if (sb == sr) != (match == "yes"):
            err(6, "section 2.4 row %s: Match column is wrong" % rid)
    # counts
    n = {k: sum(1 for r in reg if r.startswith("RISK-%s-" % k)) for k in "TBE"}
    brief_n = sum(1 for r in reg.values() if r["origin"].startswith("brief"))
    m = re.search(r"Register size: (\d+) risks \((\d+) technical, (\d+) business, (\d+) ethical\); (\d+) from the brief and (\d+) additions", text)
    if not m:
        err(6, "the register-size sentence is missing")
    else:
        want = tuple(int(x) for x in m.groups())
        got = (len(reg), n["T"], n["B"], n["E"], brief_n, len(reg) - brief_n)
        if want != got:
            err(6, "register size says %s, recomputed %s" % (want, got))
    if brief_n != 6 + 4 + BRIEF_ETHICAL:
        err(6, "expected 25 brief-origin risks, found %d" % brief_n)
    # ethical statements table maps 15 statements to RISK-E-01..15
    stm = re.findall(r"^\| (\d+) \| (?:Fairness & Bias|Transparency|Accountability|Privacy) \| \"[^\"]+\" \| (RISK-E-\d+) \|", text, re.M)
    if len(stm) != BRIEF_ETHICAL or [s[1] for s in stm] != ["RISK-E-%02d" % k for k in range(1, 16)]:
        err(6, "section 5.1 does not map the 15 A11.3 statements to RISK-E-01..15 in order")
    # bands and sums
    for kind, key_l, key_i, key_s in (("inherent", "l", "i", "inh"), ("residual", "rl", "ri", "res")):
        bands = {"red": 0, "amber": 0, "green": 0}
        for r in reg.values():
            bands[band(r[key_s])] += 1
        total = sum(r[key_s] for r in reg.values())
        col = 1 if kind == "inherent" else 2
        for bn, rng in (("red", "8 to 12"), ("amber", "4 to 6"), ("green", "1 to 3")):
            mm = re.search(r"^\| %s \(%s\) \| (\d+) \| (\d+) \|" % (bn, rng), text, re.M)
            if not mm or int(mm.group(col)) != bands[bn]:
                err(6, "band table %s %s: document %s, recomputed %d" % (kind, bn, mm.group(col) if mm else None, bands[bn]))
        mm = re.search(r"^\| Sum of scores \| (\d+) \| (\d+) \|", text, re.M)
        if not mm or int(mm.group(col)) != total:
            err(6, "sum of %s scores: document %s, recomputed %d" % (kind, mm.group(col) if mm else None, total))
    si = sum(r["inh"] for r in reg.values()); sr_ = sum(r["res"] for r in reg.values())
    mm = re.search(r"The sum of scores falls by ([\d.]+) percent", text)
    if not mm or abs(float(mm.group(1)) - round(100 * (si - sr_) / si, 1)) > 0.05:
        err(6, "'falls by' percentage: document %s, recomputed %.1f" % (mm.group(1) if mm else None, 100 * (si - sr_) / si))
    same = sorted(rid for rid, r in reg.items() if r["inh"] == r["res"])
    mm = re.search(r"(\d+) risks keep their inherent score \(([^)]*)\)", text)
    if not mm or int(mm.group(1)) != len(same) or sorted(x.strip() for x in mm.group(2).split(",")) != same:
        err(6, "risks keeping their inherent score: document %s, recomputed %s" % (mm.group(0)[:80] if mm else None, same))
    # heat maps
    blocks = re.findall(r"```\n(.*?)```", text.split("## 6. Heat maps")[1].split("| Band |")[0], re.S)
    for blk, residual in zip(blocks, (False, True)):
        cells = heat_map(reg, residual)
        lines = blk.split("\n")
        idx = [k for k, ln in enumerate(lines) if re.match(r"I\d ", ln)]
        for row_no, k in enumerate(idx):
            imp = 4 - row_no
            head_cells = lines[k].split("|")
            ids_by_col = {1: [], 2: [], 3: []}
            j = k + 1
            while j < len(lines) and not lines[j].startswith("---") and lines[j].strip():
                parts = lines[j].split("|")
                for col in (1, 2, 3):
                    if col < len(parts):
                        ids_by_col[col] += re.findall(r"[TBE]-\d+", parts[col])
                j += 1
            for col in (1, 2, 3):
                want_ids = sorted(x.replace("RISK-", "") for x in cells.get((imp, col), []))
                score = imp * col
                cell_txt = head_cells[col].strip() if col < len(head_cells) else ""
                want_txt = "score %d %s n=%d" % (score, band(score), len(want_ids))
                if cell_txt != want_txt:
                    err(6, "%s heat map I%d L%d: '%s' but recomputed '%s'" % ("residual" if residual else "inherent", imp, col, cell_txt, want_txt))
                if sorted(ids_by_col[col]) != want_ids:
                    err(6, "%s heat map I%d L%d lists %s, recomputed %s" % ("residual" if residual else "inherent", imp, col,
                                                                          sorted(ids_by_col[col]), want_ids))
    # top 10
    rank = sorted(reg, key=lambda r: (-reg[r]["res"], -reg[r]["ri"], -reg[r]["inh"], r))[:10]
    sec7 = text.split("## 7. Top 10")[1].split("## 8.")[0]
    listed = re.findall(r"^\| (\d+) \| (RISK-[TBE]-\d+) \| .*? \| (\d+) \| (\d+) \| (red|amber|green) \|", sec7, re.M)
    if [x[1] for x in listed] != rank or [int(x[0]) for x in listed] != list(range(1, 11)):
        err(6, "top 10 residual: document %s, recomputed %s" % ([x[1] for x in listed], rank))
    for _, rid, inh, res, bd in listed:
        if rid in reg and (int(inh), int(res), bd) != (reg[rid]["inh"], reg[rid]["res"], reg[rid]["band"]):
            err(6, "top 10 row %s: scores differ from the register" % rid)
    # section 10 residual column
    for m in re.finditer(r"^\| (RISK-[TBE]-\d+) \| .*? \| (D-[^|]*) \| (\d+) (red|amber|green) \|", text.split("## 10.")[1], re.M):
        rid, _, res, bd = m.groups()
        if rid in reg and (int(res), bd) != (reg[rid]["res"], reg[rid]["band"]):
            err(6, "section 10 row %s: residual differs from the register" % rid)
    # FMEA mapping
    fm = text.split("### 3.4")[1].split("## 4.")[0]
    mapped = {int(a): b for a, b in re.findall(r"^\| #(\d+) \| ([^|]+) \|", fm, re.M)}
    n_fmea = len(re.findall(r"^\| \d+ \|", read(P("docs", "architecture", "failure-modes.md")), re.M))
    if sorted(mapped) != list(range(1, n_fmea + 1)):
        err(6, "section 3.4 maps FMEA rows %s but failure-modes.md has %d rows" % (sorted(mapped), n_fmea))
    for k, ids in mapped.items():
        for rid in re.findall(r"RISK-[TBE]-\d+", ids):
            if rid not in reg:
                err(6, "section 3.4 row #%d cites %s which is not in the register" % (k, rid))
    # appetite statement and sections
    for needle in ("## 8. Risk appetite", "### 8.1 Statement", "### 8.2 Acceptance rule", "## 7. Top 10 residual risks"):
        if needle not in text:
            err(6, "risk-matrix.md lacks %r" % needle)
    return reg, n


# --------------------------------------------------------------------------------------------------
# Check 7: fairness pairs
# --------------------------------------------------------------------------------------------------
def flatten(x, prefix=""):
    out = {}
    if isinstance(x, dict):
        for k, v in x.items():
            out.update(flatten(v, prefix + "." + str(k) if prefix else str(k)))
    else:
        out[prefix] = json.dumps(x, sort_keys=True)
    return out


PROFILE_KEYS = {"display_name", "age_band", "gender", "region", "value_tier", "tenure_band", "complaints_90d", "occupation", "repeat_contact_7d"}


def check_fairness_pairs():
    path = O("tests", "compliance", "fairness-pairs.yaml")
    try:
        d = _yaml(path)
    except yaml.YAMLError as e:
        err(7, "fairness-pairs.yaml does not parse: %s" % str(e)[:150])
        return 0
    cases = d.get("cases", [])
    pairs = {}
    for c in cases:
        pairs.setdefault(c.get("pair"), {})[c.get("side")] = c
    if d.get("pair_count") != len(pairs) or d.get("case_count") != len(cases):
        err(7, "header says %s pairs and %s cases, found %d and %d" % (d.get("pair_count"), d.get("case_count"), len(pairs), len(cases)))
    if len(pairs) < 12:
        err(7, "%d pairs, at least 12 are required" % len(pairs))
    guard = {g["id"] for g in _yaml(P("config", "guardrails.yaml"))["guardrails"]}
    intents = {i["id"] for i in _yaml(P("config", "intents.yaml"))["intents"]}
    ids = [c["id"] for c in cases]
    if len(set(ids)) != len(ids):
        err(7, "duplicate case IDs")
    outcome_keys = ("expected_action", "expected_guardrails", "expected_escalation", "behaviour_checks", "must_not_contain", "severity",
                    "category", "vector", "persona", "intent", "preconditions")
    for pid, sides in sorted(pairs.items(), key=lambda kv: str(kv[0])):
        if set(sides) != {"a", "b"}:
            err(7, "%s: needs exactly sides a and b, has %s" % (pid, sorted(sides)))
            continue
        a, b = sides["a"], sides["b"]
        if a["id"] != "%s-a" % pid or b["id"] != "%s-b" % pid:
            err(7, "%s: case IDs should be %s-a and %s-b" % (pid, pid, pid))
        varies = a.get("varies")
        if b.get("varies") != varies:
            err(7, "%s: the sides name different 'varies' attributes" % pid)
        fa, fb = flatten({k: v for k, v in a.items() if k not in ("id", "side")}), flatten({k: v for k, v in b.items() if k not in ("id", "side")})
        diff = {k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k)}
        if varies in PROFILE_KEYS:
            allowed = {"fixture.profile." + varies}
        elif varies == "channel":
            allowed = {"fixture.channel"}
        elif varies == "language":
            allowed = {"language"} | {k for k in diff if k.startswith("input_turns")}
        else:
            err(7, "%s: 'varies' = %r is not a profile key, channel or language" % (pid, varies))
            continue
        if diff != allowed and not (varies == "language" and "language" in diff and diff <= allowed):
            err(7, "%s: sides differ in %s, expected exactly %s" % (pid, sorted(diff), sorted(allowed)))
        if varies == "language" and "language" not in diff:
            err(7, "%s: varies language but the language field is the same" % pid)
        for k in outcome_keys:
            if json.dumps(a.get(k), sort_keys=True) != json.dumps(b.get(k), sort_keys=True):
                err(7, "%s: expected outcome field %s differs between sides" % (pid, k))
        for s in (a, b):
            for g in s.get("expected_guardrails", []):
                if g not in guard:
                    err(7, "%s: unknown guardrail %s" % (s["id"], g))
            if s.get("intent") not in intents:
                err(7, "%s: unknown intent %s" % (s["id"], s.get("intent")))
            for e in s.get("expected_escalation", []) or []:
                if not re.fullmatch(r"ESC-0(0[1-9]|1[0-5])", e):
                    err(7, "%s: unknown escalation trigger %s" % (s["id"], e))
            if "expected_action" not in s or s["expected_action"] not in ("allow", "redirect", "escalate", "block", "mask"):
                err(7, "%s: expected_action missing or outside the vocabulary" % s["id"])
        if varies in PROFILE_KEYS and fa.get("fixture.profile." + varies) == fb.get("fixture.profile." + varies):
            err(7, "%s: varies %s but the value is the same" % (pid, varies))
    return len(pairs)


# --------------------------------------------------------------------------------------------------
# Check 8: numbers
# --------------------------------------------------------------------------------------------------
Z = NormalDist().inv_cdf


def n_diff(p, d, alpha=0.05, power=0.80):
    p2 = p + d
    za, zb = Z(1 - alpha / 2), Z(power)
    return math.ceil((za + zb) ** 2 * (p * (1 - p) + p2 * (1 - p2)) / d ** 2)


def n_equiv(p, margin, alpha=0.05, power=0.80):
    za, zb = Z(1 - alpha), Z(1 - (1 - power) / 2)
    return math.ceil((za + zb) ** 2 * 2 * p * (1 - p) / margin ** 2)


def n_mean(sd, margin, alpha=0.05, power=0.80):
    za, zb = Z(1 - alpha), Z(1 - (1 - power) / 2)
    return math.ceil((za + zb) ** 2 * 2 * sd ** 2 / margin ** 2)


def mde(n, p, alpha=0.05, power=0.8):
    return (Z(1 - alpha / 2) + Z(power)) * math.sqrt(2 * p * (1 - p) / n)


VOL = dict(n=18000, replies=7, cust=7, sysd=2, kb_conv=2.5, kb_cust=2.0, kb_agent=6.0, kb_sys=1.0, ret_share=0.6, kb_ret=1.5,
           tool_per_agent=0.5, kb_tool=0.8, esc=0.30, kb_pkg=6.0, acc=0.5, kb_acc=0.4, seal=1.15, comp=2.5, replicas=3, backups=1,
           hot=90, warm=730, total=7 * 365, idx=0.5, p_hot=0.10, p_warm=0.03, p_cold=0.005, peak=3, customers=2_700_000)


def volume(scale):
    v = VOL
    n = v["n"] * scale
    turns = v["replies"] + v["cust"] + v["sysd"]
    kb = (v["kb_conv"] + v["cust"] * v["kb_cust"] + v["replies"] * v["kb_agent"] + v["sysd"] * v["kb_sys"]
          + v["replies"] * v["ret_share"] * v["kb_ret"] + v["replies"] * v["tool_per_agent"] * v["kb_tool"]
          + v["esc"] * v["kb_pkg"] + v["acc"] * v["kb_acc"])
    sealed = kb * v["seal"]
    raw = n * sealed / 1e6
    stored = raw / v["comp"]
    copies = v["replicas"] + v["backups"]
    hot = stored * v["hot"] * (1 + v["idx"]) * copies
    warm = stored * (v["warm"] - v["hot"]) * copies
    cold = stored * (v["total"] - v["warm"]) * copies
    cost = hot * v["p_hot"] + warm * v["p_warm"] + cold * v["p_cold"]
    recs = n * (1 + turns + v["replies"] * v["ret_share"] + v["replies"] * v["tool_per_agent"] + v["esc"] + v["acc"])
    return dict(turns=turns, turn_recs=n * turns, recs=recs, avg=recs / 86400, peak=recs / 86400 * v["peak"], kb=kb, sealed=sealed,
                raw_day=raw, raw_year=raw * 365, raw_7=raw * v["total"], stored_7=stored * v["total"], hot=hot, warm=warm, cold=cold,
                total=hot + warm + cold, cost=cost, per_int=cost / (n * 30), conv_7=n * v["total"], turn_7=n * turns * v["total"])


def fmt(x, nd=0):
    return ("{:,.%df}" % nd).format(x)


def check_numbers():
    doc = read(O("docs", "compliance", "audit-logging.md"))
    v1, v10 = volume(1), volume(10)
    exp = [
        ("Turn records per conversation", [str(v1["turns"])]),
        ("Turn records per day", [fmt(v1["turn_recs"]), fmt(v10["turn_recs"])]),
        ("All log records per day", [fmt(v1["recs"]), fmt(v10["recs"])]),
        ("Bus throughput", ["%.1f and %.1f" % (v1["avg"], v1["peak"]), "%.1f and %.1f" % (v10["avg"], v10["peak"])]),
        ("Size per conversation", ["%.2f KB and %.2f KB" % (v1["kb"], v1["sealed"])]),
        ("Raw volume per day and per year", ["%.3f GB and %s GB" % (v1["raw_day"], fmt(v1["raw_year"], 1)),
                                             "%.3f GB and %s GB" % (v10["raw_day"], fmt(v10["raw_year"], 1))]),
        ("Raw volume over 7 years", [fmt(v1["raw_7"]) + " GB", fmt(v10["raw_7"]) + " GB"]),
        ("Stored, one compressed copy", [fmt(v1["stored_7"]) + " GB", fmt(v10["stored_7"]) + " GB"]),
        ("Steady state, 4 copies", ["%s, %s and %s GB" % (fmt(v1["hot"]), fmt(v1["warm"]), fmt(v1["cold"])),
                                    "%s, %s and %s GB" % (fmt(v10["hot"]), fmt(v10["warm"]), fmt(v10["cold"]))]),
        ("Steady state total", [fmt(v1["total"]) + " GB", fmt(v10["total"]) + " GB"]),
        ("Storage cost per month", ["about USD %s" % fmt(v1["cost"]), "about USD %s" % fmt(v10["cost"])]),
        ("Storage cost per interaction", ["USD %.5f" % v1["per_int"]]),
        ("Conversation records held", [fmt(v1["conv_7"]), fmt(v10["conv_7"])]),
        ("Turn records held", [fmt(v1["turn_7"]), fmt(v10["turn_7"])]),
    ]
    for label, vals in exp:
        line = next((ln for ln in doc.split("\n") if ln.startswith("| " + label)), None)
        if line is None:
            err(8, "audit-logging.md section 16 has no row starting %r" % label)
            continue
        for val in vals:
            if val not in line:
                err(8, "audit-logging.md section 16 row %r: expected %r (recomputed), row says: %s" % (label, val, line[:140]))
    buf_mb = 18000 * VOL["peak"] / 24 * 4 * v1["sealed"] / 1000
    if "about %d MB" % round(buf_mb) not in doc:
        err(8, "audit-logging.md buffer sizing: recomputed %.0f MB (4 hours at the peak factor)" % buf_mb)
    dels = [round(VOL["customers"] * r / 52) for r in (0.001, 0.005, 0.02)]
    want = "the weekly batch is %s, %s and %s requests" % (fmt(dels[0]), fmt(dels[1]), fmt(dels[2]))
    if want not in doc:
        err(8, "audit-logging.md deletion workload: expected %r (2.7 million customers at 0.1, 0.5 and 2.0 percent a year)" % want)
    if "about 1 percent of the roughly USD 8,000" in doc and not (0.5 <= 100 * v1["cost"] / 8000 <= 1.5):
        err(8, "audit-logging.md says storage is about 1 percent of USD 8,000 a month; recomputed %.2f percent" % (100 * v1["cost"] / 8000))
    # fairness sample sizes
    fdoc = read(O("docs", "risk", "fairness-testing.md"))
    rows = [("Escalation rate (FT-03) |", 0.30, 0.02), ("Escalation rate, sensitivity |", 0.20, 0.02), ("Containment (FT-05) |", 0.70, 0.02),
            ("Guardrail false positive (FT-07) |", 0.03, 0.01), ("ESC-004 fire rate (FT-03) |", 0.05, 0.01),
            ("Missed escalation among true triggers", 0.05, 0.03), ("Premature escalation among reviewed", 0.10, 0.03)]
    for label, p, m in rows:
        line = next((ln for ln in fdoc.split("\n") if ln.startswith("| " + label)), None)
        if line is None:
            err(8, "fairness-testing.md section 5 has no row %r" % label)
            continue
        cells = split_row(line)
        want = [fmt(n_diff(p, m)), fmt(n_equiv(p, m)), fmt(n_equiv(p, m, alpha=0.05 / 10))]
        if cells[-3:] != want:
            err(8, "fairness-testing.md row %r: %s but recomputed %s" % (label.strip(" |"), cells[-3:], want))
    line = next((ln for ln in fdoc.split("\n") if ln.startswith("| CSAT mean (FT-06)")), "")
    want = [fmt(n_mean(1.3, 0.1)) + " ratings", fmt(n_mean(1.3, 0.1, alpha=0.005)) + " ratings"]
    if split_row(line)[-2:] != want:
        err(8, "fairness-testing.md CSAT row: %s but recomputed %s" % (split_row(line)[-2:], want))
    line = next((ln for ln in fdoc.split("\n") if ln.startswith("| CSAT mean, standard deviation 1.0")), "")
    want = ["%s and %s ratings" % (fmt(n_mean(1.0, 0.1)), fmt(n_mean(1.5, 0.1))),
            "%s and %s ratings" % (fmt(n_mean(1.0, 0.1, alpha=0.005)), fmt(n_mean(1.5, 0.1, alpha=0.005)))]
    if split_row(line)[-2:] != want:
        err(8, "fairness-testing.md CSAT sd row: %s but recomputed %s" % (split_row(line)[-2:], want))
    ne, nc = n_equiv(0.30, 0.02), n_mean(1.3, 0.1)
    for share in (0.02, 0.05, 0.10, 0.25, 0.50):
        conv = 18000 * share
        rat = conv * 0.15
        line = next((ln for ln in fdoc.split("\n") if ln.startswith("| %d percent |" % round(share * 100))), None)
        want = [fmt(conv), "%.1f" % (ne / conv), fmt(rat), "%.1f" % (nc / rat)]
        if line is None or split_row(line)[1:] != want:
            err(8, "fairness-testing.md slice row %d percent: %s but recomputed %s" % (round(share * 100), split_row(line)[1:] if line else None, want))
    flat = re.sub(r"\s+", " ", fdoc)
    parts = []
    for k, n_ in enumerate((500, 1000, 2000, 5000)):
        a_, b_ = 100 * mde(n_, 0.30), 100 * mde(n_, 0.05)
        if k == 0:
            parts.append("at %s per group, %.1f points on a base of 0.30 and %.1f points on a base of 0.05" % (fmt(n_), a_, b_))
        else:
            parts.append("at %s, %.1f and %.1f" % (fmt(n_), a_, b_))
    if "; ".join(parts) not in flat:
        err(8, "fairness-testing.md minimum detectable gaps: expected %r" % "; ".join(parts))
    # counterfactual bounds
    for n_, pct in ((15, None),):
        ub = 100 * (1 - 0.05 ** (1 / n_))
        if "the bound is %.2f percent" % ub not in fdoc:
            err(8, "fairness-testing.md: the bound for 15 pairs should be %.2f percent" % ub)
    need = {t: math.ceil(math.log(0.05) / math.log(1 - t)) for t in (0.05, 0.01, 0.005)}
    if not ("5 percent needs %d pairs, 1 percent needs %d, and 0.5 percent needs %d" % (need[0.05], need[0.01], need[0.005])) in fdoc:
        err(8, "fairness-testing.md pair counts: recomputed %s" % need)
    base = 15 * 2 + 7 * 2 + 6 + 10
    attrs = {"name": 3, "lang": 3, "region": 3, "age": 3, "gender": 2, "tier": 2, "channel": 4, "history": 2, "register": 2}
    swaps = sum(v * (v - 1) // 2 for v in attrs.values())
    gen = base * swaps
    if not ("gives %s pairs, or %s replays" % (fmt(gen), fmt(gen * 2 * 3))) in fdoc:
        err(8, "fairness-testing.md generated matrix: %d base x %d swaps = %d pairs, %d replays" % (base, swaps, gen, gen * 6))
    if "bounds the rate at %.3f percent" % (100 * (1 - 0.05 ** (1 / gen))) not in fdoc:
        err(8, "fairness-testing.md: zero discordant in %d should bound the rate at %.3f percent" % (gen, 100 * (1 - 0.05 ** (1 / gen))))
    # repository counts quoted in the owned documents
    c = repo_counts()
    rdoc = read(O("docs", "risk", "risk-matrix.md"))
    claims = [
        (rdoc, r"(\d+) guardrails \(`config/guardrails.yaml`", c["guardrails"]),
        (rdoc, r"fixed suite of (\d+) cases", c["safety_cases"]),
        (rdoc, r"(\d+) mapped obligations", c["regulatory_obligations"]),
        (rdoc, r"Re-walk of the (\d+) obligations", c["regulatory_obligations"]),
        (rdoc, r"template mode for (\d+) of \d+ templates", None),
        (rdoc, r"(\d+) adversarial cases with (\d+) boss", None),
        (rdoc, r"(\d+) cases in `tests/escalation/`", None),
        (rdoc, r"Commission native review of the (\d+) templates", c["templates"]),
        (fdoc, r"(\d+) triggers and the (\d+) extra rules", None),
    ]
    for text_, rx, want in claims:
        for m in re.finditer(rx, text_, re.I):
            got = [int(g) for g in m.groups()]
            if want is not None and got[0] != want:
                err(8, "document says %d for /%s/, recomputed %d" % (got[0], rx[:40], want))
            if "template mode for" in rx and (got[0], int(re.search(r"of (\d+) templates", m.group(0)).group(1))) != (None, None):
                pass
    tm = re.search(r"template mode for (\d+) of (\d+) templates", rdoc)
    modes = {"template": 0}
    for f in glob.glob(P("config", "templates", "*.yaml")):
        d = _yaml(f)
        if isinstance(d, dict) and "templates" in d:
            for t in d["templates"]:
                if t.get("mode") == "template" or t.get("generation_mode") == "template":
                    modes["template"] += 1
    if tm and (int(tm.group(2)) != c["templates"]):
        err(8, "risk-matrix.md says %s templates, recomputed %d" % (tm.group(2), c["templates"]))
    if tm and modes["template"] and int(tm.group(1)) != modes["template"]:
        err(8, "risk-matrix.md says %s template-mode templates, recomputed %d" % (tm.group(1), modes["template"]))
    am = re.search(r"(\d+) adversarial cases with (\d+) boss", rdoc)
    if am and (int(am.group(1)), int(am.group(2))) != (c["adversarial_cases"], c["adversarial_boss"]):
        err(8, "risk-matrix.md says %s adversarial cases with %s boss; recomputed %d and %d" % (am.group(1), am.group(2), c["adversarial_cases"], c["adversarial_boss"]))
    em = re.search(r"(\d+) cases in `tests/escalation/`", rdoc)
    if em:
        n_esc = 0
        for f in glob.glob(P("tests", "escalation", "*.yaml")):
            n_esc += len(_yaml(f).get("cases", []))
        if int(em.group(1)) != n_esc:
            err(8, "risk-matrix.md says %s escalation cases, recomputed %d" % (em.group(1), n_esc))
    fm = re.search(r"(\d+) triggers and the (\d+) extra rules", fdoc)
    if fm and (int(fm.group(1)), int(fm.group(2))) != (c["escalation_triggers"], c["extra_rules"]):
        err(8, "fairness-testing.md says %s triggers and %s extra rules; recomputed %d and %d" % (fm.group(1), fm.group(2), c["escalation_triggers"], c["extra_rules"]))
    return v1, v10


# --------------------------------------------------------------------------------------------------
# Check 9: submission checklist
# --------------------------------------------------------------------------------------------------
# row ID -> (counter key, comparison, required). The checklist table has the columns
# ID | Requirement | Brief | Required | Repo evidence | How to count | Count now | Status
CHECKLIST_ROWS = {
    "MM-01": ("intents", ">=", 25), "MM-02": ("intents_with_3_levels", ">=", 25), "MM-03": ("utterances_min_per_intent", ">=", 10),
    "MM-04": ("utterances_total", ">=", 250), "MM-05": ("disambiguation_diagrams", "==", 6), "MM-06": ("kb_entries", ">=", 50),
    "MM-07": ("adversarial_cases", ">=", 50), "MM-08": ("attack_vectors", "==", 6), "MM-09": ("adversarial_boss", ">=", 20),
    "MM-10": ("security_rules", "==", 8), "MM-11": ("escalation_triggers", ">=", 10), "MM-12": ("escalation_triggers", "==", 15),
    "MM-13": ("handoff_elements", "==", 8), "MM-14": ("templates", ">=", 15), "MM-15": ("safety_cases", ">=", 200),
    "MM-16": ("prompt_layers", "==", 6), "MM-17": ("components", ">=", 8), "MM-18": ("fmea_rows", ">=", 12),
    "MM-19": ("scale_rows", "==", 3), "MM-20": ("latency_budget_3s", "==", 1), "MM-21": ("retrieval_200ms", "==", 1),
    "MM-22": ("patterns", "==", 5), "MM-23": ("anti_patterns", "==", 8), "MM-24": ("dashboards", "==", 3),
    "MM-25": ("cycle_stages", "==", 6), "MM-26": ("feedback_sources", "==", 3), "MM-27": ("personas", "==", 6),
    "MM-28": ("state_machine", "==", 2), "MM-29": ("structure_present", "==", 13), "MM-30": ("changelog_days", ">=", 15),
    "MM-31": ("simulations", ">=", 20), "MM-32": ("boss_l2", "==", 10), "MM-33": ("boss_l3", "==", 5),
    "MM-34": ("boss_l6", "==", 10), "MM-35": ("boss_l1_doc", "==", 1), "MM-36": ("boss_l5_doc", "==", 1),
}
CHECKLIST_ROWS.update({
    "FC-01": ("hallucination_traps", ">=", 1),
    "FC-02": ("ap1", "==", 1), "FC-03": ("ap2", "==", 1), "FC-04": ("ap3", "==", 1), "FC-05": ("ap4", "==", 1),
    "FC-06": ("ap5", "==", 1), "FC-07": ("ap6", "==", 1), "FC-08": ("ap7", "==", 1), "FC-09": ("ap8", "==", 1),
    "FC-10": ("mm_not_met", "==", 0),
})
PENDING_ROWS = {"MM-30": "pending Day 15 CHANGELOG entry"}


def compare(op, got, want):
    return got >= want if op == ">=" else got == want


def check_checklist():
    path = O("docs", "compliance", "submission-checklist.md")
    if not os.path.exists(path):
        err(9, "docs/compliance/submission-checklist.md does not exist")
        return 0
    text = read(path)
    c = repo_counts()
    c["mm_not_met"] = sum(1 for rid, (key, op, want) in CHECKLIST_ROWS.items()
                          if rid.startswith("MM-") and rid not in PENDING_ROWS and not compare(op, c[key], want))
    rows = {}
    for line in text.split("\n"):
        m = re.match(r"^\| ((?:MM|FC|DR|DD)-\d+) \|", line)
        if m:
            rows[m.group(1)] = split_row(line)
    for rid, r in rows.items():
        if len(r) != 8:
            err(9, "%s: expected 8 columns, found %d" % (rid, len(r)))
    for rid, (key, op, want) in CHECKLIST_ROWS.items():
        r = rows.get(rid)
        if not r:
            err(9, "checklist has no row %s" % rid)
            continue
        if len(r) != 8:
            continue
        shown = re.match(r"(\d+)", r[6])
        status = r[7]
        if not shown:
            err(9, "%s: 'Count now' %r holds no number" % (rid, r[6]))
            continue
        shown = int(shown.group(1))
        if rid in PENDING_ROWS:
            if PENDING_ROWS[rid].split(" ", 1)[1] not in status:
                err(9, "%s: status must say %r, found %r" % (rid, PENDING_ROWS[rid], status))
            if shown != c[key]:
                warn(9, "%s: checklist records %d at the time of writing; the repository now holds %d (another agent is writing it)" % (rid, shown, c[key]))
            continue
        if shown != c[key]:
            err(9, "%s: checklist says %d, recomputed %d (%s)" % (rid, shown, c[key], key))
        met = compare(op, c[key], want)
        if met and not status.startswith("met"):
            err(9, "%s: count %d meets %s %d but status is %r" % (rid, c[key], op, want, status))
        if not met and status.startswith("met"):
            err(9, "%s: status 'met' but count %d does not meet %s %d" % (rid, c[key], op, want))
        if str(want) not in r[3]:
            err(9, "%s: the 'Required' column %r does not state %d" % (rid, r[3], want))
    for rid, lvl in (("DR-%d" % k, k) for k in DR_FILES):
        r = rows.get(rid)
        if not r or len(r) != 8:
            err(9, "checklist has no complete row %s" % rid)
            continue
        total = len(DR_FILES[lvl])
        shown = re.match(r"(\d+) of (\d+) files", r[6])
        if not shown or int(shown.group(1)) != c["dr%d" % lvl] or int(shown.group(2)) != total:
            err(9, "%s: 'Count now' %r but recomputed %d of %d files" % (rid, r[6], c["dr%d" % lvl], total))
        if c["dr%d" % lvl] == total and not r[7].startswith("met"):
            err(9, "%s: all %d files exist but the status is %r" % (rid, total, r[7]))
        elif c["dr%d" % lvl] != total and r[7].startswith("met"):
            err(9, "%s: status 'met' but only %d of %d files exist" % (rid, c["dr%d" % lvl], total))
    for k, r in rows.items():
        if len(r) != 8:
            continue
        if not r[4]:
            err(9, "%s: no repository evidence" % k)
        if k.startswith(("MM-", "FC-")) and k != "FC-10" and not re.search(r"p\.\d+", r[2]):
            err(9, "%s: brief citation lacks a page" % k)
        if not re.match(r"(met|pending|manual|not met)", r[7]):
            err(9, "%s: status %r is not met, pending, manual or not met" % (k, r[7]))
        for ref in re.findall(r"`([^`\s]+\.(?:md|yaml|json|py|mmd|csv))`", r[4]):
            if "*" in ref:
                if not glob.glob(P(*ref.split("/"))):
                    err(9, "%s: evidence pattern %s matches nothing" % (k, ref))
            elif not os.path.exists(P(*ref.split("/"))) and not os.path.exists(O(*ref.split("/"))):
                err(9, "%s: evidence file %s does not exist" % (k, ref))
    for pref, n_exp in (("MM-", 36), ("FC-", 10), ("DR-", 7)):
        got = [k for k in rows if k.startswith(pref)]
        if len(got) != n_exp:
            err(9, "checklist has %d %s rows, expected %d" % (len(got), pref, n_exp))
    return len(rows)


# --------------------------------------------------------------------------------------------------
def main():
    print("validate_compliance: root %s%s" % (ROOT, "" if OWN == ROOT else "  (owned files read from %s)" % OWN))
    mode = check_schema_and_examples()
    print("check 1  schema + 3 examples: %s" % mode)
    check_examples_hygiene()
    print("check 2  examples hygiene (identifier patterns, record kinds)")
    nc, nt = check_brief_fields_in_schema()
    print("check 3  brief fields in schema: A10.1 %d fields, A10.2 %d fields" % (nc, nt))
    nq = check_brief_fields_in_doc()
    print("check 4  brief fields and A10.3 wording in audit-logging.md; %d worked audit queries" % nq)
    ncited, nnew = check_cited_ids()
    print("check 5  cited IDs: %d distinct IDs checked, %d of the reserved D-181..D-190 cited" % (ncited, nnew))
    reg, n = check_risk_register()
    print("check 6  risk register: %d risks (%d technical, %d business, %d ethical)" % (len(reg), n["T"], n["B"], n["E"]))
    np_ = check_fairness_pairs()
    print("check 7  fairness pairs: %d pairs" % np_)
    v1, v10 = check_numbers()
    print("check 8  numbers: 1x %s records/day, %s GB total stored, USD %s a month; repository counts quoted in the documents"
          % (fmt(v1["recs"]), fmt(v1["total"]), fmt(v1["cost"])))
    nr = check_checklist()
    print("check 9  submission checklist: %d rows" % nr)
    c = repo_counts()
    print("counts: intents %d | utterances %d | KB entries %d | adversarial %d (boss %d) | guardrail cases %d | triggers %d | templates %d | "
          "suite cases %d | layers %d | components %d | simulations %d | CHANGELOG days %d"
          % (c["intents"], c["utterances_total"], c["kb_entries"], c["adversarial_cases"], c["adversarial_boss"], c["guardrail_cases"],
             c["escalation_triggers"], c["templates"], c["safety_cases"], c["prompt_layers"], c["components"], c["simulations"], c["changelog_days"]))
    for w in WARN:
        print("WARN", w)
    for e in ERR:
        print("ERROR", e)
    print("RESULT:", "PASS" if not ERR else "FAIL (%d errors, %d warnings)" % (len(ERR), len(WARN)))
    return 0 if not ERR else 1


if __name__ == "__main__":
    sys.exit(main())
