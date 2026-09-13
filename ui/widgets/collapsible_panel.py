from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QToolButton, QVBoxLayout, QWidget


class CollapsiblePanel(QWidget):
    def __init__(self, title, content_widget, expanded=True, parent=None):
        super().__init__(parent)

        self.content_widget = content_widget

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(expanded)
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.toggle_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_widget)

        self.toggle_button.toggled.connect(self._set_expanded)
        self._set_expanded(expanded)

    def is_expanded(self):
        return self.toggle_button.isChecked()

    def set_expanded(self, expanded):
        self.toggle_button.setChecked(expanded)

    def _set_expanded(self, expanded):
        self.toggle_button.setArrowType(
            Qt.ArrowType.DownArrow
            if expanded
            else Qt.ArrowType.RightArrow
        )
        self.content_widget.setVisible(expanded)
        self.updateGeometry()