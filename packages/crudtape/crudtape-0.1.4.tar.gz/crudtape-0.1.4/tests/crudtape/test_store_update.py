import pytest

from crudtape.errors import NotFoundError, StoreError
from crudtape.store import Store

from .test_utils import A, B, C


def test_update_wrong_type():
    """Updating an object of a wrong type."""
    store = Store(A)
    
    with pytest.raises(TypeError):
        store.update(2, B(name="Zoe", age=90))
    
    with pytest.raises(TypeError):
        store.update(2, C(name="Zoe", age=90))


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_update_existing(store, obj):
    """Updating an existing object."""
    assert store._table.__len__() == 3

    res = store.update(2, obj)
    
    assert store._table.__len__() == 3
    
    data = store._table.get(doc_id=2)
    assert data["name"] == obj.name
    assert data["age"] == obj.age
    
    assert isinstance(res, store._model)
    assert res.id == 2
    assert res.name == obj.name
    assert res.age == obj.age


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_update_non_existing(store, obj):
    """Updating a non-existing object."""
    assert store._table.__len__() == 3
    
    with pytest.raises(NotFoundError) as exc:
        store.update(99, obj)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped
    assert store._table.__len__() == 3  


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_update_non_existing_no_exception(monkeypatch, store, obj):
    """Deleting a non-existing object if update() behaved like get()."""
    def mock_update(*args, **kwargs):
        return []
    
    monkeypatch.setattr(store._table, "update", mock_update)

    with pytest.raises(NotFoundError) as exc:
        store.update(99, obj)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped
    assert store._table.__len__() == 3  


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_update_error(monkeypatch, store, obj):
    """Updating an object when underlying storage raises an error."""
    def mock_update(*args, **kwargs):
        raise RuntimeError("database error")
    
    monkeypatch.setattr(store._table, "update", mock_update)
    
    with pytest.raises(StoreError) as exc:
        store.update(2, obj)
    
    assert isinstance(exc.value.__cause__, RuntimeError)


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_update_inconsistent_id(monkeypatch, store, obj):
    """Updating an object when underlying storage return different ID."""
    def mock_update(*args, **kwargs):
        return [99]
    
    monkeypatch.setattr(store._table, "update", mock_update)
    
    with pytest.raises(StoreError) as exc:
        store.update(2, obj)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_update_not_found_after(monkeypatch, store, obj):
    """Updating an object that is not found afterward."""
    def mock_get(*args, **kwargs):
        raise NotFoundError("not found")
    
    monkeypatch.setattr(store, "get", mock_get)
    
    with pytest.raises(StoreError) as exc:
        store.update(2, obj)
    
    assert isinstance(exc.value.__cause__, NotFoundError)  # original suppressed


@pytest.mark.parametrize("obj", ["obj_no_id", "obj_with_id"], indirect=True)
def test_update_error_after(monkeypatch, store, obj):
    """Updating an object that fails on retrieval afterwards."""
    def mock_get(*args, **kwargs):
        raise StoreError("database error")
    
    monkeypatch.setattr(store, "get", mock_get)
    
    with pytest.raises(StoreError) as exc:
        store.update(2, obj)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped
