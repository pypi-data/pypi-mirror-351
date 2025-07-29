import pytest

from crudtape.store import Store

from .test_utils import A, B, C


def test_enforce_type_positional():
    """Enforcing store type with positional argument."""
    store = Store(A)
    
    res = store.insert(A(name="Ash", age=3))
    assert isinstance(res, A)
    
    with pytest.raises(TypeError):
        store.insert(B(name="Bob", age=4))
    
    with pytest.raises(TypeError):
        store.insert(C(name="Cid", age=4))


def test_enforce_type_named():
    """Enforcing store type with keyword arguments"""
    store = Store(A)
    
    res = store.insert(obj=A(name="Ash", age=3))
    assert isinstance(res, A)
    
    with pytest.raises(TypeError):
        store.insert(obj=B(name="Bob", age=4))
    
    with pytest.raises(TypeError):
        store.insert(obj=C(name="Cid", age=4))


def test_enforce_type_missing_arg():
    """Enforcing store type with missing argument."""
    store = Store(A)
    
    with pytest.raises(TypeError):
        store.insert()
