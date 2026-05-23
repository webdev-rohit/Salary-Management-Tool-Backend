from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
