from app.service.errors import ServiceErrorDescription

# Roles errors: 11000...

ROLE_DOES_NOT_EXIST = ServiceErrorDescription(
    11000,
    "Role {role_name} doesn't exist",
)


# Users errors: 11100...

USER_DOES_NOT_EXIST = ServiceErrorDescription(
    11100,
    "User {user_id} doesn't exist",
)

USER_SHOULD_HAVE_UNIQUE_EMAIL = ServiceErrorDescription(
    11101,
    "User should have unique email",
)

USER_SHOULD_HAVE_UNIQUE_USERNAME = ServiceErrorDescription(
    11102,
    "User should have unique username",
)


# Auth errors: 11200...


AUTH_WRONG_CREDENTIALS = ServiceErrorDescription(
    11200,
    "Wrong credentials",
)
