# app/utils/timing.py
import time
from contextlib import contextmanager

@contextmanager
def timer():
    t0 = time.time()
    yield lambda: round((time.time() - t0) * 1000, 2)
