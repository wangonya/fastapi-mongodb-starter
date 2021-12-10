from typing import Any, Dict, List, Optional

import mongomock
import pytest

from app.core.repository import AbstractRepository


class MongoDBTestRepository(AbstractRepository):
    def __init__(self):
        self.collection = mongomock.MongoClient().db.collection
        self.collection.create_index("email", unique=True)

    def add(
        self,
        resource: Dict[str, Any] = {},
    ):
        created_id = self.collection.insert_one(resource).inserted_id
        created_resource = self.collection.find_one({"_id": created_id})
        return created_resource

    def get(self, **kwargs) -> Optional[Dict[str, Any]]:
        reference = [*kwargs][0]
        return self.collection.find_one({reference: kwargs.get(reference)})

    def filter(self, **kwargs) -> List[Optional[Dict[str, Any]]]:
        ...

    def list(self) -> List[Optional[Dict[str, Any]]]:
        ...


@pytest.fixture
def mongodb_test_repository():
    return MongoDBTestRepository()
