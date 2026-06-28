"""Wrap `arduino-cli compile` for the Nano 33 BLE Sense (compile-only, no upload)."""
import shutil
import subprocess
from pathlib import Path

FQBN = "arduino:mbed_nano:nano33ble"
CORE = "arduino:mbed_nano"


def _cli():
    exe = shutil.which("arduino-cli")
    if not exe:
        raise RuntimeError(
            "arduino-cli not found on PATH. Install it (Windows: winget install ArduinoSA.CLI)."
        )
    return exe


def preflight():
    """Return (ok, message). Checks the CLI and the Nano core are present (spec 3.4)."""
    try:
        exe = _cli()
    except RuntimeError as e:
        return False, str(e)
    cores = subprocess.run([exe, "core", "list"], capture_output=True, text=True)
    if CORE not in cores.stdout:
        return False, (
            f"Board package '{CORE}' is not installed. Install it with:\n"
            f"  arduino-cli core update-index && arduino-cli core install {CORE}"
        )
    return True, "toolchain OK (arduino-cli + arduino:mbed_nano core present)"


def write_sketch(sketch_dir: Path, sketch_code: str):
    # Arduino requires the .ino filename to match its parent directory name.
    sketch_dir.mkdir(parents=True, exist_ok=True)
    ino = sketch_dir / f"{sketch_dir.name}.ino"
    ino.write_text(sketch_code, encoding="utf-8")
    return ino


def compile_sketch(sketch_dir: Path):
    """Return (ok: bool, log: str). Non-zero exit code = compile failure."""
    exe = _cli()
    proc = subprocess.run(
        [exe, "compile", "--fqbn", FQBN, "--warnings", "none", str(sketch_dir)],
        capture_output=True, text=True,
    )
    log = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode == 0, log
