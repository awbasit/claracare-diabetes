from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole
from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.patient


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user: UserRead
    tokens: Token
