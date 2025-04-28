import threading
from collections.abc import Callable


class ExceptionThread(threading.Thread):
    def __init__(self, target: Callable, *args, **kwargs):
        self.exception = None
        super().__init__(target=target, *args, **kwargs)

    def run(self):
        try:
            super().run()
        except Exception as e:
            self.exception = e

    def join(self):
        super().join()
        if self.exception:
            raise self.exception
