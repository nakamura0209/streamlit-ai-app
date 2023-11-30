import os
from urllib import response
import openai
import streamlit as st
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage


class LangchainChatModelFactory:
    @staticmethod
    def create_instance():
        return AzureChatOpenAI(
            openai_api_base="https://openai-test-gpt4-20231118.openai.azure.com/",  # type: ignore //pylance誤検知のため
            openai_api_version="2023-07-01-preview",  # type: ignore //pylance誤検知のため
            deployment_name="openai-test-gpt4",  # type: ignore //pylance誤検知のため
            openai_api_key="547aae27000d4df79923b93736993d8a",  # type: ignore //pylance誤検知のため
            openai_api_type="azure",
            model_version="gpt-4",
            # tiktoken_model_name=os.environ.get("AZURE_OPENAI_TIKTOKEN_MODEL_NAME", ""),
            temperature=0,
        )


def main():
    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.header("Stream-AI-Chat")

    llm = LangchainChatModelFactory.create_instance()

    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [SystemMessage(content="")]

    # ユーザ入力を監視
    if user_input := st.chat_input("Input Your Message..."):
        st.session_state.messages.append(HumanMessage(content=user_input))  # type: ignore //pylance誤検知のため
        with st.spinner("Generating ChatGPT answers..."):
            response = llm(st.session_state.messages)  # type: ignore //pylance誤検知のため
        st.session_state.messages.append(AIMessage(content=response.content))  # type: ignore //pylance誤検知のため

    messages = st.session_state.get("messages", [])
    for message in messages:
        st.write(message)


if __name__ == "__main__":
    main()
