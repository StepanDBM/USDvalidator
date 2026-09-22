import pytest

pytest.importorskip("PySide6")

from s_usd_desktop.ui.widgets.comparison_browser.comparison_view import ComparisonView


class FakeEdit:
    def __init__(self):
        self.value = ""

    def setText(self, value):
        self.value = value

    def text(self):
        return self.value


class FakeComparisonView:
    previous_edit = FakeEdit()
    current_edit = FakeEdit()


def test_stored_sources_populate_existing_comparison_inputs():
    view = FakeComparisonView()

    ComparisonView.set_sources(
        view,
        "C:/cache/v0001/root.usda",
        "C:/cache/v0002/root.usda"
    )

    assert view.previous_edit.text() == "C:/cache/v0001/root.usda"
    assert view.current_edit.text() == "C:/cache/v0002/root.usda"

def test_start_comparison_delegates_to_existing_engine_entrypoint():
    called = []
    view = type("View", (), {"_compare": lambda self: called.append(True)})()

    ComparisonView.start_comparison(view)

    assert called == [True]
