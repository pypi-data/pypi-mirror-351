"""
Configuration for sync session
"""
import os 

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alchemylite import BaseConfig, BaseSQLiteConfig
from alchemylite.exceptions import SQLiteDbDoesNotExists

class SyncPostgresConfig(BaseConfig):
    """
    Class for configuring PostgreSQL sync sessions
    """
    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+psycopg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def session(self) -> sessionmaker:
        sync_engine = create_engine(
            url=self.DATABASE_URL,
            echo=False
        )
        session_factory = sessionmaker(sync_engine)
        return session_factory


# class SyncMySqlConfig(BaseConfig):
#     """
#     Class for configuring MySQL sync sessions
#     """

#     @property
#     def DATABASE_URL(self) -> str:
#         return f'mysql+pymysql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}'
    

#     @property
#     def session(self) -> sessionmaker:
#         sync_engine = create_engine(
#             url=self.DATABASE_URL,
#             echo=False
#         )
#         session_factory = sessionmaker(sync_engine)
#         return session_factory


class SyncSqliteConfig(BaseSQLiteConfig):
    """
    Class for configuring SQLite sync sessions
    """
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
    
    @property
    def DATABASE_URL(self) -> str:
        return f'sqlite:///{self._db_path}'
    
    @property
    def session(self) -> sessionmaker:
        if not os.path.exists(self._db_path):
            raise SQLiteDbDoesNotExists
        sync_engine = create_engine(
            url=self.DATABASE_URL,
            echo=False
        )
        session_factory = sessionmaker(sync_engine)
        return session_factory
