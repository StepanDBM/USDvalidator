from collections import defaultdict

from PySide6.QtCore import QObject, QThreadPool, Signal

from s_usd_desktop.client import CatalogClient, FileClient, SUsdvApiClient
from s_usd_desktop.services.workers import RequestWorker


class CatalogService(QObject):
    projects_loaded = Signal(object)
    assets_loaded = Signal(object, object)
    streams_loaded = Signal(object, object)
    versions_loaded = Signal(object, object)
    files_loaded = Signal(object, object)
    loading_changed = Signal(str, bool)
    request_failed = Signal(str, str)
    project_created = Signal(object)
    asset_created = Signal(object)
    stream_created = Signal(object)
    version_created = Signal(object)
    version_published = Signal(object)
    version_deprecated = Signal(object)

    def __init__(self, connection_service, thread_pool=None, parent=None):
        super().__init__(parent)
        self.connection_service = connection_service
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self._generations = defaultdict(int)
        self._workers = set()

    def invalidate(self, *scopes):
        for scope in scopes:
            self._generations[scope] += 1

    def load_projects(self):
        self._submit("projects", self.projects_loaded, self._catalog_call, "list_projects")

    def load_assets(self, project_id):
        self._submit("assets", self.assets_loaded, self._catalog_call, "list_assets", project_id, context=project_id)

    def load_streams(self, asset_id):
        self._submit("streams", self.streams_loaded, self._catalog_call, "list_streams", asset_id, context=asset_id)

    def load_versions(self, stream_id):
        self._submit("versions", self.versions_loaded, self._catalog_call, "list_versions", stream_id, context=stream_id)

    def load_files(self, version_id):
        self._submit("files", self.files_loaded, self._file_call, "list_files", version_id, context=version_id)

    def create_project(self, code, name, description=""):
        self._submit("mutation", self.project_created, self._catalog_call, "create_project", code, name, description)

    def create_asset(self, project_id, code, name, asset_type, description=""):
        self._submit(
            "mutation",
            self.asset_created,
            self._catalog_call,
            "create_asset",
            project_id,
            code,
            name,
            asset_type,
            description
        )

    def create_stream(self, asset_id, name, description=""):
        self._submit("mutation", self.stream_created, self._catalog_call, "create_stream", asset_id, name, description)

    def create_version(self, stream_id, comment=""):
        self._submit("mutation", self.version_created, self._catalog_call, "create_version", stream_id, comment)

    def publish_version(self, version_id):
        self._submit(
            "lifecycle", self.version_published,
            self._catalog_call, "publish_version", version_id
        )

    def deprecate_version(self, version_id):
        self._submit(
            "lifecycle", self.version_deprecated,
            self._catalog_call, "deprecate_version", version_id
        )

    def _submit(self, scope, result_signal, function, method_name, *args, context=None):
        self._generations[scope] += 1
        generation = self._generations[scope]
        self.loading_changed.emit(scope, True)
        worker = RequestWorker(function, method_name, *args)
        worker.signals.result.connect(
            lambda result, s=scope, g=generation, c=context: self._handle_result(
                s, g, c, result, result_signal
            )
        )
        worker.signals.error.connect(
            lambda error, s=scope, g=generation: self._handle_error(s, g, error)
        )
        worker.signals.finished.connect(
            lambda current=worker: self._workers.discard(current)
        )
        self._workers.add(worker)
        self.thread_pool.start(worker)

    def _catalog_call(self, method_name, *args):
        configuration = self.connection_service.preferences.to_api_configuration()
        with SUsdvApiClient(configuration) as api:
            return getattr(CatalogClient(api), method_name)(*args)

    def _file_call(self, method_name, *args):
        configuration = self.connection_service.preferences.to_api_configuration()
        with SUsdvApiClient(configuration) as api:
            return getattr(FileClient(api), method_name)(*args)

    def _handle_result(self, scope, generation, context, result, signal):
        if generation != self._generations[scope]:
            return

        self.loading_changed.emit(scope, False)

        if context is None:
            signal.emit(result)
        else:
            signal.emit(context, result)

    def _handle_error(self, scope, generation, error):
        if generation != self._generations[scope]:
            return

        self.loading_changed.emit(scope, False)
        message = getattr(error, "message", str(error))
        self.request_failed.emit(scope, message)
