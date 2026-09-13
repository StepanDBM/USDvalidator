from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolButton, QVBoxLayout, QWidget


class CollapsiblePanel(QWidget):
    def __init__(
        self,
        title,
        content_widget,
        expanded=False,
        parent=None,
    ):
        super().__init__(parent)

        self.content_widget = content_widget

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

        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_widget)

        self.toggle_button.toggled.connect(self._set_expanded)
        self._set_expanded(expanded)

    def is_expanded(self):
        return self.toggle_button.isChecked()

    def set_expanded(self, expanded):
        self.toggle_button.setChecked(expanded)

    def _set_expanded(self, expanded):
        arrow = (
            Qt.ArrowType.DownArrow
            if expanded
            else Qt.ArrowType.RightArrow
        )

        self.toggle_button.setArrowType(arrow)
        self.content_widget.setVisible(expanded)