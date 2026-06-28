"""Compile-loop demo: natural-language task -> Claude -> Arduino sketch ->
arduino-cli compile, feeding compile errors back for repair. Compile-only, no
hardware. Canonical spec: docs/features/compile-loop-demo.md.

Usage (Windows -- use the `py` launcher, not the Store `python` stub):
    py demo/mvp.py                 # run the bundled Level-1 task set
    py demo/mvp.py --check         # toolchain pre-flight only
    py demo/mvp.py --single "read the temperature and print it every second"
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from llm_client import make_client, LLMError, DEFAULT_MODEL
from prompt import SYSTEM, build_user_prompt
from extract import extract_sketch
from compile_runner import preflight, write_sketch, compile_sketch
from report import summarize_errors, render_table, write_report, status_cell

HERE = Path(__file__).resolve().parent


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def load_json(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def meaningful_task_text(task_text):
    text = task_text.strip() if isinstance(task_text, str) else ""
    return text if text and any(character.isalnum() for character in text) else None


def valid_tasks(tasks):
    accepted = []
    skipped = []
    for task in tasks:
        text = meaningful_task_text(task.get("task"))
        if text:
            accepted.append({**task, "task": text})
        else:
            print(f"[skip] {task.get('id', '<unknown>')}: task is empty or nonsensical", file=sys.stderr)
            skipped.append(
                {
                    "id": task.get("id", "<unknown>"),
                    "task": task.get("task", ""),
                    "attempts": 0,
                    "compiled": False,
                    "skipped": True,
                    "last_error": "",
                    "sketch_path": None,
                }
            )
    return accepted, skipped


def prompt_for_single_task(task_text):
    text = meaningful_task_text(task_text)
    while not text and sys.stdin.isatty():
        try:
            text = meaningful_task_text(input("Task is empty or nonsensical; enter another task: "))
        except EOFError:
            return None
    return text


def finish(records, args):
    print(render_table(records))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = HERE / "results" / f"run-{stamp}.md"
    write_report(records, out, {"model": args.model, "max_attempts": args.max_attempts})
    print(f"\n[report] {out}")
    return 0


def run_task(client, task_id, task_text, api_table, max_attempts):
    feedback = None
    last_log = ""
    sketch_path = None
    for attempt in range(1, max_attempts + 1):
        user = build_user_prompt(task_text, api_table, feedback)
        reply = client.generate(SYSTEM, user)
        sketch = extract_sketch(reply)
        sketch_dir = HERE / "sketches" / task_id
        sketch_path = write_sketch(sketch_dir, sketch)
        ok, log = compile_sketch(sketch_dir)
        last_log = log
        print(f"    attempt {attempt}/{max_attempts}: {'compiled OK' if ok else 'compile failed'}")
        if ok:
            return {
                "id": task_id,
                "task": task_text,
                "attempts": attempt,
                "compiled": True,
                "last_error": "",
                "sketch_path": str(sketch_path),
            }
        feedback = summarize_errors(log)  # spec 3.2: feed errors back, then retry
    return {
        "id": task_id,
        "task": task_text,
        "attempts": max_attempts,
        "compiled": False,
        "last_error": summarize_errors(last_log),
        "sketch_path": str(sketch_path),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Compile-loop demo (NL -> Arduino firmware, compile-only).")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="LLM model id (default: %(default)s)")
    ap.add_argument("--provider", default="anthropic")
    ap.add_argument("--max-attempts", type=positive_int, default=3, help="compile attempts per task incl. initial (default: 3)")
    ap.add_argument("--single", metavar="TASK", help="run one ad-hoc task instead of the bundled set")
    ap.add_argument("--check", action="store_true", help="run the toolchain pre-flight check and exit")
    args = ap.parse_args(argv)

    skipped_records = []
    if not args.check:
        if args.single is not None:
            task_text = prompt_for_single_task(args.single)
            if not task_text:
                print("[error] no valid task to run", file=sys.stderr)
                return 2
            tasks = [{"id": "adhoc", "task": task_text}]
        else:
            tasks, skipped_records = valid_tasks(load_json("tasks.json"))
            if not tasks:
                return finish(skipped_records, args)

    ok, msg = preflight()  # spec 3.4: catch a missing toolchain up-front
    print(f"[pre-flight] {msg}")
    if not ok:
        return 2
    if args.check:
        return 0

    api_table = load_json("api_tables/temp_humidity.json")

    try:
        client = make_client(args.provider, args.model)
        credential_status = client.validate_credentials()
    except LLMError as e:
        print(f"[error] {e}", file=sys.stderr)
        return 2
    print(f"[llm pre-flight] {credential_status}")

    print(f"[run] model={args.model}  tasks={len(tasks)}  max_attempts={args.max_attempts}\n")
    records = list(skipped_records)
    for t in tasks:
        print(f"- {t['id']}: {t['task']}")
        try:
            rec = run_task(client, t["id"], t["task"], api_table, args.max_attempts)
        except LLMError as e:  # spec 3.3: one task's API failure must not abort the batch
            print(f"    [llm error] {e}")
            rec = {
                "id": t["id"],
                "task": t["task"],
                "attempts": 0,
                "compiled": False,
                "last_error": str(e),
                "sketch_path": None,
            }
        records.append(rec)
        print(f"  => {status_cell(rec)}")
        if rec.get("sketch_path"):
            print(f"     sketch: {rec['sketch_path']}")
        print()

    return finish(records, args)


if __name__ == "__main__":
    raise SystemExit(main())
