from logging import Logger

import streamlit as st
from data_source.openai_data_source import PDFOperateOptions
from logs.app_logger import set_logging
from logs.log_decorator import log_decorator

logger: Logger = set_logging("lower.sub")


class PDFQASession:
    @log_decorator(logger)
    def initialize_chat_page_element(self) -> None:
        # ページの基本構成を初期化
        st.header("Stream-PDF-QA")
        st.sidebar.title("Options")

    def select_pdf_service_operator(self) -> str:
        return st.sidebar.radio(
            "Go to",
            [PDFOperateOptions.UPLOAD.value, PDFOperateOptions.QUESTION.value],
        )  # type: ignore

    # TODO: 文字の分析処理をここに記載していく
    def get_pdf_text(self):
        uploaded_file = st.file_uploader(label="Upload your PDF.", type="pdf")
