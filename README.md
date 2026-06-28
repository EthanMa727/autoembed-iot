# autoembed-iot

**LLM-driven automated software development for embedded IoT systems.**

A research prototype that takes a developer's plain-English requirement, resolves the
hardware libraries it needs, generates embedded firmware, compiles it, and (eventually)
flashes and verifies it on real hardware — closing the loop from natural language to a
working sketch. AutoEmbed-style.

> COMP6733 IoT research project (UNSW, 26T2) · 5-person team · Project **D3** ·
> reference paper: *AutoEmbed — LLM-driven Automated Software Development for Generic
> Embedded IoT Systems*.

---

## Status

**Early / greenfield.** The orchestration layer is not yet scaffolded. The first concrete
deliverable is a crude end-to-end **compile-loop demo** that proves the two mechanisms the
whole project rests on, ahead of the Week-5 proposal:

1. **Per-module API-table injection** — hand a small, hand-written cheat-sheet of a sensor's
   commands to the model alongside the task (≈ AutoEmbed "Knowledge Generation").
2. **Compile → repair loop** — feed compiler errors back to the model and retry, a few times
   (≈ AutoEmbed "Auto-Programming → Compile Loop").

See [`docs/features/compile-loop-demo.md`](docs/features/compile-loop-demo.md) for the
plain-language spec and [`docs/features/compile-loop-demo-implementation.md`](docs/features/compile-loop-demo-implementation.md)
for the engineering notes.

---

## The idea

```
natural-language task
        │
        ▼
  build prompt  ◄──── per-module API table (sensor cheat-sheet)
        │
        ▼
   LLM (Claude / GPT)  ──► C/C++ Arduino sketch
        │
        ▼
   arduino-cli compile ──► ✓ done
        │ ✗ (compiler errors)
        └────────► feed errors back, regenerate  (retry ≤ 3)
                          │
            (later) ──► flash to board ──► read serial ──► verify behaviour
```

The **compile-loop demo** implements everything down to the compile step, **compile-only**,
targeting the **Arduino Nano 33 BLE Sense** and its on-board temperature/humidity sensor —
no physical board required yet. Flashing, serial verification, and automatic library
resolution across the ~7,000 Arduino libraries are later milestones.

---

## Tech stack

| Layer | Choice |
|---|---|
| Orchestration / agent layer | **Python** |
| Generated firmware | **C/C++** (Arduino, built with `arduino-cli`) |
| Code generation | Cloud **LLM API** (default: Claude / Anthropic; pluggable provider) |
| Target hardware | **Arduino Nano 33 BLE Sense** (`arduino:mbed_nano:nano33ble`) |
| Tests | **pytest** + a hardware-in-the-loop / benchmark eval harness |

Planned; greenfield, not yet scaffolded.

---

## Repository structure

```
autoembed-iot/
├── docs/features/          # feature specs (CEO-domain plain language + impl notes)
│   ├── compile-loop-demo.md
│   └── compile-loop-demo-implementation.md
├── ref-doc/                # course brief, proposal rubric, tutorials, AutoEmbed paper
├── constitution.md         # project identity, principles, red lines
├── AGENTS.md               # universal project context (AGENTS.md standard) + auditor brief
├── CLAUDE.md               # AI workflow operating manual
├── docs-harness/           # CCC-MAGI harness design rationale
└── .harness/, .claude/, .codex/   # CCC-MAGI development harness (skills, agents, hooks)
```

The source tree (`demo/`, then the full pipeline) is established at first scaffold; see the
implementation notes for the planned `demo/` layout.

---

## Roadmap

- [ ] **Compile-loop demo** — NL → AI sketch → compile → repair loop, compile-only (Week-5 MVP)
- [ ] **Flash loop** — upload to a real Nano 33 BLE Sense, read serial, verify runtime behaviour
- [ ] **Library resolution** — pick the right libraries automatically instead of hand-written cheat-sheets
- [ ] **Benchmark + evaluation** — 30–50 tasks across difficulty levels; multi-model cost/latency/accuracy comparison

The AutoEmbed reference scope (~71 modules / ~350 tasks) is the north star, not the Week-8
target.

---

## Running the demo (planned)

> Not yet implemented — this is the intended workflow once the `demo/` package lands.

Prerequisites:

- Python 3
- [`arduino-cli`](https://arduino.github.io/arduino-cli/) with the Nano core:
  `arduino-cli core install arduino:mbed_nano`
- An LLM provider key in the environment (default: `ANTHROPIC_API_KEY`)
- `pip install anthropic`

```bash
# single task
python -m demo.mvp --task "read the on-board temperature and print it to serial every second"

# bundled batch → results table (compiled N/total, repairs per task)
python -m demo.mvp --batch
```

---

## How this repo is developed

This project is built with **CCC-MAGI**, a spec-driven, cross-model-audited development
harness (`CLAUDE.md`, `AGENTS.md`, `constitution.md`, `.harness/`). Features go through a
staged workflow — spec → finalize → plan → implement → test → smoke-test → commit — with an
independent cross-model auditor at each gate. Teammates and other AI tools (Codex, Cursor,
Cline, Aider, Gemini CLI) read `AGENTS.md` for project context. You can ignore the harness to
read the project itself; start with this README and `docs/features/`.

---

## References

- **AutoEmbed**: *LLM-driven Automated Software Development for Generic Embedded IoT Systems*
  (the project's anchor reference — see `ref-doc/`).
- Course materials, proposal rubric, and tutorials live under `ref-doc/`.
