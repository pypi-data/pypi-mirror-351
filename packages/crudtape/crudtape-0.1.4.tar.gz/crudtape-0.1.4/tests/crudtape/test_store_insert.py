import pytest

from crudtape.errors import NotFoundError, StoreError
from crudtape.store import Store

from .test_utils import A, B, C


def test_insert_wrong_type():
    """Inserting an object of a wrong type."""
    store = Store(A)
    
    with pytest.raises(TypeError):
        store.insert(B(name="Zoe", age=90))
    
    with pytest.raises(TypeError):
        store.insert(C(name="Zoe", age=90))


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_insert(store, obj):
    """Inserting an object"""
    assert store._table.__len__() == 3

    res = store.insert(obj)
    
    assert store._table.__len__() == 4
    
    data = store._table.get(doc_id=4)
    assert data["name"] == obj.name
    assert data["age"] == obj.age

    assert isinstance(res, store._model)
    assert res.id == 4
    assert res.name == obj.name
    assert res.age == obj.age


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_insert_error(monkeypatch, store, obj):
    """Inserting an object when underlying storage raises an error."""
    def mock_insert(*args, **kwargs):
        raise RuntimeError("database error")
    
    monkeypatch.setattr(store._table, "insert", mock_insert)
    
    with pytest.raises(StoreError) as exc:
        store.insert(obj)
    
    assert isinstance(exc.value.__cause__, RuntimeError)


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_insert_not_found_after(monkeypatch, store, obj):
    """Inserting an object that is not found afterward."""
    def mock_get(*args, **kwargs):
        raise NotFoundError("not found")
    
    monkeypatch.setattr(store, "get", mock_get)
    
    with pytest.raises(StoreError) as exc:
        store.insert(obj)
    
    assert isinstance(exc.value.__cause__, NotFoundError)  # original suppressed


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_insert_error_after(monkeypatch, store, obj):
    """Inserting an object that fails on retrieval afterwards."""
    def mock_get(*args, **kwargs):
        raise StoreError("database error")
    
    monkeypatch.setattr(store, "get", mock_get)
    
    with pytest.raises(StoreError) as exc:
        store.insert(obj)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped
