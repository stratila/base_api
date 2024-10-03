import os
import pytest
from sqlalchemy import create_engine, text
from app.config import get_postgres_connection_string
from app.database.models import Base


TEST_DB_NAME = "test_db"


def get_connection_string(test=False):
    main_connection_string = get_postgres_connection_string().split("/")
    # TODO add env variable TEST_DB_NAME

    db_name = os.environ.get("DB_NAME", "learning_api_database")
    if db_name == TEST_DB_NAME:
        db_name = "learning_api_database"

    main_connection_string[-1] = db_name if not test else TEST_DB_NAME
    return "/".join(main_connection_string)


@pytest.fixture(scope="session")
def db_connection():

    main_engine = create_engine(get_connection_string(test=False), echo=False)

    with main_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    test_engine = create_engine(get_connection_string(test=True), echo=False)

    Base.metadata.create_all(bind=test_engine)  # create the tables in the test database

    with test_engine.connect() as test_conn:
        yield test_conn
