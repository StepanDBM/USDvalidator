import math
import os

from pxr import Sdf, UsdGeom, UsdShade

from s_usd_core.contexts.lookdev_context import (
    LayerInfo,
    LookdevStatistics,
    MaterialBindingInfo,
    MaterialInfo,
    ShaderInfo,
    SurfaceInfo,
)


class LookdevExtractor:
    def extract(self, stage):
        result = LookdevStatistics()

        for prim in stage.TraverseAll():
            if prim.IsA(UsdShade.Material):
                result.materials.append(self._material(prim))
            if prim.IsA(UsdShade.Shader):
                result.shaders.append(self._shader(prim))
            if prim.IsA(UsdGeom.Imageable):
                binding = self._binding(prim)
                if binding:
                    result.bindings.append(binding)
            if prim.IsA(UsdGeom.Mesh):
                result.surfaces.append(self._surface(prim))

        session_layer = stage.GetSessionLayer()

        result.layers = [
            self._layer(layer)
            for layer in stage.GetUsedLayers()
            if layer != session_layer
        ]
        result.layers.sort(key=lambda item: item.identifier)
        return result

    @staticmethod
    def _material(prim):
        material = UsdShade.Material(prim)
        outputs = material.GetOutputs()
        return MaterialInfo(
            path=prim.GetPath().pathString,
            surface_connected=material.GetSurfaceOutput().HasConnectedSource(),
            displacement_connected=material.GetDisplacementOutput().HasConnectedSource(),
            volume_connected=material.GetVolumeOutput().HasConnectedSource(),
            output_count=len(outputs),
        )

    @staticmethod
    def _shader(prim):
        shader = UsdShade.Shader(prim)
        asset_inputs = []

        for shader_input in shader.GetInputs():
            value = shader_input.Get()
            if isinstance(value, Sdf.AssetPath):
                asset_inputs.append(value.path)

        return ShaderInfo(
            path=prim.GetPath().pathString,
            shader_id=shader.GetIdAttr().Get() or "",
            implementation_source=shader.GetImplementationSource() or "",
            input_count=len(shader.GetInputs()),
            output_count=len(shader.GetOutputs()),
            connected_input_count=sum(
                shader_input.HasConnectedSource() for shader_input in shader.GetInputs()
            ),
            asset_inputs=tuple(asset_inputs),
        )

    @staticmethod
    def _binding(prim):
        api = UsdShade.MaterialBindingAPI(prim)
        direct_rel = api.GetDirectBindingRel()
        direct_targets = direct_rel.GetTargets() if direct_rel else []

        try:
            material, relationship = api.ComputeBoundMaterial()
        except Exception:
            material, relationship = None, None

        if not material and not direct_targets:
            return None

        material_path = (
            material.GetPath().pathString
            if material
            else direct_targets[0].pathString
        )
        return MaterialBindingInfo(
            prim_path=prim.GetPath().pathString,
            material_path=material_path,
            direct=bool(direct_targets),
            resolved=bool(material and material.GetPrim().IsValid()),
        )

    @staticmethod
    def _surface(prim):
        mesh = UsdGeom.Mesh(prim)
        points = mesh.GetPointsAttr().Get() or []
        counts = mesh.GetFaceVertexCountsAttr().Get() or []
        face_vertex_count = sum(counts)
        normals = mesh.GetNormalsAttr().Get() or []
        normals_interpolation = mesh.GetNormalsInterpolation() or ""
        uv_sets = []
        uv_counts = []
        uv_interpolations = []
        uv_indices_valid = []

        for primvar in UsdGeom.PrimvarsAPI(prim).GetPrimvars():
            name = primvar.GetPrimvarName()
            value = primvar.Get()
            type_name = str(primvar.GetTypeName())

            if name not in {"st", "uv", "map1"} and "TexCoord" not in type_name:
                continue

            values = value or []
            indices = primvar.GetIndices() or []
            uv_sets.append(name)
            uv_counts.append((name, len(values)))
            uv_interpolations.append((name, primvar.GetInterpolation() or ""))
            uv_indices_valid.append((
                name,
                not indices or all(0 <= index < len(values) for index in indices),
            ))

        return SurfaceInfo(
            mesh_path=prim.GetPath().pathString,
            point_count=len(points),
            face_vertex_count=face_vertex_count,
            normals_authored=mesh.GetNormalsAttr().HasAuthoredValueOpinion(),
            normals_count=len(normals),
            normals_interpolation=normals_interpolation,
            normals_finite=all(
                math.isfinite(float(component))
                for normal in normals
                for component in normal
            ),
            uv_sets=tuple(sorted(uv_sets)),
            uv_counts=tuple(sorted(uv_counts)),
            uv_interpolations=tuple(sorted(uv_interpolations)),
            uv_indices_valid=tuple(sorted(uv_indices_valid)),
        )

    @staticmethod
    def _layer(layer):
        return LayerInfo(
            identifier=layer.identifier,
            anonymous=layer.anonymous,
            dirty=layer.dirty,
            sublayer_count=len(layer.subLayerPaths),
            documentation=layer.documentation or "",
            default_prim=layer.defaultPrim or "",
        )
