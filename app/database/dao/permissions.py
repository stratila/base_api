from sqlalchemy import Connection, insert, delete
from app.database.dao.base import BaseDataAccessObject
from app.database.models import permissions


class Permissions(BaseDataAccessObject):
    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)

    def add_permission(self, permission_name, role_id) -> int:
        with self.cm_error_handler():
            result = self.conn.execute(
                insert(permissions)
                .values(permission_name=permission_name, role_id=role_id)
                .returning(permissions.c.id)
            ).first()

            return result[0]

    def delete_permission(self, permission_id) -> int:
        with self.cm_error_handler():
            result = self.conn.execute(
                delete(permissions)
                .where(permissions.c.id == permission_id)
                .returning(permissions.c.id)
            ).first()
            return result[0] if result else None
