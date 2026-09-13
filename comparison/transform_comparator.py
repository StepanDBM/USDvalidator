from .models import ChangeImpact, ChangeKind, SemanticChange


TRANSFORM_CHECK_IDS = {
    "op_names": ("usd.transform.xform_op_count_limit", "usd.transform.matrix_xform_ops_allowed"),
    "resets_stack": ("usd.transform.root_transform_identity",),
    "time_varying": (),
    "matrix_op_count": ("usd.transform.matrix_xform_ops_allowed",),
    "scale_values": ("usd.transform.scale_nonzero", "usd.transform.negative_scale_allowed"),
    "values_finite": ("usd.transform.values_finite",),
    "local_transform_identity": ("usd.transform.root_transform_identity",),
}


class TransformComparator:
    domain = "Transforms"

    def compare(self, previous, current):
        previous = getattr(previous, "transforms", previous)
        current = getattr(current, "transforms", current)
        changes = []
        for path in sorted(set(previous) | set(current)):
            old = previous.get(path)
            new = current.get(path)
            if old is None:
                changes.append(self._change(path, "transform", "Transform prim added", ChangeKind.ADDED, None, new, ChangeImpact.MEDIUM, "A new transform-bearing prim changes the composed hierarchy."))
                continue
            if new is None:
                changes.append(self._change(path, "transform", "Transform prim removed", ChangeKind.REMOVED, old, None, ChangeImpact.HIGH, "Removing a transform-bearing prim can invalidate hierarchy and authored motion."))
                continue

            self._property(changes, path, "op_names", "Transform operation order", old.op_names, new.op_names, ChangeImpact.HIGH, "Operation order affects the resulting local transform.")
            self._property(changes, path, "resets_stack", "Reset transform stack", old.resets_stack, new.resets_stack, ChangeImpact.HIGH, "Reset-stack changes alter inherited parent transforms.")
            self._property(changes, path, "time_varying", "Transform animation state", old.time_varying, new.time_varying, ChangeImpact.MEDIUM, "Static and animated transforms behave differently in downstream playback and caching.")
            self._property(changes, path, "matrix_op_count", "Matrix transform operation count", old.matrix_op_count, new.matrix_op_count, ChangeImpact.MEDIUM, "Matrix operations can violate transform authoring policy and reduce editability.")
            self._property(changes, path, "scale_values", "Transform scale values", old.scale_values, new.scale_values, ChangeImpact.HIGH, "Scale changes can alter size, handedness and geometric validity.")
            self._property(changes, path, "values_finite", "Transform values finite", old.values_finite, new.values_finite, ChangeImpact.CRITICAL if not new.values_finite else ChangeImpact.HIGH, "Non-finite transform values can make the stage unusable.")
            root_impact = ChangeImpact.CRITICAL if old.local_transform_identity and not new.local_transform_identity else ChangeImpact.HIGH
            self._property(changes, path, "local_transform_identity", "Local transform identity", old.local_transform_identity, new.local_transform_identity, root_impact, "Identity changes at important hierarchy roots can alter the entire asset placement.")
        return changes

    def _property(self, changes, path, property_path, label, previous, current, impact, why):
        kind = ChangeKind.UNCHANGED if previous == current else ChangeKind.CHANGED
        changes.append(self._change(path, property_path, label, kind, previous, current, impact if kind is not ChangeKind.UNCHANGED else ChangeImpact.INFORMATIONAL, why))

    def _change(self, path, property_path, label, kind, previous, current, impact, why):
        return SemanticChange(
            self.domain,
            path,
            label,
            kind,
            previous,
            current,
            domain=self.domain,
            property_path=property_path,
            impact=impact,
            why_it_matters=why,
            related_check_ids=TRANSFORM_CHECK_IDS.get(property_path, ()),
            source_hint=f'{path} :: {property_path}',
        )
