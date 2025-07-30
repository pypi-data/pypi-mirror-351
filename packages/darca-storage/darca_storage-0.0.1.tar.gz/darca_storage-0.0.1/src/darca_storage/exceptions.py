from darca_exception import DarcaException


class StorageClientPathViolation(DarcaException):
    """
    Raised when a requested path escapes the storage client's base boundary.
    """

    def __init__(self, attempted_path: str, base_path: str):
        super().__init__(
            message=(
                f"Access to '{attempted_path}' is outside the storage"
                f" base path '{base_path}'."
            ),
            error_code="PATH_ESCAPES_STORAGE_ROOT",
            metadata={
                "attempted_path": attempted_path,
                "base_path": base_path,
            },
        )
