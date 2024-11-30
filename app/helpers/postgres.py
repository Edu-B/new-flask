import psycopg2

from psycopg2 import extras


# postgres.py
class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.init_connection(*args, **kwargs)
        return cls._instance

    def init_connection(self, host, port, user, password, database):
        self.connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursor_factory=extras.DictCursor,
        )

    def return_connection(self):
        return self.connection

    def __del__(self):
        if hasattr(self, "connection"):
            self.connection.close()
