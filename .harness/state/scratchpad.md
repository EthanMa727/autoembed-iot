# Working Scratchpad

## Current objective
COMP6733 D3. `demo/` (compile-loop slice) BUILT + self-verified: **Compiled 5/5, all first-try** (model=claude-sonnet-4-6, board=Nano 33 BLE Sense Rev2/HS3003). Awaiting CEO next-step choice.

## ⚠️ HARD DEADLINE (project brief, 17:00 AEST, "no extensions")
- GRADED PROPOSAL due **Fri 3 Jul 2026** (~5 days). Milestone Fri 24 Jul; Final report Fri 10 Aug; Final demo+interview 11 Aug.
- Proposal split: Topic 20% / **Background 30% = member2** / Plan 25% / Presentation 25%.
- Brief mandates (full project, not demo): flash loop + 30–50 task 3-level bench + ≥2 LLM compare + no-feedback baseline.

## Last step taken
Built `demo/` (6 .py + HS3003 api_table + 5 tasks + .gitignore + README); ran `py demo/mvp.py` → 5/5 compiled, 0 repairs; synced [CONFIRM] into both spec files. THEN wrote durable evidence doc `docs/features/compile-loop-demo-run.md` (env + pipeline diagram + console transcript + result table + all 5 generated sketches embedded + proves/doesn't-prove + reproduce). All 5 sketches confirmed genuine (HS300x init w/ failure guard, averaging, humidity hysteresis).

## Next step
Codex review reported done by CEO. Strategic call made: **proposal FIRST** (graded, due Fri 3 Jul; flash loop has no near deadline, milestone 24 Jul). Wrote completed §1+§2 → `docs/proposal/sections-1-2.md` (grounded in our demo; preserves teammates' prose; added §1.2 problem/objective/scope, §1.3 RQs, broadened §2.1 breadth incl. [4][5][6], §2.2 implemented-vs-planned honesty, NEW §2.3 preliminary feasibility w/ pipeline + 5/5 result). Fixed two wrong LLM expansions in their text ("Limited Learning Model"/"Learning Lifecycle Management" → Large Language Model). Proposal file = `ref-doc/6733 proposal .docx` (read via zipfile XML; python-docx NOT installed). Author map: §1 Guangyu / §2 yichen / §3 Huaixuan / §4 Sijun / §5&6 Jianyang.
CEO merged my §1.2/1.3/2.3 into docx + added TOC (confirmed via re-extract); trailing author block removed. Then designed cover/title page → `docs/proposal/cover-page.md` (3 title options [rec: "From Natural Language to Working Firmware"], field table, A4 ASCII mockup, typesetting spec, to-dos). Doc top currently just "Project Proposal", no real cover. Team=5: Guangyu Ma/Yichen Ma/Huaixuan Hu/Sijun Chen/Jianyang Dong; zIDs unknown (placeholders).
Course facts CONFIRMED from brief PDF: "COMP6733 IoT Research Project", **26T2** (2026 Term 2), team of **five**, proposal = preliminary report + Wk5 presentation (must include: how-to-tackle + justification, impl plan + timeline). AutoEmbed paper key terms for titles: knowledge generation/injection, auto-programming, hardware-in-the-loop, "syntactically correct but contextually inappropriate", 7000 libs / 71 modules / 350 tasks, acc 95.7% / success 86.5%. PDF text extracted via pypdf (installed) — `pdftoppm` absent so Read-PDF fails; use pypdf + `sys.stdout.reconfigure(utf-8)` (PowerShell GBK chokes on bullets).
Pending: CEO picking a NEW title (gave 4 fresh options, rec "Beyond Syntactically Correct"/"Knowledge-Injected, Compiler-in-the-Loop…"); then lock into cover-page.md. Still: group#/zIDs; unify IEEE cites; align §5 Demo (MicroPython) + §3 w/ C/C++; flash loop after proposal. Asked: board in hand + Rev2?

## Blockers / open questions
- (none) — demo works.

## Context
简体中文, professional. Win: use `py` launcher (bare `python` = Store stub). API key live (User env var, len=108); ADVISE ROTATE (was typed inline earlier → may be in shell history). arduino-cli 1.5.1, mbed_nano 4.6.0, anthropic 0.112.0.
- Side-fix: model IS already 1M (claude-opus-4-8). budget-monitor.sh was mislabeling it 200K (regex only knew `[1m]`-suffixed ids); patched to treat opus-4-6/4-7/4-8 + sonnet-4-6 + fable/mythos-5 as 1M standard. Takes effect NEXT prompt (~416K = ~42% of 1M, nag stops).
