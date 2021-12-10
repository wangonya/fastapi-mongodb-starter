from datetime import timedelta

import pytest
from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.core.env import ENV
from app.models.user import UserCreate
from app.services.user import UserService


def test_create_user(mongodb_test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    user = UserService(mongodb_test_repository).create_user(user)
    assert user_data.get("email") == user.get("email")


def test_create_duplicate_user(mongodb_test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    UserService(mongodb_test_repository).create_user(user)

    with pytest.raises(HTTPException) as e:
        UserService(mongodb_test_repository).create_user(user)

    assert e.value.status_code == 409
    assert e.value.detail == "This email is already registered"


def test_get_user_by_id(mongodb_test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    user = UserService(mongodb_test_repository).create_user(user)
    assert mongodb_test_repository.get(_id=user.get("_id")) is not None


def test_get_user_by_email(mongodb_test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    user = UserService(mongodb_test_repository).create_user(user)
    assert mongodb_test_repository.get(email=user.get("email")) is not None


def test_password_hash(faker):
    password = faker.password()
    hash = UserService.get_password_hash(password)
    assert UserService.verify_password(password, hash) is True


def test_create_access_token(faker):
    user_data = {"_id": faker.uuid4()}
    access_token = UserService.create_access_token(user_data)
    assert access_token


def test_decode_access_token(faker):
    user_data = {"_id": faker.uuid4()}
    access_token = UserService.create_access_token(
        user_data, timedelta(minutes=ENV.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    decoded_token = UserService.decode_access_token(access_token)
    assert decoded_token.get("_id") == user_data.get("_id")


def test_decode_invalid_access_token(faker):
    with pytest.raises(HTTPException):
        UserService.decode_access_token("12345")


def test_get_current_user(mongodb_test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    user = UserService(mongodb_test_repository).create_user(user)
    user["_id"] = str(user["_id"])
    access_token = UserService.create_access_token(user)
    current_user = UserService(mongodb_test_repository).get_current_user(access_token)
    assert str(current_user.get("_id")) == user.get("_id")


def test_current_user_not_found(mongodb_test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    user = UserService(mongodb_test_repository).create_user(user)
    _id = str(user["_id"])
    _id = str(int(_id[0]) + 1) + _id[1:]
    user["_id"] = _id
    access_token = UserService.create_access_token(user)

    with pytest.raises(HTTPException) as e:
        UserService(mongodb_test_repository).get_current_user(access_token)

    assert e.value.status_code == 401
    assert e.value.detail == "Could not validate credentials"


def test_login_user(mongodb_test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    form_data = OAuth2PasswordRequestForm(
        username=user_data.get("email"), password=user_data.get("password"), scope=""
    )
    user = UserCreate(**user_data)
    UserService(mongodb_test_repository).create_user(user)
    access_token = UserService(mongodb_test_repository).login_user(form_data)
    assert "access_token" in access_token.keys()


def test_login_user_invalid_credentials(mongodb_test_repository, faker):
    form_data = OAuth2PasswordRequestForm(
        username=faker.email(), password=faker.password(), scope=""
    )
    with pytest.raises(HTTPException) as e:
        UserService(mongodb_test_repository).login_user(form_data)

    assert e.value.status_code == 401
    assert e.value.detail == "Incorrect email or password"
