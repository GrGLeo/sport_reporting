from pydantic import BaseModel


class LoginModel(BaseModel):
    username: str
    password: str


class UserModel(BaseModel):
    username: str
    password: str
    email: str
