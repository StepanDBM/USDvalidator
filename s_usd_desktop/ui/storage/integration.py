from s_usd_desktop.services.catalog_service import CatalogService
from s_usd_desktop.services.transfer_service import TransferService
from s_usd_desktop.services.connection_service import ConnectionState
from s_usd_desktop.ui.storage.workspace import StorageWorkspace


def install_storage_workspace(window):
    if hasattr(window, "storage_workspace"):
        return window.storage_workspace

    window.catalog_service = CatalogService(window.connection_service, parent=window)
    window.storage_workspace = StorageWorkspace(window.catalog_service, parent=window)
    window.transfer_service = TransferService(window.connection_service, parent=window)
    window.storage_workspace.set_transfer_service(window.transfer_service)
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
