from collections import defaultdict
from typing import Any, Dict, List, Optional, Union

import pytest

from app.core.repository import AbstractRepository


class TestRepository(AbstractRepository):
    def __init__(self, faker):
        self._resources = defaultdict(list)
        self.faker = faker

    def add(self, collection: str, resource: Dict[str, Any]):
        _id = self.faker.uuid4()
        resource["_id"] = _id
        self._resources[collection].append(resource)
        return resource

    def get(self, collection: str, **kwargs) -> Union[Dict[str, Any], None]:
        reference = [*kwargs][0]
        return next(
            resource
            for resource in self._resources[collection]
            if resource.get(reference) == kwargs[reference]
        )

    def filter(self, collection: str, **kwargs) -> List[Optional[Dict[str, Any]]]:
        ...

    def list(self, collection: str) -> List[Optional[Dict[str, Any]]]:
        ...


@pytest.fixture
def test_repository(faker):
    return TestRepository(faker)
