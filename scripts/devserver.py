"""Development server script with process management.

This script runs the FastAPI development server and handles process cleanup,
including graceful shutdown when the parent process terminates.
"""

from __future__ import annotations

import ctypes
import os
import signal
import subprocess  # nosec B404
import sys
import time
from typing import Any, cast


def is_windows() -> bool:
    """Check if running on Windows."""
    return os.name == "nt"


def parent_is_alive(ppid: int) -> bool:
    """Check if parent process is still alive."""
    if ppid <= 1:
        return False

    if not is_windows():
        # On POSIX, if parent died, PPID becomes 1 (init)
        return os.getppid() != 1

    # Windows: check if process handle is valid
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000  # pylint: disable=invalid-name
    kernel32 = cast(Any, ctypes.windll).kernel32  # type: ignore[attr-defined]
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, ppid)
    if handle == 0:
        return False
    kernel32.CloseHandle(handle)
    return True


def kill_process_tree(proc: subprocess.Popen[bytes]) -> None:
    """Kill process tree including all child processes."""
    if proc.poll() is not None:
        return

    if is_windows():
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )  # nosec B603,B607
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)  # pylint: disable=no-member
        except ProcessLookupError:
            return


def main(argv: list[str]) -> int:
    """Run development server with process management."""
    # Default command
    has_custom_command = bool(argv[1:])
    cmd = argv[1:] or [
        "uv",
        "run",
        "python",
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",  # nosec B104
        "--port",
        "8000",
        "--reload",
        "--reload-dir",
        "app",
        "--reload-dir",
        "scripts",
        "--reload-dir",
        "config",
    ]

    ppid = os.getppid()
    env = os.environ.copy()

    if not has_custom_command:
        init_result = subprocess.run(  # nosec B603,B607
            ["uv", "run", "python", "scripts/init_db.py"],
            check=False,
        )
        if init_result.returncode != 0:
            return init_result.returncode
        env["SKIP_DB_INIT"] = "true"

    creationflags = 0
    preexec_fn = None
    if is_windows():
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    else:
        preexec_fn = os.setsid  # pylint: disable=no-member

    proc = subprocess.Popen(  # nosec B603  # pylint: disable=consider-using-with,subprocess-popen-preexec-fn
        cmd,
        stdin=None,
        stdout=None,
        stderr=None,
        creationflags=creationflags,
        preexec_fn=preexec_fn,
        env=env,
    )

    def shutdown() -> None:
        """Shutdown the process tree."""
        kill_process_tree(proc)

    def handle_signal(_signum: int, _frame: object | None) -> None:
        """Handle shutdown signals."""
        shutdown()

    # If we do receive signals, great.
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        # Main loop: also detect if the parent process died (e.g., make got Ctrl+C)
        while proc.poll() is None:
            if not parent_is_alive(ppid):
                shutdown()
                break
            time.sleep(0.2)
        return proc.returncode or 0
    finally:
        shutdown()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
