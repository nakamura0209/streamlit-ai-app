# ユーザーのチャット入力を会話に追加する関数
from logging import Logger
import traceback
from typing import Any, Dict, List
import openai
import streamlit as st
from data_source.langchain.lang_chain_chat_model_factory import ModelParameters
from data_source.openai_data_source import MODELS, Role
from logs.app_logger import set_logging
from logs.log_decorator import log_decorator

logger: Logger = set_logging("lower.sub")


@log_decorator(logger)
def add_user_chat_message(user_input: str) -> None:
    """
    ユーザーのチャット入力を会話に追加します。

    Args:
        user_input (str): ユーザーのチャット入力。
    """
    st.session_state.messages.append({"role": Role.USER.value, "content": user_input})
    st.chat_message(Role.USER.value).markdown(user_input)


# アシスタントのチャット応答を生成する関数
@log_decorator(logger)
def generate_assistant_chat_response(model_key: str, temperature: float, llm: ModelParameters) -> bool:
    """
    OpenAIのChat APIを使用してアシスタントのチャット応答を生成します。

    Args:
        model_key (str): 選択された言語モデルのキー。
        temperature (float): テキスト生成のためのtemperatureパラメータ。
        llm(ModelParameters): 会話を行う際のGPTモデルとそのパラメータ

    Returns:
        bool: エラーが発生した場合はTrue、それ以外はFalse。
    """
    try:
        with st.chat_message(Role.ASSISTANT.value):
            message_placeholder = st.empty()
            full_response = ""
            # OpenAIのChat APIを呼び出して応答を生成
            for response in openai.ChatCompletion.create(
                engine=MODELS[model_key]["config"]["deployment_name"],
                messages=[
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ],
                temperature=temperature,
                max_tokens=llm.max_tokens,
                top_p=llm.top_p,
                frequency_penalty=llm.frequency_penalty,
                presence_penalty=llm.presence_penalty,
                stream=True,
                stop=None,
            ):
                if response.choices:  # type: ignore
                    full_response += response.choices[0].delta.get("content", "")  # type: ignore
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": Role.ASSISTANT.value, "content": full_response})

    except openai.error.RateLimitError as e:  # type: ignore
        logger.warn(traceback.format_exc())
        err_content_message = "The execution interval is too short. Wait a minute and try again."
        with st.chat_message(Role.SYSTEM.value):
            st.markdown(err_content_message)
        return True

    except Exception as e:
        logger.warn(traceback.format_exc())
        err_content_message = "Unexpected error. Contact the administrator."
        with st.chat_message(Role.SYSTEM.value):
            st.markdown(err_content_message)
        return True

    return False


# 会話を表示する関数
@log_decorator(logger)
def display_conversations(messages: List[Dict[str, Any]], is_error: bool) -> None:
    """
    会話を表示します。エラーが発生した場合も含みます。

    Args:
        messages (List[Dict[str, Any]]): 会話のメッセージリスト。
        is_error (bool): エラーが発生したかどうかのフラグ。
    """
    for message in messages:
        role, content = message["role"], message["content"]
        if role == "user" or role == "assistant":
            with st.chat_message(role):
                st.markdown(content)
        elif role == "system":
            if is_error:
                with st.chat_message(role):
                    st.markdown(content)
