import os
from urllib import response
from dotenv import load_dotenv
from numpy import isin
import openai
import streamlit as st
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from data_source.langchain.lang_chain_chat_model_factory import LangchainChatModelFactory


def main():
    # .envを読み取る
    load_dotenv()

    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.header("Stream-AI-Chat")

    llm = LangchainChatModelFactory.create_instance()

    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [SystemMessage(content="")]

    # ユーザ入力を監視
    if user_input := st.chat_input("Input Your Message..."):
        st.session_state.messages.append(HumanMessage(content=user_input))  # type: ignore //pylance誤検知のため
        try:
            with st.spinner("Generating ChatGPT answers..."):
                response = llm(st.session_state.messages)  # type: ignore //pylance誤検知のため
            st.session_state.messages.append(AIMessage(content=response.content))  # type: ignore //pylance誤検知のため

        except Exception as e:
            err_content_message = "感覚が短すぎます。一定時間経過後、再度お試しください。"
            st.session_state.messages.append(SystemMessage(content=err_content_message))
            pass

    messages = st.session_state.get("messages", [])
    if len(messages) > 1:
        for message in messages:
            if isinstance(message, AIMessage):
                with st.chat_message("Assistant"):
                    st.markdown(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("User"):
                    st.markdown(message.content)
            else:
                with st.chat_message("System"):
                    st.markdown(message.content)


if __name__ == "__main__":
    main()
