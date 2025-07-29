class StoreError(Exception):
    """Base exception class for all store-related errors."""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NotFoundError(StoreError):
    """Exception raised when a requested object cannot be found in the store."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
