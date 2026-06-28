# Compile-Loop Demo — Implementation Notes

**Spec:** docs/features/compile-loop-demo.md (canonical, CEO domain)
**This file:** technical detail, manager domain. Doubles as source material for proposal §2.2 (System Design).

## Goal restated (engineering terms)

Closed-loop `NL → prompt(+API table) → LLM → C/C++ sketch → arduino-cli compile → on
failure, feed error back → regenerate` for the Arduino Nano 33 BLE Sense, compile-only
(no upload). Demonstrates the project's two required mechanisms — **(i) per-module
API-table injection** and **(ii) compile-error feedback loop** — minus the flash/serial half.

Maps to AutoEmbed (proposal's anchor reference):
- our API table ≈ AutoEmbed "Knowledge Generation" (§3.2), but hand-authored, not LLM-extracted
- our compile-repair loop ≈ AutoEmbed "Auto-Programming → Compile Loop" (§3.4.2)
- deliberately omitted: library resolution (§3.1, 7,000 libs) and the Flash Loop (§3.4.3)

## Pipeline / module map

Single small Python package under `demo/`:

```
demo/
  mvp.py              # entry point + orchestration (the loop)
  llm_client.py       # provider abstraction; default = Anthropic
  prompt.py           # builds the structured prompt (task + API table + rules)
  compile_runner.py   # wraps arduino-cli compile; returns (ok, log)
  extract.py          # pull pure sketch out of LLM reply (strip ``` fences / prose)
  report.py           # per-task records → markdown/console table
  api_tables/
    temp_humidity.json   # hand-written cheat-sheet for the on-board T/H sensor
  tasks.json          # the 3–5 Level-1 task descriptions
  sketches/<task-id>/<task-id>.ino   # generated (gitignored)
  results/run-<stamp>.md             # generated summary (gitignored)
```

Keep it ~150–250 LOC total. Reuse stdlib (`subprocess`, `json`, `pathlib`, `argparse`).
Only third-party dep: the provider SDK.

## Control flow (the loop) — mirrors AutoEmbed Alg. 2 compile loop (single loop, no flash)

```
for task in tasks:
    prompt = build_prompt(task, api_table, rules)
    feedback = None
    for attempt in 1..MAX_REPAIRS(=3):
        reply  = llm.generate(prompt, feedback)     # feedback=None on attempt 1
        sketch = extract_sketch(reply)
        write sketch to sketches/<task-id>/<task-id>.ino
        ok, log = arduino_compile(sketch_dir)
        if ok: record(task, attempt, compiled=True); break
        feedback = summarize_compiler_errors(log)   # appended to next prompt
    else:
        record(task, MAX_REPAIRS, compiled=False, last_error=log)
print_table(records)
```

## arduino-cli contract

- **FQBN:** `arduino:mbed_nano:nano33ble` (the Nano 33 BLE and BLE Sense share this FQBN).
- **Core install (one-time):** `arduino-cli core update-index` then
  `arduino-cli core install arduino:mbed_nano`.
- **Compile (no upload):** `arduino-cli compile --fqbn arduino:mbed_nano:nano33ble <sketch_dir>`
  - capture exit code + stdout/stderr. Non-zero exit = compile failure.
  - sketch dir name must match the `.ino` filename (Arduino requirement).
  - optional: `--warnings none` to keep logs clean; `--format json` for parseable output.
- **Pre-flight:** `arduino-cli core list` → assert `arduino:mbed_nano` present; else emit the
  install hint (spec §3.4). `arduino-cli version` to assert the CLI exists at all.
- **Separation of concerns:** compile only here. Upload (`arduino-cli upload -p <port>`) is a
  later feature → also saves flash-write wear during iteration.

## API table format (the "injection" mechanism)

`api_tables/temp_humidity.json` — structured, prompt-injected verbatim. Shape echoes
AutoEmbed Tab. 1 (API table) so the proposal can draw the parallel:

```json
{
  "component": "On-board temperature/humidity sensor (Nano 33 BLE Sense)",
  "library_include": "#include <Arduino_HTS221.h>   // Rev1; Rev2 uses Arduino_HS300x.h",
  "init": "HTS.begin();   // call once in setup()",
  "apis": [
    {"name": "HTS.readTemperature()", "returns": "float °C"},
    {"name": "HTS.readHumidity()",    "returns": "float %RH"}
  ],
  "gotchas": ["Serial.begin(9600) and wait for Serial in setup()",
              "no external wiring — sensor is on-board"]
}
```

> **Rev1 vs Rev2 [CONFIRM]:** Rev1 = HTS221 (`Arduino_HTS221`); Rev2 = HS3003
> (`Arduino_HS300x`). Pick the table that matches the team's board. A wrong header is
> exactly the kind of error the compile loop is meant to catch & repair — useful for the
> live demo either way.

## LLM client

- Default provider **Anthropic**; `pip install anthropic`; key from `ANTHROPIC_API_KEY`.
- `llm_client.generate(system, user, feedback)` → text. Thin wrapper; provider chosen by a
  `--provider` flag so a 2nd model can be slotted in later for the comparison experiment.
- Model id is a CLI flag with a sane default — **[CONFIRM] which model** (strong = more
  first-try passes; cheap = lower cost). See spec §6.
- Determinism: low temperature for reproducibility of the demo.

## Prompt shape (prompt.py) — echoes AutoEmbed Tab. 3

```
SYSTEM: You are an expert embedded-systems engineer. Output ONLY a compilable Arduino
        C/C++ sketch for the target board. No prose, no markdown fences.
USER:   ### Task
        <task text>
        ### Target
        Arduino Nano 33 BLE Sense (FQBN arduino:mbed_nano:nano33ble)
        ### Available APIs (use ONLY these for the sensor)
        <api_tables/temp_humidity.json rendered>
        ### Rules
        - setup()/loop() required; Serial.begin(9600).
        - Use only the provided sensor APIs.
        - Compilable C/C++ only.
        [### Previous compile errors — fix these:\n<feedback>]   # attempts ≥2 only
```

## extract.py (spec §3.1)

Strip a leading "```lang" / trailing "```" if present; else take the text as-is. Tolerate a
"Here is …" preamble by slicing from the first `#include` or `void setup`. Keep it dumb.

## tasks.json (starter set — [CONFIRM] wording)

3–5 Level-1 single-sensor tasks, e.g.:
1. Print temperature in °C to serial every second.
2. Print temperature and humidity once per second, labelled.
3. Print a warning line when temperature exceeds 30 °C, else print the value.
4. Average 10 temperature reads and print the mean every 10 s.
5. Print humidity only when it changes by more than 2 %RH since the last reading.

## report.py

Per-task record `{id, task, attempts, compiled, last_error_snippet}`. Emit a markdown table
to console and to `results/run-<stamp>.md`. The overall `compiled N/total` line is the demo's
headline metric and a primitive stand-in for the proposal's *completion rate*.

## Prereqs checklist (build-time)

1. `arduino-cli` installed (winget `ArduinoSA.CLI` or the zip) — **not yet installed**.
2. `arduino-cli core install arduino:mbed_nano`.
3. `pip install anthropic` (verify the Windows `python` is real, not the Store stub).
4. `ANTHROPIC_API_KEY` exported — **CEO to provide**.

## Out of scope (engineering)

Flash loop, serial-log validation, DEBUG-INFO injection, library resolution, multi-model
comparison harness, GUI, packaging. All later features.

## Scenario → automated test map

(empty until Stage 6; the demo's "[Required automated test]" scenarios are §3.1 fence-strip
and §3.2 retry-cap — both unit-testable without hardware or an API key by stubbing the LLM
reply and the compiler result.)
