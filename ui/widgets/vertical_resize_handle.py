from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget


class VerticalResizeHandle(QWidget):
    resize_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._drag_start_y = 0
        self._dragging = False

        self.setCursor(
            Qt.CursorShape.SizeVerCursor
        )

        self.setFixedHeight(10)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.setToolTip(
            "Drag to resize this section."
        )

    def mousePressEvent(self, event):
        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            super().mousePressEvent(event)
            return

        self._drag_start_y = (
            event.globalPosition().y()
        )

        self._dragging = True
        event.accept()

    def mouseMoveEvent(self, event):
        if not self._dragging:
            super().mouseMoveEvent(event)
            return

        current_y = event.globalPosition().y()
        delta = round(
            current_y - self._drag_start_y
        )

        if delta:
            self.resize_requested.emit(delta)
            self._drag_start_y = current_y

        event.accept()

    def mouseReleaseEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self._dragging = False
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        pen = QPen(
            self.palette().mid().color()
        )

        pen.setWidth(1)
        painter.setPen(pen)

        center_y = self.height() // 2
        center_x = self.width() // 2

        for offset in (-2, 0, 2):
            painter.drawLine(
                center_x - 24,
                center_y + offset,
                center_x + 24,
                center_y + offset,
            )