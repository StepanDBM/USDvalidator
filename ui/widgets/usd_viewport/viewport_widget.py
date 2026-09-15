from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QMessageBox, QSplitter, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from pxr.Usdviewq.common import RenderModes

from .prim_details import PrimDetails
from .stage_outliner import StageOutliner
from .stage_view_adapter import StageViewAdapter
from .viewport_state import ViewportState
from .viewport_toolbar import ViewportToolbar
from .viewport_tools import ViewportTools


DRAW_MODES = {
    "Smooth Shaded": RenderModes.SMOOTH_SHADED,
    "Wireframe on Surface": RenderModes.WIREFRAME_ON_SURFACE,
    "Wireframe": RenderModes.WIREFRAME,
    "Flat Shaded": RenderModes.FLAT_SHADED,
    "Geometry Only": RenderModes.GEOM_ONLY,
    "Points": RenderModes.POINTS,
}


class UsdViewportWidget(QWidget):
    source_changed = Signal(str)
    path_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = ViewportState()
        self.toolbar = ViewportToolbar()
        self.outliner = StageOutliner()
        self.viewport = StageViewAdapter(self)
        self.details = PrimDetails()
        self.tools = ViewportTools()
        self.status_label = QLabel("No stage loaded.")
        self.status_label.setObjectName("viewportStatus")

        center = QSplitter(Qt.Orientation.Vertical)
        center.addWidget(self.viewport)
        center.addWidget(self.details)
        center.setStretchFactor(0, 4)
        center.setStretchFactor(1, 1)
        center.setSizes([650, 190])

        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.addWidget(self.outliner)
        workspace.addWidget(center)
        workspace.addWidget(self.tools)
        workspace.setStretchFactor(0, 0)
        workspace.setStretchFactor(1, 1)
        workspace.setStretchFactor(2, 0)
        workspace.setSizes([280, 900, 190])

        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(workspace, 1)
        layout.addWidget(self.status_label)
        self._connect_signals()

    def _connect_signals(self):
        self.toolbar.source_requested.connect(self.set_source)
        self.outliner.path_selected.connect(self._select_from_outliner)
        self.viewport.prim_picked.connect(self._select_from_viewport)
        self.tools.frame_all_requested.connect(self.viewport.frame_all)
        self.tools.frame_selected_requested.connect(self._frame_selected)
        self.tools.reset_camera_requested.connect(self.viewport.reset_camera)
        self.tools.draw_mode_changed.connect(self._set_draw_mode)

    def set_source(self, source_path):
        if not source_path:
            return False
        try:
            stage = self.viewport.set_source(source_path)
        except Exception as error:
            self.state.error_message = str(error)
            self.state.stage_loaded = False
            self.status_label.setText(self.state.error_message)
            QMessageBox.critical(self, "Viewport", self.state.error_message)
            return False

        self.state.source_path = self.viewport.source_path
        self.state.selected_path = ""
        self.state.error_message = ""
        self.state.stage_loaded = True
        self.toolbar.source_edit.setText(self.state.source_path)
        self.outliner.set_stage(stage)
        self.details.set_prim(None)
        self._set_status("Opened stage")
        self.source_changed.emit(self.state.source_path)
        return True

    def select_path(self, path, frame=False):
        if not self.viewport.select_path(path):
            self.status_label.setText(f"Path is not present in the displayed stage: {path}")
            return False
        self._apply_selection(str(path), update_outliner=True)
        if frame:
            self._frame_selected()
        return True

    def _select_from_outliner(self, path):
        if self.viewport.select_path(path):
            self._apply_selection(path, update_outliner=False)

    def _select_from_viewport(self, path):
        self._apply_selection(path, update_outliner=True)

    def _apply_selection(self, path, update_outliner):
        stage = self.viewport.stage
        prim = stage.GetPrimAtPath(path) if stage else None
        if update_outliner:
            self.outliner.select_path(path)
        self.details.set_prim(prim)
        self.state.selected_path = path
        self._set_status(f"Selected {path}")
        self.path_selected.emit(path)

    def _frame_selected(self):
        if not self.state.selected_path:
            self.status_label.setText("Select a prim in the outliner or viewport first.")
            return
        if self.viewport.frame_selected():
            self._set_status(f"Framed {self.state.selected_path}")

    def _set_draw_mode(self, label):
        mode = DRAW_MODES.get(label)
        if mode is not None:
            self.viewport.set_draw_mode(mode)
            self._set_status(f"Display mode: {label}")

    def _set_status(self, action):
        stage = self.viewport.stage
        prim_count = sum(1 for _ in stage.TraverseAll()) if stage else 0
        name = Path(self.state.source_path).name if self.state.source_path else "No file"
        self.status_label.setText(f"{name}  |  {action}  |  {prim_count:,} prims")

    def shutdown(self):
        self.viewport.shutdown()
