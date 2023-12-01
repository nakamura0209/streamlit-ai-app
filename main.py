# 必要なライブラリとモジュールをインポート
from typing import Any, Dict, List, Union, Tuple
from dotenv import load_dotenv
import openai
import traceback
import streamlit as st

# モデルのパラメータと役割を定義するモジュールをインポート
from data_source.langchain.lang_chain_chat_model_factory import ModelParameters
from data_source.openai_data_source import MODELS, Role


# サイドバーを初期化して、モデルのパラメータを設定する関数
def initialize_sidebar(model_key: str) -> Tuple[int, float, float, float, float]:
    # 選択されたモデルのパラメータを取得
    model_parameter = MODELS[model_key]["parameter"]
    # 各種パラメータのスライダーをサイドバーに設定
    max_tokens = st.sidebar.slider(
        "max_tokens: ",  # 最大トークン数
        min_value=1,
        max_value=model_parameter["max_tokens"],
        value=2048,
        step=1,
    )
    temperature = st.sidebar.slider(
        "temperature: ",  # 温度パラメータ
        min_value=0.0,
        max_value=2.0,
        value=0.0,
        step=0.1,
    )
    top_p = st.sidebar.slider(
        "top_p: ",  # トップPサンプリング
        min_value=0.0,
        max_value=model_parameter["max_top_p"],
        value=0.0,
        step=0.1,
    )
    frequency_penalty = st.sidebar.slider(
        "frequency_penalty: ",  # 頻度ペナルティ
        min_value=0.0,
        max_value=model_parameter["max_frequency_penalty"],
        value=0.0,
        step=0.1,
    )
    presence_penalty = st.sidebar.slider(
        "presence_penalty: ",  # 存在ペナルティ
        min_value=0.0,
        max_value=model_parameter["max_presence_penalty"],
        value=0.0,
        step=0.1,
    )

    # 設定されたパラメータを返す
    return max_tokens, temperature, top_p, frequency_penalty, presence_penalty


# 会話を表示する関数
def display_conversations(messages: List[Dict[str, Any]], is_error: bool) -> None:
    """
    会話を表示します。エラーが発生した場合も含みます。

    Args:
        messages (List[Dict[str, Any]]): 会話のメッセージリスト。
        is_error (bool): エラーが発生したかどうかのフラグ。
    """
    for message in messages:
        role, content = message["role"], message["content"]
        if role == "user" or role == "assistant":
            with st.chat_message(role):
                st.markdown(content)
        elif role == "system":
            if is_error:
                with st.chat_message(role):
                    st.markdown(content)


# モデルを選択し、パラメータを設定する関数
def select_model(
    model_key: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    frequency_penalty: float,
    presence_penalty: float,
) -> ModelParameters:
    """
    言語モデルを選択し、そのパラメータを設定します。

    Args:
        model_key (str): 選択された言語モデルのキー。
        temperature (float): テキスト生成のためのtemperatureパラメータ。

    Returns:
        ModelParameters: 選択された言語モデルのパラメータ。
    """
    # 選択されたモデルの設定を取得
    model_config = MODELS[model_key]["config"]

    # OpenAI APIの設定をセッションステートに保存
    st.session_state["openai_model"] = model_config["model_version"]
    openai.api_type, openai.api_base, openai.api_version, openai.api_key = (
        model_config["api_type"],
        model_config["base_url"],
        model_config["api_version"],
        model_config["api_key"],
    )
    print(openai.api_type)

    # 選択されたモデルのパラメータを設定
    llm = ModelParameters(
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        deployment_name=model_config["deployment_name"],
    )

    # 選択されたモデルを情報として表示
    st.info(f"{model_key} is selected")

    # 設定されたモデルのパラメータを返す
    return llm


# チャットメッセージのセッションステートを初期化する関数
def initialize_message_state() -> None:
    """
    チャットメッセージのセッションステートを初期化します。
    """
    # クリアボタンをサイドバーに設定
    clear_button = st.sidebar.button("Clear", key="clear")
    if clear_button:
        st.info("Conversation history has been deleted.")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.costs = []


# ユーザーのチャット入力を会話に追加する関数
def add_user_chat_message(user_input: str) -> None:
    """
    ユーザーのチャット入力を会話に追加します。

    Args:
        user_input (str): ユーザーのチャット入力。
    """
    st.session_state.messages.append({"role": Role.UESR.value, "content": user_input})
    st.chat_message(Role.UESR.value).markdown(user_input)


# アシスタントのチャット応答を生成する関数
def generate_assistant_chat_response(model_key: str, temperature: float, llm: ModelParameters) -> bool:
    """
    OpenAIのChat APIを使用してアシスタントのチャット応答を生成します。

    Args:
        model_key (str): 選択された言語モデルのキー。
        temperature (float): テキスト生成のためのtemperatureパラメータ。

    Returns:
        bool: エラーが発生した場合はTrue、それ以外はFalse。
    """
    try:
        with st.chat_message(Role.ASSISTANT.value):
            message_placeholder = st.empty()
            full_response = ""
            # OpenAIのChat APIを呼び出して応答を生成
            for response in openai.ChatCompletion.create(
                engine=MODELS[model_key]["config"]["deployment_name"],
                messages=[
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ],
                temperature=temperature,
                max_tokens=llm.max_tokens,
                top_p=llm.top_p,
                frequency_penalty=llm.frequency_penalty,
                presence_penalty=llm.presence_penalty,
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
        err_content_message = "The execution interval is too short. Wait a minute and try again."
        with st.chat_message(Role.SYSTEM.value):
            st.markdown(err_content_message)
        return True

    except Exception as e:
        print(traceback.format_exc())
        err_content_message = "Unexpected error. Contact the administrator."
        with st.chat_message(Role.SYSTEM.value):
            st.markdown(err_content_message)
        return True

    return False


# メイン関数
def main():
    # 環境変数を読み込む
    load_dotenv()
    is_error = False

    # 基本的なページ構造をセットアップ
    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.header("Stream-AI-Chat")
    st.sidebar.title("Options")

    # 言語モデルとtemperatureを選択
    model_key: Union[str, Any] = st.sidebar.radio("Select a model:", (MODELS.keys()))

    max_tokens, temperature, top_p, frequency_penalty, presence_penalty = initialize_sidebar(model_key)

    llm = select_model(model_key, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)

    # チャットメッセージセッションステートを初期化
    initialize_message_state()

    # チャット履歴の初期化
    if not st.session_state["messages"]:
        st.session_state.messages = [{"role": Role.SYSTEM.value, "content": ""}]

    # 会話を表示（チャット履歴含む）
    display_conversations(st.session_state.messages, is_error)

    # ユーザー入力を受け付け
    user_input = st.chat_input("Input your message...")
    if user_input:
        # ユーザーの入力を表示
        add_user_chat_message(user_input)
        # アシスタントのチャット応答を生成
        is_error = generate_assistant_chat_response(model_key, temperature, llm)


# メイン関数を実行
if __name__ == "__main__":
    main()
