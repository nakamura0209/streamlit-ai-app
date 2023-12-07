import streamlit as st
from costs.get_conversation_cost import get_conversation_cost
from costs.get_token_count import get_tiktoken_count
from data_source.openai_data_source import MODELS


def calculate_cost(
    converted_history: str, assistant_chat: str, model_version: str, is_error: bool
) -> None:
    prompt_tokens: int = get_tiktoken_count(converted_history, model_version)
    completion_tokens: int = get_tiktoken_count(assistant_chat, model_version)
    if not is_error:
        total_cost = get_conversation_cost(
            prompt_tokens,
            completion_tokens,
            MODELS[model_version]["config"]["prompt_cost"],
            MODELS[model_version]["config"]["completion_cost"],
        )
        st.session_state.costs = total_cost
        st.session_state.prompt_tokens = prompt_tokens
        st.session_state.completion_tokens = completion_tokens
