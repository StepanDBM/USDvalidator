from .domain_comparator import MappingDomainComparator
from .models import ChangeImpact


class SurfaceComparator(MappingDomainComparator):
    domain = "Geometry Presentation"
    collection = "surfaces"
    fields = (
        ("normals_authored", "Normals authored", ChangeImpact.HIGH, "Removing normals can change shading and renderer interpolation.", ("USD_NORMALS_AUTHORED",)),
        ("normals_count", "Normal count", ChangeImpact.MEDIUM, "Normal count must remain compatible with interpolation and topology.", ("USD_NORMALS_COUNT_VALID",)),
        ("normals_interpolation", "Normal interpolation", ChangeImpact.HIGH, "Interpolation changes alter how normals are applied across the mesh.", ("USD_NORMALS_COUNT_VALID",)),
        ("normals_finite", "Normals finite", ChangeImpact.CRITICAL, "Non-finite normals can produce invalid shading.", ("USD_NORMALS_FINITE",)),
        ("uv_sets", "UV sets", ChangeImpact.HIGH, "UV-set changes can disconnect textures from geometry.", ("USD_UV_SET_REQUIRED",)),
        ("uv_counts", "UV value counts", ChangeImpact.MEDIUM, "UV counts must agree with mesh interpolation and indexing.", ("USD_UV_INDICES_VALID",)),
        ("uv_interpolations", "UV interpolation", ChangeImpact.HIGH, "UV interpolation changes texture mapping semantics.", ("USD_UV_INTERPOLATION_ALLOWED",)),
        ("uv_indices_valid", "UV index validity", ChangeImpact.CRITICAL, "Invalid UV indices can make texture mapping unusable.", ("USD_UV_INDICES_VALID",)),
    )


class LayerComparator(MappingDomainComparator):
    domain = "Layers"
    collection = "layers"
    fields = (
        ("anonymous", "Anonymous layer", ChangeImpact.HIGH, "Anonymous layers cannot be published as portable dependencies.", ("USD_USED_LAYERS_VALID",)),
        ("dirty", "Dirty layer", ChangeImpact.HIGH, "Dirty layers contain unsaved authored changes.", ("USD_USED_LAYERS_VALID",)),
        ("sublayer_count", "Sublayer count", ChangeImpact.MEDIUM, "Layer-stack membership changes composition strength and content.", ("USD_SUBLAYERS_VALID",)),
        ("documentation", "Layer documentation", ChangeImpact.INFORMATIONAL, "Documentation changes do not normally affect composition.", ()),
        ("default_prim", "Layer default prim", ChangeImpact.HIGH, "Default-prim changes alter implicit references into the layer.", ("USD_DEFAULT_PRIM_EXISTS",)),
    )


class CameraComparator(MappingDomainComparator):
    domain = "Cameras"
    collection = "cameras"
    fields = (
        ("projection", "Camera projection", ChangeImpact.HIGH, "Projection changes alter the rendered framing model.", ("USD_CAMERA_PROJECTION_ALLOWED",)),
        ("focal_length", "Camera focal length", ChangeImpact.MEDIUM, "Focal-length changes alter field of view and composition.", ("USD_CAMERA_FOCAL_LENGTH_VALID",)),
        ("clipping_range", "Camera clipping range", ChangeImpact.MEDIUM, "Clipping changes can hide or reveal scene geometry.", ("USD_CAMERA_CLIPPING_RANGE_VALID",)),
        ("time_varying", "Camera animation state", ChangeImpact.MEDIUM, "Animation-state changes affect playback and shot evaluation.", ()),
    )


class InstancingComparator(MappingDomainComparator):
    domain = "Instancing"
    collection = "instancing"
    fields = (
        ("instance", "Native instance state", ChangeImpact.HIGH, "Instance-state changes alter composition and memory sharing.", ("USD_INSTANCING_VALID",)),
        ("instanceable", "Instanceable metadata", ChangeImpact.MEDIUM, "Instanceable changes affect prototype generation.", ("USD_INSTANCING_VALID",)),
        ("prototype_path", "Prototype path", ChangeImpact.HIGH, "Prototype changes replace the content represented by instances.", ("USD_INSTANCING_VALID",)),
        ("point_instancer", "PointInstancer state", ChangeImpact.HIGH, "Point-instancer changes alter procedural instance semantics.", ("USD_POINT_INSTANCER_VALID",)),
        ("prototype_count", "Prototype count", ChangeImpact.MEDIUM, "Prototype-count changes affect available instance targets.", ("USD_POINT_INSTANCER_VALID",)),
        ("point_instance_count", "Point instance count", ChangeImpact.MEDIUM, "Instance-count changes alter scene population.", ()),
        ("invalid_proto_indices", "Invalid prototype indices", ChangeImpact.CRITICAL, "Invalid prototype indices make PointInstancer entries unusable.", ("USD_POINT_INSTANCER_PROTO_INDICES_VALID",)),
    )


class DependencyComparator(MappingDomainComparator):
    domain = "Dependencies"
    collection = "dependency_map"
    fields = (
        ("resolved", "Dependency resolution", ChangeImpact.CRITICAL, "An unresolved dependency removes composed content from the publish.", ("USD_DEPENDENCIES_RESOLVE",)),
    )
