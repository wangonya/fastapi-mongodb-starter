import abc
from typing import Any, Dict, List, Optional, Union

from pymongo.results import InsertOneResult

from app.core.db import db


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
    async def add(self, collection: str, resource: Dict[str, Any]) -> Dict[str, Any]:
        created = await db[collection].insert_one(resource)
        return await self.get(collection, _id=created.inserted_id)

    async def get(self, collection: str, **kwargs) -> Union[Dict[str, Any], None]:
        return await db[collection].find_one(kwargs)

    async def filter(self, collection: str, **kwargs) -> List[Optional[Dict[str, Any]]]:
        ...

    async def list(self, collection: str) -> List[Optional[Dict[str, Any]]]:
        ...
