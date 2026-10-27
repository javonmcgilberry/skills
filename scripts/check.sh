#!/bin/sh
set -e
cd "$(dirname "$0")/.."
python3 -m unittest -q scripts/test_docs_check.py
python3 scripts/docs_check.py
python3 skills/know-thyself/scripts/validate_skill.py
