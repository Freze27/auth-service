from pydantic import BaseModel, EmailStr, field_validator


class DepartmentSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    department_id: int

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    department: DepartmentSchema
    roles: list[str]
    is_active: bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_user(cls, user) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            department=DepartmentSchema.model_validate(user.department),
            roles=[role.name for role in user.roles],
            is_active=user.is_active,
        )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
