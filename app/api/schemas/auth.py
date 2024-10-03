from pydantic import BaseModel, EmailStr, Field, field_validator


class UserSignUpSchema(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    # role_name: str
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        # BS: my own random validation
        if " " in v:
            raise ValueError("username should not have a space")
        if v.startswith("_") or v.endswith("_") or v[0].isdigit():
            raise ValueError(
                "username should not to start or end "
                "with underscore and start with digit"
            )

        parts = v.split("_")
        for p in parts:
            if p == "":
                continue
            if not p.isalnum():
                raise ValueError(
                    "username should consist from alphanumeric chars and underscores"
                )

        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "username": "John_monster_gamer_2008",
                "email": "someemail@gmail.com",
                "password": "password123",
            }
        }


class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "someemail@gmail.com", "password": "password123"}
        }
