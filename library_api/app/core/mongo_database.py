import logging
from pymongo import MongoClient
from pymongo.database import Database
from .config import settings

logger = logging.getLogger(__name__)

class MongoDBClient():
    # khoi tao cac thuoc tinh mac dinh
    def __init__(self):
        self.client: MongoClient | None = None
        self._database: Database | None = None

    # ket noi
    def connect(self):
        if self.client is None:
            self.client = MongoClient(settings.MONGO_CONNECTION_STRING)
            self._database = self.client[settings.MONGO_DB_NAME]
            logger.info("Ket noi toi MongoDB thanh cong")

    # dong ket noi
    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self._database = None
            logger.info("Da dong ket noi voi MongoDB")

    def get_database(self) -> Database:
        if self._database is None:
            raise Exception("Chua ket noi toi MongoDB")
        return self._database

mongodb_client = MongoDBClient()