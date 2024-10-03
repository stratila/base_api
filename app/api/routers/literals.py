# Routes URLs
SIGN_UP_URL = "/signup"
LOG_IN_URL = "/login"

# URL constants and regexp strings for user-related operations

CREATE_USER_URL = "/users"
RETRIEVE_USER_URL = "/users/{user_id}"
UPDATE_USER_URL = "/users/{user_id}"
PARTIAL_UPDATE_USER_URL = "/users/{user_id}"
DELETE_USER_URL = "/users/{user_id}"
LIST_USERS_URL = "/users"

USER_ID_URL_REGEX = r".*/users/(?P<user_id>\d+)"
