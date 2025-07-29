import asyncio
import functools


def force_async(fn):
    """Turns a sync function to async function using threads

    Arguments:
        fn {function}

    Returns:
        function - awaitable function
    """
    from concurrent.futures import ThreadPoolExecutor

    pool = ThreadPoolExecutor()

    @functools.wraps(fn)
    def async_wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # make it awaitable

    return async_wrapper


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


def run_parallel(*coroutines):
    loop = get_or_create_eventloop()
    results = loop.run_until_complete(asyncio.gather(*coroutines))
    return results
