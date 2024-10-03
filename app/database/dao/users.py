from sqlalchemy import Connection, select, insert, delete
from app.database.dao.base import BaseDataAccessObject
from app.database.models import users, roles

# from app.database.errors.messages import (
#     USER_SHOULD_HAVE_UNIQUE_EMAIL,
#     USER_SHOULD_HAVE_UNIQUE_USERNAME,
# )


class Users(BaseDataAccessObject):

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)

    def add_user(
        self, email, username, first_name, last_name, password_hash, role_id
    ) -> int:
        with self.cm_error_handler():

            # NOTE: This is an example of defining and raising database user error,
            #       Also the corresponding tests would be named:
            #           1)
            #           tests/database/test_dao_users.py::
            #           test_add_user_with_existing_username_or_email_raise_error
            #           2)
            #           tests/api/endpoints/users/administrator_role/
            #           test_users_with_administrator_role_bad.py::
            #           test_post_user_username_or_email_exists_raise_an_error

            # stmt = select(users.c.username, users.c.email).where(
            #     (users.c.username == username) | (users.c.email == email)
            # )

            # result = self.conn.execute(stmt).mappings().all()
            # if result:
            #     for r in result:
            #         if r["username"] == username:
            #             raise DatabaseError(
            #                 USER_SHOULD_HAVE_UNIQUE_USERNAME.error_code,
            #                 USER_SHOULD_HAVE_UNIQUE_USERNAME.message,
            #             )
            #         if r["email"] == email:
            #             raise DatabaseError(
            #                 USER_SHOULD_HAVE_UNIQUE_EMAIL.error_code,
            #                 USER_SHOULD_HAVE_UNIQUE_EMAIL.message,
            #             )

            result = self.conn.execute(
                insert(users)
                .values(
                    email=email,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password_hash=password_hash,
                    role_id=role_id,
                )
                .returning(users.c.id),
            ).first()

            return result[0]

    def get_user(self, user_id):
        with self.cm_error_handler():
            result = (
                self.conn.execute(
                    select(
                        users.c.id,
                        users.c.email,
                        users.c.username,
                        users.c.first_name,
                        users.c.last_name,
                        roles.c.role_name,
                    )
                    .select_from(users.outerjoin(roles, users.c.role_id == roles.c.id))
                    .where(users.c.id == user_id)
                )
                .mappings()
                .first()
            )

        return dict(result) if result else None

    def get_users(
        self,
        user_id=None,
        user_ids=None,
        first_name=None,
        last_name=None,
        email=None,
        username=None,
        role_name=None,
    ):
        with self.cm_error_handler():
            stmt = select(
                users.c.id,
                users.c.email,
                users.c.username,
                users.c.first_name,
                users.c.last_name,
                roles.c.role_name,
            ).select_from(users.outerjoin(roles, users.c.role_id == roles.c.id))

            if user_id:
                stmt = stmt.where(users.c.id == user_id)
            if user_ids:
                stmt = stmt.where(users.c.id.in_(user_ids))
            if first_name:
                stmt = stmt.where(users.c.first_name == first_name)
            if last_name:
                stmt = stmt.where(users.c.last_name == last_name)
            if email:
                stmt = stmt.where(users.c.email == email)
            if username:
                stmt = stmt.where(users.c.username == username)
            if role_name:
                stmt = stmt.where(roles.c.role_name == role_name)

            result = self.conn.execute(stmt)
            result = result.all()
            result = [r._mapping for r in result] if result else None
            return result

    def get_hashed_password_by_email(self, email):
        with self.cm_error_handler():
            result = (
                self.conn.execute(
                    select(
                        users.c.id,
                        users.c.role_id,
                        users.c.email,
                        users.c.password_hash,
                    ).where(users.c.email == email)
                )
                .mappings()
                .first()
            )

            return dict(result) if result else None

    def delete_user(self, user_id):
        with self.cm_error_handler():
            stmt = delete(users).where(users.c.id == user_id)
            result = self.conn.execute(stmt)
            return result.rowcount
