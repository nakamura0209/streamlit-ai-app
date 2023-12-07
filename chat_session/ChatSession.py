# ユーザーのチャット入力を会話に追加する関数
from logging import Logger
import traceback
from typing import Any, Dict, List, Tuple
import openai
import streamlit as st
from chat_session.initialize_chat_page import initialize_sidebar, select_model
from data_source.langchain.lang_chain_chat_model_factory import ModelParameters
from data_source.openai_data_source import MODELS, Role
from logs.app_logger import set_logging
from logs.log_decorator import log_decorator

logger: Logger = set_logging("lower.sub")


class ChatSession:
    def __init__(self):
        # self.is_error = False
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": Role.SYSTEM.value, "content": ""}]

    @log_decorator(logger)
    def initialize_chat_page_element(self) -> Tuple[ModelParameters, str]:
        # ページの基本構成を初期化
        st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
        st.header("Stream-AI-Chat")
        st.sidebar.title("Options")

        # ユーザが設定した値にパラメータを設定
        (
            model_version,
            max_tokens,
            temperature,
            top_p,
            frequency_penalty,
            presence_penalty,
        ) = initialize_sidebar()

        # 画面上でユーザが好きなタイミングで好きなモデルを選択できる
        llm = select_model(
            model_version, max_tokens, temperature, top_p, frequency_penalty, presence_penalty
        )

        return llm, model_version

    # 会話を表示する関数
    @log_decorator(logger)
    def display_conversations(self, messages: List[Dict[str, Any]], is_error: bool) -> None:
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

    @log_decorator(logger)
    def add_user_chat_message(self, user_input: str) -> None:
        """
        ユーザーのチャット入力を会話に追加します。

        Args:
            user_input (str): ユーザーのチャット入力。
        """
        st.session_state.messages.append({"role": Role.USER.value, "content": user_input})
        st.chat_message(Role.USER.value).markdown(user_input)

    # アシスタントのチャット応答を生成する関数
    @log_decorator(logger)
    def generate_assistant_chat_response(
        self, model_version: str, llm: ModelParameters
    ) -> Tuple[bool, str, str]:
        """
        OpenAIのChat APIを使用してアシスタントのチャット応答を生成します。

        Args:
            model_version (str): 選択された言語モデルのキー。
            temperature (float): テキスト生成のためのtemperatureパラメータ。
            llm(ModelParameters): 会話を行う際のGPTモデルとそのパラメータ

        Returns:
            bool: エラーが発生した場合はTrue、それ以外はFalse。
        """
        try:
            with st.chat_message(Role.ASSISTANT.value):
                message_placeholder = st.empty()
                assistant_chat = ""
                # これまでの会話履歴もアシスタントに送信する必要があるため
                messages_with_history = [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]
                # OpenAIのChat APIを呼び出して応答を生成
                for response in openai.ChatCompletion.create(
                    engine=MODELS[model_version]["config"]["deployment_name"],
                    messages=messages_with_history,
                    temperature=llm.temperature,
                    max_tokens=llm.max_tokens,
                    top_p=llm.top_p,
                    frequency_penalty=llm.frequency_penalty,
                    presence_penalty=llm.presence_penalty,
                    stream=True,
                    stop=None,
                ):
                    if response.choices:  # type: ignore
                        assistant_chat += response.choices[0].delta.get("content", "")  # type: ignore
                        message_placeholder.markdown(assistant_chat + "▌")
                message_placeholder.markdown(assistant_chat)

            st.session_state.messages.append({"role": Role.ASSISTANT.value, "content": assistant_chat})

        except openai.error.RateLimitError as e:  # type: ignore
            logger.warn(traceback.format_exc())
            err_content_message = "The execution interval is too short. Wait a minute and try again."
            with st.chat_message(Role.SYSTEM.value):
                st.markdown(err_content_message)
            return True, "", ""

        except Exception as e:
            logger.warn(traceback.format_exc())
            err_content_message = "Unexpected error. Contact the administrator."
            with st.chat_message(Role.SYSTEM.value):
                st.markdown(err_content_message)
            return True, "", ""

        # 会話履歴のトークン数を取得するため、文字列に変換
        converted_historys = [item["content"] for item in messages_with_history]
        converted_history = " ".join(converted_historys)

        return False, converted_history, assistant_chat
