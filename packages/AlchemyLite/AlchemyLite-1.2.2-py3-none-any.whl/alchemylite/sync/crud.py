"""
CRUD Operations for sync session
"""
from typing import Any, Union

from sqlalchemy import select, update, delete
from sqlalchemy.inspection import inspect

from alchemylite.exceptions import BaseNotProvidedError, IncorrectConfig
from alchemylite.sync import SyncPostgresConfig, SyncSqliteConfig
from alchemylite import BaseConfig, BaseSQLiteConfig

class SyncCrud:
    """
    Class, which implements CRUD operations for sync session
    """
    def __init__(self, config: Union[SyncPostgresConfig, SyncSqliteConfig], 
                 model, base=None) -> None:
        if not any((isinstance(config, BaseConfig), isinstance(config, BaseSQLiteConfig))):
            raise IncorrectConfig
        self.session_factory = config.session
        self.model = model
        self.base = base  # base class of model

    def __validate_params(self, params: dict[str, Any]) -> None:
        """
        Validate parameters for CRUD operation
        :param params: A dictionary with parameters for CRUD operation
        :return: True, if parameters are valid, else ValueError
        """
        model_columns = {column.name: column.type for column in inspect(self.model).columns}
        for key, value in params.items():
            if key not in model_columns:
                raise ValueError(f'Parameter {key} is not a valid column name')

    def create(self, **kwargs) -> None:
        """
        Create operation
        :param params: A dict with parameters and values
        :return: None
        """
        self.__validate_params(kwargs)
        with self.session_factory() as session:
            model = self.model(**kwargs)
            session.add(model)
            session.commit()

    def read_all(self) -> list[dict]:
        """
        Read operation
        :return: List[dict]
        """
        with self.session_factory() as session:
            query = select(self.model)
            result = session.execute(query).scalars().all()
            return [{column: getattr(row, column) for column in row.__table__.columns.keys()} for
                    row in result]

    def read_by_id(self, id: int) -> list[dict]:
        with self.session_factory() as session:
            query = select(self.model).where(self.model.id == id)
            result = session.execute(query).scalars().all()
            return [{column: getattr(row, column) for column in row.__table__.columns.keys()} for
                    row in result]

    def limited_read(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """
        Read operation with limit and offset
        :param limit: limit
        :param offset: offset
        :return: list[dict]
        """
        with self.session_factory() as session:
            query = select(self.model).limit(limit).offset(offset)
            result = session.execute(query).scalars().all()
            return [{column: getattr(row, column) for column in row.__table__.columns.keys()} for
                    row in result]

    def update_by_id(self, **kwargs) -> None:
        """
        Update operation
        :param condition: A dict with condition
        :param params: Params for update
        :return: None
        """
        self.__validate_params(kwargs)
        if 'id' not in kwargs:
            raise ValueError('Parameter "id" is missing')
        id = kwargs['id']
        if type(id) is not int:
            raise ValueError('Parameter "id" must be an integer')

        with self.session_factory() as session:
            stmt = update(self.model).where(self.model.id == id).values(kwargs)
            session.execute(stmt)
            session.commit()

    def delete_by_id(self, **kwargs) -> None:
        """
        Delete operation
        :param condition: A dict with condition
        :return: None
        """
        if 'id' not in kwargs:
            raise ValueError('Parameter "id" is missing')
        id = kwargs['id']
        if type(id) is not int:
            raise ValueError('Parameter "id" must be an integer')

        with self.session_factory() as session:
            stmt = delete(self.model).where(self.model.id == id)
            session.execute(stmt)
            session.commit()

    def create_table(self) -> None:
        if self.base is None:
            raise BaseNotProvidedError
        with self.session_factory() as session:
            self.base.metadata.create_all(bind=session.get_bind())

    def delete_table(self) -> None:
        if self.base is None:
            raise BaseNotProvidedError
        with self.session_factory() as session:
            self.base.metadata.drop_all(bind=session.get_bind())
