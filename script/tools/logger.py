import random
import threading
from queue import Queue

from colorama import Fore, Style

from tools.singleton import Singleton

_PRINT_LOCK = threading.Lock()


class _ColorManager(metaclass=Singleton):
    def __init__(self):
        _colors = [
            Fore.BLACK,
            Fore.RED,
            Fore.GREEN,
            Fore.YELLOW,
            Fore.BLUE,
            Fore.MAGENTA,
            Fore.CYAN,
        ]
        random.shuffle(_colors)

        self._colors = Queue()
        for color in _colors:
            self._colors.put(color)

        self._thread_to_color: dict[str, str] = dict()
        self._lock = threading.Lock()

    def get_thread_color(self) -> str:
        thread_name = threading.current_thread().name

        with self._lock:
            if thread_name in self._thread_to_color:
                return self._thread_to_color[thread_name]

            next_color = self._colors.get()
            self._thread_to_color[thread_name] = next_color
            self._colors.put(next_color)
            return next_color


def _get_short_thread_name(length: int = 9) -> str:
    initial_budget_per_part = 3
    thread_name = threading.current_thread().name.upper()
    short_name = ""

    name_parts = thread_name.split("_")
    budget = length
    budget_per_part = [0] * len(name_parts)

    for i, part in enumerate(name_parts):
        available_budget = min(len(part), budget, initial_budget_per_part)
        budget -= available_budget
        budget_per_part[i] = available_budget

    for i, part in reversed(list(enumerate(name_parts))):
        budget += budget_per_part[i]
        available_budget = min(len(part), budget)
        budget -= available_budget
        budget_per_part[i] = available_budget

    for available_budget, part in zip(budget_per_part, name_parts):
        short_name += part[:available_budget]

    return short_name.ljust(length, " ")


def log(data, **print_kwargs):
    color = _ColorManager().get_thread_color()
    name = _get_short_thread_name()
    tag = f"{Style.RESET_ALL}{color}[{name}]{Style.RESET_ALL}"

    with _PRINT_LOCK:
        for line in str(data).strip("\n").split("\n"):
            print(f"{tag} {line}", flush=True, **print_kwargs)
