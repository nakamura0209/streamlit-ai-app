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
            openai_api_base="https://openai-test-gpt4-20231118.openai.azure.com/",  # type: ignore //pylance誤検知のため
            openai_api_version="2023-07-01-preview",  # type: ignore //pylance誤検知のため
            deployment_name="openai-test-gpt4",  # type: ignore //pylance誤検知のため
            openai_api_key="547aae27000d4df79923b93736993d8a",  # type: ignore //pylance誤検知のため
            openai_api_type="azure",
            model_version="gpt-4",
            # tiktoken_model_name=os.environ.get("AZURE_OPENAI_TIKTOKEN_MODEL_NAME", ""),
            temperature=0,
        )
