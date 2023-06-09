import random
import threading

from colorama import Fore, Style

_COLORS = [
    Fore.BLACK,
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
]


_PRINT_LOCK = threading.Lock()


def _hash_to_five_digits(n: int) -> int:
    while n > 100_000:
        n = (n // 100_000) ^ (n % 100_000)
    return n


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
    seed = _hash_to_five_digits(threading.get_ident())
    rng = random.Random(seed)

    color = rng.choice(_COLORS)
    name = _get_short_thread_name()
    tag = f"{Style.RESET_ALL}{color}[{name}]{Style.RESET_ALL}"

    with _PRINT_LOCK:
        for line in str(data).strip("\n").split("\n"):
            print(f"{tag} {line}", flush=True, **print_kwargs)
