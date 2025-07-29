from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, tzinfo
from functools import cached_property
from typing import (Any, Generic, Iterator, Literal, Mapping, Self, Sequence,
                    TypeVar)

from ..utils import (DelayedStr, ExtendedJSONEncoder, Secret, get_logger,
                     is_secret_defined, parse_timezone)

T_Connection = TypeVar('T_Connection', covariant=True)


class Db(Generic[T_Connection]):
    tz: tzinfo|Literal['localtime','UTC']|str|None
    slug: str|None
    name: str|None
    host: str|None
    port: int|str|None
    user: str|None
    password: str|DelayedStr|None
    encrypt: bool|str|None
    autocommit: bool|None
    

    #region Initialize instance and connect

    _temp_schema: str
    _accept_aware_datetimes: bool
    _identifier_quotechar_begin = '"'
    _identifier_quotechar_end = '"'

    def __init__(self,
                 connection: T_Connection|None = None, *,
                 tz: tzinfo|Literal['localtime','UTC']|str|None = None,
                 slug: str|None = None,
                 name: str|None = None,
                 host: str|None = None,
                 port: int|str|None = None,
                 user: str|None = None,
                 password: str|DelayedStr|None = None,
                 encrypt: bool|str|None = None,
                 autocommit: bool|None = None):
        """
        :param tz: If provided, naive datetimes coming from the database (e.g. in cursors through `to_python_value`) or going to the database (through `to_database_value`) are interpreted as aware datetimes in the given timezone.
        """
        self._logger = get_logger(self)

        self._connection = connection
        self._connection_is_external = True if connection else False

        # Datetimes configuration
        if tz is None:
            tz = getattr(self.__class__, 'tz', None)        
        self.tz = parse_timezone(tz) if tz is not None and not isinstance(tz, tzinfo) else tz


        # Parameters for create_connection
        self.slug = slug
        env_prefix = f'{self.slug.upper()}_' if self.slug else None
        
        if env_prefix and (value := os.environ.get(f'{env_prefix}NAME')):
            name = value   
        self.name = name
        
        if env_prefix and (value := os.environ.get(f'{env_prefix}HOST')):
            host = value
        self.host = host
        
        if env_prefix and (value := os.environ.get(f'{env_prefix}PORT')):
            port = value
        self.port = None if port == '' else int(port) if isinstance(port, str) else port
                
        if env_prefix and (value := os.environ.get(f'{env_prefix}USER')):
            user = value
        self.user = user
    
        self.password: str|DelayedStr|None
        if env_prefix and (value := os.environ.get(f'{env_prefix}PASSWORD')):
            self.password = value
        elif slug and is_secret_defined(f'{env_prefix}PASSWORD'):
            self.password = Secret(f'{env_prefix}PASSWORD')
        else:    
            self.password = password
        
        if env_prefix and (value := os.environ.get(f'{env_prefix}ENCRYPT')):
            encrypt = value  
        self.encrypt = None if encrypt is None else encrypt.lower() in {'1', 'yes', 'true', 'on'} if isinstance(encrypt, str) else encrypt

        self.autocommit = autocommit
    

    def __enter__(self):
        return self
    
    
    def __exit__(self, *exc_info):
        if self._connection_is_external and self._connection is not None:
            self._connection.close() # type: ignore (connection object not documented - would add unecessary complexity such as Protocol usage)
            self._connection = None


    @property
    def connection(self) -> T_Connection:
        if self._connection is None:
            if isinstance(self.password, Secret):
                self.password = self.password.value
            self._connection = self.create_connection()
        return self._connection
    

    def create_connection(self, autocommit: bool|None = None) -> T_Connection:
        raise NotImplementedError()


    def cursor(self) -> DbCursor:
        return self.connection.cursor() # type: ignore (connection object not documented - would add unecessary complexity such as Protocol usage)
    

    def get_database_name(self) -> str|None:
        """
        Return the name of the database currently associated with this connection.

        NOTE:
        - This can be distinct from :py:attribute:`name` attribute when a statement such as `USE` has been executed.
        - This can be None for mysql and mariadb.
        """
        raise NotImplementedError()
    

    def use_database(self, name: str) -> None:
        query = f"USE {self.escape_identifier(name)}"

        with self.cursor() as cursor:
            cursor.execute(query)


    #endregion


    #region Execute queries
    
    def execute(self, query: str, params: Sequence[Any]|Mapping[str,Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> int:
        raise NotImplementedError() #TODO


    def iter_rows(self, query: str, params: Sequence[Any]|Mapping[str,Any]|None = None, *, limit: int|None = None, offset: int|None = None) -> DbRowIterator:
        raise NotImplementedError() #TODO

    #endregion
        

    #region Escape and convert values

    @classmethod
    def escape_identifier(cls, value: str|type):
        if isinstance(value, type):
            value = value._meta.db_table
        elif not isinstance(value, str):
            raise TypeError(f"Invalid identifier: {value} ({type(value)})")
        return f"{cls._identifier_quotechar_begin}{value.replace(cls._identifier_quotechar_end, cls._identifier_quotechar_end+cls._identifier_quotechar_end)}{cls._identifier_quotechar_end}"


    @classmethod
    def escape_literal(cls, value) -> str:
        if value is None:
            return "null"
        elif isinstance(value, datetime):
            raise ValueError("Cannot use datetimes directly with `escape_literal`. Use `to_database_value` first to remove timezone ambiguity.")
        else:
            return f"'" + str(value).replace("'", "''") + "'"
        
    
    def to_python_value(self, value):
        if isinstance(value, datetime):
            if not value.tzinfo and self.tz:
                value = value.replace(tzinfo=self.tz) # type: ignore (`tz` parsed in the instance's `__init__`)
        return value


    def to_database_value(self, value, flatten = True):
        if isinstance(value, (list,tuple)):
            if flatten:
                return '|'.join(str(self.to_database_value(elem, flatten=False)).replace('\\', '\\\\').replace('|', '\\|') for elem in value)
            else:
                return json.dumps(value, ensure_ascii=False, cls=ExtendedJSONEncoder)
        elif isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False, cls=ExtendedJSONEncoder)
        elif isinstance(value, datetime):
            if value.tzinfo:
                if self._accept_aware_datetimes:
                    return value.isoformat()
                elif self.tz:
                    return value.astimezone(self.tz).replace(tzinfo=None).isoformat() # type: ignore (`tz` parsed in the instance's `__init__`)
                else:
                    raise ValueError(f"Input datetime may not be aware ('tz' not defined for {self.__class__.__name__} object and the database does not accept aware datetimes)")
            else:
                if self.tz:
                    return value.isoformat()
                else:
                    raise ValueError(f"Input datetime may not be naive ('tz' not defined for {self.__class__.__name__} object)")
        else:
            return value

    @classmethod
    def parse_dbobject(cls, input: str|tuple|type|DbObject, *, temp: bool|None = None):
        if isinstance(input, DbObject):
            if (temp and not input.is_temp) or (input.db != cls):
                name = input.name
                schema = input.schema
            else:
                return input
        elif isinstance(input, tuple):
            name = input[1]
            schema = input[0]
        elif isinstance(input, str):
            try:
                pos = input.index('.')
                name = input[pos+1:]
                schema = input[0:pos]
            except ValueError:
                name = input
                schema = None
        else:
            meta = getattr(input, '_meta', None) # Django model
            if meta:
                name: str = meta.db_table
                schema = None
            else:
                raise TypeError(f'input: {type(input).__name__}')
        
        if schema == '#': # sqlserver
            name = f'#{name}'
            schema = None
        elif temp:
            if cls._temp_schema == '#': # sqlserver
                name = f'#{name}'
                schema = None
            else:
                schema = cls._temp_schema
                
        return DbObject(name=name, schema=schema, db=cls)
    
    #endregion


    #region Data definition (DDL helpers)

    def database_exists(self, name: str) -> bool:
        raise NotImplementedError()


    def create_database(self, name: str, *, if_not_exists = False) -> None:
        query = f"CREATE DATABASE "
        if if_not_exists:
            query += "IF NOT EXISTS "
        query += self.escape_identifier(name)

        with self.cursor() as cursor:
            cursor.execute(query)


    def drop_database(self, name: str, *, if_exists = False) -> None:
        query = f"DROP DATABASE "
        if if_exists:
            query += "IF EXISTS "
        query += self.escape_identifier(name)

        with self.cursor() as cursor:
            cursor.execute(query)

    @classmethod
    def get_sql_type(cls, _type: type|None, key: bool|float = False):
        """
        :param key: indicate whether the column is part of a key (primary or unique). If this is a float, indicate the ratio of the max size of a key to use (for multi column keys).
        """
        raise NotImplementedError() #TODO


    def table_exists(self, name: str|tuple|type|DbObject) -> bool:
        raise NotImplementedError() #TODO


    def create_table(self, name: str|tuple|type|DbObject, columns: Sequence[str|DbColumn]|Mapping[str,str|type|DbColumn], *, if_not_exists = False) -> None:
        raise NotImplementedError() #TODO


    def create_temp_table(self, columns: Sequence[str|DbColumn]|Mapping[str,str|type|DbColumn], *, if_not_exists = False) -> TempDbObject:
        raise NotImplementedError() #TODO
    

    def drop_table(self, name: str|tuple|type|DbObject, *, if_exists = False):
        raise NotImplementedError() #TODO
    
    #endregion


@dataclass
class DbObject:
    """
    Identify a database object (table, view, procedure, etc).
    """

    name: str
    """ Name of the object. """

    schema: str|None
    """ Schema of the object (if known). """

    db: type[Db]|None
    """ Type of database (used for escaping). """

    def __str__(self):
        return self.escaped
    
    @cached_property
    def escaped(self):
        if not self.db:
            raise ValueError("Cannot escape DbObject: missing `db` class.")
        return f"{f'{self.db.escape_identifier(self.schema)}.' if self.schema else ''}{self.db.escape_identifier(self.name)}"
    
    @cached_property
    def is_temp(self):
        if not self.db:
            raise ValueError("Cannot determine if DbObject is temp: missing `db` class.")
        if self.db._temp_schema == '#' and self.name.startswith('#'): # sqlserver
            return True
        elif self.schema and self.schema == self.db._temp_schema:
            return True
        else:
            return False
        

@dataclass
class TempDbObject(DbObject):
    _db_instance: Db

    def __enter__(self):
        return self
    
    def __exit__(self, *exc_info):
        self._db_instance._logger.debug(f"Drop table {self}")
        return self._db_instance.drop_table(self)


@dataclass
class DbColumn:
    name: str
    """ Name of the column. """

    python_type: type|None
    """ Full SQL type (including precision and scale if any). """

    sql_type: str|None
    """ Full SQL type (including precision and scale if any). """

    not_null: bool|None
    """ Indicate whether the column has a NOT NULL contraint. """

    is_primary: bool|None
    """ Indicate whether the column is part of the primary key. """

    db: type[Db]|None
    """ Type of database (used for escaping). """


class DbCursor:
    def __enter__(self) -> Self:
        ...

    def __exit__(self, *exc_info):
        ...

    def __iter__(self) -> Iterator[tuple[Any,...]]:
        ...

    def close(self):
        ...
    
    def execute(self, query: str, args = None):
        ...

    @property
    def rowcount(self) -> int:
        ...

    @property
    def description(self) -> tuple[tuple[str, Any, int, int, int, int, bool]]:
        ...


class DbRowIterator:
    pass #TODO
