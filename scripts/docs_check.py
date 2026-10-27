#!/usr/bin/env python3
"""Fail when tracked Markdown names something the repository does not have.

  python3 scripts/docs_check.py [repo]    prints one line per problem and exits 1 when there is one

Rules:
  path     a path in code (a code span or fenced block) that contains a slash and starts at a tracked top-level entry of the
           repository or of the document's directory must exist. A leading ./ starts at the repository root, where commands
           run. Gitignored paths, placeholders such as <name>, globs, home and absolute paths, and URLs are skipped.
           A page inside a skill package (skills/<name>/ with a SKILL.md) is installed and run in other repositories, so its
           paths start at the package instead of the repository root. A path that starts at an entry of the package must
           exist there, a path that starts at the package's own repository path (skills/<name>/...) must exist in the
           repository, and any other path names a file in the repository the skill runs in and is skipped.
  link     a relative Markdown link must resolve to a file inside the repository.
  escape   a relative link must not leave the repository, even when it re-enters at a real file.
  anchor   a link's #fragment must match a heading in its target.
  script   a script file name without a slash in code, such as `convo.py` or `link-skill.sh`, must be the name of a tracked file.
  command  `convo.py <command>` in code must be a command the CLI defines, and each --flag after it on the line must be one
           that command accepts. The skill an install command names, in `npx skills@latest add <repo> --skill <name>` or
           `link-skill.sh <name>`, must be a skill package in skills/.

Every tracked Markdown file is checked except recorded eval results under evals/*/results/, which are an agent's raw
output kept as evidence and can name files that existed only on the machine that ran the eval.
"""

import re
import subprocess
import sys
from functools import cache
from pathlib import Path

CODE_SPAN = re.compile(r"`([^`\n]+)`")
FENCE = re.compile(r"^```.*?^```", re.S | re.M)
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
TOKEN = re.compile(r"[\w.@~<>*{}$-]*/[\w./@<>*{}$-]*")
SCRIPT = re.compile(r"(?<![\w./<>{}*$@~-])([\w-]+\.(?:py|sh|mjs|mts|cjs|js|ts))(?![\w/<>-])")
COMMAND = re.compile(r"convo\.py\s+([a-z][\w-]*)([^\n`|]*)")
FLAG = re.compile(r"(?<![\w-])--[a-z][\w-]*")
INSTALL = re.compile(r"(?:skills@latest add\s+\S+.*?--skill|link-skill\.sh)\s+([^\s`]+)")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout


def slug(heading):
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", text))


def headings(path):
    return {slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+?)\s*#*$", path.read_text(), re.M)}


def code_chunks(text):
    """Code spans and fenced blocks, each with the 1-based line it starts on."""
    chunks = []
    for match in FENCE.finditer(text):
        chunks.append((text.count("\n", 0, match.start()) + 1, match.group(0)))
    outside = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    for match in CODE_SPAN.finditer(outside):
        chunks.append((outside.count("\n", 0, match.start()) + 1, match.group(1)))
    return chunks


@cache
def cli_flags(cli, command):
    """The flags a convo.py command accepts, or None when the command does not exist."""
    result = subprocess.run([sys.executable, str(cli), command, "--help"], capture_output=True, text=True)
    return set(FLAG.findall(result.stdout)) if result.returncode == 0 else None


def leaves(repo, start, link):
    """True when walking the link part by part ever climbs above the repository root, even if it comes back in."""
    depth = len(start.relative_to(repo).parts)
    for part in Path(link).parts:
        depth += -1 if part == ".." else 0 if part == "." else 1
        if depth < 0:
            return True
    return False


def check(repo):
    repo = Path(repo).resolve()
    tracked = set(git(repo, "ls-files").split())
    names = {path.rsplit("/", 1)[-1] for path in tracked}
    packages = {path.rsplit("/", 1)[0] for path in tracked if re.fullmatch(r"skills/[^/]+/SKILL\.md", path)}
    skills = {package.split("/")[1] for package in packages}
    clis = [repo / p for p in tracked if p.endswith("scripts/convo.py")]
    problems = []

    def ignored(rel):
        return bool(git(repo, "check-ignore", "--no-index", rel).strip())

    @cache
    def entries(base):
        """The tracked top-level entries under base, a directory relative to the repository ('' for the root)."""
        prefix = f"{base}/" if base else ""
        return {path[len(prefix):].split("/")[0] for path in tracked if path.startswith(prefix)}

    def path_problem(doc, package, token):
        """Why a path token in code names nothing, or None when it exists or isn't checked."""
        token = token.removeprefix("./")
        if package and token.startswith(f"{package}/"):
            return None if (repo / token).exists() or ignored(token) else f"`{token}` does not exist"
        base = package or ""
        root = repo / base
        first = token.split("/")[0]
        local = doc.parent / token
        if first in entries(base) and not (root / token).exists() and not local.exists() \
                and not ignored(str(Path(base) / token)):
            return f"`{token}` does not exist" + (f" in {package}" if package else "")
        if first not in entries(base) and first and (doc.parent / first).exists() and not local.exists():
            return f"`{token}` does not exist next to this page"
        return None

    recorded = re.compile(r"evals/[^/]+/results/")
    for doc_rel in sorted(p for p in tracked if p.endswith(".md") and not recorded.match(p)):
        doc = repo / doc_rel
        package = next((p for p in packages if doc_rel.startswith(f"{p}/")), None)
        text = doc.read_text()
        for line, chunk in code_chunks(text):
            for offset, chunk_line in enumerate(chunk.splitlines()):
                at = line + offset
                for token in TOKEN.findall(chunk_line):
                    token = token.rstrip(".,:;)")
                    if (token.startswith(("/", "~", "$", "http")) or any(c in token for c in "<>*{}")
                            or "://" in chunk_line and token in chunk_line.split("://", 1)[1]):
                        continue
                    message = path_problem(doc, package, token)
                    if message:
                        problems.append((doc_rel, at, "path", message))
                for script in SCRIPT.findall(chunk_line):
                    if script not in names:
                        problems.append((doc_rel, at, "script", f"`{script}` is not a file in the repository"))
                for skill in INSTALL.findall(chunk_line):
                    if not re.search(r"[<>*{}$]", skill) and skill not in skills:
                        problems.append((doc_rel, at, "command", f"`{skill}` is not a skill in skills/"))
                for command, rest in COMMAND.findall(chunk_line):
                    if not clis:
                        continue
                    flags = cli_flags(clis[0], command)
                    if flags is None:
                        problems.append((doc_rel, at, "command", f"`convo.py {command}` is not a command"))
                        continue
                    for flag in FLAG.findall(rest):
                        if flag not in flags:
                            problems.append((doc_rel, at, "command", f"`convo.py {command}` has no {flag}"))
        for match in LINK.finditer(FENCE.sub("", text)):
            target = match.group(1)
            line = text[:text.find(match.group(0))].count("\n") + 1
            if re.match(r"^[a-z]+:", target):
                continue
            path_part, _, fragment = target.partition("#")
            resolved = (doc.parent / path_part).resolve() if path_part else doc
            if path_part and leaves(repo, doc.parent, path_part):
                problems.append((doc_rel, line, "escape", f"link `{target}` leaves the repository"))
                continue
            if path_part and not resolved.exists():
                problems.append((doc_rel, line, "link", f"link `{target}` does not resolve"))
                continue
            if fragment and resolved.suffix == ".md" and fragment not in headings(resolved):
                problems.append((doc_rel, line, "anchor", f"anchor `#{fragment}` is not a heading in {resolved.name}"))
    return problems


def main():
    problems = check(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    for doc, line, kind, message in problems:
        print(f"{doc}:{line}: {kind}: {message}")
    print(f"{len(problems)} problem(s)" if problems else "docs check passed")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
