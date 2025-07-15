from collections.abc import Iterator


def skip_n[T](gen: Iterator[T], n: int) -> Iterator[T]:
    for _ in range(n):
        next(gen)
    yield from gen


def take_n[T](gen: Iterator[T], n: int) -> Iterator[T]:
    for _ in range(n):
        yield next(gen)
