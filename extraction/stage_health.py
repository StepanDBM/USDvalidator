import os
from pathlib import Path

from pxr import UsdGeom

from extraction.animation import AnimationExtractor
from extraction.geometry import GeometryExtractor
from extraction.pipeline import PipelineExtractor
from extraction.lookdev import LookdevExtractor


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

        default_prim_path = self._get_default_prim_path(stage)
        default_prim = (
            stage.GetPrimAtPath(default_prim_path)
            if default_prim_path
            else None
        )
        default_prim_valid = (
            default_prim.IsValid()
            if default_prim is not None
            else None
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
                default_prim=default_prim_path,
                default_prim_valid=default_prim_valid,
                root_prim_name=(
                    default_prim.GetName()
                    if default_prim_valid
                    else ""
                ),
                root_prim_type=(
                    default_prim.GetTypeName()
                    if default_prim_valid
                    else ""
                ),
                up_axis=UsdGeom.GetStageUpAxis(stage),
                meters_per_unit=UsdGeom.GetStageMetersPerUnit(stage),
                frames_per_second=stage.GetFramesPerSecond(),
                time_codes_per_second=stage.GetTimeCodesPerSecond(),
                start_time_code=stage.GetStartTimeCode(),
                end_time_code=stage.GetEndTimeCode(),
            ),
        )

        health.composition.used_layers = len(stage.GetUsedLayers())
        health.composition.sublayers = len(stage.GetRootLayer().subLayerPaths)

        for prim in stage.TraverseAll():
            self._count_scene_prim(health.scene, prim)
            self._count_type(health.types, prim)
            self._count_composition(health.composition, prim)
            self._collect_composition_errors(health.composition, prim)

        health.scene.root_prims = len(stage.GetPseudoRoot().GetChildren())
        health.geometry = GeometryExtractor().extract(stage)
        health.animation = AnimationExtractor().extract(stage)
        health.pipeline = PipelineExtractor().extract(stage)
        health.lookdev = LookdevExtractor().extract(stage)
        return health

    @staticmethod
    def _count_scene_prim(statistics, prim):
        statistics.total_prims += 1
        statistics.active_prims += int(prim.IsActive())
        statistics.inactive_prims += int(not prim.IsActive())
        statistics.defined_prims += int(prim.IsDefined())
        statistics.abstract_prims += int(prim.IsAbstract())
        statistics.instance_prims += int(prim.IsInstance())
        statistics.maximum_prim_depth = max(
            statistics.maximum_prim_depth,
            prim.GetPath().pathString.count("/"),
        )

    @staticmethod
    def _count_type(counts, prim):
        type_name = prim.GetTypeName()
        mapping = {
            "Mesh": "meshes",
            "Xform": "xforms",
            "Camera": "cameras",
            "Material": "materials",
            "BasisCurves": "curves",
            "NurbsCurves": "curves",
            "PointInstancer": "point_instancers",
        }

        if type_name in mapping:
            name = mapping[type_name]
            setattr(counts, name, getattr(counts, name) + 1)
        elif type_name.endswith("Light"):
            counts.lights += 1

    @staticmethod
    def _count_composition(composition, prim):
        if prim.HasAuthoredReferences():
            items = prim.GetMetadata("references").GetAddedOrExplicitItems()
            composition.references += len(items)
            StageHealthExtractor._collect_asset_paths(composition, items)

        if prim.HasAuthoredPayloads():
            items = prim.GetMetadata("payload").GetAddedOrExplicitItems()
            composition.payloads += len(items)
            StageHealthExtractor._collect_asset_paths(composition, items)

        composition.variant_sets += len(prim.GetVariantSets().GetNames())

    @staticmethod
    def _collect_asset_paths(composition, items):
        for item in items:
            asset_path = getattr(item, "assetPath", "")

            if asset_path and os.path.isabs(asset_path):
                composition.absolute_asset_paths.append(asset_path)

    @staticmethod
    def _collect_composition_errors(composition, prim):
        for error in prim.GetPrimIndex().localErrors:
            message = str(error).lower()

            if "reference" in message:
                composition.unresolved_references += 1
            elif "payload" in message:
                composition.unresolved_payloads += 1
            else:
                composition.unexpected_arcs += 1

    @staticmethod
    def _get_default_prim_path(stage):
        default_prim_name = stage.GetMetadata("defaultPrim")

        if not default_prim_name:
            return ""

        return f"/{default_prim_name}"