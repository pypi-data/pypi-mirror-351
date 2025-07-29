# AlchemyLite
## A library that simplifies CRUD operations with PostgreSQL database.

# What is new in 1.2.0 release?
[Full docs](https://alchemylite.readthedocs.io/)
1.This release adds support for SQLite database  
```python
from alchemylite.sync import SyncCrud, SyncSqliteConfig

config = SyncSqliteConfig(db_path=ABSOLUTE_DB_PATH)
crud = SyncCrud(config, model, model.base)     
```
2. Changing method names
The names of some methods have been changed
* AsyncCrudOperation -> AsyncCrud
* SyncCrudOperation -> SyncCrud
* delete_all_tables -> delete_table
* create_all_tables -> create_table
3. Configuration classes are divided by database type  
  Asynchronous approach:  
  * from alchemylite.async_ import AsyncPostgresConfig (for postgresql)  
  * from alchemylite.async_ import AsyncSqliteConfig (for sqlite)  
  Synchronous approach:  
  * from alchemylite.sync import SyncPostgresConfig (for postgresql)  
  * from alchemylite.sync import SyncSqliteConfig (for sqlite)  
# How to use it?
First, install the library with the command ```pip install AlchemyLite```  
First you need to create a configuration in which you need to register the database parameters  
For synchronous operation
```python
from alchemylite.sync impoty SyncPostgresConfig

config = SyncConfig(
    db_host="your_host",
    db_port="your_port",
    db_user="your_user",
    db_pass="your_password",
    db_name="your_db_name"
)
```
Then, we create a class to which we pass our configuration, model class and base class of model
```python
from alchemylite.sync import SyncCrud

crud = SyncCrud(
    config, YourModel, Base
)
```
For async operation
```python
from alchemylite.async_ import AsyncPostgresConfig, AsyncCrud

config = AsyncPostgresConfig(
    db_host="your_host",
    db_port="your_port",
    db_user="your_user",
    db_pass="your_password",
    db_name="your_db_name"
)

crud = AsyncCrud(
    config, YourModel, Base
)
```
# How to perform CRUD operations?
The library supports the following methods
* create - Creates new data in the table.
* read_all - Reads all data from a table.
* limited_read - Reads a certain amount of data. Default values: limit = 50, offset = 0
* read_by_id - Reads all data from a table by id
* update_by_id - Update data by id
* delete_by_id - Delete data by id
* create_all_tables - Creates all tables in database
* delete_all_tables - Delete all tables in database

# Examples of use

```python
from alchemylite.sync import SyncCrud, SyncPostgresConfig 
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


config = SyncPostgresConfig(
    db_host="localhost",
    db_port="5432",
    db_user="postgres",
    db_pass="postgres",
    db_name="alchemylite"
)


class Base(DeclarativeBase):
    pass
    
    
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
   

crud = SyncCrud(
    config, User, Base
)

crud.create_all_tables()
crud.create(name="User", email="email@mail.ru")
print(crud.read_all())
print(crud.limited_read(limit=5, offset=0))
print(crud.read_by_id(id=1))
crud.update_by_id(id=1, name="new value", email="new_emal")
crud.delete_by_id(id=1)
crud.delete_all_tables()
```
## The library will be supported, this is the first version for now. New features will be added in the future.
### If you have suggestions for improvements or any comments, I'm ready to listen to you
