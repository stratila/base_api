from sqlalchemy import select, insert
from app.database.db import engine
from app.database.models import users


def add_user(username) -> int:

    with engine.connect() as connection:
        result = connection.execute(
            insert(users).values(username=username).returning(users.c.id),
        ).fetchone()
        connection.commit()
        return result[0]


def get_user(user_id):
    with engine.connect() as connection:
        result = connection.execute(
            select(users).where(users.c.id == user_id)
        ).fetchone()

        if not result:
            return None

        return result._mapping
