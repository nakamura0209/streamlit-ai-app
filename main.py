import streamlit as st

from logging import Logger
from chat_session.ChatSession import ChatSession
from costs.calculate_cost import calculate_cost
from data_source.openai_data_source import BasePage, PDFOperateOptions

from logs.app_logger import set_logging
from logs.log_decorator import log_decorator
from pdf_qa_service.PDFQASession import PDFQASession

logger: Logger = set_logging("__main__")


@log_decorator(logger)
def main() -> None:
    # 会話生成において何かしらのエラーの発生を検知する際に使用
    # あくまでもユーザに警告を出すための検知フラグであり、異常終了させるためのフラグではないことに注意
    is_error = False

    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.sidebar.title("Sections")
    page_selection = st.sidebar.radio("Go To", [BasePage.CHAT.value, BasePage.PDF_QA.value])
    if page_selection == BasePage.CHAT.value:
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

    elif page_selection == BasePage.PDF_QA.value:
        pdf_qa_service = PDFQASession()
        # ページ構成要素の初期化
        pdf_qa_service.initialize_chat_page_element()

        selected_operator: str = pdf_qa_service.select_pdf_service_operator()

        if selected_operator == PDFOperateOptions.UPLOAD.value:
            pdf_qa_service.get_pdf_text()
        # elif selected_operator == PDFOperateOptions.QUESTION.value:
        #     page_ask_my_pdf()


if __name__ == "__main__":
    main()
