#!/bin/bash
# Hierarchical Agent Pipeline - Installer
# Copies the agent system to your project or user-level Claude Code config

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Hierarchical Agent Pipeline — Installer         ║${NC}"
echo -e "${CYAN}║  11 Agents | 8 Phases | 2 Slash Commands         ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Choose installation scope
echo -e "${YELLOW}Where do you want to install?${NC}"
echo "  1) Current project (.claude/ in current directory)"
echo "  2) User-level (~/.claude/ for all projects)"
echo "  3) Custom path"
read -p "Choose [1/2/3]: " choice

case $choice in
  1)
    TARGET_DIR="$(pwd)/.claude"
    ;;
  2)
    TARGET_DIR="$HOME/.claude"
    ;;
  3)
    read -p "Enter path: " TARGET_DIR
    ;;
  *)
    echo -e "${RED}Invalid choice${NC}"
    exit 1
    ;;
esac

echo ""
echo -e "${YELLOW}Installing to: ${TARGET_DIR}${NC}"

# Create directories
mkdir -p "$TARGET_DIR/agents"
mkdir -p "$TARGET_DIR/commands"

# Copy agents
echo -e "${GREEN}Copying agents...${NC}"
AGENTS=(
  "orchestrator"
  "idea-researcher"
  "tech-scout"
  "architect"
  "project-planner"
  "doc-reviewer"
  "implementer"
  "code-optimizer"
  "test-writer"
  "qa-validator"
  "deployer"
  "monitor"
)

for agent in "${AGENTS[@]}"; do
  if [ -f "$SCRIPT_DIR/.claude/agents/${agent}.md" ]; then
    cp "$SCRIPT_DIR/.claude/agents/${agent}.md" "$TARGET_DIR/agents/"
    echo -e "  ✅ ${agent}"
  else
    echo -e "  ${RED}❌ ${agent} — not found${NC}"
  fi
done

# Copy commands
echo -e "${GREEN}Copying slash commands...${NC}"
COMMANDS=("pipeline" "quick-task")

for cmd in "${COMMANDS[@]}"; do
  if [ -f "$SCRIPT_DIR/.claude/commands/${cmd}.md" ]; then
    cp "$SCRIPT_DIR/.claude/commands/${cmd}.md" "$TARGET_DIR/commands/"
    echo -e "  ✅ /${cmd}"
  else
    echo -e "  ${RED}❌ /${cmd} — not found${NC}"
  fi
done

# Copy CLAUDE.md if installing to project level
if [ "$choice" = "1" ]; then
  if [ -f "$(pwd)/CLAUDE.md" ]; then
    echo ""
    echo -e "${YELLOW}CLAUDE.md already exists. Merge manually from:${NC}"
    echo -e "  $SCRIPT_DIR/CLAUDE.md"
  else
    cp "$SCRIPT_DIR/CLAUDE.md" "$(pwd)/CLAUDE.md"
    echo -e "${GREEN}  ✅ CLAUDE.md${NC}"
  fi
fi

# Create docs directory structure
echo -e "${GREEN}Creating docs structure...${NC}"
DOCS_DIR="$(pwd)/docs"
mkdir -p "$DOCS_DIR/reviews" "$DOCS_DIR/task-reports" "$DOCS_DIR/test-reports"
echo -e "  ✅ docs/"
echo -e "  ✅ docs/reviews/"
echo -e "  ✅ docs/task-reports/"
echo -e "  ✅ docs/test-reports/"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Installation Complete!                          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Usage:${NC}"
echo -e "  ${YELLOW}/pipeline${NC} [idea]      — Launch full pipeline"
echo -e "  ${YELLOW}/quick-task${NC} [agent]    — Run single agent"
echo -e "  ${YELLOW}@orchestrator${NC}          — Direct orchestrator call"
echo ""
echo -e "${GREEN}Agent Hierarchy:${NC}"
echo -e "  🎯 orchestrator (Opus)"
echo -e "  ├── 🔍 idea-researcher (Sonnet) + 🔭 tech-scout (Haiku)"
echo -e "  ├── 🏗️  architect (Opus)"
echo -e "  ├── 📋 project-planner (Sonnet)"
echo -e "  ├── 🔎 doc-reviewer (Sonnet)"
echo -e "  ├── 💻 implementer (Sonnet) + ⚡ code-optimizer (Sonnet)"
echo -e "  ├── 🧪 test-writer (Sonnet) + ✅ qa-validator (Sonnet)"
echo -e "  ├── 🚀 deployer (Sonnet)"
echo -e "  └── 🔧 monitor (Haiku)"
echo ""
echo -e "${YELLOW}Tip:${NC} For your Agent Platform project, start with:"
echo -e "  /pipeline Add WebSocket-based real-time market data streaming"
