from typing import Any, Dict, Type

from sqlalchemy import (Integer, String, Boolean,
                        Float, Column, Date,
                        DateTime, Time, Text,
                        ForeignKey)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Table:
    """
    A factory class for dynamically creating SQLAlchemy models.

    This class allows you to dynamically generate SQLAlchemy models based on the provided
    table name and field specifications. The fields should specify the column name, data type, and
    other column options such as 'nullable', 'default', 'unique', and 'index'.
    """
    _TYPE_MAP = {
        int: Integer,
        str: String,
        bool: Boolean,
        float: Float,
        "date": Date,
        "datetime": DateTime,
        "time": Time,
        "text": Text
    }
    def __init__(self, table_name: str, fields: Dict[str, Dict[str, Any]]) -> None:
        """
        Initializes a model factory for creating SQLAlchemy models dynamically.

        :param name: Name of the table.
        :param fields: A dictionary where the key is the column name, and the value is a dictionary of
                       column options, including 'type' (data type), 'null' (nullable),
                       'default', 'unique', and 'index'.
        """
        self.table_name = table_name
        self.fields = fields

    @property
    def model(self) -> Type[Base]:
        """
        Generates and returns a dynamic SQLAlchemy model class.

        :return: Generated SQLAlchemy model class.
        """
        attrs = {
            '__tablename__': self.table_name,
            'id': Column(Integer, primary_key=True),
            'base': Base
        }

        for field_name, field_options in self.fields.items():
            # Get field type from options; raise an error if unsupported
            field_type = field_options.get("type")
            column_type = self._TYPE_MAP.get(field_type)
            string_length = field_options.get('max_len', None)
            if field_type is str and string_length is not None:
                if type(string_length) is not int:
                    raise ValueError("'max_len' must be an integer.")
                if string_length <= 0:
                    raise ValueError("String length must be greater than 0")
                column_type = column_type(string_length)

            if not column_type:
                raise ValueError(f"Unsupported field type: {field_type}")

            # Extract other options with default settings
            nullable = field_options.get('null', True)
            default = field_options.get('default', None)
            unique = field_options.get('unique', False)
            index = field_options.get('index', False)

            # Foreign Key processing
            if field_type is int:
                foreign_key = field_options.get('foreign_key', None)
                if foreign_key is not None:
                    column_type = [column_type, ForeignKey(foreign_key)]
                else:
                    column_type = [column_type]
            else:
                column_type = [column_type]
            # Create column with specified options
            attrs[field_name] = Column(*column_type,
                                       nullable=nullable,
                                       default=default,
                                       unique=unique,
                                       index=index)

        # Dynamically create the model class
        model_class = type(self.table_name, (Base,), attrs)
        return model_class
