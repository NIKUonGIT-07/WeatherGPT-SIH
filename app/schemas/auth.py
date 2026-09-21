from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone: str | None = None
    password: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None or value == "":
            return None

        value = value.strip()

        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")

        if len(value) != 10:
            raise ValueError("Phone number must be 10 digits")

        return value


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone: str | None = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    identifier: str
    password: str