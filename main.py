import streamlit as st

from logging import Logger
from chat_session.ChatSession import ChatSession
from costs.calculate_cost import calculate_cost

from logs.app_logger import set_logging
from logs.log_decorator import log_decorator

# ロギング設定の読み込み
logger: Logger = set_logging("__main__")


# メイン関数
@log_decorator(logger)
def main() -> None:
    # 会話生成において何かしらのエラーの発生を検知する際に使用
    # あくまでもユーザに警告を出すための検知フラグであり、異常終了させるためのフラグではないことに注意
    is_error = False

    chat_session = ChatSession()
    # ページ構成要素の初期化
    llm, model_version = chat_session.initialize_chat_page_element()
    # 会話を表示（チャット履歴含む）
    chat_session.display_conversations(st.session_state.messages, is_error)
    # ユーザー入力を受け付け
    user_input = st.chat_input("Input your message...")
    if user_input:
        # ユーザーの入力を表示
        chat_session.add_user_chat_message(user_input)
        # アシスタントのチャット応答を生成
        is_error, converted_history, assistant_chat = chat_session.generate_assistant_chat_response(
            model_version, llm
        )

        # コストの計算
        calculate_cost(converted_history, assistant_chat, model_version, is_error)


# メイン関数を実行
if __name__ == "__main__":
    main()
