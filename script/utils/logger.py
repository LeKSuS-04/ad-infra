import random
import threading

from colorama import Fore, Style
from string import ascii_uppercase, digits


COLORS = [
    Fore.BLACK,
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
]


PRINT_LOCK = threading.Lock()


def hash_to_five_digits(n: int) -> int:
    while n > 100_000:
        n = (n // 100_000) ^ (n % 100_000)
    return n


def log(data, **print_kwargs):
    tid = hash_to_five_digits(threading.get_ident())
    rng = random.Random(tid)
    colors = ''.join(rng.choice(COLORS) for _ in range(3))
    log_id = ''.join(rng.choice(ascii_uppercase + digits) for _ in range(5))
    tag = f'{Style.RESET_ALL}{colors}[{log_id}]{Style.RESET_ALL}'

    with PRINT_LOCK:
        for line in str(data).strip('\n').split('\n'):
            print(f'{tag} {line}', flush=True, **print_kwargs)
