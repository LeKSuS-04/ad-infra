import subprocess
import threading
from dataclasses import dataclass
from typing import IO, Any

from util.log import get_logger


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int


def run_process(
    args: list[str],
    check: bool = True,
    **kwargs: Any,
) -> ExecutionResult:
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    kwargs |= {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }

    logger = get_logger(args[0])
    logger.info(f"Running command: {' '.join(args)}")

    process = subprocess.Popen(args, **kwargs)

    def log_output(pipe: IO[str], is_stdout: bool) -> None:
        for line in iter(pipe.readline, ""):
            line = line.rstrip("\n")
            logger.info(line)
            if is_stdout:
                stdout_lines.append(line)
            else:
                stderr_lines.append(line)

    stdout_thread = threading.Thread(
        target=log_output,
        args=(process.stdout, True),
        daemon=True,
        name="stdout",
    )
    stderr_thread = threading.Thread(
        target=log_output,
        args=(process.stderr, False),
        daemon=True,
        name="stderr",
    )

    stdout_thread.start()
    stderr_thread.start()

    exit_code = process.wait()

    stdout_thread.join()
    stderr_thread.join()

    stdout = "\n".join(stdout_lines)
    stderr = "\n".join(stderr_lines)

    if exit_code != 0:
        logger.warning(f"Process exited with non-zero code {exit_code}")
    else:
        logger.info(f"Process completed successfully (exit code: {exit_code})")

    if check and exit_code != 0:
        raise Exception(f"Process exited with non-zero code {exit_code}")

    return ExecutionResult(stdout, stderr, exit_code)
