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


def _get_short_thread_name() -> str:
    thread_name = threading.current_thread().name.upper()
    short_name = ""
    name_parts = thread_name.split("_")
    for part in name_parts:
        short_name += part[:3]
    short_name += name_parts[-1][3:]
    return short_name[:8].ljust(8, " ")


def log(data, **print_kwargs):
    seed = _hash_to_five_digits(threading.get_ident())
    rng = random.Random(seed)

    color = rng.choice(_COLORS)
    name = _get_short_thread_name()
    tag = f"{Style.RESET_ALL}{color}[{name}]{Style.RESET_ALL}"

    with _PRINT_LOCK:
        for line in str(data).strip("\n").split("\n"):
            print(f"{tag} {line}", flush=True, **print_kwargs)
