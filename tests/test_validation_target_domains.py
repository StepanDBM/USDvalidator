from types import SimpleNamespace
import pytest
pytest.importorskip("pxr")

from contexts import GeometryStatistics, MeshGeometry
from rules.common import property_target_results, target_results
from rules.geometry.checks import check_mesh_has_valid_topology
from rules.normals.checks import check_mesh_normals_count_valid
from rules.uvs.checks import check_mesh_uv_indices_valid
from validation.enums import CheckStatus, Severity


def runtime():
    return SimpleNamespace(default_severity=Severity.ERROR)

def test_target_helpers_cover_passed_failed_and_property_paths():
    items = [SimpleNamespace(path="/World/Good", valid=True), SimpleNamespace(path="/World/Bad", valid=False)]
    targets = target_results(items, lambda item: item.path, lambda item: not item.valid)
    properties = property_target_results(items, lambda item: item.path, "points", lambda item: not item.valid)
    assert [item.status for item in targets] == [CheckStatus.PASSED, CheckStatus.FAILED]
    assert properties[1].property_path == "/World/Bad.points"


def test_geometry_aggregate_emits_every_evaluated_mesh_target():
    meshes = [MeshGeometry(path="/Good", topology_valid=True), MeshGeometry(path="/Bad", topology_valid=False)]
    context = SimpleNamespace(geometry=GeometryStatistics(meshes=meshes))
    result = check_mesh_has_valid_topology(context, runtime())[0]
    assert result.status is CheckStatus.FAILED
    assert [target.prim_path for target in result.targets] == ["/Good", "/Bad"]
    assert [target.status for target in result.targets] == [CheckStatus.PASSED, CheckStatus.FAILED]


def test_normals_and_uv_aggregates_emit_mixed_property_targets():
    surfaces = [
        SimpleNamespace(mesh_path="/Good", normals_authored=True, normals_count=3, normals_interpolation="vertex", point_count=3, face_vertex_count=3, uv_indices_valid=(("st", True),)),
        SimpleNamespace(mesh_path="/Bad", normals_authored=True, normals_count=1, normals_interpolation="vertex", point_count=3, face_vertex_count=3, uv_indices_valid=(("st", False),)),
    ]
    context = SimpleNamespace(lookdev=SimpleNamespace(surfaces=surfaces))
    normals = check_mesh_normals_count_valid(context, runtime())[0]
    uvs = check_mesh_uv_indices_valid(context, runtime())[0]
    assert {target.status for target in normals.targets} == {CheckStatus.PASSED, CheckStatus.FAILED}
    assert {target.status for target in uvs.targets} == {CheckStatus.PASSED, CheckStatus.FAILED}
    assert uvs.targets[1].property_path == "/Bad.primvars:st:indices"
