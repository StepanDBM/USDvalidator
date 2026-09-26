import os
import subprocess
import sys
import textwrap

import pytest

pytest.importorskip("PySide6")


def run_qt(code):
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=os.getcwd(),
        env=environment,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, (
        f"Qt subprocess failed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_storage_controls_have_explanatory_tooltips():
    run_qt("""
        from PySide6.QtWidgets import QApplication

        from s_usd_desktop.services.catalog_service import CatalogService
        from s_usd_desktop.ui.storage.workspace import StorageWorkspace

        application = QApplication([])
        catalog_service = CatalogService(object())
        workspace = StorageWorkspace(catalog_service)

        controls = {
            "projects": workspace.project_view,
            "assets": workspace.asset_view,
            "streams": workspace.stream_view,
            "versions": workspace.version_view,
            "files": workspace.file_view,
            "upload": workspace.upload_button,
            "download": workspace.download_button,
            "download_root": workspace.download_root_button,
            "download_version": workspace.download_version_button,
            "open_version": workspace.open_version_button,
            "validate": workspace.validate_version_button,
            "lifecycle": workspace.lifecycle_button,
            "deprecate": workspace.deprecate_button,
            "compare": workspace.compare_versions_button,
            "reveal": workspace.reveal_button,
            "remove_cache": workspace.remove_cache_button,
            "clear_cache": workspace.clear_version_cache_button,
            "cache_settings": workspace.cache_settings_button,
            "refresh": workspace.refresh_button,
            "progress": workspace.progress_bar,
            "cancel": workspace.cancel_upload_button,
            "history": workspace.validation_history_view,
            "refresh_history": workspace.refresh_history_button,
            "open_history": workspace.open_history_button
        }

        for name, control in controls.items():
            assert len(control.toolTip()) >= 20, (
                f"{name} has a missing or insufficient tooltip: "
                f"{control.toolTip()!r}"
            )

        workspace.close()
        application.processEvents()
    """)


def test_storage_models_expose_contextual_row_tooltips():
    run_qt("""
        from types import SimpleNamespace

        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        from s_usd_desktop.ui.storage.models import (
            ProjectListModel,
            StoredFileTableModel,
            VersionTableModel
        )

        application = QApplication([])

        project = ProjectListModel()
        project.set_records((
            SimpleNamespace(
                id="p1",
                code="KAN",
                name="Kaneda",
                description="Project"
            ),
        ))
        project_tooltip = project.data(
            project.index(0, 0),
            Qt.ItemDataRole.ToolTipRole
        )
        assert "KAN" in project_tooltip

        version = VersionTableModel()
        version.set_records((
            SimpleNamespace(
                id="v1",
                display_name="v001",
                number=1,
                status="draft",
                comment="Work",
                updated_at=SimpleNamespace(
                    strftime=lambda value: "date"
                )
            ),
        ))
        version_tooltip = version.data(
            version.index(0, 0),
            Qt.ItemDataRole.ToolTipRole
        )
        assert "draft" in version_tooltip

        files = StoredFileTableModel()
        files.set_records((
            SimpleNamespace(
                id="f1",
                original_name="root.usda",
                relative_path="root.usda",
                role="root_layer",
                size_bytes=10,
                status="available",
                sha256="abc"
            ),
        ))
        file_tooltip = files.data(
            files.index(0, 0),
            Qt.ItemDataRole.ToolTipRole
        )
        assert "root.usda" in file_tooltip

        application.processEvents()
    """)


def test_storage_dialog_controls_have_tooltips():
    run_qt("""
        from pathlib import Path

        from PySide6.QtWidgets import QApplication

        from s_usd_desktop.cache import CacheConfiguration
        from s_usd_desktop.ui.storage.dialogs import (
            CacheSettingsDialog,
            UploadFileDialog
        )

        application = QApplication([])

        upload = UploadFileDialog(initial_role="root_layer")
        upload_controls = {
            "local_file": upload.path,
            "role": upload.role,
            "relative_path": upload.relative_path
        }

        for name, control in upload_controls.items():
            assert len(control.toolTip()) >= 20, (
                f"{name} has a missing or insufficient tooltip: "
                f"{control.toolTip()!r}"
            )

        configuration = CacheConfiguration(
            root=Path.cwd() / ".test-cache",
            maximum_bytes=50 * 1024**3,
            verify_on_access=True
        )
        cache = CacheSettingsDialog(configuration)

        cache_controls = {
            "cache_root": cache.root,
            "maximum_gib": cache.maximum_gib,
            "verify_sha256": cache.verify
        }

        for name, control in cache_controls.items():
            assert len(control.toolTip()) >= 20, (
                f"{name} has a missing or insufficient tooltip: "
                f"{control.toolTip()!r}"
            )

        upload.close()
        cache.close()
        application.processEvents()
    """)