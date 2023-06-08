import subprocess
from typing import IO, Any, cast

from .logger import log


def process(cmd: str, **options: Any) -> bytes:
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **options,
    )
    stdout = b""

    for line in cast(IO[bytes], proc.stdout):
        stdout += line
        log(line.decode())

    return stdout
