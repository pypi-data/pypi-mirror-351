from psycopg import Connection, connect

from ..utils import get_delayedstr_value
from . import Db


class PostgreSqlDb(Db[Connection]):
    _accept_aware_datetimes = True

    def create_connection(self, autocommit: bool | None = None):
        kwargs = {}
        if self.name is not None:
            kwargs['dbname'] = self.name
        if self.host is not None:
            kwargs['host'] = self.host
        if self.port is not None:
            kwargs['port'] = self.port
        if self.user is not None:
            kwargs['user'] = self.user

        password = get_delayedstr_value(self.password)
        if password is not None:
            kwargs['password'] = password

        if autocommit is None:
            if self.autocommit is not None:
                autocommit = self.autocommit
            else:
                autocommit = True

        return connect(**kwargs, autocommit=autocommit)


    def get_database_name(self) -> str:
        with self.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            return next(iter(cursor))[0]
        

    def database_exists(self, name: str) -> bool:
        query = "SELECT EXISTS (SELECT FROM pg_database WHERE datname = %s)"
        with self.cursor() as cursor:
            cursor.execute(query, [name])
            return next(iter(cursor))[0]


    def create_database(self, name: str, *, if_not_exists=False) -> None:
        if if_not_exists:
            if self.database_exists(name):
                return
        
        query = f"CREATE DATABASE {self.escape_identifier(name)}"
        with self.cursor() as cursor:
            cursor.execute(query)
