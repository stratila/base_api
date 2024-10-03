from app.database.errors import DatabaseErrorDescription

# Database errors: 21000...

DATABASE_COMMON_ERROR = DatabaseErrorDescription(
    21000, "Database Error -- Please Contact Your Administrator"
)


# Users Errors: 22000...

USER_SHOULD_HAVE_UNIQUE_EMAIL = DatabaseErrorDescription(
    22000, "User should have unique email"
)

USER_SHOULD_HAVE_UNIQUE_USERNAME = DatabaseErrorDescription(
    22001, "User should have unique username"
)
