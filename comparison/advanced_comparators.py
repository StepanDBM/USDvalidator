from .domain_comparator import MappingDomainComparator
from .models import ChangeImpact, ChangeKind, SemanticChange


class LightComparator(MappingDomainComparator):
    domain = "Lights"
    collection = "lights"
    fields = (
        ("type_name", "Light type", ChangeImpact.HIGH, "Light type changes alter illumination behavior.", ()),
        ("intensity", "Light intensity", ChangeImpact.MEDIUM, "Intensity changes alter scene illumination.", ()),
        ("exposure", "Light exposure", ChangeImpact.MEDIUM, "Exposure changes multiply emitted light.", ()),
        ("color", "Light color", ChangeImpact.MEDIUM, "Color changes alter illumination and appearance.", ()),
        ("temperature", "Color temperature", ChangeImpact.MEDIUM, "Temperature changes alter emitted color.", ()),
        ("enable_color_temperature", "Color temperature enabled", ChangeImpact.MEDIUM, "Enabling temperature changes color evaluation.", ()),
        ("normalize", "Light normalization", ChangeImpact.HIGH, "Normalization changes how size affects emitted energy.", ()),
        ("shaping", "Light shaping", ChangeImpact.HIGH, "Shaping parameters alter the distribution of emitted light.", ()),
        ("texture_assets", "Light texture assets", ChangeImpact.HIGH, "Texture changes alter environment or projected illumination.", ()),
        ("time_varying", "Light animation state", ChangeImpact.MEDIUM, "Animation changes affect lighting through time.", ()),
        ("linked_paths", "Light-link membership", ChangeImpact.HIGH, "Light linking controls which objects receive illumination.", ()),
        ("shadow_linked_paths", "Shadow-link membership", ChangeImpact.HIGH, "Shadow linking controls which objects cast shadows.", ()),
    )


class RenderSettingsComparator(MappingDomainComparator):
    domain = "Render Settings"
    collection = "render_settings"
    fields = (
        ("active", "Active render settings", ChangeImpact.HIGH, "Changing active settings changes the render configuration used by consumers.", ()),
        ("camera_path", "Render camera", ChangeImpact.HIGH, "Camera changes alter framing and projection.", ()),
        ("products", "Render products", ChangeImpact.HIGH, "Product membership controls generated outputs.", ()),
        ("included_purposes", "Included purposes", ChangeImpact.HIGH, "Purpose filtering changes rendered scene content.", ()),
        ("material_binding_purposes", "Material binding purposes", ChangeImpact.HIGH, "Binding-purpose changes alter resolved render materials.", ()),
        ("renderer_settings", "Renderer settings", ChangeImpact.HIGH, "Renderer-specific settings change output behavior.", ()),
    )


class RenderProductComparator(MappingDomainComparator):
    domain = "Render Products"
    collection = "render_products"
    fields = (
        ("product_type", "Product type", ChangeImpact.HIGH, "Product type controls the output implementation.", ()),
        ("product_name", "Product output name", ChangeImpact.HIGH, "Output-name changes alter publish destinations.", ()),
        ("camera_path", "Product camera", ChangeImpact.HIGH, "Product camera changes rendered framing.", ()),
        ("ordered_vars", "Ordered render variables", ChangeImpact.HIGH, "Render-variable membership changes generated channels.", ()),
        ("resolution", "Resolution", ChangeImpact.MEDIUM, "Resolution changes output dimensions.", ()),
        ("pixel_aspect_ratio", "Pixel aspect ratio", ChangeImpact.MEDIUM, "Pixel aspect changes image interpretation.", ()),
        ("data_window_ndc", "Data window", ChangeImpact.MEDIUM, "Data-window changes crop or expand rendered pixels.", ()),
        ("renderer_settings", "Product renderer settings", ChangeImpact.HIGH, "Renderer settings alter product generation.", ()),
    )


class RenderVarComparator(MappingDomainComparator):
    domain = "Render Vars"
    collection = "render_vars"
    fields = (
        ("source_name", "AOV source name", ChangeImpact.HIGH, "Source-name changes select a different rendered quantity.", ()),
        ("source_type", "AOV source type", ChangeImpact.HIGH, "Source-type changes alter AOV interpretation.", ()),
        ("data_type", "AOV data type", ChangeImpact.HIGH, "Data-type changes can break render outputs and downstream readers.", ()),
        ("namespaced_settings", "AOV renderer settings", ChangeImpact.MEDIUM, "Renderer-specific settings alter AOV behavior.", ()),
    )


class SkeletonComparator(MappingDomainComparator):
    domain = "Skeletons"
    collection = "skeletons"
    fields = (
        ("joints", "Joint topology", ChangeImpact.CRITICAL, "Joint order and paths define the skeleton topology used by animation and skinning.", ()),
        ("parent_indices", "Joint parent topology", ChangeImpact.CRITICAL, "Parent changes alter the skeletal hierarchy.", ()),
        ("bind_transforms_hash", "Bind transforms", ChangeImpact.CRITICAL, "Bind-transform changes can deform all skinned geometry.", ()),
        ("rest_transforms_hash", "Rest transforms", ChangeImpact.HIGH, "Rest-transform changes alter the default pose.", ()),
        ("animation_source", "Skeleton animation source", ChangeImpact.HIGH, "Animation-source changes replace skeletal motion.", ()),
    )


class SkinningComparator(MappingDomainComparator):
    domain = "Skinning"
    collection = "skinning"
    fields = (
        ("skeleton_path", "Bound skeleton", ChangeImpact.CRITICAL, "Changing the skeleton binding can invalidate deformation.", ()),
        ("geom_bind_transform_hash", "Geometry bind transform", ChangeImpact.CRITICAL, "Geometry bind changes alter skin-space conversion.", ()),
        ("joint_indices_hash", "Joint indices", ChangeImpact.HIGH, "Joint-index changes remap vertex influences.", ()),
        ("joint_weights_hash", "Joint weights", ChangeImpact.HIGH, "Weight changes alter deformation.", ()),
        ("joint_count", "Joint index count", ChangeImpact.MEDIUM, "Index-count changes alter the skinning payload.", ()),
        ("influences_per_point", "Influences per point", ChangeImpact.HIGH, "Influence width changes skinning data layout.", ()),
    )


class BlendShapeComparator(MappingDomainComparator):
    domain = "Blend Shapes"
    collection = "blend_shapes"
    fields = (
        ("offsets_hash", "Blend-shape offsets", ChangeImpact.HIGH, "Offset changes alter the deformation target.", ()),
        ("normal_offsets_hash", "Blend-shape normal offsets", ChangeImpact.HIGH, "Normal-offset changes alter deformed shading.", ()),
        ("point_indices_hash", "Blend-shape point indices", ChangeImpact.HIGH, "Point-index changes remap blend-shape offsets.", ()),
        ("inbetween_names", "Blend-shape inbetweens", ChangeImpact.MEDIUM, "Inbetween changes alter interpolation behavior.", ()),
        ("bound_prims", "Blend-shape bindings", ChangeImpact.HIGH, "Binding changes alter which geometry receives the shape.", ()),
    )


class ValueClipComparator(MappingDomainComparator):
    domain = "Value Clips"
    collection = "value_clips"
    fields = (
        ("asset_paths", "Clip asset paths", ChangeImpact.HIGH, "Clip asset changes replace streamed animation data.", ()),
        ("clip_prim_path", "Clip prim path", ChangeImpact.HIGH, "Clip prim-path changes select different source content.", ()),
        ("manifest_asset_path", "Clip manifest", ChangeImpact.HIGH, "Manifest changes alter clip property discovery.", ()),
        ("active_hash", "Clip active intervals", ChangeImpact.HIGH, "Active intervals control which clip contributes through time.", ()),
        ("times_hash", "Clip time mapping", ChangeImpact.HIGH, "Time mapping changes animation retiming.", ()),
        ("template_asset_path", "Template clip asset", ChangeImpact.HIGH, "Template changes alter generated clip filenames.", ()),
        ("template_start_time", "Template start time", ChangeImpact.MEDIUM, "Template range changes available clip time.", ()),
        ("template_end_time", "Template end time", ChangeImpact.MEDIUM, "Template range changes available clip time.", ()),
        ("template_stride", "Template stride", ChangeImpact.HIGH, "Stride changes clip sampling and file selection.", ()),
    )

    def path_for(self, key, item):
        return f"{item.prim_path}.clips:{item.clip_set}"


class TimeConfigurationComparator:
    domain = "Time Configuration"

    def compare(self, previous, current):
        old = previous.time_configuration
        new = current.time_configuration
        if old is None or new is None:
            return []
        changes = []
        for field, label, impact, why in (
            ("start_time_code", "Start time code", ChangeImpact.MEDIUM, "Start-time changes alter the playback range."),
            ("end_time_code", "End time code", ChangeImpact.MEDIUM, "End-time changes alter the playback range."),
            ("frames_per_second", "Frames per second", ChangeImpact.HIGH, "Frame-rate changes alter playback interpretation."),
            ("time_codes_per_second", "Time codes per second", ChangeImpact.HIGH, "Time-code rate changes retime authored samples."),
        ):
            previous_value = getattr(old, field)
            current_value = getattr(new, field)
            kind = ChangeKind.UNCHANGED if previous_value == current_value else ChangeKind.CHANGED
            changes.append(SemanticChange(
                self.domain, "stage", label, kind, previous_value, current_value,
                domain=self.domain, property_path=field,
                impact=ChangeImpact.INFORMATIONAL if kind is ChangeKind.UNCHANGED else impact,
                why_it_matters=why, source_hint=f"stage :: {field}",
            ))
        return changes
