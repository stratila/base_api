from sqlalchemy import create_engine
from app.config import get_postgres_connection_string

main_engine = create_engine(get_postgres_connection_string())
