from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget
)

from s_usd_desktop.ui.storage.dialogs import (
    CreateAssetDialog,
    CreateProjectDialog,
    CreateStreamDialog,
    CreateVersionDialog,
    UploadFileDialog,
    CacheSettingsDialog
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
        self.transfer_service = None
        self.download_service = None
        self.cache_manager = None
        self.cache_settings = None
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
        self.create_project_button = QPushButton("New Project")
        self.create_asset_button = QPushButton("New Asset")
        self.create_stream_button = QPushButton("New Stream")
        self.create_version_button = QPushButton("New Version")
        self.upload_button = QPushButton("Upload File")
        self.download_button = QPushButton("Download")
        self.reveal_button = QPushButton("Reveal")
        self.remove_cache_button = QPushButton("Remove Cache")
        self.clear_version_cache_button = QPushButton("Clear Version Cache")
        self.cache_settings_button = QPushButton("Cache...")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setEnabled(False)
        header = QHBoxLayout()
        header.addWidget(QLabel("S-USDv Storage"))
        header.addStretch()
        header.addWidget(self.create_project_button)
        header.addWidget(self.create_asset_button)
        header.addWidget(self.create_stream_button)
        header.addWidget(self.create_version_button)
        header.addWidget(self.upload_button)
        header.addWidget(self.download_button)
        header.addWidget(self.reveal_button)
        header.addWidget(self.remove_cache_button)
        header.addWidget(self.clear_version_cache_button)
        header.addWidget(self.cache_settings_button)
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

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.cancel_upload_button = QPushButton("Cancel Upload")
        self.cancel_upload_button.setVisible(False)
        transfer_row = QHBoxLayout()
        transfer_row.addWidget(self.progress_bar, 1)
        transfer_row.addWidget(self.cancel_upload_button)

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(browser)
        main_splitter.addWidget(lower)
        main_splitter.setSizes([420, 280])
        layout = QVBoxLayout(self)
        layout.addLayout(header)
        layout.addWidget(self.status_label)
        layout.addLayout(transfer_row)
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
        self.create_project_button.clicked.connect(self._create_project)
        self.create_asset_button.clicked.connect(self._create_asset)
        self.create_stream_button.clicked.connect(self._create_stream)
        self.create_version_button.clicked.connect(self._create_version)
        self.upload_button.clicked.connect(self._upload_file)
        self.download_button.clicked.connect(self._download_file)
        self.reveal_button.clicked.connect(self._reveal_cached_file)
        self.remove_cache_button.clicked.connect(self._remove_cached_file)
        self.clear_version_cache_button.clicked.connect(self._clear_version_cache)
        self.cache_settings_button.clicked.connect(self._show_cache_settings)
        self.project_view.selectionModel().currentChanged.connect(self._project_selected)
        self.asset_view.selectionModel().currentChanged.connect(self._asset_selected)
        self.stream_view.selectionModel().currentChanged.connect(self._stream_selected)
        self.version_view.selectionModel().currentChanged.connect(self._version_selected)
        self.file_view.selectionModel().currentChanged.connect(self._file_selected)
        self.catalog_service.projects_loaded.connect(self._projects_loaded)
        self.catalog_service.assets_loaded.connect(self._assets_loaded)
        self.catalog_service.streams_loaded.connect(self._streams_loaded)
        self.catalog_service.versions_loaded.connect(self._versions_loaded)
        self.catalog_service.files_loaded.connect(self._files_loaded)
        self.catalog_service.loading_changed.connect(self._loading_changed)
        self.catalog_service.request_failed.connect(self._request_failed)
        self.catalog_service.project_created.connect(lambda _record: self.refresh())
        self.catalog_service.asset_created.connect(lambda _record: self.catalog_service.load_assets(self.current_project_id))
        self.catalog_service.stream_created.connect(lambda _record: self.catalog_service.load_streams(self.current_asset_id))
        self.catalog_service.version_created.connect(lambda _record: self.catalog_service.load_versions(self.current_stream_id))

    def set_connected(self, connected):
        self.connected = connected
        self.refresh_button.setEnabled(connected)
        self.create_project_button.setEnabled(connected)
        self._update_action_states()

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

    def set_cache_services(self, cache_manager, download_service, cache_settings):
        self.cache_manager = cache_manager
        self.download_service = download_service
        self.cache_settings = cache_settings
        download_service.progress.connect(self._download_progress)
        download_service.completed.connect(self._download_completed)
        download_service.failed.connect(self._download_failed)
        download_service.cancelled.connect(self._download_cancelled)
        download_service.active_changed.connect(self._download_active_changed)

    def set_transfer_service(self, transfer_service):
        self.transfer_service = transfer_service
        self.cancel_upload_button.clicked.connect(self._cancel_active_transfer)
        transfer_service.progress.connect(self._upload_progress)
        transfer_service.upload_completed.connect(self._upload_completed)
        transfer_service.upload_failed.connect(self._upload_failed)
        transfer_service.upload_cancelled.connect(self._upload_cancelled)
        transfer_service.active_changed.connect(self._transfer_active_changed)

    def _update_action_states(self):
        active = bool((self.transfer_service and self.transfer_service.active) or (self.download_service and self.download_service.active))
        self.create_asset_button.setEnabled(self.connected and self.current_project_id is not None and not active)
        self.create_stream_button.setEnabled(self.connected and self.current_asset_id is not None and not active)
        self.create_version_button.setEnabled(self.connected and self.current_stream_id is not None and not active)
        self.upload_button.setEnabled(self.connected and self.current_version_id is not None and not active)
        selected_file = self._selected_file()
        cache_entry = self._inspect_file(selected_file) if selected_file else None
        available = bool(cache_entry and cache_entry.status.value == "available")
        self.download_button.setEnabled(self.connected and selected_file is not None and not available and not active)
        self.reveal_button.setEnabled(available and not active)
        self.remove_cache_button.setEnabled(available and not active)
        self.clear_version_cache_button.setEnabled(self.current_version_id is not None and not active)
        self.cache_settings_button.setEnabled(not active)

    def _create_project(self):
        dialog = CreateProjectDialog(self)
        if dialog.exec() and dialog.values():
            self.catalog_service.create_project(*dialog.values())

    def _create_asset(self):
        dialog = CreateAssetDialog(self)
        if dialog.exec() and dialog.values():
            self.catalog_service.create_asset(self.current_project_id, *dialog.values())

    def _create_stream(self):
        dialog = CreateStreamDialog(self)
        if dialog.exec() and dialog.values():
            self.catalog_service.create_stream(self.current_asset_id, *dialog.values())

    def _create_version(self):
        dialog = CreateVersionDialog(self)
        if dialog.exec():
            self.catalog_service.create_version(self.current_stream_id, *dialog.values())

    def _upload_file(self):
        if not self.transfer_service:
            return
        dialog = UploadFileDialog(self)
        if dialog.exec() and dialog.values():
            self.transfer_service.upload(self.current_version_id, *dialog.values())

    def _upload_progress(self, transferred, total):
        self.progress_bar.setMaximum(max(total, 1))
        self.progress_bar.setValue(transferred)
        self.status_label.setText(f"Uploading {transferred:,} of {total:,} bytes...")

    def _upload_completed(self, _stored_file):
        self.status_label.setText("Upload completed.")
        self.catalog_service.load_versions(self.current_stream_id)
        self.catalog_service.load_files(self.current_version_id)

    def _upload_failed(self, message):
        self.status_label.setText(f"Upload failed: {message}")
        QMessageBox.warning(self, "Upload Failed", message)

    def _upload_cancelled(self):
        self.status_label.setText("Upload cancelled.")

    def _transfer_active_changed(self, active):
        self.progress_bar.setVisible(active)
        self.cancel_upload_button.setVisible(active)
        if not active:
            self.progress_bar.reset()
        self._update_action_states()

    def _project_selected(self, current, _previous):
        project = self.project_model.record_at(current.row()) if current.isValid() else None
        self.current_project_id = project.id if project else None
        self._update_action_states()
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
        self._update_action_states()
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
        self._update_action_states()
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
        self._update_action_states()
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
        for stored_file in collection.items:
            self._update_file_cache_status(stored_file)
        cached_count = sum(
            self._inspect_file(stored_file).status.value == "available"
            for stored_file in collection.items
        ) if self.cache_manager else 0
        self.detail_files.setText(f"Files: {collection.count} | Cached: {cached_count}")
        self.status_label.setText("Version loaded.")

    def _file_selected(self, _current, _previous):
        self._update_action_states()

    def _selected_file(self):
        index = self.file_view.currentIndex()
        return self.file_model.record_at(index.row()) if index.isValid() else None

    def _cache_location(self):
        project = self.project_model.record_at(self.project_view.currentIndex().row())
        asset = self.asset_model.record_at(self.asset_view.currentIndex().row())
        stream = self.stream_model.record_at(self.stream_view.currentIndex().row())
        version = self.version_model.record_at(self.version_view.currentIndex().row())
        if not all((project, asset, stream, version)):
            return None
        from s_usd_desktop.cache import CacheLocation
        return CacheLocation(project.code, asset.code, stream.name, version.number)

    def _inspect_file(self, stored_file):
        location = self._cache_location()
        if not self.cache_manager or not location or not stored_file:
            return None
        return self.cache_manager.inspect(
            location.project_code,
            location.asset_code,
            location.stream_name,
            location.version_number,
            stored_file
        )

    def _update_file_cache_status(self, stored_file):
        entry = self._inspect_file(stored_file)
        labels = {
            "missing": "Not cached",
            "available": "Cached",
            "stale": "Stale",
            "corrupt": "Corrupt"
        }
        self.file_model.set_cache_status(
            stored_file.id,
            labels.get(entry.status.value, entry.status.value) if entry else "Unavailable"
        )

    def _download_file(self):
        stored_file = self._selected_file()
        location = self._cache_location()
        if stored_file and location and self.download_service:
            self.download_service.download(stored_file, location)

    def _cancel_active_transfer(self):
        if self.download_service and self.download_service.active:
            self.download_service.cancel()
        elif self.transfer_service and self.transfer_service.active:
            self.transfer_service.cancel()

    def _download_progress(self, transferred, total):
        self.progress_bar.setMaximum(max(total, 1))
        self.progress_bar.setValue(transferred)
        self.status_label.setText(f"Downloading {transferred:,} of {total:,} bytes...")

    def _download_completed(self, entry):
        self.status_label.setText(f"Cached: {entry.relative_path}")
        stored_file = self._selected_file()
        if stored_file:
            self._update_file_cache_status(stored_file)
        self._update_action_states()

    def _download_failed(self, message):
        self.status_label.setText(f"Download failed: {message}")
        QMessageBox.warning(self, "Download Failed", message)

    def _download_cancelled(self):
        self.status_label.setText("Download cancelled.")

    def _download_active_changed(self, active):
        self.progress_bar.setVisible(active)
        self.cancel_upload_button.setVisible(active)
        self.cancel_upload_button.setText("Cancel Download" if active else "Cancel Upload")
        if not active:
            self.progress_bar.reset()
        self._update_action_states()

    def _reveal_cached_file(self):
        entry = self._inspect_file(self._selected_file())
        if entry and entry.local_path.is_file():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(entry.local_path.parent)))

    def _remove_cached_file(self):
        stored_file = self._selected_file()
        location = self._cache_location()
        if not stored_file or not location:
            return
        self.cache_manager.remove_file(
            location.project_code,
            location.asset_code,
            location.stream_name,
            location.version_number,
            stored_file.id
        )
        self._update_file_cache_status(stored_file)
        self.status_label.setText("Local cached file removed. Remote content was not changed.")
        self._update_action_states()

    def _clear_version_cache(self):
        location = self._cache_location()
        if not location:
            return
        answer = QMessageBox.question(
            self,
            "Clear Version Cache",
            "Remove all local cached files for this version? Remote files will not be changed."
        )
        if answer != QMessageBox.Yes:
            return
        self.cache_manager.clear_version(
            location.project_code,
            location.asset_code,
            location.stream_name,
            location.version_number
        )
        for stored_file in self.file_model.records:
            self._update_file_cache_status(stored_file)
        self.status_label.setText("Local version cache cleared. Remote content was not changed.")
        self._update_action_states()

    def _show_cache_settings(self):
        if not self.cache_settings:
            return
        dialog = CacheSettingsDialog(self.cache_manager.configuration, self)
        if dialog.exec():
            configuration = dialog.configuration()
            self.cache_settings.save(configuration)
            from s_usd_desktop.cache import CacheManager
            self.cache_manager = CacheManager(configuration)
            self.download_service.cache_manager = self.cache_manager
            for stored_file in self.file_model.records:
                self._update_file_cache_status(stored_file)
            self.status_label.setText(f"Cache location changed to {configuration.root}")
            self._update_action_states()

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
