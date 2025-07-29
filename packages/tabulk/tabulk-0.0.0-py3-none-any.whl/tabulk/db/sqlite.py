from . import Db

from sqlite3 import Connection, connect

class SqliteDb(Db[Connection]):
    pass #TODO
