from pathlib import Path

from validation import CheckStatus, PublishChecker


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def get_result(report, check_id):
    return next(
        result
        for result in report.results
        if result.check_id == check_id
    )


def test_invalid_geometry_topology_is_detected():
    source_path = FIXTURES_DIR / "invalid_geometry_prims.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_MESH_HAS_VALID_TOPOLOGY",
    )

    assert result.status is CheckStatus.FAILED

def test_invalid_geometry_points():
    source_path = FIXTURES_DIR / "invalid_geometry_prims.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_MESH_HAS_VALID_POINTS",
    )

    assert result.status is CheckStatus.PASSED


def test_invalid_geometry_face_vertex_counts():
    source_path = FIXTURES_DIR / "invalid_geometry_prims.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_MESH_FACE_VERTEX_COUNTS_VALID",
    )

    assert result.status is CheckStatus.FAILED

def test_polygon_count_limit():
    source_path = FIXTURES_DIR / "invalid_geometry_polygon_limit.usda"

    report = PublishChecker().check(source_path)

    result = get_result(
        report,
        "USD_MESH_POLYGON_COUNT_LIMIT",
    )

    assert result.status is CheckStatus.FAILED