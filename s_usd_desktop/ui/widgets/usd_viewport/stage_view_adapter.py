from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from pxr import Gf, Sdf, Usd, UsdGeom
from pxr.Usdviewq.common import SelectionHighlightModes
from pxr.Usdviewq.viewSettingsDataModel import RefinementComplexities
from pxr.Usdviewq.stageView import StageView


class StageViewAdapter(StageView):
    prim_picked = Signal(str)
    renderer_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._source_path = ""
        self._stage = None
        self._selected_path = ""
        self._session_visibility_paths = set()
        self.signalPrimSelected.connect(self._on_prim_picked)

    @property
    def source_path(self):
        return self._source_path

    @property
    def stage(self):
        return self._stage

    @property
    def selected_path(self):
        return self._selected_path

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
        self._session_visibility_paths.clear()
        self._dataModel.stage = stage
        self.recomputeBBox()
        self.reset_camera()
        self.SetForceRefresh(True)
        self.updateView()
        self.update()
        self.renderer_changed.emit()
        return stage

    def set_current_time(self, value):
        if not self._stage:
            return
        self._dataModel.currentFrame = Usd.TimeCode(float(value))
        self.SetForceRefresh(True)
        self.updateView()
        self.update()

    def select_path(self, value):
        path = owning_prim_path(value)
        return self.select_paths([path.pathString], path.pathString) if path else False

    def select_paths(self, values, primary_path=""):
        if not self._stage:
            return False
        paths = []
        for value in values:
            path = owning_prim_path(value)
            prim = self._stage.GetPrimAtPath(path) if path else None
            if prim and prim.IsValid() and path not in paths:
                paths.append(path)
        if not paths:
            return False

        selection = self._dataModel.selection
        selection.clearPrims()
        for path in paths:
            selection.addPrimPath(path)
        primary = owning_prim_path(primary_path) if primary_path else paths[-1]
        self._selected_path = primary.pathString if primary in paths else paths[-1].pathString
        self.updateSelection()
        self.updateView()
        self.update()
        return True

    def set_session_visibility(self, paths, visible):
        if not self._stage:
            return False
        edit_target = self._stage.GetEditTarget()
        self._stage.SetEditTarget(self._stage.GetSessionLayer())
        try:
            for value in paths:
                path = owning_prim_path(value)
                prim = self._stage.GetPrimAtPath(path) if path else None
                if not prim or not prim.IsValid() or not prim.IsA(UsdGeom.Imageable):
                    continue
                attribute = UsdGeom.Imageable(prim).GetVisibilityAttr()
                if visible:
                    attribute.Clear()
                    self._session_visibility_paths.discard(path.pathString)
                else:
                    attribute.Set(UsdGeom.Tokens.invisible)
                    self._session_visibility_paths.add(path.pathString)
        finally:
            self._stage.SetEditTarget(edit_target)
        self.SetForceRefresh(True)
        self.updateView()
        self.update()
        return True

    def clear_session_visibility(self):
        if not self._stage:
            return False
        session = self._stage.GetSessionLayer()
        for prim_spec in list(session.rootPrims):
            session.RemovePrim(prim_spec.path)
        self.SetForceRefresh(True)
        self.updateView()
        self.update()
        return True

    def clear_selection(self):
        self._clear_selection()
        self.updateSelection()
        self.updateView()
        self.update()

    def frame_all(self):
        if not self._stage:
            return False
        self._clear_selection()
        self.recomputeBBox()
        self.resetCam()
        self.updateView()
        return True

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
            return False
        settings = self._dataModel.viewSettings
        settings.freeCamera = self._createNewFreeCamera(settings, True)
        self.switchToFreeCamera()
        self.recomputeBBox()
        self.resetCam()
        self.updateView()
        return True

    def set_draw_mode(self, draw_mode):
        self._dataModel.viewSettings.renderMode = draw_mode
        self.updateView()

    def set_complexity(self, value):
        complexity = {
            "low": RefinementComplexities.LOW,
            "medium": RefinementComplexities.MEDIUM,
            "high": RefinementComplexities.HIGH,
            "very_high": RefinementComplexities.VERY_HIGH,
        }[value]
        self._dataModel.viewSettings.complexity = complexity

    def set_display_purpose(self, purpose, enabled):
        name = {
            "guide": "displayGuide",
            "proxy": "displayProxy",
            "render": "displayRender",
        }[purpose]
        setattr(self._dataModel.viewSettings, name, bool(enabled))
        self.updateBboxPurposes()
        self.recomputeBBox()
        self.updateView()

    def set_backface_culling(self, enabled):
        self._dataModel.viewSettings.cullBackfaces = bool(enabled)

    def set_bounding_boxes(self, enabled):
        settings = self._dataModel.viewSettings
        settings.showBBoxes = bool(enabled)
        if enabled and not settings.showAABBox and not settings.showOBBox:
            settings.showAABBox = True
        self.recomputeBBox()
        self.updateView()

    def set_use_extents_hint(self, enabled):
        self._dataModel.viewSettings.useExtentsHint = bool(enabled)
        self.recomputeBBox()
        self.updateView()

    def set_auto_clipping(self, enabled):
        self._dataModel.viewSettings.autoComputeClippingPlanes = bool(enabled)

    def set_scene_lights(self, enabled):
        self._dataModel.viewSettings.enableSceneLights = bool(enabled)

    def set_camera_light(self, enabled):
        self._dataModel.viewSettings.ambientLightOnly = bool(enabled)

    def set_dome_light(self, enabled):
        self._dataModel.viewSettings.domeLightEnabled = bool(enabled)

    def set_dome_textures(self, enabled):
        self._dataModel.viewSettings.domeLightTexturesVisible = bool(enabled)

    def set_background_color(self, color):
        qcolor = QColor(color)
        self._dataModel.viewSettings.clearColor = Gf.Vec4f(
            qcolor.redF(), qcolor.greenF(), qcolor.blueF(), 1.0
        )

    def set_selection_highlight(self, enabled):
        settings = self._dataModel.viewSettings
        settings.selHighlightMode = (
            SelectionHighlightModes.ALWAYS
            if enabled
            else SelectionHighlightModes.NEVER
        )

        self.updateSelection()
        self.SetForceRefresh(True)
        self.updateView()
        self.update()
        return True

    def set_selection_color(self, color):
        color_name = {
            "#ffff00": "Yellow",
            "#ffffff": "White",
            "#00ffff": "Cyan",
        }.get(str(color).lower())

        if not color_name:
            return False

        settings = self._dataModel.viewSettings
        settings.highlightColorName = color_name

        renderer = self.ensure_renderer()
        if renderer:
            renderer.SetSelectionColor(settings.highlightColor)

        self.updateSelection()
        self.SetForceRefresh(True)
        self.updateView()
        self.update()
        return True
    
    def ensure_renderer(self):
        if self._renderer:
            return self._renderer
        if not self.context() or not self.context().isValid():
            return None
        self.makeCurrent()
        try:
            return self._getRenderer()
        finally:
            self.doneCurrent()

    def renderer_plugins(self):
        try:
            self.ensure_renderer()
            return tuple(self.GetRendererPlugins())
        except Exception:
            return ()

    def renderer_display_name(self, plugin_id):
        try:
            return self.GetRendererDisplayName(plugin_id)
        except Exception:
            return str(plugin_id)

    def set_renderer(self, plugin_id):
        if not self.ensure_renderer():
            return False
        state = self.copyViewState()
        self.SetRendererPlugin(plugin_id)
        self.restoreViewState(state)
        self.renderer_changed.emit()
        self.updateView()
        return True

    def renderer_aovs(self):
        try:
            self.ensure_renderer()
            return tuple(str(value) for value in self.GetRendererAovs())
        except Exception:
            return ()

    def set_renderer_aov(self, name):
        if name and self.ensure_renderer():
            self.SetRendererAov(name)
            self.updateView()

    def renderer_settings(self):
        try:
            self.ensure_renderer()
            return tuple(self.GetRendererSettingsList())
        except Exception:
            return ()

    def set_renderer_setting(self, key, value):
        if not self.ensure_renderer():
            return False
        self.SetRendererSetting(key, value)
        self.updateView()
        return True

    def stage_cameras(self):
        if not self._stage:
            return ()
        return tuple(
            prim.GetPath().pathString for prim in self._stage.TraverseAll()
            if prim.GetTypeName() == "Camera"
        )

    def set_camera_path(self, path):
        if not self._stage or not path:
            self.switchToFreeCamera()
            return
        prim = self._stage.GetPrimAtPath(path)
        if prim and prim.IsValid():
            self._dataModel.viewSettings.cameraPrim = prim
            self.resolveCamera()
            self.updateView()

    def grab_image(self):
        return self.grabFramebuffer()

    def _set_setting(self, names, value):
        settings = self._dataModel.viewSettings
        for name in names:
            if hasattr(settings, name):
                setattr(settings, name, value)
                self.updateView()
                self.update()
                return True
        return False

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
