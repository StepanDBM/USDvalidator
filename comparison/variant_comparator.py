from .domain_comparator import MappingDomainComparator
from .models import ChangeImpact


class VariantComparator(MappingDomainComparator):
    domain = "Variants"
    collection = "variants"
    fields = (
        ("variants", "Available variant choices", ChangeImpact.MEDIUM, "Changing available choices can invalidate authored selections and downstream overrides.", ("USD_VARIANT_SELECTIONS_VALID",)),
        ("selection", "Authored variant selection", ChangeImpact.HIGH, "Changing a selection can switch substantial composed content.", ("USD_VARIANT_SELECTIONS_AUTHORED", "USD_VARIANT_SELECTIONS_VALID")),
    )

    def path_for(self, key, item):
        return f"{item.prim_path}{{{item.name}}}"
