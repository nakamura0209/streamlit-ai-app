from decimal import Decimal
import pytest
from costs.get_conversation_cost import get_conversation_cost
from costs.get_token_count import get_tiktoken_count


def test_get_tiktoken_count_with_gpt_3_5_returns_expected_token_count():
    token_count = get_tiktoken_count("こんにちは", "gpt-3.5-turbo")
    assert token_count == 1


def test_get_tiktoken_count_with_gpt_4_returns_expected_token_count():
    token_count = get_tiktoken_count("こんにちは", "gpt-4")
    assert token_count == 1


def test_get_tiktoken_count_with_empty_string():
    token_count = get_tiktoken_count("", "gpt-3.5-turbo")
    assert token_count == 0


def test_get_tiktoken_count_with_long_string():
    long_message = "これは非常に長いメッセージです。" * 100
    token_count = get_tiktoken_count(long_message, "gpt-3.5-turbo")
    expected_token_count = 1400
    assert token_count == expected_token_count


@pytest.mark.parametrize(
    "prompt_count, completion_count, prompt_cost, completion_cost, expected_total",
    [
        (1, 1, "1", "1", Decimal("2")),
        (0, 1, "1", "1", Decimal("1")),
        (1, 0, "1", "1", Decimal("1")),
        (2, 3, "0.5", "0.4", Decimal("2.2")),
    ],
)
def test_get_conversation_cost(
    prompt_count, completion_count, prompt_cost, completion_cost, expected_total
):
    total_costs = get_conversation_cost(prompt_count, completion_count, prompt_cost, completion_cost)
    assert total_costs == expected_total


# 異常系のテストケース
@pytest.mark.parametrize(
    "prompt_count, completion_count, prompt_cost, completion_cost",
    [
        (-1, 1, "1", "1"),
        (1, -1, "1", "1"),
        (1, 1, "abc", "1"),
        (1, 1, "1", "abc"),
    ],
)
def test_get_conversation_cost_invalid_input(
    prompt_count, completion_count, prompt_cost, completion_cost
):
    with pytest.raises(ValueError):
        get_conversation_cost(prompt_count, completion_count, prompt_cost, completion_cost)
