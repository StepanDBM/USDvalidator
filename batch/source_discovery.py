from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path


USD_EXTENSIONS = frozenset({".usd", ".usda", ".usdc", ".usdz"})


@dataclass(frozen=True)
class SourceDiscoveryOptions:
    recursive: bool = True
    extensions: frozenset[str] = USD_EXTENSIONS
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    excluded_directories: frozenset[str] = field(
        default_factory=lambda: frozenset({".git", "__pycache__", ".pytest_cache"})
    )


def discover_usd_files(source, options=None):
    options = options or SourceDiscoveryOptions()
    source = Path(source).expanduser()

    if not source.exists():
        raise FileNotFoundError(f"Source does not exist: {source}")
    if source.is_file():
        return (source.resolve(),) if _matches(source, source.parent, options) else ()
    if not source.is_dir():
        raise ValueError(f"Source must be a file or directory: {source}")

    iterator = source.rglob("*") if options.recursive else source.iterdir()
    paths = {
        path.resolve()
        for path in iterator
        if path.is_file()
        and not _in_excluded_directory(path, source, options)
        and _matches(path, source, options)
    }
    return tuple(sorted(paths, key=lambda path: path.as_posix().lower()))


def _matches(path, root, options):
    if path.suffix.lower() not in options.extensions:
        return False

    relative = path.relative_to(root).as_posix()
    if options.include_patterns and not any(
        fnmatch(relative, pattern) for pattern in options.include_patterns
    ):
        return False
    return not any(fnmatch(relative, pattern) for pattern in options.exclude_patterns)


def _in_excluded_directory(path, root, options):
    relative_parts = path.relative_to(root).parts[:-1]
    return any(part in options.excluded_directories for part in relative_parts)
