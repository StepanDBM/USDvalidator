from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QGroupBox, QPushButton, QVBoxLayout, QWidget


class ViewportTools(QWidget):
    frame_all_requested = Signal()
    frame_selected_requested = Signal()
    reset_camera_requested = Signal()
    draw_mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        camera = QGroupBox("Camera")
        camera_layout = QVBoxLayout(camera)
        self.frame_all_button = QPushButton("Frame All")
        self.frame_selected_button = QPushButton("Frame Selected")
        self.reset_button = QPushButton("Reset Camera")
        camera_layout.addWidget(self.frame_all_button)
        camera_layout.addWidget(self.frame_selected_button)
        camera_layout.addWidget(self.reset_button)

        display = QGroupBox("Display")
        display_layout = QVBoxLayout(display)
        self.draw_mode_combo = QComboBox()
        self.draw_mode_combo.addItems(["Smooth Shaded", "Wireframe on Surface", "Wireframe", "Flat Shaded", "Geometry Only", "Points"])
        display_layout.addWidget(self.draw_mode_combo)

        layout.addWidget(camera)
        layout.addWidget(display)
        layout.addStretch()

        self.frame_all_button.clicked.connect(self.frame_all_requested)
        self.frame_selected_button.clicked.connect(self.frame_selected_requested)
        self.reset_button.clicked.connect(self.reset_camera_requested)
        self.draw_mode_combo.currentTextChanged.connect(self.draw_mode_changed)
