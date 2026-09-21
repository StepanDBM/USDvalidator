from s_usd_core.validation.publish_report import PublishReport
from s_usd_core.validation.version import REPORT_SCHEMA_NAME, TOOL_NAME, TOOL_VERSION


def test_new_reports_use_s_usdv_provenance():
    data = PublishReport("scene.usda", True, "scene.usda").to_dict()

    assert TOOL_NAME == "S-USDv"
    assert TOOL_VERSION == "0.6.0"
    assert REPORT_SCHEMA_NAME == "s-usdv.validation_report"
    assert data["generator"] == {"name": "S-USDv", "version": "0.6.0"}
    assert data["schema"]["name"] == "s-usdv.validation_report"
