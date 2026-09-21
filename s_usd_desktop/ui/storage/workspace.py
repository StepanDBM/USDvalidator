from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget
)

from s_usd_desktop.ui.storage.models import (
    AssetListModel,
    ProjectListModel,
    StoredFileTableModel,
    StreamListModel,
    VersionTableModel
)


class StorageWorkspace(QWidget):
    def __init__(self, catalog_service, parent=None):
        super().__init__(parent)
        self.catalog_service = catalog_service
        self.connected = False
        self.current_project_id = None
        self.current_asset_id = None
        self.current_stream_id = None
        self.current_version_id = None
        self.project_model = ProjectListModel(self)
        self.asset_model = AssetListModel(self)
        self.stream_model = StreamListModel(self)
        self.version_model = VersionTableModel(self)
        self.file_model = StoredFileTableModel(self)
        self._build_ui()
        self._connect_signals()
        self.set_connected(False)

    def _build_ui(self):
        self.status_label = QLabel("Connect to S-USDv Service to browse storage.")
        self.status_label.setWordWrap(True)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setEnabled(False)
        header = QHBoxLayout()
        header.addWidget(QLabel("S-USDv Storage"))
        header.addStretch()
        header.addWidget(self.refresh_button)

        self.project_view = self._make_list(self.project_model)
        self.asset_view = self._make_list(self.asset_model)
        self.stream_view = self._make_list(self.stream_model)
        self.version_view = self._make_table(self.version_model)
        self.version_view.horizontalHeader().setStretchLastSection(True)
        browser = QSplitter(Qt.Horizontal)
        browser.addWidget(self._group("Projects", self.project_view))
        browser.addWidget(self._group("Assets", self.asset_view))
        browser.addWidget(self._group("Streams", self.stream_view))
        browser.addWidget(self._group("Versions", self.version_view))
        browser.setSizes([220, 240, 180, 500])

        self.file_view = self._make_table(self.file_model)
        self.file_view.horizontalHeader().setStretchLastSection(True)
        self.detail_title = QLabel("No version selected")
        self.detail_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        self.detail_status = QLabel("Status: —")
        self.detail_comment = QLabel("Comment: —")
        self.detail_comment.setWordWrap(True)
        self.detail_files = QLabel("Files: 0")
        details = QFrame()
        details_layout = QVBoxLayout(details)
        details_layout.addWidget(self.detail_title)
        details_layout.addWidget(self.detail_status)
        details_layout.addWidget(self.detail_comment)
        details_layout.addWidget(self.detail_files)
        details_layout.addStretch()
        lower = QSplitter(Qt.Horizontal)
        lower.addWidget(self._group("Stored Files", self.file_view))
        lower.addWidget(self._group("Version Details", details))
        lower.setSizes([800, 400])

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(browser)
        main_splitter.addWidget(lower)
        main_splitter.setSizes([420, 280])
        layout = QVBoxLayout(self)
        layout.addLayout(header)
        layout.addWidget(self.status_label)
        layout.addWidget(main_splitter, 1)

    @staticmethod
    def _group(title, widget):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(widget)
        return group

    @staticmethod
    def _make_list(model):
        view = QListView()
        view.setModel(model)
        view.setSelectionMode(QAbstractItemView.SingleSelection)
        view.setAlternatingRowColors(True)
        return view

    @staticmethod
    def _make_table(model):
        view = QTableView()
        view.setModel(model)
        view.setSelectionBehavior(QAbstractItemView.SelectRows)
        view.setSelectionMode(QAbstractItemView.SingleSelection)
        view.setAlternatingRowColors(True)
        view.setSortingEnabled(False)
        return view

    def _connect_signals(self):
        self.refresh_button.clicked.connect(self.refresh)
        self.project_view.selectionModel().currentChanged.connect(self._project_selected)
        self.asset_view.selectionModel().currentChanged.connect(self._asset_selected)
        self.stream_view.selectionModel().currentChanged.connect(self._stream_selected)
        self.version_view.selectionModel().currentChanged.connect(self._version_selected)
        self.catalog_service.projects_loaded.connect(self._projects_loaded)
        self.catalog_service.assets_loaded.connect(self._assets_loaded)
        self.catalog_service.streams_loaded.connect(self._streams_loaded)
        self.catalog_service.versions_loaded.connect(self._versions_loaded)
        self.catalog_service.files_loaded.connect(self._files_loaded)
        self.catalog_service.loading_changed.connect(self._loading_changed)
        self.catalog_service.request_failed.connect(self._request_failed)

    def set_connected(self, connected):
        self.connected = connected
        self.refresh_button.setEnabled(connected)

        if connected:
            self.status_label.setText("Connected. Loading projects...")
            self.refresh()
        else:
            self.status_label.setText("Connect to S-USDv Service to browse storage.")
            self._clear_all()

    def refresh(self):
        if not self.connected:
            return

        self._clear_all()
        self.status_label.setText("Loading projects...")
        self.catalog_service.load_projects()

    def _project_selected(self, current, _previous):
        project = self.project_model.record_at(current.row()) if current.isValid() else None
        self.current_project_id = project.id if project else None
        self.current_asset_id = self.current_stream_id = self.current_version_id = None
        self.asset_model.clear()
        self.stream_model.clear()
        self.version_model.clear()
        self.file_model.clear()
        self._show_version(None)
        self.catalog_service.invalidate("streams", "versions", "files")

        if project:
            self.status_label.setText(f"Loading assets for {project.code}...")
            self.catalog_service.load_assets(project.id)

    def _asset_selected(self, current, _previous):
        asset = self.asset_model.record_at(current.row()) if current.isValid() else None
        self.current_asset_id = asset.id if asset else None
        self.current_stream_id = self.current_version_id = None
        self.stream_model.clear()
        self.version_model.clear()
        self.file_model.clear()
        self._show_version(None)
        self.catalog_service.invalidate("versions", "files")

        if asset:
            self.status_label.setText(f"Loading streams for {asset.code}...")
            self.catalog_service.load_streams(asset.id)

    def _stream_selected(self, current, _previous):
        stream = self.stream_model.record_at(current.row()) if current.isValid() else None
        self.current_stream_id = stream.id if stream else None
        self.current_version_id = None
        self.version_model.clear()
        self.file_model.clear()
        self._show_version(None)
        self.catalog_service.invalidate("files")

        if stream:
            self.status_label.setText(f"Loading versions for {stream.name}...")
            self.catalog_service.load_versions(stream.id)

    def _version_selected(self, current, _previous):
        version = self.version_model.record_at(current.row()) if current.isValid() else None
        self.current_version_id = version.id if version else None
        self.file_model.clear()
        self._show_version(version)

        if version:
            self.status_label.setText(f"Loading files for {version.display_name}...")
            self.catalog_service.load_files(version.id)

    def _projects_loaded(self, records):
        self.project_model.set_records(records)
        self.status_label.setText("Select a project." if records else "No projects found.")

    def _assets_loaded(self, project_id, records):
        if project_id != self.current_project_id:
            return
        self.asset_model.set_records(records)
        self.status_label.setText("Select an asset." if records else "No assets found.")

    def _streams_loaded(self, asset_id, records):
        if asset_id != self.current_asset_id:
            return
        self.stream_model.set_records(records)
        self.status_label.setText("Select a stream." if records else "No streams found.")

    def _versions_loaded(self, stream_id, records):
        if stream_id != self.current_stream_id:
            return
        self.version_model.set_records(records)
        self.status_label.setText("Select a version." if records else "No versions found.")

    def _files_loaded(self, version_id, collection):
        if version_id != self.current_version_id:
            return
        self.file_model.set_records(collection.items)
        self.detail_files.setText(f"Files: {collection.count}")
        self.status_label.setText("Version loaded.")

    def _loading_changed(self, scope, loading):
        if loading:
            self.status_label.setText(f"Loading {scope}...")

    def _request_failed(self, scope, message):
        self.status_label.setText(f"Could not load {scope}: {message}")
        {
            "projects": self.project_model,
            "assets": self.asset_model,
            "streams": self.stream_model,
            "versions": self.version_model,
            "files": self.file_model
        }[scope].clear()

    def _show_version(self, version):
        if not version:
            self.detail_title.setText("No version selected")
            self.detail_status.setText("Status: —")
            self.detail_comment.setText("Comment: —")
            self.detail_files.setText("Files: 0")
            return

        self.detail_title.setText(version.display_name)
        self.detail_status.setText(f"Status: {version.status}")
        self.detail_comment.setText(f"Comment: {version.comment or '—'}")
        self.detail_files.setText("Files: loading...")

    def _clear_all(self):
        self.current_project_id = None
        self.current_asset_id = None
        self.current_stream_id = None
        self.current_version_id = None
        self.project_model.clear()
        self.asset_model.clear()
        self.stream_model.clear()
        self.version_model.clear()
        self.file_model.clear()
        self._show_version(None)
        self.catalog_service.invalidate("projects", "assets", "streams", "versions", "files")
