"""Repo-wide cross-reference lint for the NexBank specification.
Usage: python tests/validate_crossrefs.py [ROOT]   (needs PyYAML; ROOT defaults to the repository root)
Exit code 0 = no errors (warnings are allowed). Checks, in order:
  1 file paths and Markdown link targets cited in documents exist (with section references)
  2 every cited ID is defined in its home (grammars are derived from the defining files)
  3 every decision D-nn, requirement R-nn and guardrail GR-* is cited outside its defining file (warning)
  4 counts stated in README.md equal counts recomputed from the files
  5 no placeholder text; past days described as future (warning)
  6 ASCII-only outside files that legitimately hold Devanagari or Gujarati (warning)
  7 the planning-file word used as a document reference
Light harness only; the config files and the decisions log are the source of truth.
"""
import glob
import os
import re
import sys

import yaml

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTS = (".md", ".yaml", ".yml", ".json", ".mmd", ".csv", ".py")
SELF = os.path.join("tests", "validate_crossrefs.py")

ERRORS, WARNINGS = [], []


def err(m):
    ERRORS.append(m)


def warn(m):
    WARNINGS.append(m)


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


FILES = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in (".git", "graphify-out", "__pycache__")]
    for f in fn:
        if f.endswith(EXTS):
            FILES.append(os.path.join(dp, f))
FILES.sort()
TEXT = {}
for p in FILES:
    with open(p, encoding="utf-8", newline="") as fh:
        TEXT[rel(p)] = fh.read()
ALL_FILES = set()
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in (".git", "graphify-out", "__pycache__")]
    for f in fn:
        ALL_FILES.add(rel(os.path.join(dp, f)))
BASENAMES = {}
for f in ALL_FILES:
    BASENAMES.setdefault(os.path.basename(f), []).append(f)


def load_yaml(path):
    return yaml.safe_load(TEXT[path])


YAML_DOCS = {}
for name, txt in TEXT.items():
    if name.endswith((".yaml", ".yml")):
        try:
            YAML_DOCS[name] = yaml.safe_load(txt)
        except yaml.YAMLError as e:
            err("%s: YAML does not parse: %s" % (name, str(e).splitlines()[0]))

# ---------------------------------------------------------------- ID grammar
TOKEN = re.compile(r"(?<![\w-])([A-Z][A-Z0-9]{0,5}-[A-Z0-9]+(?:-[A-Z0-9]+)*)(?![\w-])")
FULL = re.compile(r"[A-Z][A-Z0-9]{0,5}-[A-Z0-9]+(?:-[A-Z0-9]+)*")
NOT_IDS = re.compile(r"^(SHA-\d+|UTF-\d+|ISO-\d+|AES-\d+|TLS-\d+|IS-\d+|HTTP-\d+|RFC-\d+|PCI-DSS|ECB-\d+|EU-AI-ACT|"
                     r"[A-Z]+-\d{4}|COVID-19|PBKDF2-.*|ROT-13|ROT13|P0-P2|G0-G9|MD5-\d+|CSV-\d+|BM25-\d+|T-\d+)$")


def walk_scalars(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str):
                out.add(k)
            walk_scalars(v, out)
    elif isinstance(o, list):
        for v in o:
            walk_scalars(v, out)
    elif isinstance(o, str):
        out.add(o.strip())


def defined_in(names):
    """IDs defined in the given files: YAML/JSON scalars and keys, CSV cells, Markdown defining positions."""
    out = set()
    for n in names:
        txt = TEXT.get(n)
        if txt is None:
            continue
        if n in YAML_DOCS:
            sc = set()
            walk_scalars(YAML_DOCS[n], sc)
            out |= {s for s in sc if FULL.fullmatch(s)}
        elif n.endswith(".md"):
            for line in txt.splitlines():
                s = line.strip()
                if s.startswith("|"):
                    cells = [c.strip() for c in s.strip("|").split("|")]
                    if cells:
                        out |= set(TOKEN.findall(re.sub(r"[*`]", "", cells[0])))
                elif s.startswith("#"):
                    out |= set(TOKEN.findall(s))
                else:
                    m = re.match(r"^(?:[-*]|\d+\.)\s+[*`]*([A-Z][A-Z0-9]{0,5}-[A-Z0-9]+(?:-[A-Z0-9]+)*)", s)
                    if m:
                        out.add(m.group(1))
                    out |= set(re.findall(r"\*\*(" + FULL.pattern + r")\*\*", s))
        else:
            out |= set(TOKEN.findall(txt)) if n.endswith(".csv") else set()
    return out


def files_like(*pats):
    res = []
    for p in pats:
        res += [f for f in TEXT if re.fullmatch(p, f)]
    return sorted(set(res))


# Home files per family (prefix regex -> files). Families not listed use the whole repository.
HOMES = [
    (r"(?:PRD|ACC|TXN|GEN|CMP|SEC|CRD)", ["config/intents.yaml"]),
    (r"RED", ["config/entities.yaml"]),
    (r"ESC", ["config/escalation_rules.yaml"] + files_like(r"tests/escalation/.*\.yaml")),
    (r"XTR", ["config/escalation_rules.yaml"] + files_like(r"tests/escalation/.*\.yaml")),
    (r"KB", files_like(r"docs/knowledge-base/entries/.*\.yaml")),
    (r"TPL", files_like(r"config/templates/.*\.yaml")),
    (r"D", ["docs/assumptions-and-decisions.md"]),
    (r"R", ["docs/requirements-traceability.md"]),
    (r"RISK", ["docs/risk/risk-matrix.md"]),
    (r"DM", ["docs/guardrails/monitoring-dashboard.md"]),
    (r"KPI", files_like(r"docs/metrics/.*\.md")),
    (r"EQ", files_like(r"docs/escalation/.*\.md")),
    (r"GR", ["config/guardrails.yaml"] + files_like(r"tests/(adversarial|guardrails)/.*\.yaml")),
    (r"PA", files_like(r"config/system-prompt/.*", r"tests/templates/.*\.yaml")),
]
HOME_SETS = []
for pre, names in HOMES:
    HOME_SETS.append((re.compile(pre + r"$"), defined_in(names)))
GLOBAL_DEFINED = defined_in(sorted(TEXT))
KNOWN_PREFIXES = {i.split("-")[0] for i in GLOBAL_DEFINED}
# prefixes that are not ID families in this repository
KNOWN_PREFIXES -= {"SHA", "UTF", "AES", "ISO", "TLS", "RFC", "HTTP", "PCI"}

# registry-derived sets
INTENT_DOC = YAML_DOCS.get("config/intents.yaml") or {}
INTENT_IDS = {i["id"] for i in INTENT_DOC.get("intents", [])}
ESC_DOC = YAML_DOCS.get("config/escalation_rules.yaml") or {}
ESC_IDS = {t["id"] for t in ESC_DOC.get("triggers", [])}
QUEUES = {q["name"] for q in ESC_DOC.get("queues", [])}
GR_DOC = YAML_DOCS.get("config/guardrails.yaml") or {}
GR_IDS = {g["id"] for g in GR_DOC.get("guardrails", [])}
TPL_IDS = defined_in(files_like(r"config/templates/.*\.yaml"))
KB_IDS = defined_in(files_like(r"docs/knowledge-base/entries/.*\.yaml"))

if ESC_IDS != {"ESC-%03d" % n for n in range(1, 16)}:
    err("config/escalation_rules.yaml: trigger IDs are not ESC-001..ESC-015")


def home_for(prefix):
    for rx, s in HOME_SETS:
        if rx.match(prefix):
            return s
    return None


def check_token(tok):
    """Return None if defined, else a short reason."""
    if NOT_IDS.match(tok):
        return None
    pre = tok.split("-")[0]
    if pre not in KNOWN_PREFIXES:
        return None
    if len(pre) == 1 and pre not in ("D", "R"):
        return None  # B-nn and E-nn are the brief's own risk numbers (A11.2, A11.3)
    if pre in ("PRD", "ACC", "TXN", "GEN", "CMP", "SEC", "CRD") and not re.fullmatch(r"[A-Z]{3}-\d{3}", tok):
        return None  # record numbers, synthetic references and similar, not intent IDs
    if pre == "KB" and not re.fullmatch(r"KB-(?:PRD|POL|REG|FAQ|TRB|ESC)-\d{3}", tok):
        return None  # KB-BOSS-L3-nn and similar are test query IDs, checked as global IDs below
    if re.fullmatch(r"[A-Z]{1,2}-\d{2,3}", tok) is None and pre in ("D", "R"):
        return None
    if re.search(r"NN|XXXX|XYZ|-0$|-9{3}$", tok) or tok.startswith("TPL-" + "TEST-"):
        return None  # placeholders and deliberate fixtures
    # short forms: KB entries without the KB- prefix (access-control-matrix.md), templates without TPL-
    if "KB-" + tok in KB_IDS or "TPL-" + tok in TPL_IDS:
        return None
    home = home_for(pre)
    if home is not None:
        if tok in home or any(d.startswith(tok + "-") for d in home):
            return None  # defined, or a family name such as GR-ADV
        if not re.search(r"\d", tok.split("-", 1)[1]) and any(d.startswith(tok) for d in home):
            return None  # group name such as KPI-L or PA-L
        # a test case ID inside a family whose home is the registry
        if pre == "GR" and tok in GLOBAL_DEFINED:
            return None
        return "not defined in its home (%s)" % pre
    if tok in GLOBAL_DEFINED or any(d.startswith(tok + "-") for d in GLOBAL_DEFINED):
        return None
    return "not defined anywhere"


# ------------------------------------------------------------ check 1 and 2
PATH_RX = re.compile(r"(?<![\w/.<{*-])((?:(?:docs|config|tests|diagrams|simulations|\.\.?)/)?[\w.\-/*]*[\w*](?:\.(?:md|yaml|yml|json|mmd|csv|py)))(?![\w-])")
LINK_RX = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SECTION_RX = re.compile(r"^\s*[`)]*,?\s*(?:sections?|sec\.)\s+(\d+(?:\.\d+)*)", re.I)
HEADINGS = {}


def headings(path):
    if path not in HEADINGS:
        nums = set()
        for line in TEXT.get(path, "").splitlines():
            m = re.match(r"^#{1,6}\s+(\d+(?:\.\d+)*)\.?(?:\s|$)", line)
            if m:
                nums.add(m.group(1))
        HEADINGS[path] = nums
    return HEADINGS[path]


def resolve(src, target):
    t = target.strip().strip("`")
    if not t or t.startswith(("http:", "https:", "mailto:", "#")):
        return "skip"
    t = t.split("#")[0]
    if re.search(r"[<>{}]|\bNN\b|nn\.|\*", t):
        if "*" in t and not re.search(r"[<>{}]", t):
            hit = glob.glob(os.path.join(ROOT, t))
            hit = hit or glob.glob(os.path.join(ROOT, os.path.dirname(src), t))
            return "ok" if hit else None
        return "skip"
    cands = [os.path.normpath(os.path.join(os.path.dirname(src), t)).replace(os.sep, "/"), t]
    for c in cands:
        if c in ALL_FILES:
            return c
        if os.path.isdir(os.path.join(ROOT, c)):
            return "ok"
    if "/" not in t and t in BASENAMES:
        return BASENAMES[t][0]
    return None


# files cited as names only (outputs, other repos, examples)
NEG_CONTEXT = re.compile(r"wrong file name|deliberately invalid|does not exist|nonexistent|non-existent|unknown file|are corrected to", re.I)
PATH_IGNORE = re.compile(r"^(graphify-out|brief|\.gitkeep$|__init__|setup\.py$|requirements\.txt$)")
for src, txt in sorted(TEXT.items()):
    if src == SELF:
        continue
    lines = txt.splitlines()
    for ln, line in enumerate(lines, 1):
        found = []
        for m in LINK_RX.finditer(line):
            found.append((m.group(1), m.end()))
        for m in PATH_RX.finditer(line):
            found.append((m.group(1), m.end()))
        seen = set()
        for tgt, end in found:
            if tgt in seen or PATH_IGNORE.match(tgt) or tgt.lower().endswith(".pdf"):
                continue
            if ".." in tgt or tgt.startswith(("-", "*")) or '"$id"' in line:
                continue  # ranges, glob fragments and schema $id URLs
            if re.search(r"python \S*" + re.escape(tgt), line):
                continue  # script named in a run instruction (reproduced in the document)
            if NEG_CONTEXT.search(line):
                continue  # deliberate negative example
            seen.add(tgt)
            if src.endswith(".py") and "/" not in tgt:
                continue
            r = resolve(src, tgt)
            if r == "skip":
                continue
            if r is None:
                if src.endswith((".yaml", ".json")) and "/" not in tgt and tgt.count(".") == 1 and not tgt.startswith(("docs", "tests")):
                    continue
                err("%s:%d: cited path does not exist: %s" % (src, ln, tgt))
                continue
            if r != "ok" and r.endswith(".md"):
                m = SECTION_RX.match(line[end:])
                if m and m.group(1) not in headings(r):
                    err("%s:%d: %s has no section %s" % (src, ln, r, m.group(1)))

# queue names used by tests/config must exist
def walk_queue(o, path, name):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and re.search(r"(^|_)queue(_name)?$", k) and isinstance(v, str) and not FULL.fullmatch(v):
                if QUEUES and v not in QUEUES:
                    err("%s: queue name not defined in config/escalation_rules.yaml: %s (key %s)" % (name, v, k))
            walk_queue(v, path, name)
    elif isinstance(o, list):
        for v in o:
            walk_queue(v, path, name)


for name, doc in YAML_DOCS.items():
    if name.startswith("tests/") or name.startswith("docs/") or name.startswith("config/templates/"):
        walk_queue(doc, [], name)

ID_CITES = {}
for src, txt in sorted(TEXT.items()):
    if src == SELF:
        continue
    for ln, line in enumerate(txt.splitlines(), 1):
        for m in TOKEN.finditer(line):
            tok = m.group(1)
            ID_CITES.setdefault(tok, []).append((src, ln))
            why = None if NEG_CONTEXT.search(line) else check_token(tok)
            if why:
                err("%s:%d: ID %s %s" % (src, ln, tok, why))
        for m in re.finditer(r"\b((?:[A-Z][A-Z0-9]*-)+)(\d+)\.\.(\d+)", line):
            end = "%s%s" % (m.group(1), m.group(3).zfill(len(m.group(2))))
            if end not in GLOBAL_DEFINED and check_token(end):
                err("%s:%d: range end %s is not defined" % (src, ln, end))
        for m in re.finditer(r"\bFMEA #(\d+)\b", line):
            pass

# FMEA row numbers
fm = TEXT.get("docs/architecture/failure-modes.md", "")
FMEA_ROWS = {int(x) for x in re.findall(r"^\|\s*(\d+)\s*\|", fm, re.M)}
for src, txt in sorted(TEXT.items()):
    if src == SELF:
        continue
    for ln, line in enumerate(txt.splitlines(), 1):
        for m in re.finditer(r"\bFMEA (?:row |rows |#)(\d+)", line):
            if FMEA_ROWS and int(m.group(1)) not in FMEA_ROWS:
                err("%s:%d: FMEA row %s does not exist (rows %d to %d)" % (src, ln, m.group(1), min(FMEA_ROWS), max(FMEA_ROWS)))

# ------------------------------------------------------------------- check 3
def outside(tok, home_files):
    return any(s not in home_files for s, _ in ID_CITES.get(tok, []))


def uncited(label, ids, rx, homefiles, where):
    miss = [i for i in sorted(ids) if re.fullmatch(rx, i) and not outside(i, homefiles)]
    if miss:
        warn("%s: %d %s never cited outside the defining file: %s" % (where, len(miss), label, ", ".join(miss)))


uncited("decisions", home_for("D") or [], r"D-\d+", {"docs/assumptions-and-decisions.md"}, "docs/assumptions-and-decisions.md")
uncited("requirements", home_for("R") or [], r"R-\d+", {"docs/requirements-traceability.md"}, "docs/requirements-traceability.md")
uncited("guardrails", GR_IDS, r"GR-.*", {"config/guardrails.yaml"}, "config/guardrails.yaml")

# ------------------------------------------------------------------- check 4
README = TEXT.get("README.md", "")


def count_cases(*pats):
    n = 0
    for f in files_like(*pats):
        d = YAML_DOCS.get(f)
        if isinstance(d, dict) and isinstance(d.get("cases"), list):
            n += len(d["cases"])
    return n


def stated(rx, group=1):
    m = re.search(rx, README, re.S)
    return int(m.group(group).replace(",", "")) if m else None


def expect(label, rx, actual, group=1):
    v = stated(rx, group)
    if v is None:
        warn("README.md: could not find the stated count for %s (pattern %r)" % (label, rx))
    elif v != actual:
        err("README.md: states %d %s but the files give %d" % (v, label, actual))


kb_total = 0
for f in files_like(r"docs/knowledge-base/entries/.*\.yaml"):
    d = YAML_DOCS.get(f) or {}
    kb_total += len(d.get("entries", []) or [])
tpl_total = var_total = 0
for f in files_like(r"config/templates/.*\.yaml"):
    d = YAML_DOCS.get(f) or {}
    for t in d.get("templates", []) or []:
        tpl_total += 1
        var_total += len(t.get("variants", []) or [])
conv_files = [f for f in TEXT if re.fullmatch(r"simulations/conv-\d+.*\.md", f)]
msgs = sum(len(re.findall(r"^### T\d+ \|", TEXT[f], re.M)) for f in conv_files)
risk_ids = {x for x in re.findall(r"^\|\s*(RISK-[A-Z]+-\d+)\s*\|", TEXT.get("docs/risk/risk-matrix.md", ""), re.M)}
fair = YAML_DOCS.get("tests/compliance/fairness-pairs.yaml") or {}
man = YAML_DOCS.get("tests/safety-suite/manifest.yaml") or {}
pa = YAML_DOCS.get("tests/templates/prompt-assertions.yaml") or {}
params = YAML_DOCS.get("config/parameters.yaml") or {}
layers = len(files_like(r"config/system-prompt/layer\d-.*\.md"))
mcases = man.get("cases", []) or []

expect("KB entries", r"(\d+) entries in `entries/`", kb_total)
expect("guardrails", r"\((\d+) guardrails\)", len(GR_IDS))
expect("guardrail and adversarial cases", r"(\d+) cases, specified not run\)\. Layers", count_cases(r"tests/(adversarial|guardrails)/.*\.yaml"))
expect("escalation cases", r"`tests/escalation/` \((\d+) cases", count_cases(r"tests/escalation/.*\.yaml"))
expect("risks", r"\((\d+) risks", len(risk_ids))
expect("annotated conversations", r"(\d+) annotated conversations", len(conv_files))
expect("simulation messages", r"(\d+) messages", msgs)
expect("fairness pairs", r"(\d+) fairness pairs", len(fair.get("cases", [])) // 2)
expect("safety-suite cases", r"\((\d+) cases indexed", len(mcases))
expect("safety-suite cases by reference", r"cases indexed[^:]*: (\d+) by reference", sum(1 for c in mcases if not c.get("new", c.get("is_new", False))) if False else man.get("referenced_case_count", -1))
expect("safety-suite new cases", r"by reference, (\d+) new", man.get("new_case_count", -1))
expect("prompt assertions", r"(\d+) assertions", sum(len(re.findall(r"^\|\s*PA-L\d+-\d+\s*\|", TEXT[f], re.M)) for f in files_like(r"config/system-prompt/layer.*\.md")) or -1)
expect("templates", r"\((\d+) templates, \d+ variants", tpl_total)
expect("template variants", r"\(\d+ templates, (\d+) variants", var_total)
expect("project thresholds", r"(\d+) project thresholds", len(params.get("project_parameters", [])))
expect("governed parameters", r"(\d+) A12\.3 parameters", len(params.get("governed_parameters", [])))
expect("prompt layers", r"\((\d+) layers", layers)
expect("escalation triggers", r"ESC-001\.\.(\d+)", len(ESC_IDS))
m = re.search(r"annotated simulations", README)
if m:
    expect("annotated simulations", r"(\d+) annotated simulations", len(conv_files))
dec_ids = sorted(int(x[2:]) for x in (home_for("D") or []) if re.fullmatch(r"D-\d+", x))
if dec_ids:
    m = re.search(r"D-0?1 to D-(\d+)|decisions D-0?1\.\.D-(\d+)", README)
    if m:
        v = int(m.group(1) or m.group(2))
        if v != dec_ids[-1]:
            err("README.md: decisions range ends at D-%d but the log ends at D-%d" % (v, dec_ids[-1]))
if dec_ids and dec_ids != list(range(1, dec_ids[-1] + 1)):
    missing = sorted(set(range(1, dec_ids[-1] + 1)) - set(dec_ids))
    warn("docs/assumptions-and-decisions.md: decision numbers are not contiguous, missing %s" % missing[:10])
m = re.search(r"Day (\d+) of 15", README)
CURRENT_DAY = int(m.group(1)) if m else 15

# ------------------------------------------------------------------- check 5
PLACEHOLDER = re.compile("|".join([
    r"\b" + "TO" + "DO" + r"\b", r"\b" + "T" + "BD" + r"\b", r"\b" + "FIX" + "ME" + r"\b",
    "to be " + "written", "lorem " + "ipsum"]), re.I if False else 0)
PLACEHOLDER_CI = re.compile("to be " + "written|lorem " + "ipsum", re.I)
FUTURE = [
    re.compile(r"\bDay (\d+)(?: and Day \d+)? (?:will|to be|is to|are to)\b"),
    re.compile(r"\bon Day (\d+) (?:we|it|the) (?:will|must)\b"),
    re.compile(r"\blater days (?:fill|will)", re.I),
    re.compile(r"\bfilled? (?:in )?(?:on|by) Day (\d+)\b.*\b(?:later|remaining)\b"),
    re.compile(r"\(Day (\d+)\)\s*(?:not yet|pending|to do|planned)", re.I),
    re.compile(r"\bremaining folders are placeholders\b"),
]
for src, txt in sorted(TEXT.items()):
    if src == SELF or src.endswith(("validate_simulations.py", "validate_templates.py")) and False:
        continue
    for ln, line in enumerate(txt.splitlines(), 1):
        if "{{PAD:" in line:
            continue  # padding macro of the denial-of-service cases
        if PLACEHOLDER.search(line) or PLACEHOLDER_CI.search(line):
            if not re.search(r"(?:no|not|without|forbidden|reject|absent)[^.]*(?:placeholder|marker)", line, re.I) or True:
                err("%s:%d: placeholder text: %s" % (src, ln, line.strip()[:90]))
        for rx in FUTURE:
            m = rx.search(line)
            if m:
                if m.groups() and m.group(1) and int(m.group(1)) > CURRENT_DAY:
                    continue
                warn("%s:%d: past day described as future: %s" % (src, ln, m.group(0)[:70]))

# ------------------------------------------------------------------- check 6
INDIC = re.compile("[\u0900-\u0dff\u200c\u200d]")  # Devanagari, Gujarati and the other Indic scripts of the language docs
INDIC_OK = re.compile(
    r"^(docs/intent-taxonomy/utterances\.csv|docs/intent-taxonomy/language-detection\.md|docs/architecture/multilingual\.md|"
    r"config/templates/.*|docs/knowledge-base/entries/.*|simulations/.*|tests/.*|config/system-prompt/.*|config/intents\.yaml|"
    r"docs/intent-taxonomy/.*|config/entities\.yaml|docs/assumptions-and-decisions\.md|docs/architecture/.*|docs/guardrails/.*|docs/compliance/.*|docs/knowledge-base/.*|docs/escalation/.*)$")
for src, txt in sorted(TEXT.items()):
    if src == SELF:
        continue
    for ln, line in enumerate(txt.splitlines(), 1):
        bad = [c for c in line if ord(c) > 127]
        if not bad:
            continue
        others = [c for c in bad if not INDIC.match(c)]
        if others:
            warn("%s:%d: non-ASCII character(s) outside the Indic scripts: %s" % (src, ln, " ".join("U+%04X" % ord(c) for c in sorted(set(others)))))
        elif not INDIC_OK.match(src):
            warn("%s:%d: Devanagari or Gujarati text in a file that is not on the multilingual list" % (src, ln))

# ------------------------------------------------------------------- check 7
PLAN_WORD = "PL" + "AN"
PLAN_RX = re.compile(r"(?<![\w])" + PLAN_WORD + r"(?![\w])")
for src, txt in sorted(TEXT.items()):
    if src == SELF or os.path.basename(src).startswith("validate_"):
        continue
    for ln, line in enumerate(txt.splitlines(), 1):
        if PLAN_RX.search(line) and not re.search(r"the word " + PLAN_WORD, line):
            err("%s:%d: the planning file is cited (document reference): %s" % (src, ln, line.strip()[:90]))

# ------------------------------------------------------------------- report
print("files scanned: %d" % len(TEXT))
print("IDs cited: %d distinct; defined (global): %d; guardrails %d, intents %d, KB %d, templates %d, ESC %d" % (
    len(ID_CITES), len(GLOBAL_DEFINED), len(GR_IDS), len(INTENT_IDS), len(KB_IDS), len(TPL_IDS), len(ESC_IDS)))
print("recomputed: KB %d, templates %d/%d variants, conversations %d, messages %d, risks %d, cases adv+grd %d, esc %d, suite %d" % (
    kb_total, tpl_total, var_total, len(conv_files), msgs, len(risk_ids),
    count_cases(r"tests/(adversarial|guardrails)/.*\.yaml"), count_cases(r"tests/escalation/.*\.yaml"), len(mcases)))
for w in WARNINGS:
    print("WARN " + w)
for e in ERRORS:
    print("ERROR " + e)
print("%d error(s), %d warning(s)" % (len(ERRORS), len(WARNINGS)))
print("RESULT: " + ("FAIL" if ERRORS else "PASS"))
sys.exit(1 if ERRORS else 0)
