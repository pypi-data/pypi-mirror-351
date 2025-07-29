from crudtape.errors import NotFoundError, StoreError


def test_error_hierarchy():
    """Test the inheritance hierarchy of error classes."""
    assert issubclass(NotFoundError, StoreError)
    assert issubclass(StoreError, Exception) 


def test_store_error():
    message = "generic error message"
    error = StoreError(message)
    
    assert str(error) == message
    assert isinstance(error, Exception)


def test_not_found_error():
    message = "not found error message"
    error = NotFoundError(message)
    
    assert str(error) == message
    assert isinstance(error, StoreError)
    assert isinstance(error, Exception)
