from collections import defaultdict
from functools import wraps
import time


class _perf:
    RES = defaultdict(lambda: 0.0)

    def __call__(self, func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            _perf.RES[func.__name__] += execution_time
            return result

        return func_wrapper
    
    @property
    def results(self):
        return self.RES


FEasyTimer = _perf()
