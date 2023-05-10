import random
import threading

from colorama import Fore, Style
from string import ascii_uppercase


COLORS = [
    Fore.BLACK,
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
]


print_lock = threading.Lock()


def hash_to_five_digits(n: int) -> int:
    while n > 100_000:
        n = (n // 100_000) ^ (n % 100_000)
    return n


def log(data, **print_kwargs):
    with print_lock:
        tid = hash_to_five_digits(threading.get_ident())
        rng = random.Random(tid)
        colors = rng.choice(COLORS)
        letters = ''.join(rng.choice(ascii_uppercase) for _ in range(3))
        tag = f'{Style.RESET_ALL}{colors}[{letters}{tid:05}]{Style.RESET_ALL}'

        for line in str(data).strip('\n').split('\n'):
            print(f'{tag} {line}', flush=True, **print_kwargs)
