# Compile-Loop Demo (Week-5 proposal MVP slice)

Turns a plain-English embedded task into **compiled** Arduino firmware for the
Nano 33 BLE Sense — no physical board required. It proves the two core
mechanisms of the AutoEmbed-style pipeline end-to-end:

1. **API-table injection** — a hand-written per-sensor cheat-sheet
   (`api_tables/temp_humidity.json`) is injected into the prompt. This is the
   deliberately-simplified analog of AutoEmbed's auto-extracted *Knowledge
   Generation*: same role (tell the model the exact library calls), hand-authored
   instead of LLM-extracted.
2. **Compile-error feedback loop** — if `arduino-cli` rejects the generated
   sketch, the compiler log is fed back to the model to repair, up to N attempts.

Canonical behaviour spec: `docs/features/compile-loop-demo.md`.
Engineering notes: `docs/features/compile-loop-demo-implementation.md`.

## Prerequisites

- `arduino-cli` on PATH, with the Nano core: `arduino-cli core install arduino:mbed_nano`
- The on-board sensor library: `arduino-cli lib install Arduino_HS300x` (Rev2 / HS3003)
- Python 3 + the Anthropic SDK: `py -m pip install anthropic`
- `ANTHROPIC_API_KEY` set in the environment

On Windows use the **`py`** launcher (the bare `python` is the Microsoft Store stub).

## Run

```sh
py demo/mvp.py --check        # toolchain pre-flight only
py demo/mvp.py                # run the bundled 5-task Level-1 set
py demo/mvp.py --single "blink the LED and print the temperature each second"
py demo/mvp.py --max-attempts 1   # disable the repair loop (baseline)
```

Full runs check the API key with Anthropic's Models API before starting the
task batch. Empty or punctuation-only batch entries are shown as skipped; in
interactive single-task mode the CLI asks again. Neither path calls the LLM for
invalid task text.

Each run writes the generated sketches under `sketches/<task-id>/` and a summary
table to `results/run-<timestamp>.md` (both gitignored). The console prints each
generated sketch path, and failed-task reports retain the final error. The
headline metric is `Compiled N/total` — a primitive stand-in for the proposal's
*completion rate*.

## Out of scope (later features)

Flashing to hardware, serial-log validation, automatic library resolution across
the ~7,000 Arduino libraries, and the multi-model cost/latency comparison.
