import os
import argparse
import sys

from dotenv import load_dotenv

from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Column, Integer, create_engine
import sqlalchemy.dialects.postgresql

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(length=100))
    face = Column('face_feature_vector', sqlalchemy.dialects.postgresql.BYTEA)

    def __repr__(self):
        return f"<{self.username}>"

    def __init__(self, name, vector):
        self.username = name
        self.face = vector


def get_engine(connection_string):
    return create_engine(connection_string)


def make_all_tables():
    conn_string = os.getenv('FLASK_DB_CONNECTION_STRING')
    engine = get_engine(conn_string)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    load_dotenv('.flaskenv')

    args = argparse.ArgumentParser()
    args.add_argument('command')

    namespace = args.parse_args()
    command = namespace.command

    if command == 'create':
        try:
            make_all_tables()
            print("Success!")
        except:
            print("Failure!")
            sys.exit(1)
        sys.exit(0)
    sys.exit(1)
