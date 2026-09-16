from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainterPath, QPen
from PySide6.QtWidgets import QStyledItemDelegate


class PrimRowDelegate(QStyledItemDelegate):
    eye_width = 24
    badge_width = 28

    def paint(self, painter, option, index):
        if index.column() != 0:
            super().paint(painter, option, index)
            return

        hidden = bool(index.data(Qt.ItemDataRole.UserRole + 2))
        effectively_hidden = bool(
            index.data(Qt.ItemDataRole.UserRole + 3)
        )
        ancestor_hidden = bool(
            index.data(Qt.ItemDataRole.UserRole + 4)
        )
        summary = index.data(Qt.ItemDataRole.UserRole + 5)
        validation_visible = bool(
            index.data(Qt.ItemDataRole.UserRole + 6)
        )
        context_only = index.data(Qt.ItemDataRole.UserRole + 20) == 2

        validation_width = (
            self.badge_width
            if validation_visible and summary and summary.total_count
            else 0
        )

        text_option = type(option)(option)
        text_option.rect.adjust(
            self.eye_width + validation_width,
            0,
            0,
            0,
        )

        if effectively_hidden or context_only:
            text_option.palette.setColor(
                text_option.palette.ColorRole.Text,
                QColor("#777777" if effectively_hidden else "#8f98a3"),
            )

        super().paint(painter, text_option, index)

        painter.save()

        self._draw_eye(
            painter,
            self.eye_rect(option.rect),
            open_eye=not effectively_hidden,
            dimmed=ancestor_hidden and not hidden,
        )

        if validation_width:
            self._draw_badge(
                painter,
                self.badge_rect(option.rect),
                summary,
            )

        painter.restore()

    def editorEvent(self, event, model, option, index):
        if (
            index.column() != 0
            or event.type() != QEvent.Type.MouseButtonRelease
        ):
            return super().editorEvent(
                event,
                model,
                option,
                index,
            )

        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.eye_rect(option.rect).contains(
                event.position()
            )
        ):
            source_model = (
                model.sourceModel()
                if hasattr(model, "sourceModel")
                else model
            )
            source_index = (
                model.mapToSource(index)
                if hasattr(model, "mapToSource")
                else index
            )
            path = source_index.data(Qt.ItemDataRole.UserRole)
            source_model.request_visibility(path)
            return True

        return super().editorEvent(
            event,
            model,
            option,
            index,
        )

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)

        if index.column() != 0:
            return size

        summary = index.data(Qt.ItemDataRole.UserRole + 5)
        validation_visible = bool(
            index.data(Qt.ItemDataRole.UserRole + 6)
        )
        context_only = index.data(Qt.ItemDataRole.UserRole + 20) == 2
        validation_width = (
            self.badge_width
            if validation_visible and summary and summary.total_count
            else 0
        )

        size.setWidth(
            size.width()
            + self.eye_width
            + validation_width
        )
        return size

    def eye_rect(self, row_rect):
        size = min(16, row_rect.height() - 4)
        left = row_rect.left() + 3
        top = row_rect.center().y() - size / 2

        return QRectF(
            left,
            top,
            size + 3,
            size,
        )

    def badge_rect(self, row_rect):
        size = min(19, row_rect.height() - 2)
        left = row_rect.left() + self.eye_width + 2
        top = row_rect.center().y() - size / 2

        return QRectF(
            left,
            top,
            size,
            size,
        )

    @staticmethod
    def _draw_badge(painter, rect, summary):
        painter.setRenderHint(
            painter.RenderHint.Antialiasing,
            True,
        )

        fill = _badge_fill(summary)
        outline = _badge_outline(summary)

        painter.setBrush(fill)
        painter.setPen(QPen(outline, 2))
        painter.drawEllipse(rect)

        font = QFont(painter.font())
        font.setBold(True)
        font.setPixelSize(9)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))

        count = (
            "99+"
            if summary.total_count > 99
            else str(summary.total_count)
        )

        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            count,
        )

    @staticmethod
    def _draw_eye(painter, rect, open_eye, dimmed):
        color = QColor(
            "#7f8790"
            if dimmed
            else "#d7dce2"
        )

        painter.setRenderHint(
            painter.RenderHint.Antialiasing,
            True,
        )
        painter.setPen(QPen(color, 1.4))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        center = rect.center()
        eye = QPainterPath()
        eye.moveTo(rect.left(), center.y())
        eye.quadTo(
            center.x(),
            rect.top(),
            rect.right(),
            center.y(),
        )
        eye.quadTo(
            center.x(),
            rect.bottom(),
            rect.left(),
            center.y(),
        )
        painter.drawPath(eye)

        if open_eye:
            painter.setBrush(color)
            painter.drawEllipse(
                QPointF(center.x(), center.y()),
                2.5,
                2.5,
            )
        else:
            painter.drawLine(
                rect.topLeft(),
                rect.bottomRight(),
            )


def _badge_fill(summary):
    if not summary.is_aggregate:
        if summary.failed_count:
            return QColor("#d94848")

        if summary.passed_count:
            return QColor("#43a766")

        if summary.skipped_count:
            return QColor("#75808d")

        return QColor("#3f83bd")

    passed = summary.passed_count
    failed = summary.failed_count
    evaluated = passed + failed

    if not evaluated:
        return QColor("#75808d")

    ratio = passed / evaluated

    if ratio <= 0.5:
        amount = ratio * 2.0
        return _mix(
            QColor("#d94848"),
            QColor("#e3bc42"),
            amount,
        )

    amount = (ratio - 0.5) * 2.0
    return _mix(
        QColor("#e3bc42"),
        QColor("#43a766"),
        amount,
    )


def _badge_outline(summary):
    if summary.error_count:
        return QColor("#8e1515")
    if summary.failed_count and summary.highest_severity_rank >= 3:
        return QColor("#b32626")
    if summary.warning_count:
        return QColor("#e17a2d")
    if summary.information_count:
        return QColor("#3e88c5")
    if summary.skipped_count and not summary.passed_count:
        return QColor("#75808d")
    return QColor("#277343")


def _mix(first, second, amount):
    amount = max(0.0, min(1.0, amount))

    return QColor(
        round(
            first.red()
            + (second.red() - first.red()) * amount
        ),
        round(
            first.green()
            + (second.green() - first.green()) * amount
        ),
        round(
            first.blue()
            + (second.blue() - first.blue()) * amount
        ),
    )