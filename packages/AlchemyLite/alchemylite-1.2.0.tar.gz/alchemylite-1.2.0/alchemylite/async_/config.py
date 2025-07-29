"""
Configuration for async session
"""
import os 

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from alchemylite import BaseConfig, BaseSQLiteConfig
from alchemylite.exceptions import SQLiteDbDoesNotExists

class AsyncPostgresConfig(BaseConfig):
    """
    Class for configuring PostgreSQL async sessions
    """
    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def session(self) -> async_sessionmaker:
        async_engine = create_async_engine(
            url=self.DATABASE_URL,
        )
        async_session = async_sessionmaker(
            async_engine,
            expire_on_commit=False,
        )
        return async_session


# class AsyncMySqlConfig(BaseConfig):
#     """
#     Class for configuring MySQL async sessions
#     """

#     @property
#     def DATABASE_URL(self) -> str:
#         return f'mysql+aiomysql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}'


#     @property
#     def session(self) -> async_sessionmaker:
#         async_engine = create_async_engine(
#             url=self.DATABASE_URL,
#         )
#         async_session = async_sessionmaker(
#             async_engine,
#             expire_on_commit=False,
#         )
#         return async_session


class AsyncSqliteConfig(BaseSQLiteConfig):
    """
    Class for configuring SQLite async sessions
    """
    @property
    def DATABASE_URL(self) -> str:
        return f'sqlite+aiosqlite:///{self._db_path}'

    @property
    def session(self) -> async_sessionmaker:
        if not os.path.exists(self._db_path):
            raise SQLiteDbDoesNotExists
        async_engine = create_async_engine(
            url=self.DATABASE_URL,
        )
        async_session = async_sessionmaker(
            async_engine,
            expire_on_commit=False,
        )
        return async_session     
