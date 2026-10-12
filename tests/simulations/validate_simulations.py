"""Validate simulations/conv-*.md, simulations/INDEX.md and simulations/pattern-audit.md (Day 14).
Usage: python tests/simulations/validate_simulations.py              (needs PyYAML)
       python tests/simulations/validate_simulations.py --dir PATH   (check another folder of simulations, e.g. a scratch copy)
Exit code 0 = all checks pass. Light harness only: it checks structure, references, wording rules and coverage.
It does not run a model or a conversation; the simulations are designed examples. Check list: tests/simulations/README.md.
"""
import collections
import glob
import io
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SIM_DIR = os.path.join(ROOT, "simulations")
if "--dir" in sys.argv:
    SIM_DIR = os.path.abspath(sys.argv[sys.argv.index("--dir") + 1])
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def read(path):
    with io.open(path, encoding="utf8") as fh:
        return fh.read()


def load(path):
    return yaml.safe_load(read(path))


# ------------------------------------------------------------------------------------------- reference registries
INTENTS = load(os.path.join(ROOT, "config", "intents.yaml"))["intents"]
INTENT_IDS = {i["id"] for i in INTENTS}
GR = load(os.path.join(ROOT, "config", "guardrails.yaml"))
GR_IDS = {g["id"] for g in GR["guardrails"]}
ESCR = load(os.path.join(ROOT, "config", "escalation_rules.yaml"))
ESC_IDS = {t["id"] for t in ESCR["triggers"]}
ESC_SUB = {s["id"] for t in ESCR["triggers"] for s in t.get("sub_rules", [])}
XTR_IDS = {x["id"] for x in ESCR["extra_rules"]}
QUEUES = {q["name"] for q in ESCR["queues"]}
KB = {}
for f in glob.glob(os.path.join(ROOT, "docs", "knowledge-base", "entries", "*.yaml")):
    for e in load(f)["entries"]:
        KB[e["id"]] = e["version"]
TPL = {}
for f in glob.glob(os.path.join(ROOT, "config", "templates", "*.yaml")):
    d = load(f)
    if d and "templates" in d:
        for t in d["templates"]:
            TPL[t["id"]] = t
TOOLS = {"get_balance", "get_statement", "get_profile_masked", "get_txn", "search_txn", "create_dispute_ticket", "get_card_status",
         "block_card", "request_replacement", "create_complaint", "get_complaint_status", "schedule_callback", "flag_fraud",
         "send_credential_reset_link", "emi_calculator", "kb_search", "route_to_queue", "summarise_conversation"}
DECISIONS = set(re.findall(r"^\| (D-\d+) ", read(os.path.join(ROOT, "docs", "assumptions-and-decisions.md")), re.M))
DECISIONS |= {"D-%d" % n for n in range(172, 181)}  # reserved for Day 14
SEC_RULES = ["R%d" % i for i in range(1, 9)]
PERSONAS = ["Priya", "Rajesh", "Meera", "Arjun", "Sunita", "Vikram"]
VECTORS = ["prompt injection", "jailbreak", "social engineering", "data exfiltration", "denial of service", "identity spoofing"]
FAMILIES = ["ACC", "TXN", "CRD", "PRD", "CMP", "SEC", "GEN"]
ADVICE_CATEGORIES = ["investment", "loan products", "interest rates", "forex", "tax planning", "insurance"]
REQUIRED_HEADER = ["Scenario", "Persona", "Channel", "Language", "Starting auth level", "Intents covered", "Guardrails exercised",
                   "Escalation outcome", "Escalation IDs", "Priority", "Adversarial vectors", "Security rules exercised", "Patterns shown",
                   "Anti-patterns designed against", "Coverage tags", "Case study", "Templates used", "KB entries cited", "Tools called",
                   "prompt_version", "What this conversation proves"]
ROW_NAMES = ["NLU", "Sentiment", "Guardrails", "KB / tools", "Action", "Generation", "State"]
BANNED = [r"within \d+ ?(hours|hrs|minutes|mins|days)", r"guarantee", r"I promise", r"100% safe", r"will be credited", r"will be refunded",
          r"you should invest", r"I recommend", r"best option for you", r"I am human", r"I'm a human", r"your fault", r"you should have",
          r"deeply apologi", r"sincerely regret", r"didn't understand", r"(share|provide|send|tell me|type) your (OTP|PIN|CVV|password)",
          r"provide your account number", r"zero.liability"]
MAX_WORDS = 250
TURN_CEILING = 25

# ------------------------------------------------------------------------------------------------- parse
files = sorted(glob.glob(os.path.join(SIM_DIR, "conv-*.md")))
if not files:
    err("no conv-*.md files in %s" % SIM_DIR)


def parse(path):
    t = read(path)
    d = dict(path=path, name=os.path.basename(path), text=t, header={}, turns=[], events=[])
    m = re.search(r"## Header\n\n\| Field \| Value \|\n\|---\|---\|\n((?:\|.*\n)+)", t)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"\| (.*?) \| (.*) \|$", line)
            if mm:
                d["header"][mm.group(1)] = mm.group(2)
    for blk in re.finditer(r"### ((?:T|E)\d+) \| (Customer|Agent|System event)\n\n> (.*?)\n\n(.*?)(?=\n### |\n## |\Z)", t, re.S):
        tn, who, text, rest = blk.groups()
        rows = {}
        for line in rest.splitlines():
            mm = re.match(r"\| (.*?) \| (.*) \|$", line)
            if mm and mm.group(1) != "Field":
                rows[mm.group(1)] = mm.group(2)
        gloss = re.search(r"_English gloss", rest) is not None
        d["turns" if tn.startswith("T") else "events"].append(dict(tn=tn, who=who, text=text, rows=rows, gloss=gloss))
    return d


CONVS = [parse(p) for p in files]
NAME = {c["name"]: c for c in CONVS}


def words(s):
    return len(s.split())


# ---------------------------------------------------------------------------------------------- per-file checks
HEX = re.compile(r"[ऀ-ॿ઀-૿‌‍]")
for c in CONVS:
    n, t = c["name"], c["text"]
    # S1 name and title
    if not re.match(r"conv-\d\d-[a-z0-9-]+\.md$", n):
        err("%s: file name does not match conv-NN-slug.md" % n)
    if not t.startswith("# conv-%s:" % n.split("-")[1]):
        err("%s: first line is not '# conv-NN: title'" % n)
    # S2 header fields
    for f in REQUIRED_HEADER:
        if not c["header"].get(f):
            err("%s: header field missing or empty: %s" % (n, f))
    if not c["header"].get("prompt_version", "").startswith("sp-1.0.0+518d5a1e.n000000"):
        err("%s: prompt_version is not the Day 13 string" % n)
    if "Designed, illustrative conversation." not in t:
        err("%s: missing the 'designed, illustrative' statement" % n)
    if "Setup:" not in t and int(n.split("-")[1]) > 6:
        err("%s: missing Setup line" % n)
    # S3 self-audit
    pm = re.search(r"### Patterns \(A9\.1\)\n\n.*?\n\|---.*\n((?:\|.*\n)+)", t)
    am = re.search(r"### Anti-patterns \(A9\.2\)\n\n.*?\n\|---.*\n((?:\|.*\n)+)", t)
    if "## Self-audit" not in t or not pm or not am:
        err("%s: self-audit block missing or malformed" % n)
    else:
        pc = [x.split("|")[1].strip() for x in pm.group(1).splitlines()]
        ac = [x.split("|")[1].strip() for x in am.group(1).splitlines()]
        if pc != ["P1", "P2", "P3", "P4", "P5"]:
            err("%s: pattern rows are %s" % (n, pc))
        if ac != ["AP%d" % i for i in range(1, 9)]:
            err("%s: anti-pattern rows are %s" % (n, ac))
        for line in am.group(1).splitlines():
            cells = [x.strip() for x in line.strip("|").split("|")]
            if not (cells[2].startswith("absent") or cells[2].startswith("not at risk") or cells[2].startswith("not applicable")):
                err("%s: %s result is not 'absent': %s" % (n, cells[0], cells[2][:60]))
    if "## Closing" not in t:
        err("%s: Closing block missing" % n)
    if not any("Decision point" in x["rows"] for x in c["turns"]):
        err("%s: no Decision point row in any turn" % n)
    # S4 turn structure
    tn = [x["tn"] for x in c["turns"]]
    if tn != ["T%d" % (i + 1) for i in range(len(tn))]:
        err("%s: turn numbers are not T1..Tn in order: %s" % (n, tn[:6]))
    mm = re.search(r"\| Messages \| (\d+) ", t)
    if not mm or int(mm.group(1)) != len(c["turns"]):
        err("%s: Messages in Closing (%s) differs from the %d turns" % (n, mm.group(1) if mm else None, len(c["turns"])))
    if not c["turns"] or c["turns"][0]["who"] != "Customer":
        err("%s: first message is not a customer message" % n)
    for i, x in enumerate(c["turns"]):
        for r in ROW_NAMES:
            if r not in x["rows"]:
                err("%s %s: row '%s' missing" % (n, x["tn"], r))
        st = x["rows"].get("State", "")
        m2 = re.search(r"turn_count (\d+);", st)
        if not m2 or int(m2.group(1)) != i + 1:
            err("%s %s: State turn_count %s does not equal the turn number" % (n, x["tn"], m2.group(1) if m2 else None))
        for key in ["phase ", "auth ", "topic_stack [", "slots {", "pending_confirmation ", "counters: ", "turns_since_resolution ", "escalation_proximity "]:
            if key not in st:
                err("%s %s: State lacks '%s'" % (n, x["tn"], key))
        if x["who"] == "Customer" and "entities:" not in x["rows"].get("NLU", ""):
            err("%s %s: customer NLU row shows no entity extraction" % (n, x["tn"]))
        if x["who"] == "Customer" and "Input Guard" not in x["rows"].get("Guardrails", ""):
            err("%s %s: customer turn lacks the Input Guard check" % (n, x["tn"]))
        if x["who"] == "Agent" and "Output Safety Layer" not in x["rows"].get("Guardrails", ""):
            err("%s %s: agent turn lacks the Output Safety Layer check" % (n, x["tn"]))
        if x["who"] == "Agent" and not x["rows"].get("Generation", "").startswith(("template", "hybrid", "llm")):
            err("%s %s: Generation row does not name a mode" % (n, x["tn"]))
        if HEX.search(x["text"]) or re.search(r"[A-Za-z]", x["text"]) and not x["text"].isascii():
            pass
        if not x["text"].isascii() and not x["gloss"] and not x["rows"].get("Generation", "").startswith("n/a") is False:
            pass
    # non-English text needs a gloss and the not-native-reviewed statement
    nonascii_turns = [x for x in c["turns"] if not x["text"].isascii()]
    for x in nonascii_turns:
        if not x["gloss"]:
            err("%s %s: non-English turn has no English gloss" % (n, x["tn"]))
    hinglish_or_hi = c["header"].get("Language", "").lower()
    if (nonascii_turns or "hinglish" in hinglish_or_hi or hinglish_or_hi.startswith("hi") or "gu" in hinglish_or_hi) and "not native-reviewed" not in t:
        err("%s: non-English text without the 'not native-reviewed' statement" % n)
    # S5 identifiers
    for m3 in set(re.findall(r"(?<![A-Za-z]-)\b(?:ACC|TXN|CRD|PRD|CMP|SEC|GEN)-\d{3}\b", t)):
        if m3 not in INTENT_IDS and not m3.startswith(("CMP-SYN", "SEC-SYN")):
            err("%s: unknown intent id %s" % (n, m3))
    for m3 in set(re.findall(r"\bGR-(?:ADV|SEC|REG|OUT|SYS|ATK)-R?\d{1,2}\b", t)):
        if m3 not in GR_IDS:
            err("%s: unknown guardrail id %s" % (n, m3))
    for m3 in set(re.findall(r"(?<![A-Za-z]-)\bESC-\d{3}\b", t)):
        if m3 not in ESC_IDS:
            err("%s: unknown ESC id %s" % (n, m3))
    for m3 in set(re.findall(r"(?<![A-Za-z]-)\bESC-\d{3}\.[a-z]\b", t)):
        if m3 not in ESC_SUB:
            err("%s: unknown ESC sub-rule %s" % (n, m3))
    for m3 in set(re.findall(r"(?<![A-Za-z]-)\bXTR-\d{2}\b", t)):
        if m3 not in XTR_IDS:
            err("%s: unknown XTR id %s" % (n, m3))
    for m3 in set(re.findall(r"\bKB-(?:PRD|POL|REG|FAQ|TRB|ESC)-\d{3}\b", t)):
        if m3 not in KB:
            err("%s: unknown KB id %s" % (n, m3))
    for kid, ver in set(re.findall(r"\b(KB-[A-Z]{3}-\d{3})@([\d.]+)", t)):
        if KB.get(kid) != ver:
            err("%s: %s@%s is not the current version (%s)" % (n, kid, ver, KB.get(kid)))
    for tid in set(re.findall(r"\bTPL-[A-Z]+(?:-[A-Z0-9]+)*\b", t)):
        if tid not in TPL:
            err("%s: unknown template id %s" % (n, tid))
    for tid, var, ver in set(re.findall(r"`(TPL-[A-Z0-9-]+)/(\w+)@([\d.]+)`", t)):
        if tid in TPL:
            if not [v for v in TPL[tid]["variants"] if v["key"] == var]:
                err("%s: template %s has no variant %s" % (n, tid, var))
            if TPL[tid]["version"] != ver:
                err("%s: template %s version %s differs from %s" % (n, tid, ver, TPL[tid]["version"]))
    for q in set(re.findall(r"queue=([A-Za-z ]+?) [(;]", t)):
        if q.strip() not in QUEUES:
            err("%s: unknown queue %s" % (n, q))
    for q in set(re.findall(r"queue ([A-Z][A-Za-z ]+?)(?:,| SLA)", c["header"].get("Escalation outcome", "") + " " + t[t.find("| Escalation record |"):t.find("| Escalation record |") + 700])):
        if q.strip() in QUEUES or q.strip() in ("Mgr",):
            continue
    for tool in set(re.findall(r"tool: `([a-z_]+)`", t)):
        if tool not in TOOLS:
            err("%s: unknown tool %s" % (n, tool))
    for dd in set(re.findall(r"\bD-\d{2,3}\b", t)):
        if dd not in DECISIONS:
            err("%s: unknown decision id %s" % (n, dd))
    # header consistency with the turn annotations
    gen_tpls = set(re.findall(r"`(TPL-[A-Z0-9-]+)/", t))
    hdr_tpls = set(re.findall(r"TPL-[A-Z]+(?:-[A-Z0-9]+)*", c["header"].get("Templates used", "")))
    if gen_tpls != hdr_tpls:
        err("%s: Templates used header %s differs from the Generation rows %s" % (n, sorted(hdr_tpls), sorted(gen_tpls)))
    kb_rows = set()
    for x in c["turns"]:
        kb_rows |= set(re.findall(r"KB-[A-Z]{3}-\d{3}(?=@)", x["rows"].get("KB / tools", "")))
    hdr_kb = set(re.findall(r"KB-[A-Z]{3}-\d{3}", c["header"].get("KB entries cited", "")))
    if kb_rows != hdr_kb:
        err("%s: KB entries cited header %s differs from the KB rows %s" % (n, sorted(hdr_kb), sorted(kb_rows)))
    tool_rows = {m4 for x in c["turns"] for m4 in re.findall(r"tool: `([a-z_]+)`", x["rows"].get("KB / tools", ""))}
    hdr_tools = {x.strip() for x in c["header"].get("Tools called", "").split(",") if x.strip() and x.strip() != "none"}
    if tool_rows != hdr_tools:
        err("%s: Tools called header %s differs from the tool rows %s" % (n, sorted(hdr_tools), sorted(tool_rows)))
    hdr_gr = set(re.findall(r"GR-[A-Z]+-R?\d+", c["header"].get("Guardrails exercised", "")))
    row_gr = set()
    for x in c["turns"]:
        g = x["rows"].get("Guardrails", "")
        row_gr |= set(re.findall(r"GR-[A-Z]+-R?\d+", g.split("triggered:")[-1] if "triggered:" in g else ""))
    if hdr_gr != row_gr:
        err("%s: Guardrails exercised header differs from the triggered lists: %s" % (n, sorted(hdr_gr ^ row_gr)))
    hdr_intents = set(re.findall(r"[A-Z]{3}-\d{3}", c["header"].get("Intents covered", "")))
    nlu_intents = set()
    for x in c["turns"]:
        nlu_intents |= set(re.findall(r"`([A-Z]{3}-\d{3})`", x["rows"].get("NLU", "")))
    if not hdr_intents <= nlu_intents | {"GEN-006"}:
        err("%s: Intents covered %s not all found in the NLU rows" % (n, sorted(hdr_intents - nlu_intents)))
    # S6 characters
    for ch in set(t):
        o = ord(ch)
        if o > 127 and not (0x0900 <= o <= 0x097F or 0x0A80 <= o <= 0x0AFF or o in (0x200C, 0x200D)):
            err("%s: forbidden character U+%04X (em dash, smart quote, emoji or other)" % (n, o))
    if re.search(r"\bPLAN\b", t):
        err("%s: the word PLAN appears (not allowed as a file reference)" % n)
    # S7 sensitive digits
    scan = re.sub(r"\{\{[A-Z_]+\}\}", " ", t)
    checks = [
        (r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", "card-like digit run"),
        (r"(?<!\d)\d{4}[ -]\d{4}[ -]\d{4}(?!\d)", "Aadhaar-like 4-4-4 group"),
        (r"(?<![\d,])(?<!\d\.)\d{12}(?![\d,])(?!\.\d)", "12-digit run"),
        (r"(?<![\d,])(?<!\d\.)(?:\+91[ -]?)?[6-9]\d{9}(?![\d,])(?!\.\d)", "phone-like number"),
        (r"(?<![\d,])(?<!\d\.)\d{9,18}(?![\d,])(?!\.\d)", "account-number-like digit run"),
        (r"(?i)\b(?:otp|passcode|one-time code|code)\b[^.\n]{0,12}?(?<![\d,])(?<!\d\.)\d{4,8}(?![\d,])(?!\.\d)", "OTP-like digits next to the word code or OTP"),
        (r"(?i)\bcvv\b\D{0,12}\d{3,4}", "CVV-like digits"),
        (r"\b[A-Z]{5}\d{4}[A-Z]\b", "PAN-like string"),
    ]
    for pat, label in checks:
        for hit in re.finditer(pat, scan):
            err("%s: %s: %r" % (n, label, hit.group(0)[:40]))
    # S8 AI-turn wording
    prev_text, prev_who = None, None
    counts = collections.Counter()
    for x in c["turns"]:
        if x["who"] != "Agent":
            prev_who = x["who"]
            continue
        txt = x["text"]
        counts[txt] += 1
        if prev_who == "Agent" and prev_text == txt:
            err("%s %s: identical to the previous agent message (Robotic Loop)" % (n, x["tn"]))
        prev_text, prev_who = txt, "Agent"
        if "{{" in txt or "}}" in txt:
            err("%s %s: unfilled template slot in an AI turn" % (n, x["tn"]))
        if words(txt) > MAX_WORDS:
            err("%s %s: agent message of %d words (cap %d)" % (n, x["tn"], words(txt), MAX_WORDS))
        if len(re.findall(r"\b(sorry|apologi[sz]e)\b", txt, re.I)) > 1:
            err("%s %s: more than one apology in a message" % (n, x["tn"]))
        for b in BANNED:
            if re.search(b, txt, re.I):
                err("%s %s: banned phrase /%s/ in an AI turn" % (n, x["tn"], b))
        # template wording
        gen = x["rows"].get("Generation", "")
        lm = re.search(r"\(language (\w+)\)", gen)
        lang = lm.group(1) if lm else "en"
        norm = " ".join(txt.split())
        for tid, var, ver, tl in re.findall(r"`(TPL-[A-Z0-9-]+)/(\w+)@([\d.]+)`(?: \[(\w+)\])?", gen):
            if tid not in TPL:
                continue
            vv = [v for v in TPL[tid]["variants"] if v["key"] == var]
            if not vv:
                continue
            raw = vv[0]["text"].get(tl or lang)
            if raw is None:
                err("%s %s: %s/%s has no %s text" % (n, x["tn"], tid, var, tl or lang))
                continue
            for frag in re.split(r"\{\{\w+\}\}", raw):
                fr = " ".join(frag.split())
                if fr and fr not in norm:
                    err("%s %s: template wording of %s/%s not found verbatim: %r" % (n, x["tn"], tid, var, fr[:50]))
    for tx, k in counts.items():
        if k >= 3:
            err("%s: the same agent message is sent %d times" % (n, k))

# ----------------------------------------------------------------------------- INDEX.md and pattern-audit.md
index_path = os.path.join(SIM_DIR, "INDEX.md")
audit_path = os.path.join(SIM_DIR, "pattern-audit.md")
if not os.path.exists(index_path):
    err("INDEX.md missing")
else:
    idx = read(index_path)
    listed = set(re.findall(r"`(conv-\d\d-[a-z0-9-]+\.md)`", idx.split("## 2. Totals")[0]))
    present = {c["name"] for c in CONVS}
    if listed != present:
        if listed - present:
            err("INDEX.md lists file(s) that do not exist: %s" % sorted(listed - present))
        if present - listed:
            err("INDEX.md does not list file(s) that are present: %s" % sorted(present - listed))
    for needle in ["illustrative", "## 4. Coverage matrices", "## 7. Gaps"]:
        if needle not in idx:
            err("INDEX.md lacks '%s'" % needle)
if not os.path.exists(audit_path):
    err("pattern-audit.md missing")
else:
    au = read(audit_path)
    sec1 = au.split("## 2.")[0]
    sec2 = au.split("## 2.")[1].split("## 3.")[0] if "## 2." in au else ""
    sweep = au.split("## 3.")[1] if "## 3." in au else ""
    for c in CONVS:
        num = c["name"].split("-")[1]
        if not re.search(r"^\| %s \|" % num, sec1, re.M):
            err("pattern-audit.md: no pattern row for conv-%s" % num)
        if not re.search(r"^\| %s \|" % num, sec2, re.M):
            err("pattern-audit.md: no anti-pattern row for conv-%s" % num)
        rows = [l for l in sweep.splitlines() if re.match(r"\| %s \|" % num, l)]
        blob = " ".join(rows)
        for x in c["turns"]:
            if x["who"] != "Agent":
                continue
            for tok in set(re.findall(r"\d[\d,\.]*\d|\d", x["text"])):
                if tok not in blob:
                    err("pattern-audit.md: figure %r in conv-%s %s is not in the AUTO-FAIL sweep" % (tok, num, x["tn"]))
    for l in sweep.splitlines():
        if re.match(r"\| \d\d \|", l) and not l.rstrip().endswith("|"):
            err("pattern-audit.md: malformed sweep row")
    if "Figures with no source: 0" not in au:
        err("pattern-audit.md: does not state 'Figures with no source: 0'")

# ---------------------------------------------------------------------------------------------- coverage
if len(CONVS) < 20:
    err("fewer than 20 conversation files (%d)" % len(CONVS))
if len(CONVS) < 22:
    err("fewer than 22 conversations (%d)" % len(CONVS))
allint = set()
for c in CONVS:
    allint |= set(re.findall(r"[A-Z]{3}-\d{3}", c["header"].get("Intents covered", "")))
if len(allint) < 25:
    err("only %d distinct intents covered (need 25)" % len(allint))
for f in FAMILIES:
    if not any(i.startswith(f) for i in allint):
        err("intent family %s not covered" % f)
for p in PERSONAS:
    if not any(c["header"].get("Persona", "").startswith(p) for c in CONVS):
        err("persona %s not covered" % p)
for v in VECTORS:
    if not any(v in c["header"].get("Adversarial vectors", "") for c in CONVS):
        err("adversarial vector '%s' not covered" % v)
for p in ("P0", "P1", "P2"):
    if not any(re.search(p, c["header"].get("Priority", "")) for c in CONVS):
        err("no conversation at priority %s" % p)
fired = set()
for c in CONVS:
    h = c["header"].get("Escalation IDs", "")
    for m5 in re.finditer(r"(ESC-\d{3})(?! \(offered)", h):
        fired.add(m5.group(1))
if len(fired) < 10:
    err("only %d distinct ESC triggers fired (need 10): %s" % (len(fired), sorted(fired)))
for must in ("ESC-001", "ESC-004", "ESC-008", "ESC-011", "ESC-013", "ESC-015"):
    if not any(must in c["header"].get("Escalation IDs", "") for c in CONVS):
        err("%s not exercised by any conversation" % must)
for r in SEC_RULES:
    if not any(r in [x.strip() for x in c["header"].get("Security rules exercised", "").split(",")] for c in CONVS):
        err("account-security rule %s not exercised" % r)
cats = set()
for c in CONVS:
    tags = c["header"].get("Coverage tags", "").lower()
    if "information-vs-advice" in tags or "information-versus-advice" in tags:
        for cat in ADVICE_CATEGORIES:
            if cat in tags:
                cats.add(cat)
if len(cats) < 3:
    err("information-versus-advice boundary shown for only %d categories: %s" % (len(cats), sorted(cats)))
hindi = [c for c in CONVS if c["header"].get("Language") == "hi" and any(re.search(r"[ऀ-ॿ]", x["text"]) for x in c["turns"])]
hinglish = [c for c in CONVS if c["header"].get("Language") == "hinglish"]
secondary = [c for c in CONVS if c["header"].get("Language", "").startswith("gu") or "secondary" in c["header"].get("Language", "")]
if not hindi:
    err("no Hindi (Devanagari) conversation")
if len(hinglish) < 3:
    err("fewer than 3 Hinglish conversations (%d)" % len(hinglish))
if not secondary:
    err("no secondary-language conversation")
if not any(re.search(r"lang_id_floor|fallback ladder", c["text"]) for c in secondary):
    err("secondary-language conversation does not show the fallback ladder")
l7 = [c for c in CONVS if "level-7" in c["name"]]
if len(l7) != 1:
    err("expected exactly one Level 7 conversation, found %d" % len(l7))
else:
    c = l7[0]
    if len(c["turns"]) < 25:
        err("Level 7 conversation has %d messages (need 25 or more)" % len(c["turns"]))
    if len(set(re.findall(r"[A-Z]{3}-\d{3}", c["header"].get("Intents covered", "")))) < 3:
        err("Level 7 conversation covers fewer than 3 intents")
    raws = [float(m6.group(1)) for x in c["turns"] for m6 in [re.search(r"raw (-?[\d.]+),", x["rows"].get("Sentiment", ""))] if m6]
    low = [i for i, r in enumerate(raws) if r < -0.70]
    if not low or not any(r >= -0.40 for r in raws[low[-1] + 1:]):
        err("Level 7 conversation shows no sentiment drop below -0.70 followed by recovery to -0.40 or above")
    if not any("auth otp_verified" in x["rows"].get("State", "") for x in c["turns"]) or not any("auth anonymous" in x["rows"].get("State", "") for x in c["turns"]):
        err("Level 7 conversation does not show an authentication transition")
    if not re.search(r"GR-ADV-\d\d", c["text"]):
        err("Level 7 conversation shows no guardrail activation")
    if not c["header"].get("Escalation IDs") or c["header"].get("Escalation IDs") == "none":
        err("Level 7 conversation has no escalation decision")
for k in ("XTR-01", "ESC-006"):
    if not any(k in c["header"].get("Escalation IDs", "") for c in CONVS):
        err("%s not exercised" % k)
if not any("session timeout" in c["header"].get("Coverage tags", "").lower() or "timeout" in c["header"].get("Coverage tags", "").lower() for c in CONVS):
    err("no session-timeout conversation")
if not any("step-up" in c["header"].get("Coverage tags", "").lower() for c in CONVS):
    err("no step-up conversation")
if not any("ESC-014" in c["header"].get("Escalation IDs", "") for c in CONVS):
    err("no tool-failure (ESC-014) conversation")
if not any("carry-over" in c["header"].get("Coverage tags", "").lower() for c in CONVS):
    err("no multi-session carry-over conversation")
if not any("multi-intent" in c["header"].get("Coverage tags", "").lower() for c in CONVS):
    err("no multi-intent conversation")
if not any("near-miss" in c["header"].get("Coverage tags", "").lower() for c in CONVS):
    err("no non-escalation near-miss conversation")
if not any("sentiment recovery" in c["header"].get("Coverage tags", "").lower() for c in CONVS):
    err("no sentiment-recovery conversation")
if not any("degrade" in c["header"].get("Coverage tags", "").lower() or "degradation" in c["header"].get("Coverage tags", "").lower() for c in CONVS):
    err("no graceful-degradation conversation")

# ------------------------------------------------------------------------------------------------- report
print("conversation files:", len(CONVS), "in", os.path.relpath(SIM_DIR, ROOT) if SIM_DIR.startswith(ROOT) else SIM_DIR)
print("messages:", sum(len(c["turns"]) for c in CONVS))
print("distinct intents:", len(allint), "| ESC fired:", len(fired), sorted(fired))
print("personas:", sorted({c["header"].get("Persona", "").split(" (")[0] for c in CONVS}))
print("languages:", dict(collections.Counter(c["header"].get("Language", "") for c in CONVS)))
print("template ids used:", len({t for c in CONVS for t in re.findall(r"`(TPL-[A-Z0-9-]+)/", c["text"])}), "of", len(TPL))
for w in warnings:
    print("WARN", w)
for e in errors:
    print("ERROR", e)
print("RESULT:", ("FAIL (%d errors)" % len(errors)) if errors else "PASS")
sys.exit(1 if errors else 0)
