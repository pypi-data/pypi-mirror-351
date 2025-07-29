"""
CRUD Operations for async session
"""
from typing import Any, Union

from sqlalchemy import select, update, delete
from sqlalchemy.inspection import inspect

from alchemylite.exceptions import BaseNotProvidedError, IncorrectConfig
from alchemylite.async_ import AsyncPostgresConfig, AsyncSqliteConfig 
from alchemylite import BaseConfig, BaseSQLiteConfig

class AsyncCrud:
    """
    Class, which implements CRUD operations for async session
    """
    def __init__(self, config: Union[AsyncPostgresConfig, AsyncSqliteConfig],
                  model, base=None) -> None:
        if not any((isinstance(config, BaseConfig), isinstance(config, BaseSQLiteConfig))):
            raise IncorrectConfig
        self.async_session_factory = config.session
        self.model = model
        self.base = base  # Base class of model

    def __validate_params(self, params: dict[str, Any]) -> None:
        """
        Validate parameters for CRUD operation
        :param params: A dictionary with parameters for CRUD operation
        :return: True, if parameters are valid, else ValueError
        """
        model_columns = {column.name: column.type for column in inspect(self.model).columns}
        for key, _ in params.items():
            if key not in model_columns:
                raise ValueError(f'Parameter {key} is not a valid column name')

    async def create(self, **kwargs) -> None:
        """
        Create operation
        :param params: A dict with parameters and values
        :return: None
        """
        self.__validate_params(kwargs)
        async with self.async_session_factory() as session:
            model = self.model(**kwargs)
            session.add(model)
            await session.commit()

    async def read_all(self) -> list[dict]:
        """
        Read operation
        :return: List[dict]
        """
        async with self.async_session_factory() as session:
            query = select(self.model)
            result = await session.execute(query)
            result = result.scalars().all()
            return [{column: getattr(row, column) for column in row.__table__.columns.keys()} for
                    row in result]

    async def limited_read(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """
        Read operation with limit and offset
        :param limit: limit
        :param offset: offset
        :return: list[dict]
        """
        async with self.async_session_factory() as session:
            query = select(self.model).limit(limit).offset(offset)
            result = await session.execute(query)
            result = result.scalars().all()
            return [{column: getattr(row, column) for column in row.__table__.columns.keys()} for
                    row in result]

    async def read_by_id(self, id: int) -> list[dict]:
        async with self.async_session_factory() as session:
            query = select(self.model).where(self.model.id == id)
            result = await session.execute(query)
            result = result.scalars().all()
            return [{column: getattr(row, column) for column in row.__table__.columns.keys()} for
                    row in result]

    async def update_by_id(self, **kwargs) -> None:
        """
        Update operation
        :param condition: A dict with condition
        :param params: Params for update
        :return: None
        """
        self.__validate_params(kwargs)
        if 'id' not in kwargs:
            raise ValueError(f'Parameter "id" is missing')
        id = kwargs['id']
        if type(id) is not int:
            raise ValueError(f'Parameter "id" must be an integer')
        async with self.async_session_factory() as session:
            stmt = update(self.model).where(self.model.id == id).values(kwargs)
            await session.execute(stmt)
            await session.commit()

    async def delete_by_id(self, **kwargs) -> None:
        """
        Delete operation
        :param condition: A dict with condition
        :return: None
        """
        if 'id' not in kwargs:
            raise ValueError(f'Parameter "id" is missing')
        id = kwargs['id']
        if type(id) is not int:
            raise ValueError(f'Parameter "id" must be an integer')
        async with self.async_session_factory() as session:
            stmt = delete(self.model).where(self.model.id == id)
            await session.execute(stmt)
            await session.commit()

    async def delete_table(self) -> None:
        if self.base is None:
            raise BaseNotProvidedError
        async with self.async_session_factory() as session:
            engine = session.bind
            async with engine.begin() as conn:
                await conn.run_sync(self.base.metadata.drop_all)

    async def create_table(self) -> None:
        if self.base is None:
            raise BaseNotProvidedError
        async with self.async_session_factory() as session:
            engine = session.bind
            async with engine.begin() as conn:
                await conn.run_sync(self.base.metadata.create_all)
