from collections import defaultdict

from .domain_comparator import MappingDomainComparator
from .models import ChangeImpact, ChangeKind, SemanticChange


class SublayerComparator:
    domain = "Layer Stack"

    def compare(self, previous, current):
        old = _group_sublayers(previous.sublayers)
        new = _group_sublayers(current.sublayers)
        changes = []
        for layer in sorted(set(old) | set(new)):
            old_items = old.get(layer, ())
            new_items = new.get(layer, ())
            old_paths = tuple(item.asset_path for item in old_items)
            new_paths = tuple(item.asset_path for item in new_items)
            changes.append(_change(
                self.domain, layer, "sublayers", "Ordered sublayer membership",
                old_paths, new_paths, ChangeImpact.HIGH,
                "Sublayer membership and order determine composition strength.",
                ("USD_SUBLAYER_COUNT_LIMIT",),
            ))
            old_offsets = tuple((item.asset_path, item.offset, item.scale) for item in old_items)
            new_offsets = tuple((item.asset_path, item.offset, item.scale) for item in new_items)
            changes.append(_change(
                self.domain, layer, "sublayer_offsets", "Sublayer offsets",
                old_offsets, new_offsets, ChangeImpact.HIGH,
                "Layer offsets remap time and can alter all composed animation.",
            ))
        return changes


class CompositionArcComparator:
    domain = "Composition"

    def compare(self, previous, current):
        return self._compare_asset_arcs(previous.composition_arcs, current.composition_arcs) + self._compare_path_arcs(previous.path_arcs, current.path_arcs)

    def _compare_asset_arcs(self, previous, current):
        old = _group_arcs(previous)
        new = _group_arcs(current)
        changes = []
        for owner in sorted(set(old) | set(new)):
            old_items = old.get(owner, ())
            new_items = new.get(owner, ())
            paired = min(len(old_items), len(new_items))
            for index in range(paired):
                a, b = old_items[index], new_items[index]
                path = f"{owner[0]}.{owner[1]}[{index}]"
                for field, label, impact, why, checks in (
                    ("asset_path", "Dependency asset path", ChangeImpact.HIGH, "Changing an asset path changes composed content.", ("USD_NO_ABSOLUTE_DEPENDENCY_PATHS", "USD_NO_PARENT_DIRECTORY_ESCAPES")),
                    ("target_prim_path", "Reference or payload target", ChangeImpact.HIGH, "Changing the target prim selects different content inside the asset.", ()),
                    ("list_position", "Composition list position", ChangeImpact.MEDIUM, "List-edit position affects composition ordering.", ()),
                    ("absolute", "Absolute dependency path", ChangeImpact.HIGH, "Absolute paths reduce portability across machines and publishes.", ("USD_NO_ABSOLUTE_DEPENDENCY_PATHS",)),
                    ("resolved", "Dependency resolution", ChangeImpact.CRITICAL, "An unresolved dependency removes expected composed content.", ("USD_DEPENDENCIES_RESOLVE",)),
                ):
                    changes.append(_change(self.domain, path, field, label, getattr(a, field), getattr(b, field), impact, why, checks))
            for item in old_items[paired:]:
                changes.append(_object_change(self.domain, item.prim_path, f"{item.arc_type.title()} removed", ChangeKind.REMOVED, item, None, ChangeImpact.HIGH))
            for item in new_items[paired:]:
                changes.append(_object_change(self.domain, item.prim_path, f"{item.arc_type.title()} added", ChangeKind.ADDED, None, item, ChangeImpact.HIGH))
        return changes

    def _compare_path_arcs(self, previous, current):
        changes = []
        for key in sorted(set(previous) | set(current)):
            old = previous.get(key)
            new = current.get(key)
            item = old or new
            kind = ChangeKind.ADDED if old is None else ChangeKind.REMOVED if new is None else ChangeKind.UNCHANGED
            impact = ChangeImpact.HIGH if kind is not ChangeKind.UNCHANGED else ChangeImpact.INFORMATIONAL
            changes.append(SemanticChange(
                self.domain, item.prim_path, f"{item.arc_type.title()} target {kind.value.lower()}",
                kind, old.target_path if old else None, new.target_path if new else None,
                domain=self.domain, property_path=item.arc_type, impact=impact,
                why_it_matters="Inherits and specializes alter composed opinions and schema reuse.",
                source_hint=f"{item.prim_path} :: {item.arc_type}",
            ))
        return changes


class RelationshipComparator(MappingDomainComparator):
    domain = "Relationships"
    collection = "relationships"
    fields = (
        ("targets", "Relationship targets", ChangeImpact.HIGH, "Relationship targets connect authored scene objects and semantics.", ()),
        ("forwarded_targets", "Forwarded relationship targets", ChangeImpact.HIGH, "Forwarded target changes alter the effective relationship destination.", ()),
    )

    def path_for(self, key, item):
        return item.property_path


class CollectionComparator(MappingDomainComparator):
    domain = "Collections"
    collection = "collections"
    fields = (
        ("includes", "Collection includes", ChangeImpact.HIGH, "Include changes alter collection membership.", ()),
        ("excludes", "Collection excludes", ChangeImpact.HIGH, "Exclude changes alter effective collection membership.", ()),
        ("expansion_rule", "Collection expansion rule", ChangeImpact.HIGH, "Expansion rules control descendant membership.", ()),
        ("include_root", "Collection includes root", ChangeImpact.MEDIUM, "Root inclusion can broaden collection membership substantially.", ()),
    )

    def path_for(self, key, item):
        return f"{item.prim_path}.collection:{item.name}"


class GeomSubsetComparator(MappingDomainComparator):
    domain = "Geometry Subsets"
    collection = "geom_subsets"
    fields = (
        ("family_name", "Subset family", ChangeImpact.MEDIUM, "Subset families define grouping and partition semantics.", ()),
        ("family_type", "Subset family type", ChangeImpact.HIGH, "Family type determines whether subset membership must partition geometry.", ()),
        ("element_type", "Subset element type", ChangeImpact.HIGH, "Element type changes how indices select geometry components.", ()),
        ("element_count", "Subset element count", ChangeImpact.MEDIUM, "Element-count changes alter assigned geometry membership.", ()),
        ("indices_hash", "Subset membership fingerprint", ChangeImpact.HIGH, "Changed membership can reassign material or processing to different faces.", ()),
        ("material_path", "Subset material assignment", ChangeImpact.HIGH, "Per-subset binding changes visible material assignment.", ("USD_MATERIAL_BINDINGS_RESOLVE",)),
    )


class PrimvarComparator(MappingDomainComparator):
    domain = "Primvars"
    collection = "primvars"
    fields = (
        ("type_name", "Primvar type", ChangeImpact.HIGH, "Type changes can break consumers and authored values.", ()),
        ("role", "Primvar role", ChangeImpact.MEDIUM, "Role changes alter interpretation of the data.", ()),
        ("interpolation", "Primvar interpolation", ChangeImpact.HIGH, "Interpolation controls how values map onto geometry.", ("USD_MESH_UV_INTERPOLATION_VALID",)),
        ("element_size", "Primvar element size", ChangeImpact.MEDIUM, "Element size changes tuple grouping semantics.", ()),
        ("indexed", "Indexed primvar state", ChangeImpact.HIGH, "Indexed and direct primvars use different value addressing.", ()),
        ("value_count", "Primvar value count", ChangeImpact.MEDIUM, "Value counts must remain compatible with interpolation.", ()),
        ("index_count", "Primvar index count", ChangeImpact.MEDIUM, "Index counts must remain compatible with mesh topology.", ("USD_MESH_UV_INDICES_VALID",)),
        ("values_hash", "Primvar values fingerprint", ChangeImpact.HIGH, "Value changes alter the authored geometric attribute.", ()),
        ("indices_hash", "Primvar indices fingerprint", ChangeImpact.HIGH, "Index changes remap values onto geometry.", ("USD_MESH_UV_INDICES_VALID",)),
        ("uv_like", "Texture-coordinate primvar", ChangeImpact.MEDIUM, "UV-specialized interpretation affects texture mapping validation.", ("USD_MESH_UV_SET_REQUIRED",)),
    )

    def path_for(self, key, item):
        return item.property_path


def _group_sublayers(items):
    grouped = defaultdict(list)
    for item in items:
        grouped[item.layer_identifier].append(item)
    return {key: tuple(sorted(value, key=lambda item: item.index)) for key, value in grouped.items()}


def _group_arcs(items):
    grouped = defaultdict(list)
    for item in items.values():
        grouped[(item.prim_path, item.arc_type)].append(item)
    return {key: tuple(sorted(value, key=lambda item: (item.list_position, item.asset_path, item.target_prim_path))) for key, value in grouped.items()}


def _change(domain, path, property_path, label, previous, current, impact, why, checks=()):
    kind = ChangeKind.UNCHANGED if previous == current else ChangeKind.CHANGED
    return SemanticChange(
        domain, path, label, kind, previous, current,
        domain=domain, property_path=property_path,
        impact=ChangeImpact.INFORMATIONAL if kind is ChangeKind.UNCHANGED else impact,
        why_it_matters=why, related_check_ids=checks,
        source_hint=f"{path} :: {property_path}",
    )


def _object_change(domain, path, label, kind, previous, current, impact):
    return SemanticChange(
        domain, path, label, kind, previous, current,
        domain=domain, property_path="item", impact=impact,
        why_it_matters="Composition object membership changed.",
        source_hint=path,
    )
