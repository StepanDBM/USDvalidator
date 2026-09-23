from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox, QPushButton, QVBoxLayout, QWidget


from s_usd_desktop.ui.tooltips import TooltipText


class ViewportTools(QWidget):
    action_requested = Signal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self._camera_group())
        layout.addWidget(self._renderer_group())
        layout.addWidget(self._display_group())
        layout.addWidget(self._lighting_group())
        layout.addWidget(self._selection_group())
        layout.addStretch()

    def _camera_group(self):
        group = QGroupBox("Camera")
        grid = QGridLayout(group)
        self.camera_combo = QComboBox()
        self.camera_combo.addItem("Free Camera", "")
        self.camera_combo.setToolTip(TooltipText.VIEWPORT_CAMERA_MODE)
        buttons = (("Frame All", "frame_all"), ("Frame Selected", "frame_selected"), ("Reset", "reset_camera"), ("Copy Image", "copy_image"), ("Save Image", "save_image"))
        grid.addWidget(self.camera_combo, 0, 0, 1, 2)
        for index, (label, action) in enumerate(buttons, 1):
            button = QPushButton(label)
            button.setToolTip({
                "frame_all": TooltipText.VIEWPORT_FRAME_ALL,
                "frame_selected": TooltipText.VIEWPORT_FRAME_SELECTION,
                "reset_camera": "Reset the free camera to its default orientation and framing.",
                "copy_image": "Copy the current viewport image to the operating-system clipboard.",
                "save_image": TooltipText.VIEWPORT_SCREENSHOT
            }[action])
            button.clicked.connect(lambda checked=False, name=action: self.action_requested.emit(name, None))
            grid.addWidget(button, (index + 1) // 2, (index - 1) % 2)
        self.auto_clip = QCheckBox("Auto clipping")
        self.auto_clip.setChecked(True)
        self.auto_clip.setToolTip(
            "Automatically derive near and far clipping planes from visible stage bounds."
        )
        self.auto_clip.toggled.connect(lambda value: self.action_requested.emit("auto_clipping", value))
        grid.addWidget(self.auto_clip, 4, 0, 1, 2)
        self.camera_combo.currentIndexChanged.connect(lambda index: self.action_requested.emit("camera", self.camera_combo.itemData(index)))
        return group

    def _renderer_group(self):
        group = QGroupBox("Renderer")
        grid = QGridLayout(group)
        self.renderer_combo = QComboBox()
        self.aov_combo = QComboBox()
        self.renderer_combo.setToolTip(TooltipText.VIEWPORT_RENDERER)
        self.aov_combo.setToolTip(TooltipText.VIEWPORT_AOV)
        settings = QPushButton("Hydra Settings...")
        settings.setToolTip(TooltipText.VIEWPORT_HYDRA_SETTINGS)
        settings.clicked.connect(lambda: self.action_requested.emit("renderer_settings", None))
        self.renderer_combo.currentIndexChanged.connect(lambda index: self.action_requested.emit("renderer", self.renderer_combo.itemData(index)))
        self.aov_combo.currentTextChanged.connect(lambda value: self.action_requested.emit("aov", value))
        grid.addWidget(self.renderer_combo, 0, 0, 1, 2)
        grid.addWidget(self.aov_combo, 1, 0, 1, 2)
        grid.addWidget(settings, 2, 0, 1, 2)
        return group

    def _display_group(self):
        group = QGroupBox("Display")
        grid = QGridLayout(group)
        self.draw_mode_combo = QComboBox()
        self.draw_mode_combo.addItems(["Smooth Shaded", "Wireframe on Surface", "Wireframe", "Flat Shaded", "Geometry Only", "Geometry Smooth", "Geometry Flat", "Hidden Surface Wireframe", "Points"])
        self.complexity_combo = QComboBox()
        for label, value in (("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Very High", "very_high")):
            self.complexity_combo.addItem(label, value)
        self.background_combo = QComboBox()
        self.draw_mode_combo.setToolTip(
            "Choose the viewport draw style, such as smooth shaded, wireframe, or points."
        )
        self.complexity_combo.setToolTip(
            "Choose Hydra refinement complexity. Higher values may improve subdivision display but cost performance."
        )
        self.background_combo.setToolTip(
            "Choose the viewport background color used only for interactive display."
        )
        for label, value in (("Black", "#000000"), ("Dark Grey", "#404040"), ("Light Grey", "#a0a0a0"), ("White", "#ffffff")):
            self.background_combo.addItem(label, value)
        grid.addWidget(self.draw_mode_combo, 0, 0, 1, 2)
        grid.addWidget(self.complexity_combo, 1, 0)
        grid.addWidget(self.background_combo, 1, 1)
        checks = (("Guide", "purpose_guide", False), ("Proxy", "purpose_proxy", True), ("Render", "purpose_render", True), ("Cull Backfaces", "cull_backfaces", False), ("Bounding Boxes", "bounding_boxes", False), ("Use Extents Hint", "extents_hint", False))
        for index, (label, action, checked) in enumerate(checks):
            box = QCheckBox(label)
            box.setChecked(checked)
            box.toggled.connect(lambda value, name=action: self.action_requested.emit(name, value))
            grid.addWidget(box, 2 + index // 2, index % 2)
        self.draw_mode_combo.currentTextChanged.connect(lambda value: self.action_requested.emit("draw_mode", value))
        self.complexity_combo.currentIndexChanged.connect(lambda index: self.action_requested.emit("complexity", self.complexity_combo.itemData(index)))
        self.background_combo.currentIndexChanged.connect(lambda index: self.action_requested.emit("background", self.background_combo.itemData(index)))
        return group

    def _lighting_group(self):
        group = QGroupBox("Lighting")
        grid = QGridLayout(group)
        for index, (label, action, checked) in enumerate((("Scene Lights", "scene_lights", True), ("Camera/Ambient Light", "camera_light", True), ("Default Dome", "dome_light", False), ("Dome Textures", "dome_textures", True))):
            box = QCheckBox(label)
            box.setChecked(checked)
            box.toggled.connect(lambda value, name=action: self.action_requested.emit(name, value))
            grid.addWidget(box, index // 2, index % 2)
        return group

    def _selection_group(self):
        group = QGroupBox("Selection")
        grid = QGridLayout(group)
        clear = QPushButton("Clear")
        clear.setToolTip(
            "Clear the current prim selection without modifying the USD stage."
        )
        clear.clicked.connect(lambda: self.action_requested.emit("clear_selection", None))
        self.highlight = QCheckBox("Highlight")
        self.highlight.setChecked(True)
        self.highlight.setToolTip(
            "Draw a viewport highlight around selected prims. This changes display only."
        )
        self.highlight.toggled.connect(lambda value: self.action_requested.emit("selection_highlight", value))
        self.highlight_color = QComboBox()
        self.highlight_color.setToolTip(
            "Choose the viewport selection-highlight color. This changes display only."
        )
        for label, value in (("Yellow", "#ffff00"), ("White", "#ffffff"), ("Cyan", "#00ffff")):
            self.highlight_color.addItem(label, value)
        self.highlight_color.currentIndexChanged.connect(lambda index: self.action_requested.emit("selection_color", self.highlight_color.itemData(index)))
        grid.addWidget(clear, 0, 0)
        grid.addWidget(self.highlight, 0, 1)
        grid.addWidget(self.highlight_color, 1, 0, 1, 2)
        return group

    def set_renderers(self, values):
        self.renderer_combo.blockSignals(True)
        self.renderer_combo.clear()
        for plugin_id, label in values:
            self.renderer_combo.addItem(label, plugin_id)
        self.renderer_combo.blockSignals(False)

    def set_aovs(self, values):
        self.aov_combo.blockSignals(True)
        self.aov_combo.clear()
        self.aov_combo.addItems(values)
        self.aov_combo.blockSignals(False)

    def set_cameras(self, paths):
        self.camera_combo.blockSignals(True)
        self.camera_combo.clear()
        self.camera_combo.addItem("Free Camera", "")
        for path in paths:
            self.camera_combo.addItem(path.rsplit("/", 1)[-1], path)
        self.camera_combo.blockSignals(False)
