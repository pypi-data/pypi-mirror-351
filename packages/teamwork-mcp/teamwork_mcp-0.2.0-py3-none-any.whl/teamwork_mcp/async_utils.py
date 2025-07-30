import asyncio
import time
from loguru import logger

def run_in_subprocess_wrapper_func(func, args, kwargs, return_dict, exception_dict):
    import sys
    import os
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    try:
        result = func(*args, **kwargs)
        return_dict["result"] = result
    except Exception as e:
        exc_info = sys.exc_info()
        exception_dict["exception"] = str(exc_info)

def run_in_subprocess(func, timeout=None, max_try=3, fallback_fn=None):
    import multiprocessing
    wrap_contrl = {'timeout': timeout, 'max_try': max_try}
    def wrapper(*args, **kwargs):
        while wrap_contrl['max_try'] > 0:
            try:
                return_dict = multiprocessing.Manager().dict()
                exception_dict = multiprocessing.Manager().dict()
                process = multiprocessing.Process(
                    target=run_in_subprocess_wrapper_func,
                    args=(func, args, kwargs, return_dict, exception_dict),
                )
                logger.info("new process begins ...")
                wrap_contrl['max_try'] -= 1
                process.start()
                process.join(timeout=wrap_contrl['timeout'])
                if process.is_alive():
                    logger.info("process is still alive, terminating ...")
                    process.kill()  # kill it with the hard way, process.terminate may timeout.
                    process.join()
                    process.close()
                    raise TimeoutError
                logger.info("closing process ...")
                process.close()
                if "exception" in exception_dict:
                    exc_info = exception_dict["exception"]
                    raise RuntimeError(exc_info)
                if "result" in return_dict.keys():
                    return return_dict["result"]
            except:
                logger.error(f"Function {func.__name__} timed out (or error) after {timeout} seconds [ chance left: {wrap_contrl['max_try']-1} ]")
                if wrap_contrl['max_try'] == 0:
                    logger.exception("No more chance to retry!")
                    if fallback_fn:
                        # if there are any fallback options
                        return fallback_fn(*args, **kwargs)
                    else:
                        # if there is no fallback options, raise an error
                        raise RuntimeError("No more chance to retry!")
    return wrapper

def execute_with_retry(func, *args, **kwargs):
    warp_fn = run_in_subprocess(func, timeout=3600, max_try=3)
    task = warp_fn(*args, **kwargs)
    result = task
    return result