"""
This checks are used in authorization.py ENDPOINTS_REGEXPS object
"""

import re
from fastapi import Request, HTTPException


def users_endpoint_permission_check(
    request: Request, current_user: dict, match: re.Match
) -> bool | None:
    permissions = current_user.get("permissions", [])

    # see USER_ID_URL_REGEX in app/api/routers/literals.py
    target_user_id = int(match.group("user_id"))
    if (request.method in ["PUT", "PATCH"] and "write_self_user" in permissions) or (
        request.method in ["GET", "DELETE"] and "read_self_user" in permissions
    ):
        if target_user_id != current_user.get("user_id"):
            raise HTTPException(
                status_code=403,
                detail=(
                    "You don't have a permission to perform write/read for other user",
                ),
            )
