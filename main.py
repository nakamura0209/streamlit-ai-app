# 必要なライブラリとモジュールをインポート
from logging import Logger
from dotenv import load_dotenv
import streamlit as st
from data_access.conversations import (
    add_user_chat_message,
    display_conversations,
    generate_assistant_chat_response,
)
from data_access.initialize_chat_page import initialize_page_base, initialize_sidebar, select_model

# モデルのパラメータと役割を定義するモジュールをインポート
from data_source.openai_data_source import Role

from logs.app_logger import set_logging
from logs.log_decorator import log_decorator

# from logs.AzureBlobHandler import write_log_to_blob

# ロギング設定の読み込み
logger: Logger = set_logging("__main__")

# 環境変数を読み込む
load_dotenv()


# メイン関数
@log_decorator(logger)
def main():
    is_error = False

    # 基本的なページ構造をセットアップ
    initialize_page_base()

    model_key, max_tokens, temperature, top_p, frequency_penalty, presence_penalty = initialize_sidebar()

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
        is_error = generate_assistant_chat_response(model_key, temperature, llm)


# メイン関数を実行
if __name__ == "__main__":
    main()
