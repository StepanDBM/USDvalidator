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
    def __init__(self):
        self.previous_edit = FakeEdit()
        self.current_edit = FakeEdit()
        self.contexts_refreshed = False

    def _refresh_source_contexts(self):
        self.contexts_refreshed = True


def test_stored_sources_populate_existing_comparison_inputs():
    view = FakeComparisonView()

    ComparisonView.set_sources(
        view,
        "C:/cache/v0001/root.usda",
        "C:/cache/v0002/root.usda"
    )

    assert view.previous_edit.text() == "C:/cache/v0001/root.usda"
    assert view.current_edit.text() == "C:/cache/v0002/root.usda"
    assert view.contexts_refreshed is True

def test_start_comparison_delegates_to_existing_engine_entrypoint():
    called = []
    view = type("View", (), {"_compare": lambda self: called.append(True)})()

    ComparisonView.start_comparison(view)

    assert called == [True]


class FakeLabel:
    def __init__(self):
        self.value = ""

    def setText(self, value):
        self.value = value


class FakeRecognizer:
    def recognize(self, value):
        if "cache" not in value:
            return None
        return type("Source", (), {"display_name": "Managed cache: EXP / probe / model / v0002 / root/probe.usda"})()


def test_swap_exchanges_previous_and_current_sources():
    view = type("View", (), {
        "worker_thread": None,
        "previous_edit": FakeEdit(),
        "current_edit": FakeEdit(),
        "_refresh_source_contexts": lambda self: None
    })()
    view.previous_edit.setText("previous.usda")
    view.current_edit.setText("current.usda")

    ComparisonView.swap_sources(view)

    assert view.previous_edit.text() == "current.usda"
    assert view.current_edit.text() == "previous.usda"


def test_source_context_recognizes_managed_cache():
    view = type("View", (), {
        "cache_recognizer": FakeRecognizer(),
        "previous_context_label": FakeLabel(),
        "current_context_label": FakeLabel(),
        "previous_source": None,
        "current_source": None
    })()

    ComparisonView._source_changed(view, "previous", "C:/cache/probe.usda")

    assert view.previous_source is not None
    assert "EXP / probe / model / v0002" in view.previous_context_label.value
