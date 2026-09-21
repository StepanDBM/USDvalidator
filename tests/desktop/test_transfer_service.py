import os
from io import BytesIO

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from s_usd_desktop.services.transfer_service import (
    CancellationToken,
    ProgressFile,
    TransferCancelledError
)


def test_progress_file_reports_bytes():
    values = []
    source = ProgressFile(BytesIO(b"abcdef"), 6, lambda sent, total: values.append((sent, total)), CancellationToken())

    assert source.read(2) == b"ab"
    assert source.read(4) == b"cdef"
    assert values == [(2, 6), (6, 6)]


def test_progress_file_can_be_cancelled():
    token = CancellationToken()
    source = ProgressFile(BytesIO(b"abcdef"), 6, lambda *_: None, token)
    token.cancel()

    with pytest.raises(TransferCancelledError):
        source.read(2)
