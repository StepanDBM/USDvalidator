from PySide6.QtWidgets import QMenu


class CheckContextMenu(QMenu):
    def __init__(
        self,
        fields,
        get_override,
        create_override,
        edit_override,
        set_override_enabled,
        remove_override,
        remove_check,
        parent=None,
    ):
        super().__init__(parent)
        self.fields = tuple(fields)
        self.get_override = get_override
        self.create_override = create_override
        self.edit_override = edit_override
        self.set_override_enabled = set_override_enabled
        self.remove_override = remove_override
        self.remove_check = remove_check
        self._build()

    def _build(self):
        if not self.fields:
            action = self.addAction("No configurable values")
            action.setEnabled(False)
        else:
            missing = [
                field for field in self.fields
                if self.get_override(field.path) is None
            ]
            existing = [
                field for field in self.fields
                if self.get_override(field.path) is not None
            ]
            enabled = [
                field for field in existing
                if self.get_override(field.path).enabled
            ]
            disabled = [
                field for field in existing
                if not self.get_override(field.path).enabled
            ]
            self._add_field_actions(
                "Create Override", missing, self.create_override, True
            )
            self._add_field_actions(
                "Edit Override", existing, self.edit_override, True
            )
            self._add_field_actions(
                "Enable Override",
                disabled,
                lambda field: self.set_override_enabled(field, True),
            )
            self._add_field_actions(
                "Disable Override",
                enabled,
                lambda field: self.set_override_enabled(field, False),
            )
            self._add_field_actions(
                "Remove Override", existing, self.remove_override
            )

        self.addSeparator()
        self.addAction("Remove Check from Profile").triggered.connect(
            self.remove_check
        )

    def _add_field_actions(self, title, fields, callback, ellipsis=False):
        if not fields:
            return

        if len(fields) == 1:
            action = self.addAction(f"{title}..." if ellipsis else title)
            action.triggered.connect(
                lambda checked=False, field=fields[0]: callback(field)
            )
            return

        submenu = self.addMenu(title)

        for field in fields:
            label = f"{field.label}..." if ellipsis else field.label
            action = submenu.addAction(label)
            action.triggered.connect(
                lambda checked=False, current=field: callback(current)
            )
