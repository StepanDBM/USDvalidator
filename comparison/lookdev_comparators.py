from .domain_comparator import MappingDomainComparator
from .models import ChangeImpact


class MaterialComparator(MappingDomainComparator):
    domain = "Materials"
    collection = "materials"
    fields = (
        ("surface_connected", "Surface output connected", ChangeImpact.HIGH, "A disconnected surface output can make the material unusable.", ("USD_MATERIAL_SURFACE_OUTPUT_CONNECTED",)),
        ("displacement_connected", "Displacement output connected", ChangeImpact.MEDIUM, "Displacement connectivity changes rendered surface shape.", ()),
        ("volume_connected", "Volume output connected", ChangeImpact.MEDIUM, "Volume connectivity changes volumetric rendering.", ()),
        ("output_count", "Material output count", ChangeImpact.LOW, "Output changes alter the material interface.", ()),
    )


class ShaderComparator(MappingDomainComparator):
    domain = "Shaders"
    collection = "shaders"
    fields = (
        ("shader_id", "Shader identifier", ChangeImpact.HIGH, "The shader identifier selects the implementation used by renderers.", ("USD_SHADER_ID_AUTHORED", "USD_SHADER_IDS_ALLOWED")),
        ("implementation_source", "Implementation source", ChangeImpact.HIGH, "Changing implementation source changes how the shader is resolved.", ()),
        ("input_count", "Shader input count", ChangeImpact.MEDIUM, "Input-interface changes can break authored lookdev values.", ()),
        ("output_count", "Shader output count", ChangeImpact.MEDIUM, "Output-interface changes can break downstream connections.", ("USD_SHADER_OUTPUTS_AUTHORED",)),
        ("connected_input_count", "Connected input count", ChangeImpact.MEDIUM, "Connection changes alter the shading graph topology.", ()),
        ("asset_inputs", "Shader asset inputs", ChangeImpact.HIGH, "Asset input changes can alter textures and portability.", ("USD_SHADER_ASSET_PATHS_RELATIVE",)),
        ("input_values", "Shader input values", ChangeImpact.HIGH, "Shader input values directly affect rendered appearance.", ()),
        ("connections", "Shader connection topology", ChangeImpact.HIGH, "Connection changes alter the shading graph topology and data flow.", ()),
    )


class MaterialBindingComparator(MappingDomainComparator):
    domain = "Material Bindings"
    collection = "material_bindings"
    fields = (
        ("material_path", "Bound material", ChangeImpact.HIGH, "Binding changes alter the material resolved for geometry.", ("USD_GEOMETRY_HAS_MATERIAL_BINDING", "USD_MATERIAL_BINDINGS_RESOLVE")),
        ("direct", "Direct binding", ChangeImpact.LOW, "Direct versus inherited binding changes override behavior.", ()),
        ("resolved", "Binding resolution", ChangeImpact.CRITICAL, "An unresolved binding leaves geometry without a usable material.", ("USD_MATERIAL_BINDINGS_RESOLVE",)),
    )
