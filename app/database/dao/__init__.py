"""Models data access objects"""

from app.database.dao.users import Users
from app.database.dao.roles import Roles
from app.database.dao.permissions import Permissions


class DbModels:
    def __init__(self, conn) -> None:
        self.conn = conn
        self.users = Users(self.conn)
        self.roles = Roles(self.conn)
        self.permissions = Permissions(self.conn)
