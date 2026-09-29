import time
import functools

def time_node(func):
    @functools.wraps(func)
    async def wrapper(state, *args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(state, *args, **kwargs)
            end_time = time.perf_counter()
            print(f"--- [TIMER] Node '{func.__name__}' a pris {end_time - start_time:.2f}s ---")
            return result
        except Exception as e:
            end_time = time.perf_counter()
            print(f"--- [TIMER] ERREUR dans le node '{func.__name__}' après {end_time - start_time:.2f}s: {e} ---")
            raise  # Re-raise the exception to stop the graph
    return wrapper
