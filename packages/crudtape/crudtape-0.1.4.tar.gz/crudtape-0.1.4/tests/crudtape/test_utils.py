from dataclasses import dataclass

from pydantic import BaseModel

from crudtape.store import Storable


class A(BaseModel):
    """Test model based on Pydantic."""
    name: str
    age: int
    id: int = None


@dataclass
class B:
    """Test model based on dataclass."""
    name: str
    age: int
    id: int = None

    def model_dump(self, *args, **kwargs):
        return {"name": self.name, "age": self.age}


class C:
    """Test model based on custom class."""
    def __init__(self, **data):
        self.name = data.get("name")
        self.age = data.get("age")
        self.id = data.get("id", None)

    def model_dump(self, *args, **kwargs):
        return {"name": self.name, "age": self.age}


def test_type_compatibility():
    """Test model compatibility with Storable protocol."""
    a = A(name="Ash", age=3)
    assert isinstance(a, BaseModel)
    assert isinstance(a, Storable)

    b = B(name="Bob", age=4)
    assert not isinstance(b, BaseModel)
    assert isinstance(b, Storable)
    
    c = C(name="Cid", age=5)
    assert not isinstance(c, BaseModel)
    assert isinstance(c, Storable)
