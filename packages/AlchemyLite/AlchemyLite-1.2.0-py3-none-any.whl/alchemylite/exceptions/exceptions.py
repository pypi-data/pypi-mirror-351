class BaseNotProvidedError(Exception):
    """The exception that is thrown if base was not provided."""
    def __init__(self):
        self.message = 'Base is required but was not provided.'
        super().__init__(self.message)


class IncorrectConfig(Exception):
    """Exception thrown when specifying invalid config instance in AsyncCrudOperation/SyncCrudOperation"""
    def __init__(self):
        self.message = 'The passed config must be an instance of the config class.'
        super().__init__(self.message)


class SQLiteDbDoesNotExists(Exception):
    """Exception thrown when specified sqlite url does not exists"""
    def __init__(self):
        self.message = 'The specified sqlite database path does not exist.'
        super().__init__(self.message)
