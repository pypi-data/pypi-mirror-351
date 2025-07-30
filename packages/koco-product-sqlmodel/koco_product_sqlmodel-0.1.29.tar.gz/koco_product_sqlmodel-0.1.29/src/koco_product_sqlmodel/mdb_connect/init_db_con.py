from sqlmodel import create_engine
from dotenv import load_dotenv
import os

load_dotenv()


def create_mdb_engine():
    engine = create_engine(url=os.environ["MARIADB_CONNECTOR_STRING"])
    return engine


mdb_engine = create_mdb_engine()
# print(mdb_engine)


def Main():
    print(mdb_engine)


if __name__ == "__main__":
    Main()
