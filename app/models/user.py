from pydantic.networks import EmailStr

from app.models import BaseModel, PydanticBaseModel


class User(BaseModel):
    email: EmailStr
    is_active: bool = False


class UserCreate(PydanticBaseModel):
    email: EmailStr
    password: str


class UserInDB(User):
    password: str


class Token(PydanticBaseModel):
    access_token: str
    token_type: str
