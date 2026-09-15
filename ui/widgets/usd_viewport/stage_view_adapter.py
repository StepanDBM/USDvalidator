from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from pxr import Sdf, Usd
from pxr.Usdviewq.stageView import StageView


class StageViewAdapter(StageView):
    prim_picked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._source_path = ""
        self._stage = None
        self._selected_path = ""
        self.signalPrimSelected.connect(self._on_prim_picked)

    @property
    def source_path(self):
        return self._source_path

    @property
    def stage(self):
        return self._stage

    def set_source(self, source_path):
        path = Path(source_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"USD source does not exist: {path}")

        stage = Usd.Stage.Open(str(path), load=Usd.Stage.LoadAll)
        if not stage:
            raise RuntimeError(f"Could not open USD stage: {path}")

        self._close_renderer_for_stage_change()
        self._clear_selection()
        self._source_path = str(path)
        self._stage = stage
        self._selected_path = ""
        self._dataModel.stage = stage
        self.recomputeBBox()
        self.reset_camera()
        self.SetForceRefresh(True)
        self.updateView()
        self.update()
        return stage

    def reload_source(self):
        if not self._source_path:
            return None
        return self.set_source(self._source_path)

    def select_path(self, value):
        path = owning_prim_path(value)
        if not path or not self._stage:
            return False

        prim = self._stage.GetPrimAtPath(path)
        if not prim or not prim.IsValid():
            return False

        selection = self._dataModel.selection
        selection.clearPrims()
        selection.addPrimPath(path)
        self._selected_path = path.pathString
        self.updateSelection()
        self.updateView()
        self.update()
        return True

    def frame_all(self):
        if not self._stage:
            return
        self._clear_selection()
        self.recomputeBBox()
        self.resetCam()
        self.updateView()

    def frame_selected(self):
        if not self._stage or not self._selected_path:
            return False

        self.select_path(self._selected_path)
        self.getSelectionBBox()
        self.resetCam()
        self.updateView()
        self.update()
        return True

    def reset_camera(self):
        if not self._stage:
            return
        settings = self._dataModel.viewSettings
        settings.freeCamera = self._createNewFreeCamera(settings, True)
        self.switchToFreeCamera()
        self.recomputeBBox()
        self.resetCam()
        self.updateView()

    def selected_paths(self):
        selection = self._dataModel.selection
        for name in ("getPrimPaths", "GetPrimPaths"):
            getter = getattr(selection, name, None)
            if getter:
                return tuple(str(path) for path in getter())
        paths = getattr(selection, "_primSelection", {})
        return tuple(str(path) for path in paths)

    def set_draw_mode(self, draw_mode):
        self._dataModel.viewSettings.renderMode = draw_mode
        self.updateView()

    def _on_prim_picked(self, *args):
        for value in args:
            path = owning_prim_path(value)
            if not path:
                continue
            if self.select_path(path):
                self.prim_picked.emit(path.pathString)
            return

    def _close_renderer_for_stage_change(self):
        context = self.context()
        if not context or not context.isValid():
            self._renderer = None
            return
        self.makeCurrent()
        try:
            self.closeRenderer()
            self._renderer = None
        finally:
            self.doneCurrent()

    def _clear_selection(self):
        self._selected_path = ""
        try:
            self._dataModel.selection.clearPrims()
        except Exception:
            pass

    def shutdown(self):
        context = self.context()
        if not context or not context.isValid():
            return
        self.makeCurrent()
        try:
            self.closeRenderer()
            self._renderer = None
        finally:
            self.doneCurrent()


def owning_prim_path(value):
    if isinstance(value, Sdf.Path):
        path = value
    else:
        text = str(value or "").strip().replace("\\", "/")
        if not text.startswith("/"):
            return ""
        path = Sdf.Path(text)
    if path.IsPrimPath():
        return path
    if path.IsPropertyPath():
        return path.GetPrimPath()
    return ""
