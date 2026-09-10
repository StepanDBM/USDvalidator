# extraction/stage_health.py

from pathlib import Path

from pxr import UsdGeom, UsdShade

from extraction.geometry import GeometryExtractor
from extraction.animation import AnimationExtractor

# I intentionally do not use schema wrappers such as:
# UsdGeom.Mesh(prim)
# just to count types. For a factual health scan, prim.GetTypeName() is simpler and cheaper.
class StageHealthExtractor:
    def extract(self, stage, source_path, open_duration_seconds):
        source_path = Path(source_path)

        from contexts import (
            CompositionStatistics,
            FileHealth,
            SceneStatistics,
            StageHealthContext,
            StageMetadata,
            TypeCounts,
        )

        health = StageHealthContext(
            file=FileHealth(
                filename=source_path.name,
                extension=source_path.suffix.lower(),
                size_bytes=source_path.stat().st_size,
                modification_time=source_path.stat().st_mtime,
            ),
            stage=StageMetadata(
                open_duration_seconds=open_duration_seconds,
                root_layer=stage.GetRootLayer().identifier,
                default_prim=self._get_default_prim_name(stage),
                default_prim_valid=self._is_default_prim_valid(stage),
                up_axis=UsdGeom.GetStageUpAxis(stage),
                meters_per_unit=UsdGeom.GetStageMetersPerUnit(stage),
                frames_per_second=stage.GetFramesPerSecond(),
                time_codes_per_second=stage.GetTimeCodesPerSecond(),
                start_time_code=stage.GetStartTimeCode(),
                end_time_code=stage.GetEndTimeCode(),
            ),
        )
        for prim in stage.TraverseAll():
            self._count_scene_prim(health.scene, prim)
            self._count_type(health.types, prim)
            self._count_composition(health.composition, prim)

        # Root prims are the direct children of the pseudo-root.
        health.scene.root_prims = len(
            stage.GetPseudoRoot().GetChildren()
        )

        health.composition.used_layers = len(stage.GetUsedLayers())
        health.composition.sublayers = len(
            stage.GetRootLayer().subLayerPaths
        )
        health.geometry = GeometryExtractor().extract(stage)
        health.animation = AnimationExtractor().extract(stage)

        return health

    @staticmethod
    def _get_default_prim_name(stage):
        default_prim_name = stage.GetMetadata("defaultPrim")

        if not default_prim_name:
            return ""

        return f"/{default_prim_name}"


    @staticmethod
    def _is_default_prim_valid(stage):
        default_prim_name = stage.GetMetadata("defaultPrim")

        if not default_prim_name:
            return None

        default_prim_path = f"/{default_prim_name}"

        return stage.GetPrimAtPath(default_prim_path).IsValid()

    @staticmethod
    def _count_scene_prim(statistics, prim):
        statistics.total_prims += 1

        if prim.IsActive():
            statistics.active_prims += 1
        else:
            statistics.inactive_prims += 1

        if prim.IsDefined():
            statistics.defined_prims += 1

        if prim.IsAbstract():
            statistics.abstract_prims += 1

        if prim.IsInstance():
            statistics.instance_prims += 1

    @staticmethod
    def _count_type(type_counts, prim):
        type_name = prim.GetTypeName()

        if type_name == "Mesh":
            type_counts.meshes += 1
        elif type_name == "Xform":
            type_counts.xforms += 1
        elif type_name == "Camera":
            type_counts.cameras += 1
        elif type_name in {"DistantLight", "DiskLight", "DomeLight", "RectLight", "SphereLight"}:
            type_counts.lights += 1
        elif type_name == "Material":
            type_counts.materials += 1
        elif type_name in {"BasisCurves", "NurbsCurves"}:
            type_counts.curves += 1
        elif type_name == "PointInstancer":
            type_counts.point_instancers += 1

    @staticmethod
    def _count_composition(composition, prim):
        composition.references += len(
            prim.GetMetadata("references").GetAddedOrExplicitItems()
        ) if prim.HasAuthoredReferences() else 0

        composition.payloads += len(
            prim.GetMetadata("payload").GetAddedOrExplicitItems()
        ) if prim.HasAuthoredPayloads() else 0

        composition.variant_sets += len(
            prim.GetVariantSets().GetNames()
        )