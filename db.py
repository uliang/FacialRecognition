from flask import g
from model import get_engine

from sqlalchemy.orm import sessionmaker

class Database:

    def __init__(self):
        self._engine = None
        self.session_factory = None

    def init_app(self, app):
        _conn_string = app.config.get('DB_CONNECTION_STRING')
        self._engine = get_engine(_conn_string) 
        self.session_factory = sessionmaker(bind=self._engine)

    def get_session(self):
        if 'session' in g:
            return g.session
        g.session = self.session_factory()
        return g.session


database = Database()