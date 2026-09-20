from s_usd_core.comparison.models import ChangeImpact, ChangeKind, TransformSnapshot
from s_usd_core.comparison.transform_comparator import TransformComparator


def _transform(path="/World", **changes):
    values = {
        "path": path,
        "op_names": ("xformOp:translate",),
        "resets_stack": False,
        "time_varying": False,
        "matrix_op_count": 0,
        "scale_values": (),
        "values_finite": True,
        "local_transform_identity": True,
    }
    values.update(changes)
    return TransformSnapshot(**values)


def test_transform_comparator_detects_added_and_removed_prims():
    comparator = TransformComparator()
    added = comparator.compare({}, {"/Added": _transform("/Added")})
    removed = comparator.compare({"/Removed": _transform("/Removed")}, {})
    assert added[0].kind is ChangeKind.ADDED
    assert removed[0].kind is ChangeKind.REMOVED
    assert removed[0].impact is ChangeImpact.HIGH


def test_transform_comparator_detects_operation_order_change():
    previous = _transform(op_names=("xformOp:translate", "xformOp:rotateXYZ"))
    current = _transform(op_names=("xformOp:rotateXYZ", "xformOp:translate"))
    changes = TransformComparator().compare({"/World": previous}, {"/World": current})
    change = next(change for change in changes if change.property_path == "op_names")
    assert change.kind is ChangeKind.CHANGED
    assert change.impact is ChangeImpact.HIGH
    assert change.related_check_ids
    assert change.source_hint == "/World :: op_names"


def test_non_finite_transform_is_critical():
    previous = _transform(values_finite=True)
    current = _transform(values_finite=False)
    changes = TransformComparator().compare({"/World": previous}, {"/World": current})
    change = next(change for change in changes if change.property_path == "values_finite")
    assert change.impact is ChangeImpact.CRITICAL


def test_unchanged_transform_contract_is_preserved():
    transform = _transform()
    changes = TransformComparator().compare({"/World": transform}, {"/World": transform})
    assert changes
    assert all(change.kind is ChangeKind.UNCHANGED for change in changes)
    assert all(change.impact is ChangeImpact.INFORMATIONAL for change in changes)
