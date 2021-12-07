from typing import List

from pydantic import BaseSettings


class Env(BaseSettings):
    HOST: str
    PORT: int
    ALLOWED_ORIGINS: List[str]

    # auth
    AUTH_SECRET_KEY: str
    AUTH_ALGORITHM: str
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int

    # db
    MONGODB_URL: str
    MONGODB_DBNAME: str

    class Config:
        case_sensitive = True
        env_file = ".env"


ENV = Env()
