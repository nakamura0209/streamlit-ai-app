import os
from logging import Logger, getLogger
from logging.config import dictConfig
from typing import Any, Dict
from datetime import datetime

from dotenv import load_dotenv
from logs.AzureBlobHandler import AzureBlobHandler

# 環境変数をロードする
load_dotenv()


# ログ設定を関数で生成する
def create_logging_config() -> Dict[str, Any]:
    """ログ設定を生成する関数"""
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={os.getenv('STORAGE_ACCOUNT_NAME')};"
        f"AccountKey={os.getenv('STORAGE_ACCESS_KEY')};"
        f"EndpointSuffix=core.windows.net"
    )
    container_name = os.getenv("CONTAINER_NAME")
    blob_name = f"logs/{os.getenv('BLOB_NAME')}"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s"
            }
        },
        "handlers": {
            "consoleHandler": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "azureBlobHandler": {
                "()": AzureBlobHandler,
                "level": "INFO",
                "formatter": "simple",
                "connection_string": connection_string,
                "container_name": container_name,
                "blob_name": blob_name,
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
    """指定されたモジュール名のロガーを設定して返す"""
    dictConfig(create_logging_config())
    return getLogger(module_name)
