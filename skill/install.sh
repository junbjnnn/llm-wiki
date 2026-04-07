#!/usr/bin/env bash
# Install llm-wiki skill for Claude Code.
# Usage: bash skill/install.sh

set -euo pipefail

SKILL_DIR="$HOME/.claude/skills/llm-wiki"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

echo "Installing llm-wiki skill..."

mkdir -p "$SKILL_DIR"
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"

# Copy templates
mkdir -p "$SKILL_DIR/templates"
cp "$SCRIPT_DIR/templates/"* "$SKILL_DIR/templates/"

# Copy scripts
mkdir -p "$SKILL_DIR/scripts"
cp "$REPO_DIR/scripts/"*.py "$SKILL_DIR/scripts/"

echo "Skill installed at $SKILL_DIR"
echo "Activate with /wiki in Claude Code."
