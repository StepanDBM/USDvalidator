import os
from types import SimpleNamespace

import httpx
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from s_usd_desktop.client import AuthenticationClient, SUsdvApiClient
from s_usd_desktop.client.configuration import ApiClientConfiguration
from s_usd_desktop.ui.dialogs.workspace import CreateWorkspaceDialog


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


def test_create_workspace_client_sends_expected_payload():
    captured = {}

    def handler(request):
        captured["path"] = request.url.path
        captured["payload"] = request.read().decode()
        return httpx.Response(
            201,
            json={
                "id": "6d017841-177a-4225-ab94-3f4756c302cd",
                "code": "HOME",
                "name": "Home Workspace",
                "description": "Production",
                "status": "active",
            },
        )

    with SUsdvApiClient(ApiClientConfiguration(), transport=httpx.MockTransport(handler)) as api:
        workspace = AuthenticationClient(api).create_workspace("HOME", "Home Workspace", "Production")

    assert captured["path"] == "/api/v1/workspaces"
    assert '"code":"HOME"' in captured["payload"]
    assert workspace.code == "HOME"


def test_create_workspace_dialog_requires_code_and_name(application):
    dialog = CreateWorkspaceDialog()
    dialog._validate()
    assert dialog.error_label.isVisibleTo(dialog)
    dialog.code_edit.setText("HOME")
    dialog.name_edit.setText("Home Workspace")
    assert dialog.workspace_data() == {
        "code": "HOME",
        "name": "Home Workspace",
        "description": "",
    }
    dialog.close()


def test_main_window_workspace_controls_are_authenticated_only(application, monkeypatch):
    from s_usd_desktop.services.session_service import SessionState
    from s_usd_desktop.ui.main_window import MainWindow

    monkeypatch.setattr(MainWindow, "_change_theme", lambda *_: None)
    window = MainWindow()
    window._session_state_changed(SessionState.SIGNED_OUT)
    assert not window.create_workspace_button.isEnabled()
    window._session_state_changed(SessionState.AUTHENTICATED)
    assert window.create_workspace_button.isEnabled()
    window._set_workspaces((SimpleNamespace(id="one", code="ONE", name="One"),))
    assert window.workspace_selector.isEnabled()
    assert window.manage_workspace_button.isEnabled()
    window.close()
