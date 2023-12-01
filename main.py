from typing import Any, Dict, List, Union
from dotenv import load_dotenv
import openai
import streamlit as st

from data_source.langchain.lang_chain_chat_model_factory import (
    ModelParameters,
)
from data_source.openai_data_source import MODELS, Role


def create_conversations(messages: List[Dict[str, Any]], is_error: bool) -> None:
    """
    会話を表示します。エラーが発生した場合も含みます。

    Args:
        messages (List[Dict[str, Any]]): 会話のメッセージリスト。
        is_error (bool): エラーが発生したかどうかのフラグ。
    """
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
    """
    言語モデルを選択し、そのパラメータを設定します。

    Args:
        model (Union[str, Any]): 選択された言語モデル。
        temperature (float): テキスト生成のための温度パラメータ。

    Returns:
        ModelParameters: 選択された言語モデルのパラメータ。
    """
    st.session_state["openai_model"] = MODELS[model]["config"]["model_version"]

    openai.api_type = MODELS[model]["config"]["api_type"]
    openai.api_base = MODELS[model]["config"]["base_url"]
    openai.api_version = MODELS[model]["config"]["api_version"]
    openai.api_key = MODELS[model]["config"]["api_key"]

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
    """
    チャットメッセージのセッションステートを初期化します。
    """
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button:
        st.info("会話履歴が削除されました。")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.costs = []


def create_user_chat(user_input: str) -> None:
    """
    ユーザーのチャット入力を会話に追加します。

    Args:
        user_input (str): ユーザーのチャット入力。
    """
    st.session_state.messages.append({"role": Role.UESR.value, "content": user_input})
    st.chat_message(Role.UESR.value).markdown(user_input)


def generate_assistant_chat(model: str, temperature: float) -> bool:
    """
    OpenAIのChat APIを使用してアシスタントのチャット応答を生成します。

    Args:
        model (str): 選択された言語モデル。
        temperature (float): テキスト生成のための温度パラメータ。

    Returns:
        bool: エラーが発生した場合はTrue、それ以外はFalse。
    """
    try:
        with st.chat_message(Role.ASSISTANT.value):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                engine=MODELS[model]["config"]["deployment_name"],
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
                if response.choices:  # type: ignore
                    full_response += response.choices[0].delta.get("content", "")  # type: ignore
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": Role.ASSISTANT.value, "content": full_response})

    except openai.error.RateLimitError as e:  # type: ignore
        print(e)
        err_content_message = "感覚が短すぎます。1分ほど待ってから、再度お試しください。"
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
    # 環境変数を読み込む
    load_dotenv()
    is_error = False

    # 基本的なページ構造をセットアップ
    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.header("Stream-AI-Chat")
    st.sidebar.title("オプション")

    # 言語モデルと温度を選択
    model: Union[str, Any] = st.sidebar.radio("モデルの選択: ", (MODELS.keys()))
    temperature = st.sidebar.slider("温度: ", min_value=0.0, max_value=2.0, value=0.0, step=0.1)

    llm = select_model(model, temperature)

    # チャットメッセージセッションステートを初期化
    init_message()

    # チャット履歴の初期化
    if not st.session_state["messages"]:
        st.session_state.messages = [{"role": Role.SYSTEM.value, "content": ""}]

    # 会話を表示（チャット履歴含む）
    create_conversations(st.session_state.messages, is_error)

    # ユーザー入力を監視
    user_input = st.chat_input("メッセージを入力...")
    if user_input:
        # ユーザーの入力を表示
        create_user_chat(user_input)
        # アシスタントのチャット応答を生成
        is_error = generate_assistant_chat(model, temperature)


if __name__ == "__main__":
    main()
