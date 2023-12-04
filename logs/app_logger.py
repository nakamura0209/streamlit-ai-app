# loggingモジュールから必要なクラスや関数をインポートしています。
from logging import getLogger
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Dict

# ログファイルのパスを定義しています。
LOG_FILE_PATH = "streamlit_ai_app.log"

# ログ設定を辞書形式で定義しています。
logging_config: Dict[str, Any] = {
    "version": 1,  # 設定のバージョンを指定しています。
    "disable_existing_loggers": False,  # 既存のロガーを無効にしないように設定しています。
    "formatters": {
        # ログのフォーマットを定義しています。
        "simple": {"format": "%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s"}
    },
    "handlers": {
        # コンソール出力用のハンドラーを設定しています。
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        # ファイル出力用のハンドラーを設定しています。
        "fileHandler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": LOG_FILE_PATH,
            "when": "D",
            "interval": 1,
            "backupCount": 5,
        },
    },
    "loggers": {
        # メインモジュールのロガー設定をしています。
        "__main__": {
            "level": "INFO",
            "handlers": ["consoleHandler", "fileHandler"],
            "propagate": False,
        },
        # 同じ階層のモジュールのロガー設定をしています。
        "same_hierarchy": {
            "level": "INFO",
            "handlers": ["consoleHandler", "fileHandler"],
            "propagate": False,
        },
        # 下位階層のモジュールのロガー設定をしています。
        "lower.sub": {
            "level": "DEBUG",
            "handlers": ["consoleHandler", "fileHandler"],
            "propagate": False,
        },
    },
    "root": {"level": "INFO"},  # ルートロガーのレベルを設定しています。
}

# 辞書形式の設定を適用しています。
dictConfig(logging_config)

# 現在のモジュールのロガーを取得しています。
logger = getLogger(__name__)
