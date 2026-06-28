# Working Scratchpad

## Current objective
COMP6733 D3. Feature `compile-loop-demo` specs DRAFTED + checkpoint written. Build demo FIRST, then write proposal §2 (Background 30%, user=member2). Flow: docs✅→CEO Q&A→Codex audit→build.

## Last step taken
- Wrote 2 specs (docs/features/compile-loop-demo.md + -implementation.md) + Stage-1 checkpoint.
- FIXED hook noise: removed 3 broken OpenPets companion PowerShell hooks from .claude/settings.json (#1 PreToolUse, #2 Stop). JSON re-validated VALID. CCC `.sh` hooks untouched.
- REMOVED OpenPets MCP from ~/.claude.json (user asked; unused). `claude mcp list` = none. Takes full effect next session restart.
- #3 Auto-update: NOT auto-fixed — user must run `claude migrate-installer` themselves (Claude Code self-updater, not CCC).

## Next step (awaiting CEO)
Confirm before build: D1 AI model (rec Claude Sonnet); D2 board revision (Rev1 HTS221 vs Rev2 HS3003); tasks.json wording. Prereqs: install arduino-cli + mbed_nano (me); ANTHROPIC_API_KEY (CEO). Then Codex audit spec → build demo/.

## Blockers
- arduino-cli not installed; API key needed; board revision unknown.
- Context budget 95%+ — user declined handoff.

## Context
简体中文, professional. AutoEmbed mapping: API table≈KnowledgeGen, compile loop≈AutoProg compile loop. Proposal due ~Week 5.
