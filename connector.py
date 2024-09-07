import sqlite3


class DBConnector:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBConnector, cls).__new__(cls, *args, **kwargs)
        return cls.instance
    

    def __init__(self) -> None:
        self._conn = sqlite3.connect('mydatabase.db')


    def fetch(self, query):
        cursor = self._conn.cursor()
        print(query)
        cursor.execute(query)
        return cursor.fetchall()
    
    def create(self, query):
        cursor = self._conn.cursor()
        print(query)
        cursor.execute(query)
        self._conn.commit()
        return cursor.lastrowid