from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SummaryMetric(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        self.value_label = QLabel("0")
        self.title_label = QLabel(title)
        layout.addWidget(self.value_label)
        layout.addWidget(self.title_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class SummaryHeader(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self)
        self.status_label = QLabel("NO RESULTS")
        self.source_label = QLabel("")
        self.source_label.setWordWrap(True)
        identity = QVBoxLayout()
        identity.addWidget(self.status_label)
        identity.addWidget(self.source_label)
        layout.addLayout(identity, 1)
        self.metrics = {
            "total": SummaryMetric("Checks"),
            "passed": SummaryMetric("Passed"),
            "failed": SummaryMetric("Failed"),
            "skipped": SummaryMetric("Skipped"),
            "internal_errors": SummaryMetric("Internal"),
        }
        for metric in self.metrics.values():
            layout.addWidget(metric)

    def show_report(self, report):
        status = "PASSED" if report.publish_passed else "FAILED"
        color = "#4CAF50" if report.publish_passed else "#F44336"
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: 700;")
        self.source_label.setText(str(report.source_path))
        self.source_label.setToolTip(str(report.source_path))
        summary = report.summary
        for name, metric in self.metrics.items():
            metric.set_value(getattr(summary, name))

    def show_batch(self, batch):
        passed = batch.failed_files == 0
        color = "#4CAF50" if passed else "#F44336"
        self.status_label.setText("BATCH PASSED" if passed else "BATCH FAILED")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: 700;")
        self.source_label.setText(
            f"{batch.total_files} files, {batch.passed_files} passed, "
            f"{batch.failed_files} failed"
        )
        totals = {
            "total": sum(report.summary.total for report in batch.reports),
            "passed": sum(report.summary.passed for report in batch.reports),
            "failed": sum(report.summary.failed for report in batch.reports),
            "skipped": sum(report.summary.skipped for report in batch.reports),
            "internal_errors": sum(
                report.summary.internal_errors for report in batch.reports
            ),
        }
        for name, metric in self.metrics.items():
            metric.set_value(totals[name])

    def clear_summary(self, message="NO RESULTS"):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("")
        self.source_label.clear()
        for metric in self.metrics.values():
            metric.set_value(0)
