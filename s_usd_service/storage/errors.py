class StorageError(Exception):
    pass


class InvalidStorageKeyError(StorageError):
    pass


class StorageObjectNotFoundError(StorageError):
    pass
