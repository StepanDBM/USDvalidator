from dataclasses import dataclass

import httpx


@dataclass(frozen=True, slots=True)
class ApiClientConfiguration:
    base_url: str = "http://127.0.0.1:8000"
    connect_timeout: float = 3.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    pool_timeout: float = 3.0

    def __post_init__(self):
        normalized = self.base_url.strip().rstrip("/")
        url = httpx.URL(normalized)

        if url.scheme not in {"http", "https"} or not url.host:
            raise ValueError("base_url must be a valid HTTP or HTTPS URL")

        for name in ("connect_timeout", "read_timeout", "write_timeout", "pool_timeout"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be greater than zero")

        object.__setattr__(self, "base_url", normalized)

    def make_timeout(self):
        return httpx.Timeout(
            connect=self.connect_timeout,
            read=self.read_timeout,
            write=self.write_timeout,
            pool=self.pool_timeout
        )
