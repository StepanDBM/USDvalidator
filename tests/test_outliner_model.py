import pytest

pytest.importorskip("PySide6")
pxr = pytest.importorskip("pxr")
from pxr import Usd

from ui.widgets.usd_viewport.outliner_model import PrimOutlinerModel


def test_model_preserves_usd_parent_child_hierarchy():
    stage = Usd.Stage.CreateInMemory()
    stage.DefinePrim("/Kitchen_set", "Xform")
    stage.DefinePrim("/Kitchen_set/Props_grp", "Xform")
    stage.DefinePrim("/Kitchen_set/Props_grp/Table_grp", "Xform")
    stage.DefinePrim("/Kitchen_set/Props_grp/Table_grp/Plate", "Mesh")
    model = PrimOutlinerModel()
    model.set_stage(stage)

    plate = model.index_for_path("/Kitchen_set/Props_grp/Table_grp/Plate")
    table = plate.parent()
    props = table.parent()
    kitchen = props.parent()

    assert plate.data() == "Plate"
    assert table.data() == "Table_grp"
    assert props.data() == "Props_grp"
    assert kitchen.data() == "Kitchen_set"


def test_hidden_parent_marks_descendant_effectively_hidden():
    stage = Usd.Stage.CreateInMemory()
    stage.DefinePrim("/World", "Xform")
    stage.DefinePrim("/World/Child", "Mesh")
    model = PrimOutlinerModel()
    model.set_stage(stage)
    model.set_hidden_paths({"/World"})

    assert model.is_hidden("/World")
    assert model.is_effectively_hidden("/World/Child")
    assert model.is_hidden_by_ancestor("/World/Child")
