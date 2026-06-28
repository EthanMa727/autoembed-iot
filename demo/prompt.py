"""Build the structured prompt: task + per-sensor API table + coding rules.

This is the "API-table injection" mechanism -- the demo's hand-written analog of
AutoEmbed's auto-extracted Knowledge Generation. The sensor cheat-sheet is fed
into the prompt verbatim so the model uses the correct library calls.
"""

SYSTEM = (
    "You are an expert embedded-systems engineer. Output ONLY a single, "
    "compilable Arduino C/C++ sketch for the target board. No prose, no "
    "explanations, no markdown code fences."
)

TARGET = "Arduino Nano 33 BLE Sense (FQBN arduino:mbed_nano:nano33ble)"


def render_api_table(table):
    lines = [
        f"Component: {table['component']}",
        f"Include: {table['library_include']}",
        f"Init: {table['init']}",
        "Functions:",
    ]
    for api in table["apis"]:
        lines.append(f"  - {api['name']} -> {api['returns']}")
    if table.get("gotchas"):
        lines.append("Notes:")
        for g in table["gotchas"]:
            lines.append(f"  - {g}")
    return "\n".join(lines)


def build_user_prompt(task_text, api_table, feedback=None):
    parts = [
        "### Task", task_text,
        "### Target", TARGET,
        "### Available APIs (use ONLY these for the sensor)", render_api_table(api_table),
        "### Rules",
        "- Define setup() and loop().",
        "- Call Serial.begin(9600) in setup().",
        "- Use only the provided sensor APIs for the sensor.",
        "- Output compilable C/C++ only.",
    ]
    if feedback:  # attempts >= 2 only -- the compile-error feedback loop
        parts += ["### Previous compile errors - fix these:", feedback]
    return "\n".join(parts)
