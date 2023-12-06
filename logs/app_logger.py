import os
from logging import Logger, getLogger
from logging.config import dictConfig
from typing import Any, Dict

from dotenv import load_dotenv
from logs.AzureBlobHandler import AzureBlobHandler
from opencensus.ext.azure.log_exporter import AzureLogHandler

# 環境変数をロードする
load_dotenv()


# ログ設定を関数で生成する
def create_logging_config() -> Dict[str, Any]:
    """ログ設定を生成する関数"""
    # Azure Blob
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={os.getenv('STORAGE_ACCOUNT_NAME')};"
        f"AccountKey={os.getenv('STORAGE_ACCESS_KEY')};"
        f"EndpointSuffix=core.windows.net"
    )
    container_name = os.getenv("CONTAINER_NAME")
    blob_name = f"logs/{os.getenv('BLOB_NAME')}"

    # Application Insights
    instrumentation_key = os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY")

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
                "()": AzureBlobHandler,  # 使用していないが、今後Blobのコンテナにログ出力する場合のために保持
                "level": "INFO",
                "formatter": "simple",
                "connection_string": connection_string,
                "container_name": container_name,
                "blob_name": blob_name,
            },
            "azureApplicationInsightsHandler": {
                "()": AzureLogHandler,
                "level": "INFO",
                "formatter": "simple",
                "instrumentation_key": instrumentation_key,
            },
        },
        "loggers": {
            "__main__": {
                "level": "INFO",
                "handlers": ["consoleHandler", "azureApplicationInsightsHandler"],
                "propagate": False,
            },
            "same_hierarchy": {
                "level": "INFO",
                "handlers": ["consoleHandler", "azureApplicationInsightsHandler"],
                "propagate": False,
            },
            "lower.sub": {
                "level": "DEBUG",
                "handlers": ["consoleHandler", "azureApplicationInsightsHandler"],
                "propagate": False,
            },
        },
        "root": {"level": "INFO"},
    }


def set_logging(module_name: str) -> Logger:
    """指定されたモジュール名のロガーを設定して返す"""
    dictConfig(create_logging_config())
    return getLogger(module_name)
