from logging import Handler
from azure.storage.blob import BlobServiceClient, BlobClient
import datetime


class AzureBlobHandler(Handler):
    def __init__(self, connection_string, container_name, blob_name):
        super().__init__()
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name
        self.blob_name = blob_name

    def emit(self, record):
        # ログメッセージをフォーマットします。
        message = self.format(record)
        # 現在の日付を取得します。
        date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        # Blob名に日付を追加します。
        blob_name_with_date = f"{self.blob_name}-{date}.log"
        # Blobクライアントを取得します。
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_name_with_date
        )
        # Blobにログメッセージを追記します。
        blob_client.upload_blob(message + "\n", blob_type="AppendBlob", overwrite=False)
