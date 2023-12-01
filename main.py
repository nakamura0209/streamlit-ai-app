from typing import Any, Dict, List, Union
from dotenv import load_dotenv
import openai
import streamlit as st

from data_source.langchain.lang_chain_chat_model_factory import (
    ModelParameters,
)
from data_source.openai_data_source import MODELS, Role


def create_converstations(messages: List[Dict[str, Any]], is_error: bool) -> None:
    # 会話の履歴も含めてやり取りを描画
    for message in messages:
        if message["role"] == "assistant":
            with st.chat_message(Role.ASSISTANT.value):
                st.markdown(message["content"])
        elif message["role"] == "user":
            with st.chat_message(Role.UESR.value):
                st.markdown(message["content"])
        else:
            if is_error:
                with st.chat_message(Role.SYSTEM.value):
                    st.markdown(message["content"])


def select_model(model: Union[str, Any], temperature: float) -> ModelParameters:
    # モデルの切り替え
    st.session_state["openai_model"] = MODELS[model]["config"]["model_version"]

    # OpenAI初期設定
    openai.api_type = MODELS[model]["config"]["api_type"]
    print(openai.api_type)
    openai.api_base = MODELS[model]["config"]["base_url"]
    openai.api_version = MODELS[model]["config"]["api_version"]
    openai.api_key = MODELS[model]["config"]["api_key"]

    # チャット用パラメータを付与したインスタンスを生成
    llm = ModelParameters(
        max_tokens=MODELS[model]["parameter"]["max_tokens"],
        temperature=temperature,
        top_p=MODELS[model]["parameter"]["top_p"],
        frequency_penalty=MODELS[model]["parameter"]["frequency_penalty"],
        presence_penalty=MODELS[model]["parameter"]["presence_penalty"],
        deployment_name=MODELS[model]["config"]["deployment_name"],
    )

    return llm


def init_message() -> None:
    clear_button = st.sidebar.button("Clear Conversation", key="clear")  # 会話履歴削除ボタン
    if clear_button:
        st.info("Conversation history deleted.")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.costs = []


def create_user_chat(user_input: str) -> None:
    st.session_state.messages.append({"role": Role.UESR.value, "content": user_input})  # type: ignore
    st.chat_message(Role.UESR.value).markdown(user_input)


def generate_assistant_chat(model: str, temperature: float) -> bool:
    try:
        with st.chat_message(Role.ASSISTANT.value):
            message_placeholder = st.empty()  # 一時的なプレースホルダーを作成
            full_response = ""
            for response in openai.ChatCompletion.create(
                engine=MODELS[model]["config"]["deployment_name"],
                # model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ],
                temperature=temperature,
                max_tokens=MODELS[model]["parameter"]["max_tokens"],
                top_p=MODELS[model]["parameter"]["top_p"],
                frequency_penalty=MODELS[model]["parameter"]["frequency_penalty"],
                presence_penalty=MODELS[model]["parameter"]["presence_penalty"],
                stream=True,
                stop=None,
            ):
                if response.choices:
                    full_response += response.choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌")  # レスポンスの途中結果を表示
            message_placeholder.markdown(full_response)  # 最終レスポンスを表示

        st.session_state.messages.append({"role": Role.ASSISTANT.value, "content": full_response})

    except openai.error.RateLimitError as e:
        print(e)
        err_content_message = "感覚が短すぎます。1分ほど待ってから、再度お試しください。"
        # st.session_state.messages.append({"role": Role.SYSTEM.value, "content": err_content_message})
        with st.chat_message(Role.SYSTEM.value):
            st.markdown(err_content_message)
        return True

    except Exception as e:
        print(e)
        err_content_message = "想定外のエラーです。管理者に問い合わせてください。"
        st.session_state.messages.append({"role": Role.SYSTEM.value, "content": err_content_message})
        return True

    return False


def main():
    # .envを読み取る
    load_dotenv()
    is_error = False

    # ページの基本構成
    ## ページタイトルとヘッダの設定
    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.header("Stream-AI-Chat")
    ## サイドバーの設定
    st.sidebar.title("Options")

    # AzureOpenAIChatのモデルとtemperatureを選択する
    model: Union[str, Any] = st.sidebar.radio("Choose a model: ", (MODELS.keys()))
    # スライダーの追加(min=0, max=2, default=0.0, stride=0.1)
    temperature = st.sidebar.slider("Temperature: ", min_value=0.0, max_value=2.0, value=0.0, step=0.1)

    llm = select_model(model, temperature)

    # 会話履歴の削除(clearボタンが押された場合)
    init_message()

    # チャット履歴の初期化
    if not st.session_state["messages"]:
        st.session_state.messages = [{"role": Role.SYSTEM.value, "content": ""}]

    # 履歴も含めた会話の生成
    create_converstations(st.session_state.messages, is_error)

    # ユーザ入力を監視
    user_input = st.chat_input("Input Your Message...")
    if user_input:
        # ユーザーが入力したインプットの描画
        create_user_chat(user_input)
        # アシスタントの回答を生成
        is_error = generate_assistant_chat(model, temperature)


if __name__ == "__main__":
    main()
