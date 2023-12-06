# サイドバーを初期化して、モデルのパラメータを設定する関数
from logging import Logger
import os
from typing import Any, Dict, List, Tuple, Union
import openai

import streamlit as st
from data_source.langchain.lang_chain_chat_model_factory import ModelParameters
from data_source.openai_data_source import MODELS, Role
from logs.app_logger import set_logging
from logs.log_decorator import log_decorator


logger: Logger = set_logging("lower.sub")


@log_decorator(logger)
def draw_sidebar_divider():
    st.sidebar.markdown("---")


# 会話履歴をマークダウン形式で保存する関数
@log_decorator(logger)
def save_conversation_to_markdown(filename: str, messages: List[Dict[str, str]]) -> str:
    """
    指定された会話履歴をマークダウン形式でファイルに保存します。

    Parameters:
    filename (str): 保存するファイルの名前。".md" で終わっていない場合は、拡張子が追加されます。
    messages (List[Dict[str, str]]): 会話の各メッージを含む辞書のリスト。

    Returns:
    str: 保存されたファイルの名前。

    Raises:
    IOError: ファイルの書き込みに失敗した場合に発生します。
    """
    markdown_filename = f"{filename}.md" if not filename.endswith(".md") else filename

    # マークダウン形式のテキストを生成
    markdown_text = ""
    for message in messages:
        role = message.get("role")
        content = message.get("content", "")
        prefix = f"**{role.title()}:** " if role in (Role.USER.value, Role.ASSISTANT.value) else ""
        markdown_text += f"{prefix}{content}\n\n"

    # ファイルに書き込み
    with open(markdown_filename, "w", encoding="utf-8") as file:
        file.write(markdown_text)

    return markdown_filename


# Streamlitを使用してサイドバーにダウンロード機能を追加する関数
@log_decorator(logger)
def add_download_button_to_sidebar(messages: List[Dict[str, str]]):
    """
    サイドバーにダウンロードボタンとファイル名入力フォームを追加する。

    この関数はStreamlitを使用して、ユーザーが会話履歴をダウンロードできるようにサイドバーにセクションを追加する。
    ユーザーはダウンロードするファイル名を入力し、'Generate History Log'ボタンをクリックすると、
    会話がMarkdownファイルに保存され、ダウンロードボタンが表示される。

    Parameters:
    - messages (List[Dict[str, str]]): 会話の各メッセージの詳細を含む辞書のリスト。
    """
    with st.sidebar:
        st.write("## Download Conversation")
        default_filename = "conversation"
        filename = st.text_input("Enter filename for download:", value=default_filename)

        # ユーザーが'Generate History Log'ボタンをクリックした場合の処理
        if st.button("Generate History Log"):
            # 会話が存在するか確認（初期化時の空メッセージを除く）
            if len(messages) > 1:
                # 会話をMarkdownファイルに保存し、ダウンロードボタンを表示
                markdown_filename = save_conversation_to_markdown(filename, messages)
                with open(markdown_filename, "rb") as file:
                    st.download_button(
                        label="Download",
                        data=file,
                        file_name=markdown_filename,
                        mime="text/markdown",
                    )
                # ダウンロード後にファイルを削除
                os.remove(markdown_filename)
            else:
                st.warning("No conversation to download.")


# チャットメッセージのセッションステートを初期化する関数
@log_decorator(logger)
def clear_conversations() -> None:
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
        st.session_state.prompt_tokens = []
        st.session_state.completion_tokens = []


@log_decorator(logger)
# 会話のコストを表示する
def display_total_costs() -> None:
    """
    サイドバーに会話の総コストを表示する関数。

    この関数は、Streamlitのサイドバーに「Show Total Costs」ボタンを追加し、
    ユーザーがこのボタンをクリックすると、セッション状態に保存されている
    総コストを表示します。コストが未定義の場合は、0円として表示します。

    Returns:
        None
    """
    st.sidebar.markdown("## Costs")
    show_cost_button = st.sidebar.button("Show Total Costs")
    if show_cost_button:
        logger.debug(f"st.session_state.costs = {st.session_state.costs}")
        if st.session_state.costs:
            st.sidebar.markdown(f"**{st.session_state.costs} YEN**")
            st.sidebar.markdown(f"**Prompt Tokens: {st.session_state.prompt_tokens}**")
            st.sidebar.markdown(f"**Completion Tokens: {st.session_state.completion_tokens}**")
        else:
            st.sidebar.markdown(f"**0 YEN**")


# モデルを選択し、パラメータを設定する関数
@log_decorator(logger)
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
    model_config: Dict[str, Any] = MODELS[model_key]["config"]

    # OpenAI APIの設定をセッションステートに保存
    st.session_state["openai_model"] = model_config["model_version"]
    openai.api_type, openai.api_base, openai.api_version, openai.api_key = (
        model_config["api_type"],
        model_config["base_url"],
        model_config["api_version"],
        model_config["api_key"],
    )

    # 選択されたモデルのパラメータを設定
    language_model_parameters = ModelParameters(
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        deployment_name=model_config["deployment_name"],
    )

    st.info(f"{model_key} is selected")

    return language_model_parameters


@log_decorator(logger)
def initialize_page_base() -> None:
    """基本的なページ構造をセットアップ"""
    st.set_page_config(page_title="Stream-AI-Chat", page_icon="🤖")
    st.header("Stream-AI-Chat")
    st.sidebar.title("Options")


@log_decorator(logger)
def initialize_sidebar() -> Tuple[Union[str, Any], int, float, float, float, float]:
    """
    サイドバーにモデルパラメータのスライダーを初期化し、その値を返します。

    選択されたモデルに関連する様々なパラメータのためのスライダーをStreamlitサイドバーに作成します。
    モデルのキーを使用してパラメータの制限を取得し、それに応じてスライダーを設定します。

    Args:

    Returns:
    - Tuple[int, float, float, float, float]: max_tokens, temperature, top_p, frequency_penalty,
      presence_penaltyのスライダーの値を含むタプル。
    """
    # セクション1: モデル選択とクリアボタン
    st.sidebar.header("Model Selection")  # セクションのヘッダー
    # モデルの選択
    model_key: str = st.sidebar.radio("Select a model:", list(MODELS.keys()))  # type: ignore
    logger.info(f"User has switched to model {model_key}")
    # 会話履歴削除ボタンの追加
    clear_conversations()
    draw_sidebar_divider()  # セクションの区切り線

    # 会話履歴ダウンロードボタンの追加
    add_download_button_to_sidebar(st.session_state.messages)
    draw_sidebar_divider()

    # コスト表示ボタンの追加
    display_total_costs()
    draw_sidebar_divider()  # セクションの区切り線

    # セクション2: モデルパラメータ
    st.sidebar.header("Model Parameters")
    model_parameter = MODELS[model_key]["parameter"]

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
        max_value=model_parameter["max_temperature"],
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

    return model_key, max_tokens, temperature, top_p, frequency_penalty, presence_penalty
