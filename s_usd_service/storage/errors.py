class StorageError(Exception):
    pass


class InvalidStorageKeyError(StorageError):
    pass


class StorageObjectNotFoundError(StorageError):
    pass


class StorageLimitExceededError(StorageError):
    def __init__(self, maximum_bytes):
        self.maximum_bytes = maximum_bytes
        super().__init__(f"Upload exceeds the {maximum_bytes}-byte limit")
