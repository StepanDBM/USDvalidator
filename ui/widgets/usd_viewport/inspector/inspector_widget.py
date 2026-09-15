from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from .context_tabs import ContextTabs
from .property_table import PropertyTable


class PrimInspector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.properties = PropertyTable()
        self.context = ContextTabs()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.properties)
        splitter.addWidget(self.context)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([650, 430])
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        self.properties.property_selected.connect(self.context.set_property)

    def set_prim(self, prim):
        self.properties.set_prim(prim)
        self.context.set_prim(prim)

    def select_property(self, property_path):
        return self.properties.select_property(property_path)

    def show_validation_results(self, results, selected=None):
        self.context.show_validation_results(results, selected)

    def show_semantic_change(self, change, side):
        self.context.show_semantic_change(change, side)

    def set_current_time(self, value):
        self.properties.set_current_time(value)

    def selected_time_samples(self):
        return self.properties.selected_time_samples()
