from pydantic import BaseModel


class RegisterUsernameV0(BaseModel):
    username: str
    password: str
    admin_password: str


class LoginUsernameV0(BaseModel):
    username: str
    password: str


class RemoveAppForSelfV0(BaseModel):
    password: str
