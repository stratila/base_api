from sqlalchemy import Connection, select, insert, func
from app.database.dao.base import BaseDataAccessObject
from app.database.models import roles, permissions


class Roles(BaseDataAccessObject):

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)

    def add_role(self, role_name) -> int:
        with self.cm_error_handler():
            result = self.conn.execute(
                insert(roles).values(role_name=role_name).returning(roles.c.id)
            ).fetchone()
            self.conn.commit()
            return result[0]

    def get_role(self, role_id=None, role_name=None) -> dict:
        with self.cm_error_handler():
            q1 = select(roles)

            if role_id is not None:
                q1 = q1.where(roles.c.id == role_id)

            if role_name is not None:
                q1 = q1.where(roles.c.role_name == role_name)

            result = self.conn.execute(q1).fetchone()
            return result._mapping if result else None

    def get_role_with_permissions(
        self, role_id
    ) -> dict:  # Typing can be a schema from Pydantic
        with self.cm_error_handler():
            q = (
                select(
                    roles.c.id,
                    roles.c.role_name,
                    func.json_agg(permissions.c.permission_name).label("permissions"),
                )
                .select_from(
                    roles.join(permissions, roles.c.id == permissions.c.role_id)
                )
                .where(roles.c.id == role_id)
                .group_by(roles.c.id)
            )

            result = self.conn.execute(q).fetchone()

            return result._mapping if result else None
