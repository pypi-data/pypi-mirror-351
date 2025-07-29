import pytest

from crudtape.errors import NotFoundError, StoreError


def test_get_existing(store, seed_data):
    """Getting an existing object."""
    assert store._table.__len__() == 3
    
    res = store.get(2)

    assert res.id == 2
    assert res.name == seed_data[1]["name"]
    assert res.age == seed_data[1]["age"]


def test_get_existing_list(monkeypatch, store):
    """Getting an existing object when underlying storage returns a list."""
    def mock_get(*args, **kwargs):
        return [{"id": 99, "name": "Zoe", "age": 90}]
    
    monkeypatch.setattr(store._table, "get", mock_get)
    
    res = store.get(99)

    assert res.id == 99
    assert res.name == "Zoe"
    assert res.age == 90


def test_get_non_existing(store):
    """Getting an non-existing object."""
    assert store._table.__len__() == 3

    with pytest.raises(NotFoundError) as exc:
        store.get(99)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped


def test_get_non_existing_list(monkeypatch, store):
    """Getting an non-existing object when underlying storage returns a list."""
    def mock_get(*args, **kwargs):
        return []
    
    monkeypatch.setattr(store._table, "get", mock_get)
    
    with pytest.raises(NotFoundError) as exc:
        store.get(99)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped


@pytest.mark.parametrize("bad", ["str", ["list"]])
def test_get_invalid_data(store, monkeypatch, bad):
    """Getting an object when underlying storage returns bad data type."""
    def mock_get(*args, **kwargs):
        return bad
    
    monkeypatch.setattr(store._table, "get", mock_get)
    
    with pytest.raises(StoreError) as exc:
        store.get(1)
    
    assert not isinstance(exc.value, NotFoundError)
    assert exc.value.__cause__ is None  # should not be re-wrapped


def test_get_error(store, monkeypatch):
    """Getting an object when underlying storage raises an error."""
    def mock_get(*args, **kwargs):
        raise RuntimeError("database error")
    
    monkeypatch.setattr(store._table, "get", mock_get)
    
    with pytest.raises(StoreError) as exc:
        store.get(1)
    assert isinstance(exc.value.__cause__, RuntimeError)
