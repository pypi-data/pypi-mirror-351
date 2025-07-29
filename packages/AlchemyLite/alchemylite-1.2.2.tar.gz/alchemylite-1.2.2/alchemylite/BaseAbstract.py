from abc import ABC, abstractmethod

class BaseConfig(ABC):
    """
    Abstract base class for database configuration.

    This class provides the basic structure for configuring database connection
    parameters, such as host, port, user, password, and database name. Concrete
    implementations of this class should define the `DATABASE_URL` property and
    the `session` property to establish and manage the database connection.
    """
    def __init__(self, db_host: str, db_port: str, db_user: str, db_pass: str,
                 db_name: str) -> None:
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name

    @property
    @abstractmethod
    def DATABASE_URL(self) -> str:
        pass

    @property
    @abstractmethod
    def session(self):
        pass


class BaseSQLiteConfig(ABC):
    """Abstract base class for SQLite configuration."""
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    @property
    @abstractmethod
    def DATABASE_URL(self) -> str:
        pass

    @property
    @abstractmethod
    def session(self):
        pass
