from decimal import Decimal
import decimal
from logging import Logger
from logs.app_logger import set_logging

from logs.log_decorator import log_decorator


logger: Logger = set_logging("lower.sub")


@log_decorator(logger)
def get_conversation_cost(
    prompt_token_count: int,
    completion_token_count: int,
    prompt_cost: str,
    completion_cost: str,
) -> Decimal:
    """
    プロンプトとコンプリーションのトークン数に基づいて会話のコストを計算する。

    各トークンのコストを乗算して、プロンプトとコンプリーションの合計コストを算出し、
    それらを加算して会話の総コストを求める。

    Args:
        prompt_token_count (int): プロンプトのトークン数。
        completion_token_count (int): コンプリーションのトークン数。
        prompt_cost (str): プロンプトのトークンごとのコスト（文字列で指定）。
        completion_cost (str): コンプリーションのトークンごとのコスト（文字列で指定）。

    Returns:
        Decimal: 計算された会話の総コスト。

    """
    # 負のトークン数をチェック
    if prompt_token_count < 0 or completion_token_count < 0:
        raise ValueError("Token counts cannot be negative")

    # 有効な数値であるかをチェック
    try:
        total_prompt_cost: Decimal = prompt_token_count * Decimal(prompt_cost)
        total_completion_cost: Decimal = completion_token_count * Decimal(completion_cost)
    except decimal.InvalidOperation as e:
        raise ValueError("Invalid cost value") from e

    # 合計コストを計算
    total_cost: Decimal = total_prompt_cost + total_completion_cost

    return total_cost
