import os

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    jwt_secret_key: str = Field(default="secret")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)


# JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
# JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")


def get_postgres_connection_string(main_db=True):
    """
    db_name: used in tests to connect to the test_db
    """

    # If DB_HOST is not set in the environment, it indicates that the code is being run
    # locally for testing purposes. In this case, the connection should be made to the
    # exposed port 54321 (refer to the Docker Compose file for details).SAME FOR DB_NAME

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = "54321" if DB_HOST == "localhost" else "5432"

    # The default values for DB_PASSWORD, DB_USER, and DB_NAME should match the defaults
    # specified in the Docker Compose file (after the ":-" in the environment variables)
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "learning_api_database_password")
    DB_USER = os.environ.get("DB_USER", "learning_api_db_user")

    DB_NAME = (
        "test_db"
        if DB_HOST == "localhost"
        else os.environ.get("DB_NAME", "learning_api_database")
    )

    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


settings = Settings()
