#!/usr/bin/env bash
# Symlink a skill from this repo into every agent runtime's skills directory.
#
# Creates a chain: runtime → ~/.agents/skills/<skill> → this repo
# so edits in the repo propagate instantly to every runtime.
#
# Usage:
#   ./bin/link-skill.sh <skill-name>
#
# Example:
#   ./bin/link-skill.sh no-directors-commentary

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <skill-name>"
  echo "Example: $0 no-directors-commentary"
  exit 1
fi

SKILL="$1"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_PATH="$REPO_DIR/$SKILL"

if [ ! -d "$SKILL_PATH" ]; then
  echo "Error: skill '$SKILL' not found at $SKILL_PATH" >&2
  exit 1
fi

AGENTS_DIR="$HOME/.agents/skills"
mkdir -p "$AGENTS_DIR"

# Relative link when the repo sits at $HOME/skills so it survives
# a username change; absolute otherwise.
if [ "$REPO_DIR" = "$HOME/skills" ]; then
  AGENTS_TARGET="../../skills/$SKILL"
else
  AGENTS_TARGET="$SKILL_PATH"
fi

ln -sfn "$AGENTS_TARGET" "$AGENTS_DIR/$SKILL"
echo "  ~/.agents/skills/$SKILL  →  $AGENTS_TARGET"

for runtime in .cursor .claude .codex; do
  runtime_dir="$HOME/$runtime/skills"
  if [ ! -d "$runtime_dir" ]; then
    echo "  ~/$runtime/skills                  (skipped — directory doesn't exist)"
    continue
  fi
  ln -sfn "../../.agents/skills/$SKILL" "$runtime_dir/$SKILL"
  echo "  ~/$runtime/skills/$SKILL  →  ../../.agents/skills/$SKILL"
done

echo ""
echo "Linked. Verify with:"
echo "  readlink -f ~/.agents/skills/$SKILL"
