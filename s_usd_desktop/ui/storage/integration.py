from PySide6.QtCore import QTimer

from s_usd_desktop.cache import CacheManager
from s_usd_desktop.services.catalog_service import CatalogService
from s_usd_desktop.services.download_service import DownloadService
from s_usd_desktop.services.version_download_service import VersionDownloadService
from s_usd_desktop.services.version_open_service import VersionOpenService
from s_usd_desktop.services.validation_submission_service import ValidationSubmissionService
from s_usd_desktop.services.validation_history_service import ValidationHistoryService
from s_usd_desktop.services.stored_comparison_service import StoredComparisonService
from s_usd_desktop.services.transfer_service import TransferService
from s_usd_desktop.services.connection_service import ConnectionState
from s_usd_desktop.ui.storage.workspace import StorageWorkspace
from s_usd_desktop.ui.storage.dialogs.cache_settings import CacheSettings


def install_storage_workspace(window):
    if hasattr(window, "storage_workspace"):
        return window.storage_workspace

    window.catalog_service = CatalogService(window.connection_service, parent=window)
    window.storage_workspace = StorageWorkspace(window.catalog_service, parent=window)
    window.transfer_service = TransferService(window.connection_service, parent=window)
    window.storage_workspace.set_transfer_service(window.transfer_service)
    window.cache_settings = CacheSettings()
    window.cache_manager = CacheManager(window.cache_settings.configuration())
    window.download_service = DownloadService(
        window.connection_service,
        cache_manager=window.cache_manager,
        parent=window
    )
    window.storage_workspace.set_cache_services(
        window.cache_manager,
        window.download_service,
        window.cache_settings
    )
    window.stored_comparison_service = StoredComparisonService(
        window.connection_service,
        window.cache_manager,
        parent=window
    )
    window.storage_workspace.set_stored_comparison_service(
        window.stored_comparison_service
    )
    window.storage_workspace.comparison_pair_ready.connect(
        lambda pair: _open_stored_comparison(window, pair)
    )
    window.storage_workspace.comparison_preparation_requested.connect(
        lambda _pair: window.storage_workspace.status_label.setText(
            "Nope, not yet integrated, but this signal works :D"
        )
    )
    window.version_open_service = VersionOpenService(window.cache_manager)
    window.version_download_service = VersionDownloadService(
        window.connection_service,
        window.cache_manager,
        parent=window
    )
    window.storage_workspace.set_version_services(
        window.version_open_service,
        window.version_download_service
    )
    window.storage_workspace.local_source_open_requested.connect(
        lambda path: _open_cached_source(window, path, validate=False)
    )
    window.validation_history_service = ValidationHistoryService(
        window.connection_service,
        parent=window
    )
    window.storage_workspace.set_validation_history_service(
        window.validation_history_service
    )
    window.storage_workspace.historical_report_ready.connect(
        lambda report: _show_historical_report(window, report)
    )
    window.validation_submission_service = ValidationSubmissionService(
        window.connection_service,
        parent=window
    )
    window.storage_workspace.local_source_validation_requested.connect(
        lambda path, version_id, stored_file_id: _validate_cached_source(
            window,
            path,
            version_id,
            stored_file_id
        )
    )
    window.validation_view.report_ready.connect(
        window.validation_submission_service.submit_matching_report
    )
    window.validation_submission_service.submission_started.connect(
        lambda _target: window.storage_workspace.status_label.setText(
            "Validation complete. Saving validation history..."
        )
    )
    window.validation_submission_service.submission_completed.connect(
        lambda record: _validation_history_saved(window, record)
    )
    window.validation_submission_service.submission_failed.connect(
        lambda message: window.storage_workspace.status_label.setText(
            f"Validation completed, but history could not be saved: {message}"
        )
    )
    window.validation_submission_service.submission_skipped.connect(
        window.storage_workspace.status_label.setText
    )
    window.tabs.addTab(window.storage_workspace, "Storage")
    window.tab_bar.addTab("Storage")
    window.connection_service.connected.connect(
        lambda _health: window.storage_workspace.set_connected(True)
    )
    window.connection_service.disconnected.connect(
        lambda: window.storage_workspace.set_connected(False)
    )
    window.connection_service.connection_failed.connect(
        lambda _error: window.storage_workspace.set_connected(False)
    )

    if window.connection_service.state == ConnectionState.CONNECTED:
        window.storage_workspace.set_connected(True)

    return window.storage_workspace


def _open_cached_source(window, path, validate=False):
    window.validation_view.source_selector.set_source(path)
    index = window.tabs.indexOf(window.validation_view)
    window.tabs.setCurrentIndex(index)
    window.tab_bar.setCurrentIndex(index)


def _validate_cached_source(window, path, version_id, stored_file_id):
    window.validation_submission_service.expect_report(
        version_id,
        stored_file_id,
        path
    )
    _open_cached_source(window, path)

    if not window.validation_view.validate_source(path):
        window.validation_submission_service.clear_pending()


def _validation_history_saved(window, record):
    window.storage_workspace.status_label.setText(
        f"Validation history saved: {record.id}"
    )
    if record.version_id == window.storage_workspace.current_version_id:
        window.storage_workspace._refresh_validation_history()


def _show_historical_report(window, report):
    from pathlib import Path

    window.validation_view.results_view.show_single_report(report)
    if Path(report.source_path).is_file():
        window.validation_view.source_selector.set_source(report.source_path)
    index = window.tabs.indexOf(window.validation_view)
    window.tabs.setCurrentIndex(index)
    window.tab_bar.setCurrentIndex(index)


def _open_stored_comparison(window, pair):
    window.comparison_view.set_sources(pair.base.root_path, pair.target.root_path)
    index = window.tabs.indexOf(window.comparison_view)
    window.tabs.setCurrentIndex(index)
    window.tab_bar.setCurrentIndex(index)
    QTimer.singleShot(0, window.comparison_view.start_comparison)
