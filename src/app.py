import os
import openai
import streamlit as st
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage


def main():
    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.header("Stream-AI-Chat")

    if user_input := st.chat_input("聞きたいことを入力してね！"):
        # なにか入力されればここが実行される
        st.write(user_input)


if __name__ == "__main__":
    main()
