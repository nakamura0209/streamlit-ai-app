import os
from urllib import response
from dotenv import load_dotenv
from numpy import isin
import openai
import streamlit as st
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from data_source.langchain.lang_chain_chat_model_factory import LangchainChatModelFactory
from data_source.openai_data_source import Role


def main():
    # .envを読み取る
    load_dotenv()
    is_error = False
    print(is_error)

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

        except openai.error.RateLimitError as e:  # type: ignore
            err_content_message = "感覚が短すぎます。一定時間経過後、再度お試しください。"
            st.session_state.messages.append(SystemMessage(content=err_content_message))
            is_error = True
            pass
        except Exception as e:
            err_content_message = "想定外のエラーです。管理者に問い合わせてください。"
            st.session_state.messages.append(SystemMessage(content=err_content_message))
            is_error = True
            pass

    messages = st.session_state.get("messages", [])
    if len(messages) > 1:
        for message in messages:
            if message.type == "ai":
                with st.chat_message(Role.ASSISTANT.value):
                    st.markdown(message.content)
            elif message.type == "human":
                with st.chat_message(Role.UESR.value):
                    st.markdown(message.content)
            else:
                if is_error:
                    with st.chat_message(Role.SYSTEM.value):
                        st.markdown(message.content)


if __name__ == "__main__":
    main()
