class CacheError(Exception):
    pass


class InvalidCachePathError(CacheError):
    pass


class CacheManifestError(CacheError):
    pass
