from fastapi import HTTPException


class AuthWrongCredentials(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Wrong credentials.")


class AuthInvalidScheme(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Invalid authentication scheme.")


class AuthInvalidToken(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Invalid token or expired token.")


class AuthInvalidCode(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Invalid authorization code.")
