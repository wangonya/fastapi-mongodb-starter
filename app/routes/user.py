from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.core.repository import MongoDBRepository
from app.models.user import Token, User, UserCreate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return UserService(MongoDBRepository("users")).login_user(form_data)


@router.get("/me", response_model=User)
def get_current_user(
    current_user=Depends(UserService(repo=MongoDBRepository("users")).get_current_user),
):
    return current_user


@router.post("", response_model=User)
def create_user(new_user: UserCreate):
    return UserService(repo=MongoDBRepository("users")).create_user(new_user)
