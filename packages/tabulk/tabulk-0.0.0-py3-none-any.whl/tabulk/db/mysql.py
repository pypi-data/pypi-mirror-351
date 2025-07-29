from . import Db
from ..utils import get_delayedstr_value

from MySQLdb import connect
from MySQLdb.connections import Connection

class MysqlDb(Db[Connection]):
    _identifier_quotechar_begin = '`'
    _identifier_quotechar_end = '`'

    def create_connection(self, autocommit: bool|None = None):
        kwargs = {}
        if self.name is not None:
            kwargs['database'] = self.name
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


    def get_database_name(self) -> str|None:
        with self.cursor() as cursor:
            cursor.execute("SELECT database()")
            return next(iter(cursor))[0]


    def database_exists(self, name: str) -> bool:
        query = "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s"
        with self.cursor() as cursor:
            cursor.execute(query, [name])
            try:
                return next(iter(cursor))[0] == 1
            except StopIteration:
                return False
