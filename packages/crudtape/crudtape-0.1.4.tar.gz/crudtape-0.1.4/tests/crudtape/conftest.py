import pytest

from crudtape.store import Store

from .test_utils import A, B, C


@pytest.fixture(params=[A, B, C])
def model(request):
    return request.param


@pytest.fixture
def seed_data():
    return [
        {"name": "Ace", "age": 10},
        {"name": "Bob", "age": 20}, 
        {"name": "Cid", "age": 30}
    ]


@pytest.fixture
def store(model, seed_data):
    store = Store(model)
    for o in seed_data:
        store._table.insert(o)
    
    assert store._table.__len__() == 3
    return store


@pytest.fixture
def obj_data():
    return {"name": "Dan", "age": 40}


@pytest.fixture
def obj_no_id(model, obj_data):
    return model(**obj_data)


@pytest.fixture
def obj_with_id(model, obj_data):
    return model(**{"id": 99, **obj_data})


@pytest.fixture
def obj(request):
    return request.getfixturevalue(request.param)
