import psycopg2
from psycopg2 import sql
from config import Config
import logging

logger = logging.getLogger(__name__)

class PgSqlManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
            cls._instance.cursor = None
        return cls._instance

    def connect(self, config: Config) -> bool:
        try:
            self.connection = psycopg2.connect(config.pgsql_connection)
            self.cursor = self.connection.cursor()
            logger.info("PostgreSQL connection established successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
        return False

    def disconnect(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("PostgreSQL connection closed.")

    def execute_query(self, query: str, params: tuple = ()) -> None:
        if not self.connection:
            logger.error("Not connected to the database.")
            return
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            logger.info("Query executed successfully.")
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
