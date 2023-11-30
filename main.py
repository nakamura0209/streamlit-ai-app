from typing import Any, List, Union
from urllib import response
from xmlrpc.client import boolean
from dotenv import load_dotenv
from numpy import isin
import openai
import streamlit as st
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from data_source.langchain.lang_chain_chat_model_factory import LangchainChatModelFactory
from data_source.openai_data_source import MODELS, Role


def create_converstations(
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]], is_error: boolean
) -> None:
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


def generate_ai_messages(
    history_messages: List[Union[SystemMessage, Any]], llm: AzureChatOpenAI
) -> bool:
    try:
        with st.spinner("Generating ChatGPT answers..."):
            response = llm(history_messages)  # type: ignore //pylance誤検知のため
        st.session_state.messages.append(AIMessage(content=response.content))  # type: ignore //pylance誤検知のため

    except openai.error.RateLimitError as e:  # type: ignore
        err_content_message = "感覚が短すぎます。一定時間経過後、再度お試しください。"
        st.session_state.messages.append(SystemMessage(content=err_content_message))
        return True

    except Exception as e:
        print(e)
        err_content_message = "想定外のエラーです。管理者に問い合わせてください。"
        st.session_state.messages.append(SystemMessage(content=err_content_message))
        return True

    return False


def main():
    # .envを読み取る
    load_dotenv()
    # エラー判断フラグ初期化
    is_error = False

    # ページの基本構成

    ## ページタイトルとヘッダの設定
    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.header("Stream-AI-Chat")

    ## サイドバーの設定
    st.sidebar.title("Options")
    model: Union[str, Any] = st.sidebar.radio("Choose a model: ", (MODELS.keys()))  # オプションボタン
    clear_button = st.sidebar.button("Clear Conversation", key="clear")  # 会話履歴削除ボタン

    ## コスト表示
    st.sidebar.markdown("## Costs")
    st.sidebar.markdown("**Total Cost**")
    for i in range(3):
        st.sidebar.markdown(f"- ${i+0.01}")

    # スライダーの追加(min=0, max=2, default=0.0, stride=0.1)
    temperature = st.sidebar.slider("Temperature: ", min_value=0.0, max_value=2.0, value=0.0, step=0.1)

    # AzureOpenAIのパラメータ設定
    llm = LangchainChatModelFactory.create_instance(temperature, model)

    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [SystemMessage(content="")]

    # ユーザ入力を監視
    if user_input := st.chat_input("Input Your Message..."):
        st.session_state.messages.append(HumanMessage(content=user_input))  # type: ignore //pylance誤検知のため
        # 会話履歴をもとに回答生成開始
        is_error = generate_ai_messages(st.session_state.messages, llm)

    messages = st.session_state.get("messages", [])
    if len(messages) > 1:
        # 会話の描画
        create_converstations(messages, is_error)


if __name__ == "__main__":
    main()
