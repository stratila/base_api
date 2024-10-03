import sys
import logging
import traceback


from typing import List, Set, Dict
from pathlib import Path
from csv import DictReader
from collections import defaultdict

from pydantic import BaseModel

from app.database import db
from app.database.models import roles, permissions


from sqlalchemy import Connection, select, insert, delete, case, not_, or_, and_
from sqlalchemy.sql.functions import coalesce, func


# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # set logger level
logFormatter = logging.Formatter("%(levelname)-2s [%(filename)s] %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)  # set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

API_DIR_PATH = Path(__file__).parent.parent.parent
ROLES_CSV_PATH = API_DIR_PATH / "api/security/permissions/roles.csv"
PERMISSIONS_CSV_PATH = API_DIR_PATH / "api/security/permissions/permissions.csv"


class Role(BaseModel):
    role_name: str


class Permission(BaseModel):
    permission_name: str
    role_name: str


def read_roles() -> List[Role]:
    result_roles: List[Role] = []
    with open(ROLES_CSV_PATH, "r") as file:
        roles_csv = DictReader(file, delimiter=",")
        for role in roles_csv:
            result_roles.append(Role(**role))
    return result_roles


def read_permissions() -> List[Permission]:
    result_permissions = []
    with open(PERMISSIONS_CSV_PATH, "r") as file:
        permissions_csv = DictReader(file, delimiter=",")
        for permission in permissions_csv:
            result_permissions.append(Permission(**permission))
    return result_permissions


EMPTY_JSON_ARRAY = func.json_build_array()


def validate_roles_in_permissions(
    roles_sqnc: List[Role], permissions_sqnc: List[Permission]
):
    existing_roles: Set[str] = set([role.role_name for role in roles_sqnc])
    existing_roles_in_permissions: Set[str] = {
        permission.role_name for permission in permissions_sqnc
    }

    diff_roles = existing_roles_in_permissions - existing_roles

    if diff_roles:
        raise Exception(
            "permissions.csv has roles that don't exist in roles.csv: "
            f"{','.join(diff_roles)}"
        )


def get_role_permissions_dict(permission_objects) -> Dict[Role, List[Permission]]:
    current_role_permission_map = defaultdict(list)
    for p in permission_objects:
        current_role_permission_map[p.role_name].append(p.permission_name)
    return current_role_permission_map


def execute_select_roles_to_persist_and_delete(
    role_names: List[str], connection: Connection
):
    to_persist_sbq = (
        select(coalesce(func.json_agg(roles.c.role_name), EMPTY_JSON_ARRAY))
        .where(roles.c.role_name.in_(role_names))
        .scalar_subquery()
    )
    to_delete_sbq = (
        select(coalesce(func.json_agg(roles.c.role_name), EMPTY_JSON_ARRAY))
        .where(not_(roles.c.role_name.in_(role_names)))
        .scalar_subquery()
    )

    main_q = select(
        to_persist_sbq.label("to_persist"),
        to_delete_sbq.label("to_delete"),
    )

    result = connection.execute(main_q).fetchone()
    result = result._mapping if result else None
    return result


def execute_insert_and_delete_roles(
    role_names_to_ins, role_names_to_del, connection: Connection
):
    if role_names_to_del:
        connection.execute(
            delete(roles).where(roles.c.role_name.in_(role_names_to_del))
        )
    if role_names_to_ins:
        connection.execute(
            insert(roles).values(
                [{"role_name": role_name} for role_name in role_names_to_ins]
            )
        )


def execute_select_all_roles_with_permissions(connection):
    q2 = (
        select(
            roles.c.id.label("role_id"),
            roles.c.role_name,
            case(
                (
                    func.max(permissions.c.id) != None,  # noqa: E711
                    func.json_agg(
                        func.json_build_object(
                            "permission_id",
                            permissions.c.id,
                            "permission_name",
                            permissions.c.permission_name,
                        )
                    ),
                ),
                else_=EMPTY_JSON_ARRAY,
            ).label("permissions"),
        )
        .select_from(roles.outerjoin(permissions, roles.c.id == permissions.c.role_id))
        .group_by(roles.c.id, roles.c.role_name)
    )

    result = connection.execute(q2).fetchall()
    result = [r._mapping for r in result] if result else []
    return result


def get_roles_for_update(result, file_role_names):
    to_persist = result.get("to_persist", [])
    to_delete = result.get("to_delete", [])
    to_insert = list(set(file_role_names) - set(to_persist))

    logger.info(
        f"ROLES to persist: {to_persist}, to delete: {to_delete},"
        f" to insert {to_insert}"
    )

    return to_delete, to_insert


def get_role_permissions_insert_and_delete_map(
    roles_with_permissions, permission_objects
):
    current_role_permission_map = get_role_permissions_dict(permission_objects)
    role_permission_update_map = defaultdict(dict)
    for role in roles_with_permissions:
        if role["permissions"] is None:
            pass

        current = set(current_role_permission_map[role["role_name"]])
        database = set([p["permission_name"] for p in role["permissions"]])
        to_persist = current.intersection(database)
        to_delete = database.difference(current)
        to_insert = current.difference(database)

        logger.info(
            f"PERMISSIONS for {role['role_name']} ROLE to persist: "
            f"{list(to_persist)}, to delete: {list(to_delete)}, "
            f"to insert {list(to_insert)}"
        )

        role_permission_update_map[role["role_id"]]["delete"] = to_delete
        role_permission_update_map[role["role_id"]]["insert"] = to_insert

    return role_permission_update_map


def get_insert_and_delete_permissions_values(role_permission_update_map):
    insert_values = []
    delete_values = []
    for role_id, action in role_permission_update_map.items():
        for permission_name in action["insert"]:
            insert_values.append(
                {"role_id": role_id, "permission_name": permission_name}
            )
        for permission_name in action["delete"]:
            delete_values.append(
                {"role_id": role_id, "permission_name": permission_name}
            )

    return insert_values, delete_values


def execute_insert_and_delete_permissions(
    insert_values, delete_values, connection: Connection
):
    if insert_values:
        connection.execute(insert(permissions).values(insert_values))
    if delete_values:
        and_clauses = (
            and_(
                permissions.c.role_id == dv["role_id"],
                permissions.c.permission_name == dv["permission_name"],
            )
            for dv in delete_values
        )
        connection.execute(delete(permissions).where(or_(*and_clauses)))


def update_roles_and_permissions(connection):
    try:
        logger.info("Updating roles and permissions...")
        role_objects: List[Role] = read_roles()
        permission_objects: List[Permission] = read_permissions()

        validate_roles_in_permissions(role_objects, permission_objects)

        current_role_names = [role.role_name for role in role_objects]

        # 1. Update roles
        logger.info("Performing roles update...")
        result = execute_select_roles_to_persist_and_delete(
            current_role_names, connection
        )

        if result:
            to_delete, to_insert = get_roles_for_update(result, current_role_names)
            execute_insert_and_delete_roles(to_insert, to_delete, connection)

        # 2. Update permissions
        logger.info("Performing permissions update...")
        result = execute_select_all_roles_with_permissions(connection)
        if result:
            role_permission_update_map = get_role_permissions_insert_and_delete_map(
                result, permission_objects
            )

            insert_values, delete_values = get_insert_and_delete_permissions_values(
                role_permission_update_map
            )

            execute_insert_and_delete_permissions(
                insert_values, delete_values, connection
            )

        connection.commit()
        logger.info("Update of roles and permissions to db has been completed")
    except Exception as e:
        logger.error(f"Exception {e}, trace:\n{traceback.print_exc()}")
        connection.rollback()


if __name__ == "__main__":
    with db.main_engine.connect() as connection:
        sys.exit(update_roles_and_permissions(connection))
