"""
This file contains the authorization logic for the API.
The authorization logic is based on the permissions that are assigned to a role.
Permissions class dependency:
https://fastapi.tiangolo.com/advanced/advanced-dependencies/
"""

import logging
import re
from fastapi import Depends, HTTPException, Request

# from typing import Dict, Callable, Union

from app.api.security.authentication import JWTToken, JWTBearer
from app.api.security.checks import (
    users_endpoint_permission_check,
)
from app.api.routers.literals import (
    USER_ID_URL_REGEX,
)


logger = logging.getLogger(__name__)


# Dict[str, Callable[[Request, dict, re.Match], Union[bool, None]]]
ENDPOINTS_REGEXPS = {
    USER_ID_URL_REGEX: users_endpoint_permission_check,
}


def get_current_user(token: str = Depends(JWTBearer())):
    if payload := JWTToken().decode(token):
        return payload["access_token"]  # contains the user_id and permissions
    return {}


def run_additional_permission_check(request: Request = None, current_user: dict = {}):
    for regexp, run_check in ENDPOINTS_REGEXPS.items():
        if match := re.match(regexp, request.url.path):
            run_check(request, current_user, match)  # throws HTTP error
            break


class Permissions:
    """
    A dependency class that checks if the current user has the required permissions.
    """

    def __init__(self, *args):
        self.permissions_required = set(args)

    def __call__(
        self,
        current_user: dict = Depends(get_current_user),
        request: Request = None,
    ):
        return self.check_permissions(request, current_user, self.permissions_required)

    def check_permissions(self, request, current_user, permissions_required):

        permissions = current_user.get("permissions", [])

        run_additional_permission_check(request, current_user)

        permission_match = False
        for up in permissions:  # user_permissions
            for ep in permissions_required:  # endpoint_permissions
                if up == ep:
                    permission_match = True

        if not permission_match:
            raise HTTPException(
                status_code=403,
                detail="You don't have a permission to perform this action",
            )
        return True
