"""Validate tests/safety-suite/manifest.yaml, the index of the fixed safety regression suite (brief A5.4).

Usage:
  python tests/safety-suite/validate_manifest.py            validate (exit code 0 = all checks pass)
  python tests/safety-suite/validate_manifest.py --rebuild  regenerate manifest.yaml from the case files, then validate

Needs PyYAML. Light harness only: it checks the structure of the specification, it does not run any case
against an agent. Rules are in tests/safety-suite/README.md and docs/learning-pipeline/safety-invariants.md.
--rebuild is add-only: it refuses to drop a case that the current manifest lists, and it never lowers case_floor.
"""
import collections
import glob
import hashlib
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MANIFEST = os.path.join(HERE, "manifest.yaml")
REFERENCED = ["tests/adversarial/*.yaml", "tests/guardrails/*.yaml",
              "tests/escalation/*.yaml"]                                # Day 10 files and Day 12 escalation files, indexed by reference
OWN = "tests/safety-suite/*.yaml"                                      # Day 11 SS-* files
MIN_CASES = 200                                                        # brief A5.4

SS_CATEGORIES = {"pii_masking", "auth_gating", "escalation_trigger", "hallucination_trap", "commitment_trap", "learning_invariant"}
SUITE_CATEGORIES = SS_CATEGORIES | {"guardrail", "adversarial"}
PERSONAS = {"Priya", "Rajesh", "Meera", "Arjun", "Sunita", "Vikram"}
ACTIONS = {"block", "redirect", "escalate", "mask", "allow"}
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM"}
ESC_IDS = ["ESC-%03d" % n for n in range(1, 16)]
REQUIRED = ["id", "category", "vector", "persona", "input_turns", "preconditions", "expected_action",
            "expected_guardrails", "must_not_contain", "severity"]
PLACEHOLDERS = {"SYN_CARD", "SYN_AADHAAR", "SYN_OTP", "SYN_CVV", "SYN_PIN", "SYN_PASSWORD", "SYN_PAN", "SYN_DOB", "SYN_PHONE_NEW",
                "SYN_LAST4", "SYN_LAST4_A", "SYN_LAST4_B", "SYN_ACCT_OWN", "SYN_ACCT_OTHER", "SYN_CUSTOMER_ID_OTHER",
                # added by the safety suite (README section 4)
                "SYN_AADHAAR_NATIVE_DIGITS", "SYN_OTP_SPELLED", "SYN_POSTAL_PIN", "SYN_DATE_FROM_TOOL"}
ID_PATTERNS = {"guardrail": r"GR-[A-Z]+-[A-Z0-9]+", "esc": r"ESC-\d{3}", "kb": r"KB-[A-Z]{3}-\d{3}", "intent": r"(?<![A-Z0-9-])(?:ACC|TXN|CRD|PRD|CMP|SEC|GEN)-\d{3}(?!-\d)",
               "red": r"RED-\d{2}"}

errors = []


def err(msg):
    errors.append(msg)


def load(path):
    with open(path, encoding="utf8") as f:
        return yaml.safe_load(f)


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def case_sha(case):
    """SHA-256 of the canonical JSON form of a case; any change to a case changes it."""
    return hashlib.sha256(json.dumps(case, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("ascii")).hexdigest()


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from strings(k)
            yield from strings(v)
    elif isinstance(x, (list, tuple)):
        for v in x:
            yield from strings(v)


# ---------------------------------------------------------------- registries
guard_reg = load(os.path.join(ROOT, "config", "guardrails.yaml"))["guardrails"]
GUARDRAILS = {g["id"]: g for g in guard_reg}
intents_doc = load(os.path.join(ROOT, "config", "intents.yaml"))
INTENTS = {i["id"]: i for i in intents_doc["intents"]}
AUTH_LEVELS = intents_doc["auth_levels"]
KB_IDS = set()
for f in glob.glob(os.path.join(ROOT, "docs", "knowledge-base", "entries", "*.yaml")):
    KB_IDS |= {e["id"] for e in load(f)["entries"]}
with open(os.path.join(ROOT, "config", "entities.yaml"), encoding="utf8") as f:
    RED_IDS = set(re.findall(r"\bRED-\d{2}\b", f.read()))
RESERVED_IDS = {"%s-%02d" % (g["id"], n) for g in guard_reg for n in range(1, g["tests_reserved"] + 1)}


def own_guardrail(case_id):
    m = re.match(r"(GR-[A-Z]+-[A-Z0-9]+)-\d{2}$", case_id)
    return m.group(1) if m else None


def suite_category(case, file_rel):
    """Mapping of tests/README.md section 8, extended with learning_invariant for GR-SYS-02 and GR-SYS-03."""
    cid = case["id"]
    if file_rel.startswith("tests/safety-suite/"):
        return case["category"]
    if file_rel.startswith("tests/escalation/"):
        return "escalation_trigger"
    gr = own_guardrail(cid)
    if gr in ("GR-SEC-R1", "GR-SEC-R5", "GR-OUT-02", "GR-REG-05", "GR-REG-06") or cid == "GR-ATK-07-02":
        return "pii_masking"
    if gr in ("GR-SEC-R2", "GR-SEC-R7", "GR-ATK-10", "GR-REG-08"):
        return "auth_gating"
    if gr in ("GR-OUT-01", "GR-OUT-03", "GR-REG-18") or cid == "GR-REG-02-02":
        return "hallucination_trap"
    if gr == "GR-OUT-05" or cid == "GR-ATK-09-02":
        return "commitment_trap"
    if gr in ("GR-SYS-02", "GR-SYS-03"):
        return "learning_invariant"
    return "adversarial" if cid.startswith("GR-ATK-") else "guardrail"


def tier(case):
    """Run order (tests/README.md section 8): 1 rule layer and system events, 2 classifier, 3 multi-turn and boss."""
    if case.get("boss") or len(case.get("input_turns", [])) > 1:
        return 3
    gr = own_guardrail(case["id"])
    if gr:
        return 1 if GUARDRAILS.get(gr, {}).get("type") == "rule" else 2
    return 1 if case["category"] in ("learning_invariant", "pii_masking", "auth_gating") else 2


def refs(case, kind):
    return sorted(set(re.findall(r"(?<![A-Z0-9])%s\b" % ID_PATTERNS[kind], " ".join(strings(case)))))


def row(case, file_rel):
    guardrails = list(case.get("expected_guardrails") or [])
    gr = own_guardrail(case["id"])
    if gr and gr not in guardrails:
        guardrails.insert(0, gr)
    esc = sorted(set(case.get("expected_escalation") or []) | {c for c in case.get("covers", []) if c.startswith("ESC-")})
    intents = sorted(set(([case["intent"]] if case.get("intent") else []) + refs(case, "intent")))
    r = collections.OrderedDict()
    r["id"] = case["id"]
    r["file"] = file_rel
    r["suite_category"] = suite_category(case, file_rel)
    r["category"] = case["category"]
    r["guardrails"] = guardrails
    r["esc"] = esc
    r["escalation_expected"] = bool(case.get("expected_escalation"))
    r["intents"] = intents
    r["kb"] = refs(case, "kb")
    r["severity"] = case["severity"]
    r["expected_action"] = case["expected_action"]
    r["turns"] = len(case["input_turns"])
    r["tier"] = tier(case)
    for flag in ("boss", "kind", "language"):
        if case.get(flag):
            r[flag] = case[flag]
    r["sha256"] = case_sha(case)
    return r


def source_files():
    files = []
    for pattern in REFERENCED + [OWN]:
        files += sorted(glob.glob(os.path.join(ROOT, *pattern.split("/"))))
    return [f for f in files if os.path.basename(f) != "manifest.yaml"]


def read_sources():
    out = []
    for f in source_files():
        doc = load(f)
        cases = doc.get("cases") or []
        if doc.get("case_count") != len(cases):
            err("%s: case_count %s but %d cases" % (rel(f), doc.get("case_count"), len(cases)))
        for c in cases:
            out.append((rel(f), c))
    return out


def rebuild():
    sources = read_sources()
    rows = [row(c, f) for f, c in sources]
    floor = len(rows)
    if os.path.exists(MANIFEST):
        old = load(MANIFEST)
        missing = sorted({r["id"] for r in old.get("cases", [])} - {r["id"] for r in rows})
        if missing:
            sys.exit("REFUSED: rebuild would drop %d case(s) the manifest lists: %s. Cases are never removed by tooling "
                     "(safety-invariants.md section 4)." % (len(missing), ", ".join(missing[:10])))
        floor = max(floor, old.get("case_floor", 0))
    by_file = collections.Counter(r["file"] for r in rows)
    by_cat = collections.Counter(r["suite_category"] for r in rows)
    head = ["# Fixed safety regression suite: manifest (brief A5.4, minimum 200 cases). GENERATED - do not edit by hand.",
            "# Rebuild: python tests/safety-suite/validate_manifest.py --rebuild   Validate: python tests/safety-suite/validate_manifest.py",
            "# One row per case: id, source file, suite category, guardrail / ESC / intent / KB IDs, severity, run tier, SHA-256 of the case.",
            "# The Day 10 cases in tests/adversarial and tests/guardrails and the Day 12 cases in tests/escalation are indexed by reference, not copied. Specified, not run (D-79).",
            "# Governance: add-only. A case is never removed or weakened by the learning pipeline (docs/learning-pipeline/safety-invariants.md section 4).",
            ""]
    doc = collections.OrderedDict()
    doc["schema_version"] = "1.0"
    doc["suite_id"] = "NEXBANK-FIXED-SAFETY-SUITE"
    doc["pass_rule"] = "100 percent of cases pass on every repetition before any model, prompt, threshold or KB change ships"
    doc["minimum_cases"] = MIN_CASES
    doc["case_floor"] = floor
    doc["case_count"] = len(rows)
    doc["referenced_case_count"] = sum(1 for r in rows if not r["file"].startswith("tests/safety-suite/"))
    doc["new_case_count"] = sum(1 for r in rows if r["file"].startswith("tests/safety-suite/"))
    doc["files"] = [collections.OrderedDict([("path", p), ("cases", n)]) for p, n in sorted(by_file.items())]
    doc["by_suite_category"] = dict(sorted(by_cat.items()))
    doc["cases"] = rows

    class D(yaml.SafeDumper):
        pass
    D.add_representer(collections.OrderedDict, lambda d, data: d.represent_mapping("tag:yaml.org,2002:map", data.items()))

    def flow_lists(dumper, data):
        return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=all(isinstance(x, str) for x in data))
    D.add_representer(list, flow_lists)
    text = "\n".join(head) + yaml.dump(doc, Dumper=D, sort_keys=False, width=200, allow_unicode=False)
    text.encode("ascii")
    with open(MANIFEST, "w", encoding="ascii", newline="\n") as f:
        f.write(text)
    print("manifest rebuilt: %d cases (%d referenced, %d new), case_floor %d" % (len(rows), doc["referenced_case_count"], doc["new_case_count"], floor))


def validate():
    # 1. manifest parses
    try:
        man = load(MANIFEST)
    except Exception as e:  # noqa: BLE001
        err("manifest does not parse: %s" % e)
        return {}
    rows = man.get("cases") or []
    ids = [r.get("id") for r in rows]
    # 2. unique IDs and counts
    for i, n in collections.Counter(ids).items():
        if n > 1:
            err("duplicate id %s" % i)
    if man.get("case_count") != len(rows):
        err("case_count %s but %d rows" % (man.get("case_count"), len(rows)))
    if len(rows) < MIN_CASES:
        err("only %d cases; the brief requires at least %d" % (len(rows), MIN_CASES))
    if len(rows) < man.get("case_floor", 0):
        err("%d cases is below case_floor %s: cases were removed" % (len(rows), man.get("case_floor")))
    # 3. every referenced file and case exists; no orphan case in the source files
    sources = read_sources()
    src = {}
    for f, c in sources:
        if c["id"] in src:
            err("case id %s appears in more than one source file" % c["id"])
        src[c["id"]] = (f, c)
    for r in rows:
        path = os.path.join(ROOT, *r.get("file", "?").split("/"))
        if not os.path.isfile(path):
            err("%s: file %s does not exist" % (r.get("id"), r.get("file")))
            continue
        if r["id"] not in src:
            err("%s: not found in any source file" % r["id"])
            continue
        f, c = src[r["id"]]
        if f != r["file"]:
            err("%s: manifest says %s but the case is in %s" % (r["id"], r["file"], f))
        # 4. SHA: a changed case must be a reviewed manifest change
        if case_sha(c) != r.get("sha256"):
            err("%s: SHA mismatch (case text changed without a manifest rebuild)" % r["id"])
        expected = row(c, f)
        for key in ("suite_category", "category", "guardrails", "esc", "intents", "kb", "severity", "expected_action", "tier"):
            if expected[key] != r.get(key):
                err("%s: manifest field %s is stale" % (r["id"], key))
    for cid in sorted(set(src) - set(ids)):
        err("%s (%s) is in a source file but not in the manifest" % (cid, src[cid][0]))
    # 5. every guardrail, intent, ESC, KB and RED ID exists
    for r in rows:
        for g in r.get("guardrails", []):
            if g not in GUARDRAILS:
                err("%s: unknown guardrail %s" % (r["id"], g))
        for e in r.get("esc", []):
            if e not in ESC_IDS:
                err("%s: unknown escalation %s" % (r["id"], e))
        for i in r.get("intents", []):
            if i not in INTENTS:
                err("%s: unknown intent %s" % (r["id"], i))
        for k in r.get("kb", []):
            if k not in KB_IDS and not k.startswith("KB-TEST-"):
                err("%s: unknown KB entry %s" % (r["id"], k))
        if r.get("suite_category") not in SUITE_CATEGORIES:
            err("%s: unknown suite_category %s" % (r["id"], r.get("suite_category")))
        if r.get("severity") not in SEVERITIES:
            err("%s: bad severity %s" % (r["id"], r.get("severity")))
    for cid, (f, c) in src.items():
        for red in refs(c, "red"):
            if red not in RED_IDS:
                err("%s: unknown redaction rule %s" % (cid, red))
        for g in refs(c, "guardrail"):
            if g not in GUARDRAILS and own_guardrail(g) not in GUARDRAILS:
                err("%s: mentions unknown guardrail %s" % (cid, g))
    # 6. schema of the SS-* cases (the Day 10 files have their own checker, tests/README.md section 9)
    for cid, (f, c) in src.items():
        if not f.startswith("tests/safety-suite/"):
            continue
        if not re.match(r"SS-(PII|AUTH|ESC|HAL|COM|LRN)-\d{2}$", cid):
            err("%s: id does not match SS-<AREA>-<NN>" % cid)
        for k in REQUIRED:
            if k not in c:
                err("%s: missing field %s" % (cid, k))
        if c.get("category") not in SS_CATEGORIES:
            err("%s: category %s not allowed in tests/safety-suite" % (cid, c.get("category")))
        if c.get("persona") not in PERSONAS:
            err("%s: persona %s" % (cid, c.get("persona")))
        if c.get("expected_action") not in ACTIONS:
            err("%s: expected_action %s" % (cid, c.get("expected_action")))
        if c.get("preconditions", {}).get("auth_level") not in AUTH_LEVELS:
            err("%s: auth_level %s" % (cid, c.get("preconditions")))
        if c.get("kind") not in (None, "control"):
            err("%s: kind %s" % (cid, c.get("kind")))
        if (c.get("expected_action") == "allow") != (c.get("kind") == "control"):
            err("%s: expected_action allow and kind control must go together" % cid)
        if c.get("intent") and c["intent"] not in INTENTS:
            err("%s: intent %s" % (cid, c["intent"]))
        if not isinstance(c.get("input_turns"), list) or not c.get("input_turns"):
            err("%s: input_turns must be a non-empty list" % cid)
        text = " ".join(strings(c))
        for ph in re.findall(r"\{\{([A-Z0-9_]+)", text):
            if ph not in PLACEHOLDERS:
                err("%s: placeholder %s not on the allowed list" % (cid, ph))
        plain = re.sub(r"re:\S+", "", text)
        if re.search(r"\d{9,}", plain) or re.search(r"\b\d{4}[ -]\d{4}[ -]\d{4}\b", plain):
            err("%s: sensitive-looking digit run" % cid)
        try:
            text.encode("ascii")
        except UnicodeEncodeError:
            err("%s: non-ASCII text" % cid)
        for pat in [s[3:] for s in strings(c) if s.startswith("re:")]:
            try:
                re.compile(pat)
            except re.error as e:
                err("%s: bad regular expression %s (%s)" % (cid, pat, e))
    # 7. coverage
    cover = {"esc": collections.Counter(), "guardrail": collections.Counter(), "auth": collections.Counter(), "gap": collections.Counter()}
    for r in rows:
        if r.get("escalation_expected") and r.get("kind") != "control":
            f, c = src.get(r["id"], (None, {}))
            for e in c.get("expected_escalation", []):
                cover["esc"][e] += 1
        for g in r.get("guardrails", []):
            cover["guardrail"][g] += 1
        if r.get("suite_category") == "auth_gating" and r.get("kind") != "control":
            for i in r.get("intents", []):
                cover["auth"][i] += 1
        if r.get("suite_category") == "hallucination_trap":
            for i in r.get("intents", []):
                cover["gap"][i] += 1
    for e in ESC_IDS:
        if not cover["esc"][e]:
            err("coverage: no case expects %s" % e)
    for g in GUARDRAILS:
        if not cover["guardrail"][g]:
            err("coverage: guardrail %s has no case" % g)
    for g in GUARDRAILS.values():
        if not g.get("immutable"):
            err("registry: %s is not immutable (D-58)" % g["id"])
    for i, spec in INTENTS.items():
        if spec["auth"] != "anonymous" and not cover["auth"][i]:
            err("coverage: intent %s (auth %s) has no auth-gating case" % (i, spec["auth"]))
        if spec.get("kb_gap") and not cover["gap"][i]:
            err("coverage: kb_gap intent %s has no hallucination trap" % i)
    for rid in sorted(RESERVED_IDS - set(ids)):
        err("coverage: reserved test ID %s is not in the suite" % rid)
    cats = collections.Counter(r.get("suite_category") for r in rows)
    for cat in SUITE_CATEGORIES:
        if not cats[cat]:
            err("coverage: suite category %s is empty" % cat)
    if man.get("by_suite_category") != dict(sorted(cats.items())):
        err("by_suite_category header is stale")
    return dict(rows=rows, cats=cats, cover=cover, man=man)


if __name__ == "__main__":
    if "--rebuild" in sys.argv:
        rebuild()
    info = validate()
    if info:
        rows = info["rows"]
        print("cases: %d (referenced %d, new %d); floor %s; minimum %d" % (
            len(rows), sum(1 for r in rows if not r["file"].startswith("tests/safety-suite/")),
            sum(1 for r in rows if r["file"].startswith("tests/safety-suite/")), info["man"].get("case_floor"), MIN_CASES))
        print("by suite category: %s" % ", ".join("%s %d" % kv for kv in sorted(info["cats"].items())))
        print("severity: %s" % ", ".join("%s %d" % kv for kv in sorted(collections.Counter(r["severity"] for r in rows).items())))
        print("controls %d, boss %d, multi-turn %d, tier 1/2/3: %s" % (
            sum(1 for r in rows if r.get("kind") == "control"), sum(1 for r in rows if r.get("boss")), sum(1 for r in rows if r["turns"] > 1),
            "/".join(str(sum(1 for r in rows if r["tier"] == t)) for t in (1, 2, 3))))
        print("ESC coverage (positive cases): %s" % ", ".join("%s %d" % (e[4:], info["cover"]["esc"][e]) for e in ESC_IDS))
        print("guardrails covered: %d of %d; intents with auth gating case: %d; kb_gap intents with trap: %d" % (
            sum(1 for g in GUARDRAILS if info["cover"]["guardrail"][g]), len(GUARDRAILS), len(info["cover"]["auth"]),
            sum(1 for i, s in INTENTS.items() if s.get("kb_gap") and info["cover"]["gap"][i])))
    if errors:
        print("FAIL: %d error(s)" % len(errors))
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    print("OK: all checks pass (structure only; no case is executed against an agent)")
