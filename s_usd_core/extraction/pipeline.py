import math
import os
from pathlib import PurePosixPath

from pxr import Gf, UsdGeom

from s_usd_core.contexts.pipeline_context import (
    CameraInfo,
    DependencyInfo,
    InstancingInfo,
    PipelineStatistics,
    PrimInfo,
    TransformInfo,
    VariantSetInfo,
)


class PipelineExtractor:
    TEMPORARY_TOKENS = ("temp", "tmp", "backup", "copy", "preview")

    def extract(self, stage):
        result = PipelineStatistics()

        for prim in stage.TraverseAll():
            path = prim.GetPath().pathString
            result.prims.append(PrimInfo(
                path=path,
                name=prim.GetName(),
                parent_path=prim.GetPath().GetParentPath().pathString,
                type_name=prim.GetTypeName(),
                depth=path.count("/"),
            ))
            result.transforms.append(self._transform(prim))
            result.variants.extend(self._variants(prim))
            result.dependencies.extend(self._dependencies(prim))

            if prim.IsA(UsdGeom.Camera):
                result.cameras.append(self._camera(prim))

            if prim.IsInstance() or prim.IsInstanceable() or prim.IsA(UsdGeom.PointInstancer):
                result.instances.append(self._instancing(prim))

        return result

    @staticmethod
    def _transform(prim):
        xformable = UsdGeom.Xformable(prim)

        if not xformable:
            return TransformInfo(
                path=prim.GetPath().pathString,
                op_names=(),
                resets_stack=False,
                time_varying=False,
                matrix_op_count=0,
                scale_values=(),
                values_finite=True,
                local_transform_identity=True,
            )

        ops = xformable.GetOrderedXformOps()
        values = []
        scales = []
        time_varying = False

        for op in ops:
            value = op.Get()
            values.extend(PipelineExtractor._numbers(value))
            time_varying = time_varying or op.GetAttr().ValueMightBeTimeVarying()

            if op.GetOpType() == UsdGeom.XformOp.TypeScale and value is not None:
                scales.append(tuple(float(component) for component in value))

        matrix = xformable.GetLocalTransformation()
        resets_stack = xformable.GetResetXformStack()
        identity = Gf.IsClose(matrix, Gf.Matrix4d(1.0), 1e-9)

        return TransformInfo(
            path=prim.GetPath().pathString,
            op_names=tuple(op.GetOpName() for op in ops),
            resets_stack=resets_stack,
            time_varying=time_varying,
            matrix_op_count=sum(
                op.GetOpType() == UsdGeom.XformOp.TypeTransform for op in ops
            ),
            scale_values=tuple(scales),
            values_finite=all(math.isfinite(value) for value in values),
            local_transform_identity=identity,
        )


    @staticmethod
    def _numbers(value):
        if value is None:
            return []

        try:
            return [float(item) for item in value]
        except TypeError:
            try:
                return [float(value)]
            except (TypeError, ValueError):
                return []

    @staticmethod
    def _variants(prim):
        sets = prim.GetVariantSets()
        return [
            VariantSetInfo(
                prim_path=prim.GetPath().pathString,
                name=name,
                variants=tuple(sets.GetVariantSet(name).GetVariantNames()),
                selection=sets.GetVariantSet(name).GetVariantSelection(),
            )
            for name in sets.GetNames()
        ]

    @staticmethod
    def _camera(prim):
        camera = UsdGeom.Camera(prim)
        clipping = camera.GetClippingRangeAttr().Get() or (0.1, 1000000.0)
        attributes = (
            camera.GetProjectionAttr(),
            camera.GetFocalLengthAttr(),
            camera.GetClippingRangeAttr(),
        )
        return CameraInfo(
            path=prim.GetPath().pathString,
            projection=camera.GetProjectionAttr().Get() or "perspective",
            focal_length=float(camera.GetFocalLengthAttr().Get() or 0.0),
            clipping_range=(float(clipping[0]), float(clipping[1])),
            time_varying=any(attr.ValueMightBeTimeVarying() for attr in attributes),
        )

    @staticmethod
    def _instancing(prim):
        point_instancer = prim.IsA(UsdGeom.PointInstancer)
        prototype_count = 0
        point_instance_count = 0
        invalid_proto_indices = 0

        if point_instancer:
            instancer = UsdGeom.PointInstancer(prim)
            prototype_count = len(instancer.GetPrototypesRel().GetTargets())
            indices = instancer.GetProtoIndicesAttr().Get() or []
            point_instance_count = len(indices)
            invalid_proto_indices = sum(
                index < 0 or index >= prototype_count for index in indices
            )

        prototype = prim.GetPrototype()
        return InstancingInfo(
            path=prim.GetPath().pathString,
            instance=prim.IsInstance(),
            instanceable=prim.IsInstanceable(),
            prototype_path=prototype.GetPath().pathString if prototype else "",
            point_instancer=point_instancer,
            prototype_count=prototype_count,
            point_instance_count=point_instance_count,
            invalid_proto_indices=invalid_proto_indices,
        )

    @classmethod
    def _dependencies(cls, prim):
        result = []
        entries = (
            ("reference", "references", prim.HasAuthoredReferences()),
            ("payload", "payload", prim.HasAuthoredPayloads()),
        )

        for arc_type, metadata_name, authored in entries:
            if not authored:
                continue

            for item in prim.GetMetadata(metadata_name).GetAddedOrExplicitItems():
                path = item.assetPath
                lower = path.lower()
                result.append(DependencyInfo(
                    prim_path=prim.GetPath().pathString,
                    arc_type=arc_type,
                    asset_path=path,
                    absolute=os.path.isabs(path),
                    parent_escape=".." in PurePosixPath(path.replace("\\", "/")).parts,
                    temporary=any(token in lower for token in cls.TEMPORARY_TOKENS),
                ))

        return result
