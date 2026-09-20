import os
from pathlib import Path

import pytest

TEST_DB = Path(".s_usdv_test.db").resolve()
TEST_DATA = Path(".s_usdv_test_data").resolve()
os.environ["S_USDV_DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["S_USDV_DATA_ROOT"] = TEST_DATA.as_posix()
os.environ["S_USDV_STORAGE_ROOT"] = (TEST_DATA / "storage").as_posix()
os.environ["S_USDV_TEMPORARY_ROOT"] = (TEST_DATA / "temp").as_posix()

from fastapi.testclient import TestClient

from s_usd_service.config import get_settings

get_settings.cache_clear()

from s_usd_service.api.dependencies import get_object_storage
from s_usd_service.app import create_application
from s_usd_service.database.base_class import Base
from s_usd_service.database.session import engine


@pytest.fixture(autouse=True)
def database_schema():
    get_object_storage.cache_clear()
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    engine.dispose()
    get_object_storage.cache_clear()
    TEST_DB.unlink(missing_ok=True)

    if TEST_DATA.exists():
        import shutil
        shutil.rmtree(TEST_DATA)


@pytest.fixture
def client():
    with TestClient(create_application()) as test_client:
        yield test_client
