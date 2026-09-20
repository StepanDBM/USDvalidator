import hashlib
import json
from pathlib import Path

from pxr import Sdf, Usd, UsdGeom, UsdShade

from s_usd_core.extraction.lookdev import LookdevExtractor
from s_usd_core.extraction.pipeline import PipelineExtractor

from .advanced_snapshot import extract_advanced_domains
from .composition_snapshot import extract_extended_domains
from .models import (
    AnimationSnapshot,
    DependencySnapshot,
    CameraSnapshot,
    InstancingSnapshot,
    LayerSnapshot,
    MaterialBindingSnapshot,
    MaterialSnapshot,
    MeshSnapshot,
    PrimSnapshot,
    ShaderSnapshot,
    StageComparisonSnapshot,
    SurfaceSnapshot,
    TransformSnapshot,
    VariantSnapshot,
)


def _hash(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class StageComparisonSnapshotBuilder:
    def build(self, source_path):
        source_path = Path(source_path).expanduser().resolve()
        stage = Usd.Stage.Open(str(source_path), load=Usd.Stage.LoadAll)

        if stage is None:
            raise ValueError(f"Could not open USD stage: {source_path}")

        prims = {}
        meshes = {}
        dependencies = []
        animation = {}
        transforms = {}

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
            transform = self._transform(prim)
            if transform is not None:
                transforms[path] = transform

            if prim.GetTypeName() == "Mesh":
                meshes[path] = self._mesh(prim)

        pipeline = PipelineExtractor().extract(stage)
        lookdev = LookdevExtractor().extract(stage)
        variants = {
            (item.prim_path, item.name): VariantSnapshot(
                item.prim_path, item.name, item.variants, item.selection
            )
            for item in pipeline.variants
        }
        materials = {item.path: MaterialSnapshot(**item.__dict__) for item in lookdev.materials}
        shaders = {
            item.path: self._shader_snapshot(stage.GetPrimAtPath(item.path), item)
            for item in lookdev.shaders
        }
        bindings = {
            item.prim_path: MaterialBindingSnapshot(**item.__dict__)
            for item in lookdev.bindings
        }
        surfaces = {
            item.mesh_path: SurfaceSnapshot(
                item.mesh_path,
                item.normals_authored,
                item.normals_count,
                item.normals_interpolation,
                item.normals_finite,
                item.uv_sets,
                item.uv_counts,
                item.uv_interpolations,
                item.uv_indices_valid,
            )
            for item in lookdev.surfaces
        }
        layers = {item.identifier: LayerSnapshot(**item.__dict__) for item in lookdev.layers}
        cameras = {item.path: CameraSnapshot(**item.__dict__) for item in pipeline.cameras}
        instancing = {item.path: InstancingSnapshot(**item.__dict__) for item in pipeline.instances}

        extended = extract_extended_domains(stage)
        advanced = extract_advanced_domains(stage)

        return StageComparisonSnapshot(
            source_path=source_path.as_posix(),
            metadata=self._metadata(stage),
            prims=prims,
            meshes=meshes,
            dependencies=tuple(sorted(
                dependencies,
                key=lambda item: (item.arc_type, item.prim_path, item.asset_path),
            )),
            animation=animation,
            transforms=transforms,
            variants=variants,
            materials=materials,
            shaders=shaders,
            material_bindings=bindings,
            surfaces=surfaces,
            layers=layers,
            cameras=cameras,
            instancing=instancing,
            dependency_map={
                (item.prim_path, item.arc_type, item.asset_path, item.prim_path_in_asset): item
                for item in dependencies
            },
            **extended,
            **advanced,
        )


    @staticmethod
    def _shader_snapshot(prim, item):
        shader = UsdShade.Shader(prim)
        values = []
        connections = []
        for shader_input in shader.GetInputs():
            name = shader_input.GetBaseName()
            value = shader_input.Get()
            values.append((name, json.dumps(value, default=str, sort_keys=True)))
            sources = shader_input.GetConnectedSources()[0]
            for source in sources:
                source_path = source.source.GetPrim().GetPath().pathString
                connections.append((name, f"{source_path}.{source.sourceName}"))
        return ShaderSnapshot(
            item.path,
            item.shader_id,
            item.implementation_source,
            item.input_count,
            item.output_count,
            item.connected_input_count,
            item.asset_inputs,
            tuple(sorted(values)),
            tuple(sorted(connections)),
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
    def _transform(prim):
        xformable = UsdGeom.Xformable(prim)
        if not xformable:
            return None
        ops = xformable.GetOrderedXformOps()
        if not ops:
            return None
        matrix, resets_stack = xformable.GetLocalTransformation(), xformable.GetResetXformStack()
        scale_values = []
        values_finite = True
        time_varying = False
        for op in ops:
            value = op.Get()
            time_varying = time_varying or op.MightBeTimeVarying()
            values_finite = values_finite and _finite(value)
            if "scale" in op.GetOpName().lower() and value is not None:
                try:
                    scale_values.append(tuple(float(component) for component in value))
                except TypeError:
                    pass
        identity = matrix == matrix.__class__(1.0)
        return TransformSnapshot(
            path=prim.GetPath().pathString,
            op_names=tuple(op.GetOpName() for op in ops),
            resets_stack=bool(resets_stack),
            time_varying=time_varying,
            matrix_op_count=sum(op.GetOpType() == UsdGeom.XformOp.TypeTransform for op in ops),
            scale_values=tuple(scale_values),
            values_finite=values_finite,
            local_transform_identity=identity,
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


def _finite(value):
    if value is None:
        return True
    try:
        import math
        if isinstance(value, (int, float)):
            return math.isfinite(float(value))
        return all(_finite(item) for item in value)
    except TypeError:
        return True


StageSnapshotBuilder = StageComparisonSnapshotBuilder
