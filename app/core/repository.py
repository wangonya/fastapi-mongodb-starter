import abc
from typing import Any, Dict, List

from pymongo.results import InsertOneResult

from app.core.db import db
from app.models import BaseModel


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, collection, resource):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, collection, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def filter(self, collection, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, collection):
        raise NotImplementedError


class MongoDBRepository(AbstractRepository):
    async def add(self, collection: str, resource: BaseModel) -> InsertOneResult:
        return await db[collection].insert_one(resource)

    async def get(self, collection: str, **kwargs) -> Dict[str, Any]:
        print(f"kwargs = {kwargs}")
        return await db[collection].find_one(kwargs)

    async def filter(self, collection: str, **kwargs) -> List[BaseModel]:
        ...

    async def list(self, collection: str) -> List[BaseModel]:
        ...
