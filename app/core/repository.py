import abc
from typing import Any, Dict, List, Optional

from app.core.db import db


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, resource):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def filter(self, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def list(self):
        raise NotImplementedError


class MongoDBRepository(AbstractRepository):
    def __init__(self, collection) -> None:
        self.collection: str = collection

    def add(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        created = db[self.collection].insert_one(resource)
        return self.get(_id=created.inserted_id)

    def get(self, **kwargs) -> Optional[Dict[str, Any]]:
        return db[self.collection].find_one(kwargs)

    def filter(self, **kwargs) -> List[Optional[Dict[str, Any]]]:
        ...

    def list(self) -> List[Optional[Dict[str, Any]]]:
        ...
