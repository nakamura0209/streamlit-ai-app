from logging import Logger
import streamlit as st
from data_access.conversations import (
    add_user_chat_message,
    display_conversations,
    generate_assistant_chat_response,
)
from utils.get_conversation_cost import get_conversation_cost
from utils.get_token_count import get_tiktoken_count
from data_access.initialize_chat_page import (
    initialize_page_base,
    initialize_sidebar,
    select_model,
)

from data_source.openai_data_source import MODELS, Role

from logs.app_logger import set_logging
from logs.log_decorator import log_decorator

# ロギング設定の読み込み
logger: Logger = set_logging("__main__")


# メイン関数
@log_decorator(logger)
def main() -> None:
    # 会話生成において何かしらのエラーの発生を検知する際に使用
    # あくまでもユーザに警告を出すための検知フラグであり、異常終了させるためのフラグではな言うことに注意
    is_error = False

    initialize_page_base()

    model_key, max_tokens, temperature, top_p, frequency_penalty, presence_penalty = initialize_sidebar()

    # 画面上でユーザが好きなタイミングで好きなモデルを選択できる
    llm = select_model(model_key, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)

    # チャット履歴の初期化
    if not st.session_state["messages"]:
        st.session_state.messages = [{"role": Role.SYSTEM.value, "content": ""}]

    # 会話を表示（チャット履歴含む）
    display_conversations(st.session_state.messages, is_error)

    # ユーザー入力を受け付け
    user_input = st.chat_input("Input your message...")
    if user_input:
        # ユーザーの入力を表示
        add_user_chat_message(user_input)
        # アシスタントのチャット応答を生成
        is_error, converted_history, assistant_chat = generate_assistant_chat_response(
            model_key, temperature, llm
        )

        # コストの計算
        prompt_tokens: int = get_tiktoken_count(converted_history, model_key)
        completion_tokens: int = get_tiktoken_count(assistant_chat, model_key)
        if not is_error:
            total_cost = get_conversation_cost(
                get_tiktoken_count(converted_history, model_key),
                get_tiktoken_count(assistant_chat, model_key),
                MODELS[model_key]["config"]["prompt_cost"],
                MODELS[model_key]["config"]["completion_cost"],
            )
            st.session_state.costs = total_cost
            st.session_state.prompt_tokens = prompt_tokens
            st.session_state.completion_tokens = completion_tokens


# メイン関数を実行
if __name__ == "__main__":
    main()
