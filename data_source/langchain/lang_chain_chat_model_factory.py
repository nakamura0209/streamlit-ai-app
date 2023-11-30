import os
from langchain.chat_models import AzureChatOpenAI


class ModelParameters:
    def __init__(
        self,
        max_tokens: int,
        temperature: float,
        top_p: float,
        frequency_penalty: float,
        presence_penalty: float,
        deployment_name: str,
    ) -> None:
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.deployment_name = deployment_name
        pass


class LangchainChatModelFactory:
    @staticmethod
    def create_instance():
        return AzureChatOpenAI(
            openai_api_base=os.environ.get("OPENAI_BASE_URL", ""),  # type: ignore //pylance誤検知のため
            # openai_api_version=os.environ.get("OPENAI_API_VERSION", ""),  # type: ignore //pylance誤検知のため
            openai_api_version="2023-07-01-preview",  # type: ignore //pylance誤検知のため
            deployment_name=os.environ.get("OPENAI_API_DEPLOYMENT_NAME", ""),  # type: ignore //pylance誤検知のため
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),  # type: ignore //pylance誤検知のため
            openai_api_type=os.environ.get("OPENAI_API_TYPE", ""),
            model_version=os.environ.get("OPENAI_API_MODEL_VERSION", ""),
            # tiktoken_model_name=os.environ.get("AZURE_OPENAI_TIKTOKEN_MODEL_NAME", "", ""),
            temperature=0,
        )
