class CacheError(Exception):
    pass


class InvalidCachePathError(CacheError):
    pass


class CacheManifestError(CacheError):
    pass


class DownloadError(CacheError):
    pass


class DownloadCancelledError(DownloadError):
    pass


class ChecksumMismatchError(DownloadError):
    pass


class SizeMismatchError(DownloadError):
    pass


class CacheWriteError(DownloadError):
    pass


class StoredContentMissingError(DownloadError):
    pass
