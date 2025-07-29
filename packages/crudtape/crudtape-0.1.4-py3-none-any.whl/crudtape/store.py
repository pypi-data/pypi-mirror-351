import secrets
from collections.abc import Callable
from functools import wraps
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from .errors import NotFoundError, StoreError


@runtime_checkable
class Storable(Protocol):
    """Minimal interface required for a storable object.

    This protocol defines a simplified, generalized subset of the Pydantic model 
    interface, including only the methods actually used by the `Store` class. It 
    enables seamless integration with Pydantic models without introducing a direct 
    dependency on the Pydantic library, while also supporting custom model classes 
    that meet the same minimal requirements.
    """
    
    def __init__(self, **kwargs: Any) -> None: 
        """Initializes the object with the given keyword arguments.
        
        The object is required to support an `id` (int) attribute.

        Args:
            **kwargs: Keyword arguments to initialize the object.
        """
        ...  # pragma: no cover
    
    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]: 
        """Dumps the object into a dictionary.
        
        The `id` attribute should be omitted, as it is ignored by the store, 
        which handles ID management internally.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            A dictionary representation of the object.
        """
        ...  # pragma: no cover
    

T = TypeVar('T', bound=Storable)

_db = TinyDB(storage=MemoryStorage)


def enforce_type(method: Callable) -> Callable:
    """Decorator enforcing that inbound object matches the declared store model."""
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        # look for keyword parameter
        if "obj" in kwargs:
            obj = kwargs["obj"]
        
        # fallback to positional argument
        else:
            arg_names = method.__code__.co_varnames[1:len(args)+1]
            params = dict(zip(arg_names, args, strict=False))
            obj = params.get("obj")
            
        if not isinstance(obj, self._model):
            raise TypeError(f"Expected type {self._model.__name__}, got {type(obj).__name__}")
            
        return method(self, *args, **kwargs)
    return wrapper


class Store(Generic[T]):
    """Simple in-memory CRUD store for Pydantic-like objects."""
    def __init__(self, model: type[T]):
        self._model = model
        self._table = _db.table(secrets.token_hex(3))


    def all(self) -> list[T]:
        """Retrieve all objects.

        Returns:
            A list of all objects.

        Raises:
            StoreError: For any failure.
        """
        try:
            # CAUTION: all() doesn't put the doc_id in the dict representation.

            return [self._model(id=d.doc_id, **d) for d in self._table.all()]
        except Exception as exc:
            raise StoreError("Failed to retrieve all objects") from exc
    
    
    def get(self, id: int) -> T:
        """Retrieve an object by its ID.

        Args:
            id: ID of an object.

        Returns:
            A retrieved object.

        Raises:
            NotFoundError: If the given ID does not exist.
            StoreError: For any other failure.
        """
        try:
            data = self._table.get(doc_id=id)
            if not data:
                raise NotFoundError(f"Object not found [id={id}]")

            if isinstance(data, list):
                data = data[0]
            if not isinstance(data, dict):
                raise StoreError(f"Unexpected return type detected [id={id}]")
            
            data["id"] = id
            return self._model(**data)
        
        except StoreError:
            raise
        except Exception as exc:
            raise StoreError("Failed to retrieve object [id={id}]") from exc

    
    @enforce_type
    def insert(self, obj: T) -> T:
        """Insert a new object.

        Args:
            obj: Object to insert.

        Returns:
            An inserted object with its assigned ID.

        Raises:
            TypeError: If the object is of an incompatible type.
            StoreError: For any other failure.
        """
        try:
            data = obj.model_dump()
            data.pop("id", None)

            id = self._table.insert(data)
            return self.get(id)
        
        except NotFoundError as nfe:
            raise StoreError("Object missing after insert") from nfe
        except StoreError:
            raise
        except Exception as exc:
            raise StoreError("Failed to insert object") from exc

    
    @enforce_type
    def update(self, id: int, obj: T) -> T:
        """Update an object by its ID.

        Args:
            id: ID of an object.
            obj: Object to update.

        Returns:
            An updated object.

        Raises:
            TypeError: If the object is of an incompatible type.
            NotFoundError: If the given ID does not exist.
            StoreError: For any other failure.
        """
        try:
            data = obj.model_dump()
            data.pop("id", None)

            res = self._table.update(data, doc_ids=[id])
            if not res: 
                raise NotFoundError(f"Object not found [id={id}]")
            if id != res[0]:
                raise StoreError(f"Object ID inconsistent after update [{id} / {res[0]}]")
        
        # CAUTION: update() raises KeyError for missing doc_id rather than returning 
        # None as get() does (see https://github.com/msiemens/tinydb/issues/591).

        except KeyError:
            raise NotFoundError("Object not found [id={id}]") from None
        except StoreError:
            raise
        except Exception as exc:
            raise StoreError("Failed to update object") from exc
            
        try:
            return self.get(id)
        
        except NotFoundError as nfe:
            raise StoreError("Object missing after update") from nfe

    
    def delete(self, id: int) -> None:
        """Delete an object by its ID.

        Args:
            id: ID of an object.

        Raises:
            NotFoundError: If the given ID does not exist.
            StoreError: For any other failure.
        """
        try:
            if not self._table.remove(doc_ids=[id]):
                raise NotFoundError(f"Object not found [id={id}]")

        # CAUTION: remove() raises KeyError doc_id rather than returning None
        # as get() does (see https://github.com/msiemens/tinydb/issues/591).

        except KeyError:
            raise NotFoundError("Object not found [id={id}]") from None
        except StoreError:
            raise
        except Exception as exc:
            raise StoreError("Failed to delete object [id={id}]") from exc
