"""Each rule is proven by a seeded break that only that rule catches, plus clean cases that must pass.

A clean case that passes only because of a rule, such as a ./ path or a skill page naming a file in the repository it runs
in, is that rule's seed: without the rule, the case reports a problem.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_check  # noqa: E402

CLI = '''import argparse
parser = argparse.ArgumentParser()
commands = parser.add_subparsers(dest="command", required=True)
score = commands.add_parser("score")
score.add_argument("--markdown", action="store_true")
commands.add_parser("mine")
parser.parse_args()
'''


def repo_with(files):
    root = Path(tempfile.mkdtemp()) / "repo"
    base = {"tool/scripts/convo.py": CLI, "docs/guide.md": "# Guide\n\n## Setup steps\n", ".gitignore": "data/\n",
            "bin/link-skill.sh": "", "skills/tool/SKILL.md": "# Tool\n", "skills/tool/samples/a.txt": "",
            "skills/tool/references/notes.md": "# Notes\n"}
    for rel, body in {**base, **files}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root


def kinds(files):
    return sorted(kind for _, _, kind, _ in docs_check.check(repo_with(files)))


class DocsCheck(unittest.TestCase):
    def test_clean_docs_pass(self):
        self.assertEqual(kinds({"README.md": "Run `tool/scripts/convo.py score --markdown`, see [setup](docs/guide.md#setup-steps), "
                                             "data goes to `data/corpus.jsonl` and reports to `<reports>/x.md`.\n"}), [])

    def test_recorded_eval_results_are_evidence_not_docs(self):
        self.assertEqual(kinds({"evals/tool/results/run-1/response.md": "Wrote [it](/home/ana/workspace/gone.md).\n"}), [])

    def test_eval_docs_outside_results_are_checked(self):
        self.assertEqual(kinds({"evals/tool/README.md": "See [it](missing.md).\n"}), ["link"])

    def test_missing_path(self):
        self.assertEqual(kinds({"README.md": "Read `docs/missing.md`.\n"}), ["path"])

    def test_missing_path_in_fenced_block(self):
        self.assertEqual(kinds({"README.md": "```sh\npython3 tool/scripts/gone.py\n```\n"}), ["path"])

    def test_path_next_to_page_that_shadows_a_top_level_entry(self):
        self.assertEqual(kinds({"scripts/check.sh": "", "tool/README.md": "Run `scripts/convo.py`.\n"}), [])

    def test_missing_path_that_shadows_a_top_level_entry(self):
        self.assertEqual(kinds({"scripts/check.sh": "", "tool/README.md": "Run `scripts/gone.py`.\n"}), ["path"])

    def test_broken_link(self):
        self.assertEqual(kinds({"README.md": "See [guide](docs/nope.md).\n"}), ["link"])

    def test_link_that_escapes_and_reenters(self):
        self.assertEqual(kinds({"README.md": "See [guide](../repo/docs/guide.md).\n"}), ["escape"])

    def test_broken_anchor(self):
        self.assertEqual(kinds({"README.md": "See [setup](docs/guide.md#install).\n"}), ["anchor"])

    def test_unknown_command(self):
        self.assertEqual(kinds({"README.md": "Run `convo.py profile`.\n"}), ["command"])

    def test_unknown_flag(self):
        self.assertEqual(kinds({"README.md": "Run `convo.py score --table`.\n"}), ["command"])

    def test_dot_slash_starts_at_the_root(self):
        self.assertEqual(kinds({"docs/install.md": "Run `./bin/link-skill.sh tool`.\n"}), [])

    def test_missing_dot_slash_path(self):
        self.assertEqual(kinds({"docs/install.md": "Run `./bin/gone.txt`.\n"}), ["path"])

    def test_skill_page_names_a_path_in_the_repository_it_runs_in(self):
        self.assertEqual(kinds({"skills/tool/SKILL.md": "Write `docs/target-only.md` in the repository you run on.\n"}), [])

    def test_missing_path_in_the_skill_package(self):
        self.assertEqual(kinds({"skills/tool/references/notes.md": "See `samples/gone.txt`.\n"}), ["path"])

    def test_skill_page_names_a_missing_path_by_its_repository_path(self):
        self.assertEqual(kinds({"skills/tool/SKILL.md": "Grade with `skills/tool/samples/a.txt`, not "
                                                        "`skills/tool/samples/gone.txt`.\n"}), ["path"])

    def test_bare_script_name_that_is_a_tracked_file(self):
        self.assertEqual(kinds({"README.md": "Run `convo.py mine` or `link-skill.sh <name>`.\n"}), [])

    def test_unknown_script(self):
        self.assertEqual(kinds({"README.md": "Run `gone.py` first.\n"}), ["script"])

    def test_install_commands_name_real_skills(self):
        self.assertEqual(kinds({"README.md": "```sh\nnpx skills@latest add owner/repo --skill tool\n./bin/link-skill.sh tool\n"
                                             "./bin/link-skill.sh <skill-name>\n```\n"}), [])

    def test_install_command_for_an_unknown_skill(self):
        self.assertEqual(kinds({"README.md": "Run `npx skills@latest add owner/repo --skill gone`.\n"}), ["command"])

    def test_link_command_for_an_unknown_skill(self):
        self.assertEqual(kinds({"README.md": "Run `./bin/link-skill.sh gone`.\n"}), ["command"])


if __name__ == "__main__":
    unittest.main()
