# tests/test_stage_health.py

from pathlib import Path

from validation import PublishChecker


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def get_report():
    source_path = FIXTURES_DIR / "valid_stage.usda"
    return PublishChecker().check(source_path)


def test_valid_stage_produces_health_report():
    report = get_report()

    assert report.stage_health is not None


def test_file_health_is_extracted():
    report = get_report()
    health = report.stage_health

    assert health.file.filename == "valid_stage.usda"
    assert health.file.extension == ".usda"
    assert health.file.size_bytes > 0
    assert health.file.modification_time is not None


def test_stage_metadata_is_extracted():
    report = get_report()
    stage = report.stage_health.stage

    assert stage.root_layer
    assert stage.default_prim == "/World"
    assert stage.up_axis == "Y"
    assert stage.meters_per_unit == 1
    assert stage.frames_per_second == 24
    assert stage.time_codes_per_second == 24
    assert stage.start_time_code == 1
    assert stage.end_time_code == 120
    assert stage.open_duration_seconds >= 0


def test_scene_statistics_are_extracted():
    report = get_report()
    scene = report.stage_health.scene

    assert scene.total_prims == 11
    assert scene.active_prims == 11
    assert scene.inactive_prims == 0
    assert scene.defined_prims == 11


def test_type_counts_are_extracted():
    report = get_report()
    types = report.stage_health.types

    assert types.meshes == 3
    assert types.xforms == 4
    assert types.cameras == 1
    assert types.materials == 1
    assert types.curves == 0
    assert types.point_instancers == 0


def test_composition_statistics_are_extracted():
    report = get_report()
    composition = report.stage_health.composition

    assert composition.used_layers >= 1
    assert composition.sublayers == 0
    assert composition.references == 0
    assert composition.payloads == 0
    assert composition.variant_sets == 0


def test_missing_stage_has_no_health_report():
    source_path = FIXTURES_DIR / "does_not_exist.usda"
    report = PublishChecker().check(source_path)

    assert report.stage_health is None

def test_default_prim_validity_is_extracted():
    report = get_report()
    stage = report.stage_health.stage

    assert stage.default_prim == "/World"
    assert stage.default_prim_valid is True