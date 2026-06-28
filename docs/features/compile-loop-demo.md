# Feature: Compile-Loop Demo (Week-5 proposal MVP slice)

## Status: DRAFT 2026-06-28

> Streamlined Stage 1. The happy path was paraphrased in conversation and the CEO
> chose to build this crude demo before writing proposal §2. Defaults the manager
> picked are flagged in §8 Decision history with a **[CONFIRM]** tag — these are the
> questions the CEO said they'd come back on.

## 1. What this feature is for

A laptop-side command-line tool that turns a plain-English embedded task into compiled
Arduino firmware for the Nano 33 BLE Sense — **without touching a physical board yet**.

You type (or pick) a task like *"read the on-board temperature sensor and print it to
serial every second."* The tool hands the request — together with a small hand-written
cheat-sheet of that sensor's commands — to an AI model, which writes the C/C++ sketch.
The tool then compiles the sketch with the Arduino command-line builder. If compilation
fails, the tool feeds the compiler's error message back to the AI to repair, and retries
a few times. For each task it reports whether the code compiled and how many repair
attempts it took.

Its purpose is **evidence, not product**: it proves the two core mechanisms of the whole
project (injecting a per-sensor command cheat-sheet into the prompt + a closed compile→
fix loop) work end-to-end, so the proposal's system-design section and the Week-8
milestone rest on something real instead of a promise.

## 2. Happy path

### 2.1 Single task compiles on the first try

When the user runs the tool against one task, the system builds a prompt from the task
text + the sensor cheat-sheet + a few coding rules, asks the AI for a sketch, saves it,
and compiles it. When the sketch compiles cleanly, the tool reports `compiled ✓, 0
repairs` for that task and shows the path to the generated sketch.

### 2.2 A small batch produces a results table

When the user runs the tool against the bundled set of 3–5 tasks, the system processes
each task in turn and prints one summary table at the end: per task, whether it compiled
and how many repair attempts were used, plus an overall "compiled N/total" line.

### 2.3 A failed compile gets repaired and then succeeds

When the AI's first sketch does not compile, the system shows that it caught the failure,
sends the compiler's error text back to the AI for a fix, compiles again, and — if the
fix worked — reports `compiled ✓, 1 repair` for that task. This is the behaviour the demo
most wants to show off live.

## 3. Edge-case behavior

### 3.1 The AI wraps the code in prose or markdown fences

#### Behavior (CEO sign-off)
- When the AI replies with explanation text and/or ```` ```cpp ```` fences around the sketch
- The system extracts just the sketch before compiling (strips fences / surrounding prose)
- The user sees a normal compile attempt, not a compile error caused by stray text

#### Classification
[Required automated test]

#### Smoke test procedure
**Reproduce:** Run a task; inspect the saved sketch file.
**Pass criteria:** The saved sketch is pure C/C++ (no ``` fences, no "Here is your code:" line).
**Failure signals:** Saved sketch contains markdown/prose; compile fails on the first line.

### 3.2 Compilation never succeeds within the retry limit

#### Behavior (CEO sign-off)
- When a task still fails to compile after the maximum repair attempts
- The system stops retrying that task, records it as `failed after N`, keeps the last
  error and last sketch for inspection, and moves on to the next task
- The user sees the run finish (it never hangs) with that task marked failed in the table

#### Classification
[Required automated test]

#### Smoke test procedure
**Reproduce:** Feed a deliberately impossible task (or set retry limit = 1 on a hard task).
**Pass criteria:** Run completes; failed task shown as `failed after N`; other tasks unaffected.
**Failure signals:** Tool hangs, crashes, or aborts the whole batch on one task's failure.

### 3.3 The AI call fails (no network, timeout, rate-limit, bad key)

#### Behavior (CEO sign-off)
- When the AI request errors out mid-run
- The system reports the failure for that task in plain terms and continues the batch;
  a missing/invalid API key is caught up-front before any task runs, with a clear message
- The user is never shown a raw stack trace as the primary signal

#### Classification
[Smoke test only]

#### Smoke test procedure
**Reproduce:** Unset the API key, then run the tool.
**Pass criteria:** Tool stops immediately with "API key not set / invalid" guidance.
**Failure signals:** Tool starts processing tasks then crashes deep in a request.

### 3.4 The build toolchain isn't ready

#### Behavior (CEO sign-off)
- When the Arduino command-line builder or the Nano board package is missing
- The system says so clearly at startup (a pre-flight check) and tells the user the one
  command to fix it, instead of failing obscurely on the first compile
- The user sees a setup hint, not a confusing toolchain error

#### Classification
[Smoke test only]

#### Smoke test procedure
**Reproduce:** Run the tool on a machine without the board package installed.
**Pass criteria:** Clear "install the Nano board package with: …" message before any task.
**Failure signals:** Cryptic "unknown FQBN" error surfaces mid-run.

### 3.5 Empty or nonsense task text

#### Behavior (CEO sign-off)
- When a task entry is blank or meaningless
- The system skips it with a note (batch mode) or asks again (single mode); it does not
  send an empty prompt to the AI
- The user sees the skip noted in the results

#### Classification
[Smoke test only]

## 4. Who can use this

- Our own 5-person team, on a developer laptop. No auth, no multi-user, no deployment.
- Requires: the Arduino command-line builder + Nano board package installed, an AI
  provider API key available in the environment, and Python.

## 5. External dependencies (plain language)

- **An AI model provider** (default: Claude / Anthropic). If it is unreachable or the key
  is wrong, see §3.3 — the demo fails that task gracefully or stops with a clear key error.
- **The Arduino command-line builder + Nano board package.** If missing, see §3.4 —
  caught at startup with a one-line fix.
- **A real Nano 33 BLE Sense board: NOT required for this demo.** Flashing and reading the
  board come in a later feature (the "flash loop").

## 6. Deferred / unresolved

- **RESOLVED — AI model = Claude (Anthropic), `claude-sonnet-4-6`.** A strong, low-cost
  model; one provider is enough for the demo. Comparing ≥2 models stays a later, separate
  experiment required by the proposal.
- **RESOLVED — board = Nano 33 BLE Sense Rev2**, so the cheat-sheet targets the on-board
  HS3003 temperature/humidity sensor (`Arduino_HS300x` library).
- **RESOLVED — starter task set** of 5 Level-1 single-sensor tasks is bundled; CEO can
  swap any wording.

## 7. Out of scope

- Flashing to hardware, reading serial output, runtime/behaviour verification ("flash loop").
- Automatic library resolution across the ~7,000 Arduino libraries — the demo hand-writes
  a cheat-sheet for the on-board sensors only.
- The full 30–50-task, 3-level benchmark and the multi-model cost/latency comparison —
  later milestones.
- Any GUI; any security/privacy filtering; any board other than the Nano 33 BLE Sense.

## 8. Decision history

- **D1 — Provider = Claude (Anthropic), model `claude-sonnet-4-6`** for the demo; single
  provider for now. Why: the eventual project must compare ≥2 LLMs, but the demo only needs
  to prove the loop. Multi-model comparison deferred to the evaluation milestone.
- **D2 — Cheat-sheet sensor = on-board HS3003 (Nano 33 BLE Sense Rev2), `Arduino_HS300x`.**
  Why: no wiring, always present, a clean Level-1 task. Board confirmed as Rev2.
- **D3 — Compile-repair retry cap = 3.** Why: mirrors the AutoEmbed finding that 3 compile
  trials capture almost all of the gain — a defensible, citable default for the proposal.
- **D4 — Compile-only, no flashing.** Why: removes the hardware dependency so the demo can
  be built and shown today; the flash loop is a separate later feature.
- **D5 — Crude on purpose.** CEO asked for fast/simple-but-effective; this is the trivial-ish
  end of the Full lane (it still gets a spec + auditor pass before code).

## 9. (Audit mode only — leave empty in new-feature mode) Code vs spec delta
