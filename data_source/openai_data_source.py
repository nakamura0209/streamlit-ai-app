from enum import Enum, auto
import os
from typing import Any, Dict, Final
from dotenv import load_dotenv
from openai import ChatCompletion

load_dotenv()


MODELS: Dict[str, Dict[str, Any]] = {
    "gpt-3.5-turbo": {
        "parameter": {
            "name": "gpt-3.5-turbo",
            "max_temperature": 2.0,
            "max_tokens": 4096,
            "max_prompt_tokens": 3096,
            "max_response_tokens": 1000,
            "max_top_k": 10,
            "max_top_p": 1.0,
            "max_frequency_penalty": 1.0,
            "max_presence_penalty": 1.0,
        },
        "config": {
            "api_key": os.getenv("GPT_3_5_TURBO_API_KEY"),
            "base_url": os.getenv("GPT_3_5_TURBO_BASE_URL"),
            "api_version": os.getenv("GPT_3_5_TURBO_API_VERSION"),
            "api_type": os.getenv("GPT_3_5_TURBO_API_TYPE"),
            "deployment_name": os.getenv("GPT_3_5_TURBO_API_DEPLOYMENT_NAME"),
            "model_version": os.getenv("GPT_3_5_TURBO_API_MODEL_VERSION"),
            "prompt_cost": os.getenv("GPT_3_5_PROMPT_COST"),
            "completion_cost": os.getenv("GPT_3_5_COMPLETION_COST"),
        },
    },
    "gpt-4": {
        "parameter": {
            "name": "gpt-4",
            "max_temperature": 2.0,
            "max_tokens": 4096,
            "max_prompt_tokens": 6196,
            "max_response_tokens": 2000,
            "max_top_k": 20,
            "max_top_p": 1.0,
            "max_frequency_penalty": 1.0,
            "max_presence_penalty": 1.0,
        },
        "config": {
            "api_key": os.getenv("GPT_4_API_KEY"),
            "base_url": os.getenv("GPT_4_BASE_URL"),
            "api_version": os.getenv("GPT_4_API_VERSION"),
            "api_type": os.getenv("GPT_4_API_TYPE"),
            "deployment_name": os.getenv("GPT_4_API_DEPLOYMENT_NAME"),
            "model_version": os.getenv("GPT_4_API_MODEL_VERSION"),
            "prompt_cost": os.getenv("GPT_4_PROMPT_COST"),
            "completion_cost": os.getenv("GPT_4_COMPLETION_COST"),
        },
    },
}


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class BasePage(Enum):
    CHAT = "Chat"
    PDF_QA = "PDF_QA"


class PDFOperateOptions(Enum):
    UPLOAD = "PDF Upload"
    QUESTION = "Ask My PDF(s)"
