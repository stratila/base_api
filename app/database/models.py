from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, String, Integer, ForeignKey

Base = declarative_base()

users = Table(
    "users",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(100), nullable=False, unique=True),
    Column("first_name", String(50), nullable=False),
    Column("last_name", String(50), nullable=False),
    Column("email", String(100), nullable=False, unique=True),
    Column("password_hash", String(1000), nullable=False),
    Column("role_id", ForeignKey("roles.id", ondelete="SET NULL"), nullable=False),
)


roles = Table(
    "roles",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("role_name", String(100), nullable=False, unique=True),
)


permissions = Table(
    "permissions",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("permission_name", String(100), nullable=False, unique=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
)
