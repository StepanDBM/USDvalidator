from contexts import StageHealthContext
from contexts.pipeline_context import CameraInfo, DependencyInfo, InstancingInfo, PrimInfo, TransformInfo, VariantSetInfo
from rules.cameras.checks import check_camera_count_limit
from rules.hierarchy.checks import check_required_hierarchy_paths_exist
from rules.instancing.checks import check_point_instancer_indices_valid
from rules.naming.checks import check_forbidden_prim_names
from rules.packaging.checks import check_no_parent_directory_escapes
from rules.transforms.checks import check_negative_scale_allowed
from rules.variants.checks import check_variant_selections_authored
from validation.enums import CheckStatus, Severity
from validation.rule_config import ValidationRuleConfig
from validation.runtime_context import CheckRuntimeContext


def runtime(config=None):
    return CheckRuntimeContext("TEST", Severity.ERROR, config or ValidationRuleConfig())


def test_naming_forbidden_name():
    context = StageHealthContext()
    context.pipeline.prims = [PrimInfo("/World/pCube1", "pCube1", "/World", "Mesh", 2)]
    assert check_forbidden_prim_names(context, runtime())[0].status is CheckStatus.FAILED


def test_hierarchy_required_path():
    context = StageHealthContext()
    context.pipeline.prims = [PrimInfo("/World", "World", "/", "Xform", 1)]
    config = ValidationRuleConfig()
    config.hierarchy.required_paths_csv = "/World,/World/Geometry"
    assert check_required_hierarchy_paths_exist(context, runtime(config))[0].status is CheckStatus.FAILED


def test_negative_scale_policy():
    context = StageHealthContext()
    context.pipeline.transforms = [TransformInfo("/World/Mirror", ("xformOp:scale",), False, False, 0, ((-1.0, 1.0, 1.0),), True, False)]
    assert check_negative_scale_allowed(context, runtime())[0].status is CheckStatus.FAILED


def test_variant_selection_required():
    context = StageHealthContext()
    context.pipeline.variants = [VariantSetInfo("/World", "modelVariant", ("A", "B"), "")]
    assert check_variant_selections_authored(context, runtime())[0].status is CheckStatus.FAILED


def test_camera_count_override():
    context = StageHealthContext()
    context.pipeline.cameras = [CameraInfo("/World/A", "perspective", 35.0, (0.1, 1000.0), False), CameraInfo("/World/B", "perspective", 50.0, (0.1, 1000.0), False)]
    config = ValidationRuleConfig()
    config.cameras.maximum_count = 1
    assert check_camera_count_limit(context, runtime(config))[0].status is CheckStatus.FAILED


def test_point_instancer_indices():
    context = StageHealthContext()
    context.pipeline.instances = [InstancingInfo("/World/Instances", False, False, "", True, 1, 3, 2)]
    assert check_point_instancer_indices_valid(context, runtime())[0].status is CheckStatus.FAILED


def test_packaging_parent_escape():
    context = StageHealthContext()
    context.pipeline.dependencies = [DependencyInfo("/World/Asset", "reference", "../outside.usda", False, True, False)]
    assert check_no_parent_directory_escapes(context, runtime())[0].status is CheckStatus.FAILED
