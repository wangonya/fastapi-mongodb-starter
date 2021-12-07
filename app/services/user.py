from datetime import datetime, timedelta
from typing import Optional, Union

from bson.objectid import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic.networks import EmailStr

from app.core.env import CREDENTIALS
from app.core.repository import AbstractRepository
from app.models.user import User, UserCreate, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


class UserService:
    def __init__(self, repo: AbstractRepository) -> None:
        self.repo = repo

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=CREDENTIALS.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            CREDENTIALS.AUTH_SECRET_KEY,
            algorithm=CREDENTIALS.AUTH_ALGORITHM,
        )
        return encoded_jwt

    async def get_user(self, **kwargs) -> Union[UserInDB, None]:
        user = await self.repo.get("users", **kwargs)
        if user:
            return UserInDB(**user)

    async def authenticate_user(self, email: EmailStr, password: str):
        user = await self.get_user(email=email)
        if not user:
            return False
        if not self.verify_password(password, user.password):
            return False
        return user

    async def login_user(self, form_data: OAuth2PasswordRequestForm) -> dict:
        user = await self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(
            minutes=CREDENTIALS.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = self.create_access_token(
            data={"_id": user.id},
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token,
                CREDENTIALS.AUTH_SECRET_KEY,
                algorithms=[CREDENTIALS.AUTH_ALGORITHM],
            )
            _id = payload.get("_id")
            if _id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = await self.get_user(_id=ObjectId(_id))
        if user is None:
            raise credentials_exception
        return User(**user.dict())

    async def create_user(self, new_user_data: UserCreate):
        new_user_data.password = self.get_password_hash(new_user_data.password)
        user = UserCreate(**new_user_data.dict())
        new_user = await self.repo.add("users", user.dict())
        created_user = await self.get_user(_id=new_user.inserted_id)
        return created_user
