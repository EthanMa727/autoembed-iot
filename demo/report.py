"""Per-task records -> console + markdown table. Headline metric: compiled N/total."""
from pathlib import Path


def summarize_errors(log, limit=1200):
    """Keep the tail of the compiler log (where the real errors are) for feedback."""
    log = log.strip()
    return log[-limit:] if len(log) > limit else log


def status_cell(rec):
    if rec.get("skipped"):
        return "SKIPPED (invalid task)"
    if rec["compiled"]:
        reps = rec["attempts"] - 1
        return f"compiled OK ({reps} repair{'s' if reps != 1 else ''})"
    return f"FAILED after {rec['attempts']} attempts"


def render_table(records):
    rows = ["| Task | Result | Attempts |", "| --- | --- | --- |"]
    for record in records:
        rows.append(f"| {record['id']} | {status_cell(record)} | {record['attempts']} |")
    compiled = sum(1 for record in records if record["compiled"])
    rows.append("")
    rows.append(f"**Compiled {compiled}/{len(records)}**")

    failures = [
        record for record in records
        if not record["compiled"] and not record.get("skipped")
    ]
    if failures:
        rows.extend(["", "## Failure details"])
        for record in failures:
            rows.extend(["", f"### {record['id']}", "", f"Task: {record['task']}"])
            if record.get("sketch_path"):
                rows.append(f"Sketch: {record['sketch_path']}")
            rows.extend(["", "Last error:", ""])
            error_lines = record.get("last_error", "").splitlines() or ["(no error output)"]
            rows.extend(f"> {line}" if line else ">" for line in error_lines)
    return "\n".join(rows)


def write_report(records, out_path: Path, meta):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "# Compile-loop demo run",
        "",
        f"- model: {meta['model']}",
        f"- max attempts per task: {meta['max_attempts']}",
        "",
    ]
    out_path.write_text("\n".join(header) + render_table(records) + "\n", encoding="utf-8")
