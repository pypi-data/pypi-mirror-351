import re
from pyodbc import Connection, connect, drivers

from ..utils import get_delayedstr_value
from . import Db


class SqlServerDb(Db[Connection]):
    def create_connection(self, autocommit: bool | None = None):
        def escape(s: str):
            if ';' in s or '{' in s or '}' in s or '=' in s:
                return "{" + s.replace('}', '}}') + "}"
            else:
                return s

        # Use "ODBC Driver XX for SQL Server" if available ("SQL Server" seems not to work with LocalDB, and takes several seconds to establish connection on my standard Windows machine with SQL Server Developer).
        driver = "SQL Server"
        for a_driver in sorted(drivers(), reverse=True):
            if re.match(r'^ODBC Driver \d+ for SQL Server$', a_driver):
                driver = a_driver
                break        
        connection_string = 'Driver={%s}' % escape(driver)
                
        server = self.host or '(local)'
        if self.port:
            server += f',{self.port}'
        connection_string += ';Server=%s' % escape(server)

        if self.name is not None:
            connection_string += ';Database=%s' % escape(self.name)

        if self.user:
            connection_string += ';UID=%s' % escape(self.user)
            if self.password:
                password = get_delayedstr_value(self.password)
                if password:
                    connection_string += ';PWD=%s' % escape(password)
        else:
            connection_string += ';Trusted_Connection=yes'
            
        connection_string += ';Encrypt=%s' % ('yes' if self.encrypt else 'no',)

        if autocommit is None:
            if self.autocommit is not None:
                autocommit = self.autocommit
            else:
                autocommit = True

        return connect(connection_string, autocommit=autocommit)


    def get_database_name(self) -> str:
        with self.cursor() as cursor:
            cursor.execute("SELECT db_name()")
            return next(iter(cursor))[0]


    def database_exists(self, name: str) -> bool:
        query = "SELECT 1 FROM master.sys.databases WHERE name = ?"
        with self.cursor() as cursor:
            cursor.execute(query, [name])
            try:
                return next(iter(cursor))[0] == 1            
            except StopIteration:
                return False


    def create_database(self, name: str, *, if_not_exists=False) -> None:
        if if_not_exists:
            if self.database_exists(name):
                return
        
        query = f"CREATE DATABASE {self.escape_identifier(name)}"
        with self.cursor() as cursor:
            cursor.execute(query)
