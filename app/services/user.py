from datetime import datetime, timedelta
from typing import Optional

from bson.objectid import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic.networks import EmailStr
from pymongo.errors import DuplicateKeyError

from app.core.env import ENV
from app.core.repository import AbstractRepository
from app.models.user import UserCreate, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


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
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=ENV.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            ENV.AUTH_SECRET_KEY,
            algorithm=ENV.AUTH_ALGORITHM,
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                ENV.AUTH_SECRET_KEY,
                algorithms=[ENV.AUTH_ALGORITHM],
            )
            return payload
        except JWTError:
            raise credentials_exception

    def authenticate_user(self, email: EmailStr, password: str) -> UserInDB:
        user = self.repo.get(email=email)
        if user and self.verify_password(password, user.get("password")):
            return UserInDB(**user)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def login_user(self, form_data: OAuth2PasswordRequestForm) -> dict:
        user = self.authenticate_user(form_data.username, form_data.password)
        access_token_expires = timedelta(minutes=ENV.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"_id": user.id},
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        decoded_token = self.decode_access_token(token)
        _id = decoded_token.get("_id")
        user = self.repo.get(_id=ObjectId(_id))
        if user is None:
            raise credentials_exception
        return user

    def create_user(self, new_user_data: UserCreate):
        new_user_data.password = self.get_password_hash(new_user_data.password)
        user = UserCreate(**new_user_data.dict())
        try:
            new_user = self.repo.add(user.dict())
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already registered",
            )
        return new_user
