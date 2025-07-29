import pytest

from crudtape.errors import StoreError


def test_all(store, seed_data):
    """Getting all objects."""
    exp = {o["name"]: o for o in seed_data}
    assert len(exp) == 3
    assert store._table.__len__() == 3
    
    res = store.all()
    
    assert len(res) == 3
    for i, obj in enumerate(res):
        assert obj.id == i + 1
        assert obj.name in exp
        assert obj.age == exp[obj.name]["age"]
        del exp[obj.name]
    assert len(exp) == 0


def test_all_empty(store):
    """Getting all objects from an empty store."""
    store._table.truncate()
    assert store._table.__len__() == 0
    
    res = store.all()
    
    assert len(res) == 0


def test_all_error(store, monkeypatch):
    """Getting all objects when underlying storage raises an error."""
    def mock_all(*args, **kwargs):
        raise RuntimeError("database error")
    
    monkeypatch.setattr(store._table, "all", mock_all)
    
    with pytest.raises(StoreError) as exc:
        store.all()
    
    assert isinstance(exc.value.__cause__, RuntimeError)
