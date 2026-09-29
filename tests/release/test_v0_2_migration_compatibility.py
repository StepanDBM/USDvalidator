from uuid import uuid4

import sqlalchemy as sa
from alembic import command
from alembic.config import Config


def alembic_config(database_url):
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_existing_0004_catalog_survives_upgrade_to_0008(tmp_path, monkeypatch):
    database_path = tmp_path / "legacy.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("S_USDV_DATABASE_URL", database_url)
    from s_usd_service.config import get_settings

    get_settings.cache_clear()
    config = alembic_config(database_url)
    command.upgrade(config, "0004")

    ids = {name: uuid4().hex for name in ("project", "asset", "stream", "version", "file", "run")}
    engine = sa.create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            sa.text(
                "INSERT INTO projects (code, name, description, status, id, created_at, updated_at) "
                "VALUES ('LEGACY_PROJECT', 'Legacy Project', 'Preserve me', 'active', :id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"id": ids["project"]},
        )
        connection.execute(
            sa.text(
                "INSERT INTO assets (project_id, code, name, asset_type, description, status, id, created_at, updated_at) "
                "VALUES (:project, 'asset', 'Asset', 'prop', '', 'active', :id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"project": ids["project"], "id": ids["asset"]},
        )
        connection.execute(
            sa.text(
                "INSERT INTO streams (asset_id, name, description, id, created_at, updated_at) "
                "VALUES (:asset, 'model', '', :id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"asset": ids["asset"], "id": ids["stream"]},
        )
        connection.execute(
            sa.text(
                "INSERT INTO versions (stream_id, number, status, comment, published_content_fingerprint, id, created_at, updated_at) "
                "VALUES (:stream, 1, 'validated', '', NULL, :id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"stream": ids["stream"], "id": ids["version"]},
        )
        connection.execute(
            sa.text(
                "INSERT INTO stored_files (version_id, role, original_name, relative_path, storage_key, content_type, "
                "size_bytes, sha256, status, id, created_at, updated_at) VALUES "
                "(:version, 'root_layer', 'root.usda', 'root.usda', 'legacy/root.usda', 'application/octet-stream', "
                "10, :sha, 'available', :id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {"version": ids["version"], "sha": "a" * 64, "id": ids["file"]},
        )
        connection.execute(
            sa.text(
                "INSERT INTO validation_runs (version_id, stored_file_id, profile_name, report_schema_version, tool_name, "
                "tool_version, configuration_fingerprint, check_catalog_fingerprint, started_at, completed_at, "
                "duration_seconds, publish_passed, total_count, passed_count, failed_count, skipped_count, error_count, "
                "warning_count, report, content_fingerprint, id, created_at, updated_at) VALUES "
                "(:version, :file, 'default', '1.0.0', 'S-USDv', '0.1.0', :fingerprint, :fingerprint, CURRENT_TIMESTAMP, "
                "CURRENT_TIMESTAMP, 0.1, 1, 1, 1, 0, 0, 0, 0, '{}', :fingerprint, :id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            ),
            {
                "version": ids["version"],
                "file": ids["file"],
                "fingerprint": "b" * 64,
                "id": ids["run"],
            },
        )

    command.upgrade(config, "head")
    with engine.connect() as connection:
        project = connection.execute(
            sa.text(
                "SELECT code, workspace_id, created_by_user_id, default_validation_profile, archived_at "
                "FROM projects WHERE id = :id"
            ),
            {"id": ids["project"]},
        ).one()
        assert project.code == "LEGACY_PROJECT"
        assert project.workspace_id
        assert project.created_by_user_id
        assert project.default_validation_profile == "default"
        assert project.archived_at is None
        assert connection.scalar(sa.text("SELECT COUNT(*) FROM assets")) == 1
        assert connection.scalar(sa.text("SELECT COUNT(*) FROM streams")) == 1
        assert connection.scalar(sa.text("SELECT COUNT(*) FROM versions")) == 1
        assert connection.scalar(sa.text("SELECT COUNT(*) FROM stored_files")) == 1
        assert connection.scalar(sa.text("SELECT COUNT(*) FROM validation_runs")) == 1
        assert connection.scalar(sa.text("SELECT COUNT(*) FROM workspaces WHERE code = 'LEGACY'")) == 1
        assert connection.scalar(sa.text("SELECT COUNT(*) FROM workspace_memberships WHERE role = 'owner'")) == 1
        assert connection.scalar(sa.text("SELECT version_num FROM alembic_version")) == "0008"
    engine.dispose()
    get_settings.cache_clear()
