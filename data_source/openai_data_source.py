from enum import Enum
import os
from langchain.schema import SystemMessage, HumanMessage, AIMessage


MODELS = {
    "gpt-3.5-turbo": {
        "name": "gpt-3.5-turbo",
        "max_tokens": 4096,
        "max_prompt_tokens": 3096,
        "max_response_tokens": 1000,
        "top_k": 10,
        "deployment_name": os.getenv("GPT3_5_TURBO_MODEL_DEPLOYMENT_NAME"),
    },
    "gpt-3.5-turbo-16k": {
        "name": "gpt-3.5-turbo-16k",
        "max_tokens": 16384,
        "max_prompt_tokens": 15384,
        "max_response_tokens": 1000,
        "top_k": 40,
        "deployment_name": os.getenv("GPT3_5_TURBO_16K_MODEL_DEPLOYMENT_NAME"),
    },
    "gpt-4": {
        "name": "gpt-4",
        "max_tokens": 8192,
        "max_prompt_tokens": 6196,
        "max_response_tokens": 2000,
        "top_k": 20,
        "deployment_name": os.getenv("GPT4_MODEL_DEPLOYMENT_NAME"),
    },
}


class Role(Enum):
    UESR = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
