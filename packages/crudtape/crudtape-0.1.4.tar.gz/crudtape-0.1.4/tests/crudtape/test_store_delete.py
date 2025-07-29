import pytest

from crudtape.errors import NotFoundError, StoreError


def test_delete_existing(store):
    """Deleting an existing object."""
    assert store._table.__len__() == 3
    
    store.delete(2)
    
    assert store._table.__len__() == 2
    assert store._table.get(doc_id=2) is None


def test_delete_non_existing(store):
    """Deleting a non-existing object."""
    assert store._table.__len__() == 3
    
    with pytest.raises(NotFoundError) as exc:
        store.delete(99)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped
    assert store._table.__len__() == 3  


def test_delete_non_existing_no_exception(monkeypatch, store):
    """Deleting a non-existing object if remove() behaved like get()."""
    def mock_remove(*args, **kwargs):
        return []
    
    monkeypatch.setattr(store._table, "remove", mock_remove)

    with pytest.raises(NotFoundError) as exc:
        store.delete(99)
    
    assert exc.value.__cause__ is None  # should not be re-wrapped
    assert store._table.__len__() == 3  


def test_delete_error(store, monkeypatch):
    """Deleting an object when underlying storage raises an error."""
    def mock_remove(*args, **kwargs):
        raise RuntimeError("database error")
    
    monkeypatch.setattr(store._table, "remove", mock_remove)
    
    with pytest.raises(StoreError) as exc:
        store.delete(1)
    
    assert isinstance(exc.value.__cause__, RuntimeError)
    assert store._table.__len__() == 3  
