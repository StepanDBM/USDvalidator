from .models import ChangeImpact, ChangeKind, SemanticChange


class MappingDomainComparator:
    domain = ""
    collection = ""
    fields = ()

    def compare(self, previous, current):
        old_items = getattr(previous, self.collection)
        new_items = getattr(current, self.collection)
        changes = []
        for key in sorted(set(old_items) | set(new_items), key=str):
            old = old_items.get(key)
            new = new_items.get(key)
            path = self.path_for(key, old or new)
            if old is None:
                changes.append(self.change(path, "item", f"{self.domain[:-1]} added", ChangeKind.ADDED, None, new, ChangeImpact.MEDIUM, "A new authored semantic object changes the publish contract."))
                continue
            if new is None:
                changes.append(self.change(path, "item", f"{self.domain[:-1]} removed", ChangeKind.REMOVED, old, None, ChangeImpact.HIGH, "Removing an authored semantic object can break downstream consumers."))
                continue
            for field, label, impact, why, check_ids in self.fields:
                previous_value = getattr(old, field)
                current_value = getattr(new, field)
                kind = ChangeKind.UNCHANGED if previous_value == current_value else ChangeKind.CHANGED
                changes.append(self.change(path, field, label, kind, previous_value, current_value, ChangeImpact.INFORMATIONAL if kind is ChangeKind.UNCHANGED else impact, why, check_ids))
        return changes

    def path_for(self, key, item):
        for attribute in ("path", "prim_path", "identifier"):
            value = getattr(item, attribute, "")
            if value:
                return value
        return str(key)

    def change(self, path, property_path, label, kind, previous, current, impact, why, check_ids=()):
        return SemanticChange(
            self.domain, path, label, kind, previous, current,
            domain=self.domain,
            property_path=property_path,
            impact=impact,
            why_it_matters=why,
            related_check_ids=check_ids,
            source_hint=f"{path} :: {property_path}",
        )
