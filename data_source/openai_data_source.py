from enum import Enum
import os
from langchain.schema import SystemMessage, HumanMessage, AIMessage


MODELS = {
    "gpt-3.5-turbo": {
        "parameter": {
            "name": "gpt-3.5-turbo",
            "max_tokens": 4096,
            "max_prompt_tokens": 3096,
            "max_response_tokens": 1000,
            "top_k": 10,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        },
        "config": {
            "api_key": os.getenv("GPT_3_5_TURBO_API_KEY"),
            "base_url": os.getenv("GPT_3_5_TURBO_BASE_URL"),
            "api_version": os.getenv("GPT_3_5_TURBO_API_VERSION"),
            "api_type": os.getenv("GPT_3_5_TURBO_API_TYPE"),
            "deployment_name": os.getenv("GPT_3_5_TURBO_API_DEPLOYMENT_NAME"),
            "model_version": os.getenv("GPT_3_5_TURBO_API_MODEL_VERSION"),
        },
    },
    "gpt-4": {
        "parameter": {
            "name": "gpt-4",
            "max_tokens": 8192,
            "max_prompt_tokens": 6196,
            "max_response_tokens": 2000,
            "top_k": 20,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        },
        "config": {
            "api_key": os.getenv("GPT_4_API_KEY"),
            "base_url": os.getenv("GPT_4_BASE_URL"),
            "api_version": os.getenv("GPT_4_API_VERSION"),
            "api_type": os.getenv("GPT_4_API_TYPE"),
            "deployment_name": os.getenv("GPT_4_API_DEPLOYMENT_NAME"),
            "model_version": os.getenv("GPT_4_API_MODEL_VERSION"),
        },
    },
}


class Role(Enum):
    UESR = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
