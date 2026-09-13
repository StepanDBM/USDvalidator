import hashlib
import json
from pathlib import Path

from pxr import Sdf, Usd, UsdGeom

from .models import (
    AnimationSnapshot,
    DependencySnapshot,
    MeshSnapshot,
    PrimSnapshot,
    StageSnapshot,
)


def _hash(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class StageSnapshotBuilder:
    def build(self, source_path):
        source_path = Path(source_path).expanduser().resolve()
        stage = Usd.Stage.Open(str(source_path), load=Usd.Stage.LoadAll)

        if stage is None:
            raise ValueError(f"Could not open USD stage: {source_path}")

        prims = {}
        meshes = {}
        dependencies = []
        animation = {}

        for prim in stage.TraverseAll():
            path = prim.GetPath().pathString
            prims[path] = PrimSnapshot(
                path=path,
                type_name=prim.GetTypeName(),
                active=prim.IsActive(),
                defined=prim.IsDefined(),
                abstract=prim.IsAbstract(),
                instance=prim.IsInstance(),
                properties=tuple(sorted(prop.GetName() for prop in prim.GetProperties())),
            )
            dependencies.extend(self._dependencies(prim))
            animation.update(self._animation(prim))

            if prim.GetTypeName() == "Mesh":
                meshes[path] = self._mesh(prim)

        return StageSnapshot(
            source_path=source_path.as_posix(),
            metadata=self._metadata(stage),
            prims=prims,
            meshes=meshes,
            dependencies=tuple(sorted(
                dependencies,
                key=lambda item: (item.arc_type, item.prim_path, item.asset_path),
            )),
            animation=animation,
        )

    @staticmethod
    def _metadata(stage):
        default_name = stage.GetMetadata("defaultPrim") or ""
        return {
            "default_prim": f"/{default_name}" if default_name else "",
            "up_axis": UsdGeom.GetStageUpAxis(stage),
            "meters_per_unit": UsdGeom.GetStageMetersPerUnit(stage),
            "frames_per_second": stage.GetFramesPerSecond(),
            "time_codes_per_second": stage.GetTimeCodesPerSecond(),
            "start_time_code": stage.GetStartTimeCode(),
            "end_time_code": stage.GetEndTimeCode(),
            "root_layer": stage.GetRootLayer().identifier,
            "used_layers": tuple(sorted(layer.identifier for layer in stage.GetUsedLayers())),
        }

    @staticmethod
    def _mesh(prim):
        mesh = UsdGeom.Mesh(prim)
        points = mesh.GetPointsAttr().Get() or []
        counts = mesh.GetFaceVertexCountsAttr().Get() or []
        indices = mesh.GetFaceVertexIndicesAttr().Get() or []
        extent = mesh.GetExtentAttr().Get() or []
        return MeshSnapshot(
            path=prim.GetPath().pathString,
            points_count=len(points),
            face_count=len(counts),
            topology_hash=_hash({"counts": list(counts), "indices": list(indices)}),
            points_hash=_hash([tuple(point) for point in points]),
            extent=tuple(tuple(value) for value in extent),
            subdivision_scheme=mesh.GetSubdivisionSchemeAttr().Get() or "none",
            orientation=mesh.GetOrientationAttr().Get() or "rightHanded",
        )

    @staticmethod
    def _dependencies(prim):
        dependencies = []
        entries = (
            ("reference", "references", prim.HasAuthoredReferences()),
            ("payload", "payload", prim.HasAuthoredPayloads()),
        )

        for arc_type, metadata_name, authored in entries:
            if not authored:
                continue

            for item in prim.GetMetadata(metadata_name).GetAddedOrExplicitItems():
                asset_path = item.assetPath
                resolved = bool(Sdf.ComputeAssetPathRelativeToLayer(
                    prim.GetStage().GetRootLayer(), asset_path
                )) if asset_path else True
                dependencies.append(DependencySnapshot(
                    prim_path=prim.GetPath().pathString,
                    arc_type=arc_type,
                    asset_path=asset_path,
                    prim_path_in_asset=str(item.primPath),
                    resolved=resolved,
                ))

        return dependencies

    @staticmethod
    def _animation(prim):
        animation = {}

        for attribute in prim.GetAttributes():
            times = attribute.GetTimeSamples()

            if not times:
                continue

            values = [attribute.Get(time) for time in times]
            path = attribute.GetPath().pathString
            animation[path] = AnimationSnapshot(
                attribute_path=path,
                sample_count=len(times),
                first_sample=times[0],
                last_sample=times[-1],
                sample_times_hash=_hash(times),
                values_hash=_hash(values),
            )

        return animation
