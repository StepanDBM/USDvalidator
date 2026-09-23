from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)

from s_usd_core.validation.attribute_override import AttributeOverride


from s_usd_desktop.ui.tooltips import TooltipText


class OverridePickerDialog(QDialog):
    def __init__(
        self,
        fields,
        base_config,
        definitions,
        profile_check_ids=(),
        existing_override=None,
        parent=None,
    ):
        super().__init__(parent)
        self.fields = tuple(fields)
        self.base_config = base_config
        self.definitions = {item.check_id: item for item in definitions}
        self.profile_check_ids = set(profile_check_ids)
        self.existing_override = existing_override
        self.value_editor = None
        self._loading = False
        self.setWindowTitle("Edit Override" if existing_override else "Create Override")
        self.resize(620, 470)
        self._build_ui()
        self._populate_sections()
        self._load_existing_override()

    def selected_override(self):
        field = self._current_field()
        return AttributeOverride(
            path=field.path,
            value=self._editor_value(),
            enabled=self.enabled_checkbox.isChecked(),
        )

    def related_check_ids_to_add(self):
        if not self.add_related_checkbox.isChecked():
            return ()

        return tuple(
            check_id for check_id in self._current_field().related_check_ids
            if check_id not in self.profile_check_ids
        )

    def _build_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Edit Override" if self.existing_override else "Create Override")
        help_label = QLabel(
            "Select a known configuration field. The final path and value type are generated automatically."
        )
        help_label.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(help_label)

        form_group = QGroupBox("Override Setup")
        self.form = QFormLayout(form_group)
        self.section_combo = QComboBox()
        self.attribute_combo = QComboBox()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.value_row = QHBoxLayout()
        self.form.addRow("Section:", self.section_combo)
        self.form.addRow("Attribute:", self.attribute_combo)
        self.form.addRow("Generated Path:", self.path_edit)
        self.form.addRow("Value:", self.value_row)
        layout.addWidget(form_group)

        metadata_group = QGroupBox("Field Information")
        metadata_layout = QFormLayout(metadata_group)
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.default_label = QLabel()
        self.type_label = QLabel()
        self.related_label = QLabel()
        self.related_label.setWordWrap(True)
        self.enabled_checkbox = QCheckBox("Enabled")
        self.add_related_checkbox = QCheckBox("Also add missing related checks")
        self.section_combo.setToolTip(TooltipText.OVERRIDE_PICKER_SEARCH)
        self.attribute_combo.setToolTip(TooltipText.PROFILE_CREATE_OVERRIDE)
        self.path_edit.setToolTip(TooltipText.PROFILE_OVERRIDE_ROW)
        self.enabled_checkbox.setToolTip(TooltipText.PROFILE_TOGGLE_OVERRIDE)
        self.add_related_checkbox.setToolTip(
            "Add checks associated with this setting when those checks are not "
            "already included in the profile. This can broaden validation scope."
        )
        metadata_layout.addRow("Description:", self.description_label)
        metadata_layout.addRow("Default:", self.default_label)
        metadata_layout.addRow("Expected Type:", self.type_label)
        metadata_layout.addRow("Related Checks:", self.related_label)
        metadata_layout.addRow("", self.enabled_checkbox)
        metadata_layout.addRow("", self.add_related_checkbox)
        layout.addWidget(metadata_group, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Replace Override" if self.existing_override else "Create Override"
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.section_combo.currentTextChanged.connect(self._populate_attributes)
        self.attribute_combo.currentIndexChanged.connect(self._on_field_changed)

    def _populate_sections(self):
        sections = sorted({field.path.split(".", 1)[0] for field in self.fields})
        self.section_combo.addItems(sections)

    def _populate_attributes(self):
        section = self.section_combo.currentText()
        self.attribute_combo.blockSignals(True)
        self.attribute_combo.clear()

        for field in self.fields:
            if field.path.split(".", 1)[0] == section:
                self.attribute_combo.addItem(field.label, field.path)

        self.attribute_combo.blockSignals(False)
        self._on_field_changed()

    def _load_existing_override(self):
        self.enabled_checkbox.setChecked(
            self.existing_override.enabled if self.existing_override else True
        )

        if not self.existing_override:
            return

        section = self.existing_override.path.split(".", 1)[0]
        self.section_combo.setCurrentText(section)
        index = self.attribute_combo.findData(self.existing_override.path)

        if index >= 0:
            self.attribute_combo.setCurrentIndex(index)
            self._set_editor_value(self.existing_override.value)

    def _current_field(self):
        path = self.attribute_combo.currentData()
        return next(field for field in self.fields if field.path == path)

    def _on_field_changed(self, index=0):
        if self.attribute_combo.currentIndex() < 0:
            return

        field = self._current_field()
        default = self._get_config_value(self.base_config, field.path)
        self.path_edit.setText(field.path)
        self.description_label.setText(field.description)
        self.default_label.setText(str(default))
        self.type_label.setText(field.value_type.__name__)
        related_names = [
            self.definitions[check_id].label
            for check_id in field.related_check_ids
            if check_id in self.definitions
        ]
        self.related_label.setText(", ".join(related_names) or "None")
        has_missing_related = any(
            check_id not in self.profile_check_ids
            for check_id in field.related_check_ids
        )
        self.add_related_checkbox.setVisible(has_missing_related)
        self.add_related_checkbox.setChecked(has_missing_related)
        self._replace_value_editor(field, default)

    def _replace_value_editor(self, field, value):
        while self.value_row.count():
            item = self.value_row.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        if field.choices:
            editor = QComboBox()
            editor.addItems([str(choice) for choice in field.choices])
            editor.setCurrentText(str(value))
        elif field.value_type is bool:
            editor = QComboBox()
            editor.addItems(["True", "False"])
            editor.setCurrentText(str(bool(value)))
        elif field.value_type is int:
            editor = QSpinBox()
            editor.setRange(
                int(field.minimum if field.minimum is not None else -2147483648),
                int(field.maximum if field.maximum is not None else 2147483647),
            )
            editor.setValue(int(value))
        elif field.value_type is float:
            editor = QDoubleSpinBox()
            editor.setRange(
                float(field.minimum if field.minimum is not None else -999999999.0),
                float(field.maximum if field.maximum is not None else 999999999.0),
            )
            editor.setDecimals(6)
            editor.setValue(float(value))
        else:
            editor = QLineEdit(str(value))

        self.value_editor = editor
        self.value_editor.setToolTip(TooltipText.OVERRIDE_VALUE)
        self.value_row.addWidget(editor)

    def _editor_value(self):
        field = self._current_field()

        if field.choices:
            value = self.value_editor.currentText()
            return next((item for item in field.choices if str(item) == value), value)
        if field.value_type is bool:
            return self.value_editor.currentText() == "True"
        if field.value_type in (int, float):
            return self.value_editor.value()

        return self.value_editor.text()

    def _set_editor_value(self, value):
        field = self._current_field()

        if field.choices or field.value_type is bool:
            self.value_editor.setCurrentText(str(value))
        elif field.value_type in (int, float):
            self.value_editor.setValue(value)
        else:
            self.value_editor.setText(str(value))

    @staticmethod
    def _get_config_value(config, path):
        value = config

        for part in path.split("."):
            value = getattr(value, part)

        return value
