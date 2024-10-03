import random
import string

from sqlalchemy import insert

from app.database.models import roles


def random_string(length=8):
    """Generate a random string of fixed length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def create_role(db_connection, role_name) -> int:
    # create a role
    [role_id] = db_connection.execute(
        insert(roles).values(role_name=role_name).returning(roles.c.id)
    ).first()
    db_connection.commit()
    return role_id
