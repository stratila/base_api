from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, String, Integer

Base = declarative_base()

users = Table(
    "users",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(100), nullable=False),
)
