from app.models.user import UserCreate
from app.services.user import UserService


def test_create_user(test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    user = UserService(test_repository).create_user(user)
    assert user_data.get("email") == user.get("email")


def test_get_user_by_id(test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    user = UserService(test_repository).create_user(user)
    assert test_repository.get("users", _id=user.get("_id")) is not None


def test_get_user_by_email(test_repository, faker):
    user_data = {"email": faker.email(), "password": faker.password()}
    user = UserCreate(**user_data)
    user = UserService(test_repository).create_user(user)
    assert test_repository.get("users", email=user.get("email")) is not None


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
    access_token = UserService.create_access_token(user_data)
    decoded_token = UserService.decode_access_token(access_token)
    assert decoded_token == user_data.get("_id")
