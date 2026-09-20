import os
from pathlib import Path

import pytest

TEST_DB = Path(".s_usdv_test.db").resolve()
os.environ["S_USDV_DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

from fastapi.testclient import TestClient

from s_usd_service.config import get_settings

get_settings.cache_clear()

from s_usd_service.app import create_application
from s_usd_service.database.base_class import Base
from s_usd_service.database.session import engine


@pytest.fixture(autouse=True)
def database_schema():
    Base.metadata.create_all(engine)

    yield

    Base.metadata.drop_all(engine)
    engine.dispose()
    TEST_DB.unlink(missing_ok=True)


@pytest.fixture
def client():
    with TestClient(create_application()) as test_client:
        yield test_client