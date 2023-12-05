from logging import Logger
import tiktoken as tk
from logs.app_logger import set_logging

from logs.log_decorator import log_decorator


logger: Logger = set_logging("lower.sub")


@log_decorator(logger)
def get_tiktoken_count(target_message: str, model_version: str) -> int:
    """
    指定されたメッセージのトークン数を、指定されたモデルバージョンのエンコーディングを使用して計算する。

    Args:
        target_message (str): トークン数を計算する対象のメッセージ。
        model_version (str): 使用するモデルのバージョン。

    Returns:
        int: エンコードされたメッセージのトークン数。
    """
    encoding = tk.encoding_for_model(model_version)
    return len(encoding.encode(target_message))
