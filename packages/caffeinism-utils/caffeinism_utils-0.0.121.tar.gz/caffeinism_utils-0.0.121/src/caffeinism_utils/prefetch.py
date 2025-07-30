from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

from .asyncio import run_in_executor
from .utils import DummyStopIteration, next_without_stop_iteration


async def aprefetch_iterator(iterator):
    with ThreadPoolExecutor(1) as p:
        iterator = await run_in_executor(p, iter, iterator)
        prefetched = run_in_executor(p, next_without_stop_iteration, iterator)
        while True:
            try:
                ret = await prefetched
            except DummyStopIteration:
                break
            prefetched = run_in_executor(p, next_without_stop_iteration, iterator)
            yield ret


def prefetch_iterator(iterator):
    with ThreadPoolExecutor(1) as p:
        iterator = iter(iterator)
        prefetched = p.submit(next, iterator)
        while True:
            try:
                rets = prefetched.result()
            except StopIteration:
                break
            prefetched = p.submit(next, iterator)
            yield rets


class BasePrefetcher:
    def __init__(self):
        self._p = ThreadPoolExecutor(1)
        self._future = None


class AsyncPrefetcher(BasePrefetcher):
    async def prefetch(self, func, *args, **kwargs):
        ret = None
        if self._future is not None:
            ret = await self._future
            self._future = None

        if func is None:
            return ret

        self._future = run_in_executor(self._p, func, *args, **kwargs)
        return ret

    async def __aenter__(self):
        self._p.__enter__()
        return self

    async def __aexit__(self, *args):
        await self.prefetch(None)
        self._p.__exit__(*args)


class Prefetcher(BasePrefetcher):
    def prefetch(self, func, *args, **kwargs):
        ret = None
        if self._future is not None:
            ret = self._future.result()
            self._future = None

        if func is None:
            return ret

        self._future = self._p.submit(func, *args, **kwargs)
        return ret

    def __enter__(self):
        self._p.__enter__()
        return self

    def __exit__(self, *args):
        self.prefetch(None)
        self._p.__exit__(*args)
