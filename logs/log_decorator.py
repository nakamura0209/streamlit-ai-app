import functools
from logging import Logger
from typing import Callable

from logs.app_logger import set_logging


import json


def log_decorator(logger: Logger) -> Callable:
    """関数の開始、引数、戻り値、終了時にログを出力するデコレータを生成する"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            func_args = ", ".join([repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()])
            logger.info(f"START: {func_name} (args: {func_args})")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Returns: {func_name} -> {result!r}")
                return result
            except Exception as e:
                logger.error(f"An exception occurred: {func_name} -> {e!r}")
                raise
            finally:
                logger.info(f"END: {func_name}")

        return wrapper

    return decorator
