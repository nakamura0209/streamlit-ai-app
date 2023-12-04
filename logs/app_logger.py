# loggingモジュールから必要なクラスや関数をインポートしています。
from logging import Logger, getLogger
from logging.config import dictConfig
import os
from typing import Any, Dict

from dotenv import load_dotenv

from logs.AzureBlobHandler import AzureBlobHandler

load_dotenv()

# ログ設定を辞書形式で定義しています。
logging_config: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s"}
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        # Azure Blob Storageへの出力用ハンドラーを設定します。
        "azureBlobHandler": {
            "()": AzureBlobHandler,
            "level": "INFO",
            "formatter": "simple",
            "connection_string": f"DefaultEndpointsProtocol=https;AccountName={os.getenv('STORAGE_ACCOUNT_NAME')};AccountKey={os.getenv('STORAGE_ACCESS_KEY')};EndpointSuffix=core.windows.net",
            "container_name": os.getenv("CONTAINER_NAME"),
            "blob_name": os.getenv("CONTAINER_NAME"),
        },
    },
    "loggers": {
        "__main__": {
            "level": "INFO",
            "handlers": ["consoleHandler", "azureBlobHandler"],
            "propagate": False,
        },
        "same_hierarchy": {
            "level": "INFO",
            "handlers": ["consoleHandler", "azureBlobHandler"],
            "propagate": False,
        },
        "lower.sub": {
            "level": "DEBUG",
            "handlers": ["consoleHandler", "azureBlobHandler"],
            "propagate": False,
        },
    },
    "root": {"level": "INFO"},
}


def set_logging(module_name: str) -> Logger:
    dictConfig(logging_config)
    return getLogger(module_name)
