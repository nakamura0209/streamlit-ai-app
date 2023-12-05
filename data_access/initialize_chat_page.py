# サイドバーを初期化して、モデルのパラメータを設定する関数
from logging import Logger
from typing import Any, Dict, Tuple, Union
import openai

import streamlit as st
from data_source.langchain.lang_chain_chat_model_factory import ModelParameters
from data_source.openai_data_source import MODELS
from logs.app_logger import set_logging
from logs.log_decorator import log_decorator


logger: Logger = set_logging("lower.sub")


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
    model_key: Union[str, Any] = st.sidebar.radio("Select a model:", list(MODELS.keys()))
    # 会話履歴削除ボタンの追加
    initialize_message_state()
    st.sidebar.markdown("---")  # セクションの区切り線

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
    llm = ModelParameters(
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        deployment_name=model_config["deployment_name"],
    )

    st.info(f"{model_key} is selected")

    return llm


# チャットメッセージのセッションステートを初期化する関数
@log_decorator(logger)
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
