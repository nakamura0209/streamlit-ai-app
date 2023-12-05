import functools
from logging import Logger
from typing import Callable


# log_decoratorは、ロギングを行うためのデコレータを生成するファクトリ関数です。
def log_decorator(logger: Logger) -> Callable:
    """関数の開始、引数、戻り値、終了時にログを出力するデコレータを生成する"""

    # 実際のデコレータ関数です。デコレートされる関数を引数として受け取ります。
    def decorator(func: Callable) -> Callable:
        # functools.wrapsは、デコレートされた関数のメタデータを保持するために使用されます。
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

        # デコレータはwrapper関数を返します。
        return wrapper

    # デコレータファクトリーはdecorator関数を返します。
    return decorator
