from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen
from PySide6.QtWidgets import QStyle, QStyledItemDelegate


class PrimRowDelegate(QStyledItemDelegate):
    eye_width = 24

    def paint(self, painter, option, index):
        if index.column() != 0:
            super().paint(painter, option, index)
            return

        path = index.data(Qt.ItemDataRole.UserRole)
        hidden = bool(index.data(Qt.ItemDataRole.UserRole + 2))
        effective_hidden = bool(index.data(Qt.ItemDataRole.UserRole + 3))
        ancestor_hidden = bool(index.data(Qt.ItemDataRole.UserRole + 4))

        text_option = type(option)(option)
        text_option.rect.adjust(self.eye_width, 0, 0, 0)
        if effective_hidden:
            text_option.palette.setColor(text_option.palette.ColorRole.Text, QColor("#777777"))
        super().paint(painter, text_option, index)

        painter.save()
        self._draw_eye(
            painter,
            self.eye_rect(option.rect),
            open_eye=not effective_hidden,
            dimmed=ancestor_hidden and not hidden,
        )
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if index.column() != 0 or event.type() != QEvent.Type.MouseButtonRelease:
            return super().editorEvent(event, model, option, index)
        if event.button() == Qt.MouseButton.LeftButton and self.eye_rect(option.rect).contains(event.position()):
            source_model = model.sourceModel() if hasattr(model, "sourceModel") else model
            source_index = model.mapToSource(index) if hasattr(model, "mapToSource") else index
            source_model.request_visibility(source_index.data(Qt.ItemDataRole.UserRole))
            return True
        return super().editorEvent(event, model, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        if index.column() == 0:
            size.setWidth(size.width() + self.eye_width)
        return size

    def eye_rect(self, row_rect):
        size = min(16, row_rect.height() - 4)
        left = row_rect.left() + 3
        top = row_rect.center().y() - size / 2
        return QRectF(left, top, size + 3, size)

    @staticmethod
    def _draw_eye(painter, rect, open_eye, dimmed):
        color = QColor("#7f8790" if dimmed else "#d7dce2")
        painter.setRenderHint(painter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(color, 1.4))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        center = rect.center()
        eye = QPainterPath()
        eye.moveTo(rect.left(), center.y())
        eye.quadTo(center.x(), rect.top(), rect.right(), center.y())
        eye.quadTo(center.x(), rect.bottom(), rect.left(), center.y())
        painter.drawPath(eye)

        if open_eye:
            painter.setBrush(color)
            painter.drawEllipse(QPointF(center.x(), center.y()), 2.5, 2.5)
        else:
            painter.drawLine(rect.topLeft(), rect.bottomRight())
