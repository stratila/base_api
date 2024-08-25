import os


def get_postgres_connection_string():
    DB_HOST = os.environ["DB_HOST"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_USER = os.environ["DB_USER"]
    DB_NAME = os.environ["DB_NAME"]
    port = "5432"
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{port}/{DB_NAME}"
