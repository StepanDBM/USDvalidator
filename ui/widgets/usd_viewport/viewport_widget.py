from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox, QSplitter, QVBoxLayout, QWidget
from pxr.Usdviewq.common import RenderModes

from .inspector import PrimInspector
from .renderer_settings_dialog import RendererSettingsDialog
from .stage_outliner import StageOutliner
from .stage_view_adapter import StageViewAdapter
from .viewport_models import StageStatistics
from .viewport_state import ViewportState
from .viewport_toolbar import ViewportToolbar
from .viewport_tools import ViewportTools
from ui.navigation import resolve_validation_target


DRAW_MODES = {
    "Smooth Shaded": RenderModes.SMOOTH_SHADED,
    "Wireframe on Surface": RenderModes.WIREFRAME_ON_SURFACE,
    "Wireframe": RenderModes.WIREFRAME,
    "Flat Shaded": RenderModes.FLAT_SHADED,
    "Geometry Only": RenderModes.GEOM_ONLY,
    "Geometry Smooth": RenderModes.GEOM_SMOOTH,
    "Geometry Flat": RenderModes.GEOM_FLAT,
    "Hidden Surface Wireframe": RenderModes.HIDDEN_SURFACE_WIREFRAME,
    "Points": RenderModes.POINTS,
}


class UsdViewportWidget(QWidget):
    source_changed = Signal(str)
    path_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = ViewportState()
        self.statistics = StageStatistics()
        self.toolbar = ViewportToolbar()
        self.outliner = StageOutliner()
        self.viewport = StageViewAdapter(self)
        self.inspector = PrimInspector()
        self.tools = ViewportTools()
        self.status_label = QLabel("No stage loaded.")

        center = QSplitter(Qt.Orientation.Vertical)
        center.addWidget(self.viewport)
        center.addWidget(self.inspector)
        center.setStretchFactor(0, 4)
        center.setStretchFactor(1, 2)
        center.setSizes([640, 290])

        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.addWidget(self.outliner)
        workspace.addWidget(center)
        workspace.addWidget(self.tools)
        workspace.setStretchFactor(0, 0)
        workspace.setStretchFactor(1, 1)
        workspace.setStretchFactor(2, 0)
        workspace.setSizes([270, 920, 280])

        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(workspace, 1)
        layout.addWidget(self.status_label)
        self._connect_signals()

    def _connect_signals(self):
        self.toolbar.source_requested.connect(self.set_source)
        self.outliner.path_selected.connect(self._select_from_outliner)
        self.viewport.prim_picked.connect(self._select_from_viewport)
        self.viewport.renderer_changed.connect(self._refresh_renderer_controls)
        self.tools.action_requested.connect(self._handle_action)

    def set_source(self, source_path):
        if not source_path:
            return False
        try:
            stage = self.viewport.set_source(source_path)
        except Exception as error:
            self.state.error_message = str(error)
            self.status_label.setText(self.state.error_message)
            QMessageBox.critical(self, "Viewport", self.state.error_message)
            return False

        self.state.source_path = self.viewport.source_path
        self.state.selected_path = ""
        self.state.stage_loaded = True
        self.toolbar.source_edit.setText(self.state.source_path)
        self.outliner.set_stage(stage)
        self.inspector.set_prim(None)
        self.statistics = _stage_statistics(stage)
        self.tools.set_cameras(self.viewport.stage_cameras())
        QTimer.singleShot(0, self._refresh_renderer_controls)
        QTimer.singleShot(100, self._refresh_renderer_controls)
        self._set_status("Opened stage")
        self.source_changed.emit(self.state.source_path)
        return True

    def show_validation_result(self, report, result):
        target = resolve_validation_target(report, result)
        if self.state.source_path != target.source_path and not self.set_source(target.source_path):
            return False
        if target.prim_path:
            self.select_path(target.prim_path, frame=True)
        else:
            self.viewport.frame_all()
        self.inspector.show_validation_results(report.results, result)
        if target.property_path:
            self.inspector.select_property(target.property_path)
        self._set_status(f"Validation: {result.check_id}")
        return True

    def select_path(self, path, frame=False):
        if not self.viewport.select_path(path):
            self.status_label.setText(f"Path is not present in the displayed stage: {path}")
            return False
        self._apply_selection(str(path), True)
        if frame:
            self._frame_selected()
        return True

    def _select_from_outliner(self, path):
        if self.viewport.select_path(path):
            self._apply_selection(path, False)

    def _select_from_viewport(self, path):
        self._apply_selection(path, True)

    def _apply_selection(self, path, update_outliner):
        stage = self.viewport.stage
        prim = stage.GetPrimAtPath(path) if stage else None
        if update_outliner:
            self.outliner.select_path(path)
        self.inspector.set_prim(prim)
        self.state.selected_path = path
        self._set_status(f"Selected {path}")
        self.path_selected.emit(path)

    def _handle_action(self, action, value):
        handlers = {
            "frame_all": self.viewport.frame_all,
            "frame_selected": self._frame_selected,
            "reset_camera": self.viewport.reset_camera,
            "clear_selection": self._clear_selection,
            "auto_clipping": lambda: self.viewport.set_auto_clipping(value),
            "camera": lambda: self.viewport.set_camera_path(value),
            "renderer": lambda: self.viewport.set_renderer(value) if value else None,
            "aov": lambda: self.viewport.set_renderer_aov(value),
            "renderer_settings": self._show_renderer_settings,
            "draw_mode": lambda: self.viewport.set_draw_mode(DRAW_MODES[value]),
            "complexity": lambda: self.viewport.set_complexity(value),
            "background": lambda: self.viewport.set_background_color(value),
            "purpose_guide": lambda: self.viewport.set_display_purpose("guide", value),
            "purpose_proxy": lambda: self.viewport.set_display_purpose("proxy", value),
            "purpose_render": lambda: self.viewport.set_display_purpose("render", value),
            "cull_backfaces": lambda: self.viewport.set_backface_culling(value),
            "bounding_boxes": lambda: self.viewport.set_bounding_boxes(value),
            "extents_hint": lambda: self.viewport.set_use_extents_hint(value),
            "scene_lights": lambda: self.viewport.set_scene_lights(value),
            "camera_light": lambda: self.viewport.set_camera_light(value),
            "dome_light": lambda: self.viewport.set_dome_light(value),
            "dome_textures": lambda: self.viewport.set_dome_textures(value),
            "selection_highlight": lambda: self.viewport.set_selection_highlight(value),
            "selection_color": lambda: self.viewport.set_selection_color(value),
            "copy_image": self._copy_image,
            "save_image": self._save_image,
        }
        handler = handlers.get(action)
        if handler:
            handler()
            self._set_status(action.replace("_", " ").title())

    def _frame_selected(self):
        if not self.viewport.frame_selected():
            self.status_label.setText("Select a prim in the outliner or viewport first.")

    def _clear_selection(self):
        self.viewport.clear_selection()
        self.outliner.tree.clearSelection()
        self.inspector.set_prim(None)
        self.state.selected_path = ""

    def _refresh_renderer_controls(self):
        renderers = [(plugin, self.viewport.renderer_display_name(plugin)) for plugin in self.viewport.renderer_plugins()]
        self.tools.set_renderers(renderers)
        self.tools.set_aovs(self.viewport.renderer_aovs())

    def _show_renderer_settings(self):
        RendererSettingsDialog(self.viewport, self).exec()

    def _copy_image(self):
        QGuiApplication.clipboard().setPixmap(self.viewport.grab_image())

    def _save_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Viewer Image", "viewport.png", "PNG Image (*.png);;JPEG Image (*.jpg)")
        if path:
            self.viewport.grab_image().save(path)

    def _set_status(self, action):
        stats = self.statistics
        name = Path(self.state.source_path).name if self.state.source_path else "No file"
        selected = self.state.selected_path or "No selection"
        self.status_label.setText(
            f"{name} | {action} | {selected} | {stats.prims:,} prims | {stats.meshes:,} meshes | "
            f"{stats.points:,} points | {stats.materials:,} materials | {stats.shaders:,} shaders"
        )

    def shutdown(self):
        self.viewport.shutdown()


def _stage_statistics(stage):
    counts = {"prims": 0, "meshes": 0, "points": 0, "materials": 0, "shaders": 0, "cameras": 0, "lights": 0}
    for prim in stage.TraverseAll():
        counts["prims"] += 1
        type_name = prim.GetTypeName()
        if type_name == "Mesh":
            counts["meshes"] += 1
            value = prim.GetAttribute("points").Get()
            counts["points"] += len(value or ())
        elif type_name == "Material":
            counts["materials"] += 1
        elif type_name == "Shader":
            counts["shaders"] += 1
        elif type_name == "Camera":
            counts["cameras"] += 1
        elif type_name.endswith("Light"):
            counts["lights"] += 1
    return StageStatistics(**counts)
