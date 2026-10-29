"""What must never be stored or shown: secrets, emails, phone numbers, and the profile's Keep out terms.

Secrets are found with gitleaks' default rules, vendored in gitleaks.toml (MIT, see GITLEAKS-LICENSE), using its keywords,
entropy thresholds, and allowlists the way gitleaks does. Refresh the rules with:

  curl -sL https://raw.githubusercontent.com/gitleaks/gitleaks/master/config/gitleaks.toml -o scripts/gitleaks.toml

then delete the gcp-api-key rule's allowlist of literal Google API keys, which secret scanners and pre-commit hooks flag. The
package validator fails until it's gone.
"""
import collections
import hashlib
import math
import re
import tomllib
from pathlib import Path

RULES_FILE = Path(__file__).with_name("gitleaks.toml")
Rule = collections.namedtuple("Rule", "id regex keywords entropy group allow stopwords")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<![\w-])(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]\d{3}[ .-]\d{4}(?![\w-])")
MASK = re.compile(r"\[(?:REDACTED:[\w-]+|EMAIL|PHONE|KEPT OUT)\]")
# gitleaks skips low-entropy values on purpose, which lets a typed password like password=hunter22 through, so this one
# rule stays alongside its rules.
ASSIGNMENT = re.compile(r"(?i)\b((?:api[_-]?key|secret|token|password|passwd|client[_-]?secret)\b\s*[:=]\s*)(?!\[REDACTED:[\w-]+\](?:[\s'\"]|$))['\"]?[^\s'\"]{8,}['\"]?")


def scoped_flags(pattern):
    """Go regexes allow (?i) mid-pattern, applying to the rest of its group; Python needs that written as (?i:...)."""
    pattern = pattern.replace("[[:alnum:]]", "[A-Za-z0-9]").replace(r"\z", r"\Z")
    while (at := pattern.find("(?i)", 1)) > 0:
        depth, end, i = 0, len(pattern), at + 4
        while i < len(pattern):
            char = pattern[i]
            if char == "\\":
                i += 2
                continue
            if char == "[":
                i += 2 if pattern[i + 1:i + 2] == "^" else 1
                i += 1 if pattern[i:i + 1] == "]" else 0
                while i < len(pattern) and pattern[i] != "]":
                    i += 2 if pattern[i] == "\\" else 1
            elif char == "(":
                depth += 1
            elif char == ")":
                if not depth:
                    end = i
                    break
                depth -= 1
            i += 1
        pattern = f"{pattern[:at]}(?i:{pattern[at + 4:end]}){pattern[end:]}"
    return pattern


def load_rules():
    config = tomllib.loads(RULES_FILE.read_text())
    rules = []
    for rule in config["rules"]:
        if "regex" not in rule:
            continue
        lists = [a for a in rule.get("allowlists", []) if a.get("regexTarget", "secret") == "secret" and "paths" not in a]
        rules.append(Rule(rule["id"], re.compile(scoped_flags(rule["regex"])), [k.lower() for k in rule.get("keywords", [])],
                          rule.get("entropy"), rule.get("secretGroup"),
                          [re.compile(scoped_flags(p)) for a in lists for p in a.get("regexes", [])],
                          [w.lower() for a in lists for w in a.get("stopwords", [])]))
    shared = config.get("allowlist", {})
    return (rules, [re.compile(scoped_flags(p)) for p in shared.get("regexes", [])],
            [w.lower() for w in shared.get("stopwords", [])])


RULES, ALLOW, STOPWORDS = load_rules()
DIGEST = hashlib.sha256(RULES_FILE.read_bytes() + Path(__file__).read_bytes()).hexdigest()[:16]


def entropy(text):
    counts = collections.Counter(text)
    return -sum(n / len(text) * math.log2(n / len(text)) for n in counts.values())


def secret_spans(text):
    lower = text.lower()
    for rule in RULES:
        if rule.keywords and not any(k in lower for k in rule.keywords):
            continue
        for match in rule.regex.finditer(text):
            group = rule.group or next((g for g in range(1, match.re.groups + 1) if match.group(g)), 0)
            secret = match.group(group)
            if (not secret or MASK.fullmatch(secret) or (rule.entropy and entropy(secret) < rule.entropy)
                    or any(a.search(secret) for a in (*rule.allow, *ALLOW))
                    or any(w in secret.lower() for w in (*rule.stopwords, *STOPWORDS))):
                continue
            yield match.start(group), match.end(group), rule.id


def redact_secrets(text):
    """Replace each secret gitleaks would report with [REDACTED:<rule id>], keeping the text around it."""
    spans = sorted(secret_spans(text))
    if not spans:
        return ASSIGNMENT.sub(r"\1[REDACTED:assignment]", text)
    merged = [list(spans[0])]
    for start, end, rule in spans[1:]:
        if start < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end, rule])
    for start, end, rule in reversed(merged):
        text = f"{text[:start]}[REDACTED:{rule}]{text[end:]}"
    return ASSIGNMENT.sub(r"\1[REDACTED:assignment]", text)


def keep_out_pattern(terms):
    terms = sorted({t for t in terms if t}, key=len, reverse=True)
    return re.compile(rf"(?<!\w)(?:{'|'.join(map(re.escape, terms))})(?!\w)", re.I) if terms else None


def scrub(text, keep_out=None):
    """Everything the script prints for the agent: secrets again, in case the corpus predates a rule, then emails, phone
    numbers, and the profile's Keep out terms."""
    if not text:
        return text
    text = PHONE.sub("[PHONE]", EMAIL.sub("[EMAIL]", redact_secrets(text)))
    return keep_out.sub("[KEPT OUT]", text) if keep_out else text
