import os
from pathlib import Path

import pytest

TEST_DB = Path(".s_usdv_test.db").resolve()
TEST_DATA = Path(".s_usdv_test_data").resolve()
os.environ["S_USDV_DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["S_USDV_DATA_ROOT"] = TEST_DATA.as_posix()
os.environ["S_USDV_STORAGE_ROOT"] = (TEST_DATA / "storage").as_posix()
os.environ["S_USDV_TEMPORARY_ROOT"] = (TEST_DATA / "temp").as_posix()
os.environ["S_USDV_TOKEN_SIGNING_KEY"] = "pytest-signing-key-at-least-32-bytes-long"
os.environ["S_USDV_ALLOW_REGISTRATION"] = "true"
os.environ["S_USDV_VALIDATION_WORKER_ENABLED"] = "false"

from fastapi.testclient import TestClient

from s_usd_service.config import get_settings

get_settings.cache_clear()

from sqlalchemy import select

from s_usd_service.api.dependencies import get_object_storage
from s_usd_service.app import create_application
from s_usd_service.database.base_class import Base
from s_usd_service.database.models.user import User
from s_usd_service.database.session import SessionLocal, engine


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
        credentials = {
            "email": "test-owner@example.com",
            "display_name": "Test Owner",
            "password": "correct horse battery staple",
        }
        assert test_client.post("/api/v1/auth/register", json=credentials).status_code == 201
        login = test_client.post(
            "/api/v1/auth/login",
            json={"email": credentials["email"], "password": credentials["password"]},
        )
        assert login.status_code == 200
        test_client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        workspace = test_client.post("/api/v1/workspaces", json={"code": "TEST", "name": "Test Workspace"})
        assert workspace.status_code == 201
        test_client.workspace_id = workspace.json()["id"]
        with SessionLocal() as database:
            user = database.scalar(select(User).where(User.email == credentials["email"]))
            user.is_platform_admin = True
            database.commit()
        yield test_client


@pytest.fixture
def anonymous_client():
    with TestClient(create_application()) as test_client:
        yield test_client
