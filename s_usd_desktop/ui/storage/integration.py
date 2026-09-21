from s_usd_desktop.cache import CacheManager
from s_usd_desktop.services.catalog_service import CatalogService
from s_usd_desktop.services.download_service import DownloadService
from s_usd_desktop.services.version_download_service import VersionDownloadService
from s_usd_desktop.services.version_open_service import VersionOpenService
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
    window.storage_workspace.local_source_validation_requested.connect(
        lambda path: _open_cached_source(window, path, validate=True)
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


def _open_cached_source(window, path, validate):
    window.validation_view.source_selector.set_source(path)
    if validate:
        window.validation_view.validate_source(path)
    index = window.tabs.indexOf(window.validation_view)
    window.tabs.setCurrentIndex(index)
    window.tab_bar.setCurrentIndex(index)
