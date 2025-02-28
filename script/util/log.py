import logging
import sys
import threading
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ColorFormatter:
    COLORS: ClassVar[dict[LogLevel, str]] = {
        LogLevel.DEBUG: "\033[36m",
        LogLevel.INFO: "\033[32m",
        LogLevel.WARNING: "\033[33m",
        LogLevel.ERROR: "\033[31m",
        LogLevel.CRITICAL: "\033[35m",
    }

    THREAD_COLORS: ClassVar[list[str]] = [
        "\033[38;5;51m",
        "\033[38;5;75m",
        "\033[38;5;147m",
        "\033[38;5;180m",
        "\033[38;5;186m",
        "\033[38;5;157m",
        "\033[38;5;219m",
    ]

    RESET: ClassVar[str] = "\033[0m"

    @classmethod
    def get_thread_color(cls, thread_name: str) -> str:
        thread_hash = hash(thread_name) % len(cls.THREAD_COLORS)
        return cls.THREAD_COLORS[thread_hash]


class Logger:
    def __init__(self, name: str = "app") -> None:
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)

    def _format_line(
        self,
        level: LogLevel,
        msg: str,
        prefix: str | None = None,
    ) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        thread_name = threading.current_thread().name
        thread_color = ColorFormatter.get_thread_color(thread_name)
        level_color = ColorFormatter.COLORS[level]

        prefix_str = f"[{prefix}] " if prefix else ""
        logger_color = ColorFormatter.get_thread_color(self.name)

        formatted_msg = (
            f"{ColorFormatter.RESET}{now} {level_color}{level.value:8}{ColorFormatter.RESET} "
            f"[{logger_color}{self.name}{ColorFormatter.RESET}] "
            f"[{thread_color}{thread_name}{ColorFormatter.RESET}] "
            f"{prefix_str}{msg}"
        )

        return formatted_msg

    def _log_multiline(
        self,
        level: LogLevel,
        msg: str,
        prefix: str | None = None,
        log_func: Any = None,
    ) -> None:
        lines = msg.splitlines() or [""]

        for i, line in enumerate(lines):
            formatted_line = self._format_line(level, line, prefix)
            log_func(formatted_line)

        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            stack_trace = "".join(traceback.format_stack()[:-3])
            log_func(f"{stack_trace}")

    def debug(self, msg: Any, prefix: str | None = None) -> None:
        self._log_multiline(LogLevel.DEBUG, str(msg), prefix, self.logger.debug)

    def info(self, msg: Any, prefix: str | None = None) -> None:
        self._log_multiline(LogLevel.INFO, str(msg), prefix, self.logger.info)

    def warning(self, msg: Any, prefix: str | None = None) -> None:
        self._log_multiline(LogLevel.WARNING, str(msg), prefix, self.logger.warning)

    def error(self, msg: Any, prefix: str | None = None) -> None:
        self._log_multiline(LogLevel.ERROR, str(msg), prefix, self.logger.error)

    def critical(self, msg: Any, prefix: str | None = None) -> None:
        self._log_multiline(LogLevel.CRITICAL, str(msg), prefix, self.logger.critical)


_loggers_lock = threading.Lock()
_loggers = {}


def get_logger(name: str = "app") -> Logger:
    with _loggers_lock:
        if name not in _loggers:
            _loggers[name] = Logger(name)
        return _loggers[name]
