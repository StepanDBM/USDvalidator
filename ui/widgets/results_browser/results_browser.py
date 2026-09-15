from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .filter_bar import ResultsFilterBar
from .result_details import ResultDetails
from .results_tree import ResultsTree
from .summary_header import SummaryHeader


class ResultsBrowser(QWidget):
    open_in_viewport_requested = Signal(object, object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_report = None
        self.batch_report = None
        self._build_ui()
        self._connect_signals()
        self.show_message("Run validation to see results.")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.summary_header = SummaryHeader()
        self.filter_bar = ResultsFilterBar()
        layout.addWidget(self.summary_header)
        layout.addWidget(self.filter_bar)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.file_panel = QWidget()

        file_layout = QVBoxLayout(self.file_panel)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.addWidget(QLabel("Batch Files"))

        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)

        self.file_panel.setMinimumWidth(240)
        self.file_panel.hide()

        results_splitter = QSplitter(Qt.Orientation.Vertical)
        self.results_tree = ResultsTree()
        self.result_details = ResultDetails()

        results_splitter.addWidget(self.results_tree)
        results_splitter.addWidget(self.result_details)
        results_splitter.setStretchFactor(0, 2)
        results_splitter.setStretchFactor(1, 1)

        self.main_splitter.addWidget(self.file_panel)
        self.main_splitter.addWidget(results_splitter)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)

        layout.addWidget(self.main_splitter, 1)

        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)

        layout.addWidget(self.message_label)
        self.message_label.hide()

    def _connect_signals(self):
        self.filter_bar.filters_changed.connect(self._refresh_results)
        self.results_tree.result_selected.connect(self.result_details.show_result)
        self.results_tree.open_in_viewport_requested.connect(self._request_viewport)
        self.file_list.currentRowChanged.connect(self._on_file_selected)

    def show_single_report(self, report):
        self.batch_report = None
        self.current_report = report
        self.file_panel.hide()
        self.message_label.hide()
        self.main_splitter.show()
        self.summary_header.show_report(report)
        self.filter_bar.set_categories(
            {result.category for result in report.results if result.category}
        )
        self._refresh_results()

    def show_batch_report(self, batch):
        self.batch_report = batch
        self.current_report = None
        self.message_label.hide()
        self.main_splitter.show()
        self.file_panel.show()
        self.summary_header.show_batch(batch)
        self.file_list.blockSignals(True)
        self.file_list.clear()
        for report in batch.reports:
            item = QListWidgetItem(Path(report.source_path).name)
            item.setData(Qt.ItemDataRole.UserRole, report)
            item.setToolTip(str(report.source_path))
            item.setForeground(
                QColor("#4CAF50" if report.publish_passed else "#F44336")
            )
            item.setText(
                f"{'PASSED' if report.publish_passed else 'FAILED'}  "
                f"{Path(report.source_path).name}"
            )
            self.file_list.addItem(item)
        self.file_list.blockSignals(False)
        if self.file_list.count():
            self.file_list.setCurrentRow(0)
        else:
            self.show_message("The batch contains no reports.")

    def show_message(self, message):
        self.current_report = None
        self.batch_report = None
        self.file_panel.hide()
        self.main_splitter.hide()
        self.message_label.setText(str(message))
        self.message_label.show()
        self.summary_header.clear_summary("MESSAGE")

    def clear_results(self):
        self.current_report = None
        self.batch_report = None
        self.file_list.clear()
        self.results_tree.clear()
        self.result_details.show_result(None)
        self.show_message("Run validation to see results.")

    def _on_file_selected(self, row):
        if row < 0:
            return
        item = self.file_list.item(row)
        report = item.data(Qt.ItemDataRole.UserRole)
        self.current_report = report
        self.filter_bar.set_categories(
            {result.category for result in report.results if result.category}
        )
        self._refresh_results()

    def _refresh_results(self):
        if self.current_report is None:
            return
        self.results_tree.set_results(
            self.current_report.results,
            self.filter_bar.values(),
        )

    def _request_viewport(self, result):
        if self.current_report is not None:
            self.open_in_viewport_requested.emit(self.current_report, result)
