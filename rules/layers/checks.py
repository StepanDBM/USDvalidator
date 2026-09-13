from rules.common import result
from validation.check_ids import (
    USD_LAYER_COUNT_LIMIT,
    USD_NO_ANONYMOUS_LAYERS,
    USD_NO_DIRTY_LAYERS,
    USD_ROOT_LAYER_DEFAULT_PRIM_AUTHORED,
    USD_SUBLAYER_COUNT_LIMIT,
)


def check_layer_count_limit(context, runtime_context):
    count = len(context.lookdev.layers)
    limit = runtime_context.config.layers.maximum_used_layers
    return result(USD_LAYER_COUNT_LIMIT, "Layer Count Limit", "Layers", runtime_context, count <= limit, f"Used layers {count}; allowed maximum {limit}.", details={"count": count, "limit": limit})


def check_no_anonymous_layers(context, runtime_context):
    allowed = runtime_context.config.layers.allow_anonymous_layers
    invalid = [item.identifier for item in context.lookdev.layers if item.anonymous and not allowed]
    return result(USD_NO_ANONYMOUS_LAYERS, "No Anonymous Layers", "Layers", runtime_context, not invalid, f"Anonymous layers: {len(invalid)}.", details={"layers": invalid, "allowed": allowed})


def check_no_dirty_layers(context, runtime_context):
    allowed = runtime_context.config.layers.allow_dirty_layers
    invalid = [item.identifier for item in context.lookdev.layers if item.dirty and not allowed]
    return result(USD_NO_DIRTY_LAYERS, "No Dirty Layers", "Layers", runtime_context, not invalid, f"Dirty layers: {len(invalid)}.", details={"layers": invalid, "allowed": allowed})


def check_sublayer_count_limit(context, runtime_context):
    limit = runtime_context.config.layers.maximum_sublayers_per_layer
    invalid = {item.identifier: item.sublayer_count for item in context.lookdev.layers if item.sublayer_count > limit}
    return result(USD_SUBLAYER_COUNT_LIMIT, "Sublayer Count Limit", "Layers", runtime_context, not invalid, f"Layers exceeding {limit} sublayers: {len(invalid)}.", details={"layers": invalid, "limit": limit})


def check_root_layer_default_prim_authored(context, runtime_context):
    required = runtime_context.config.layers.require_root_default_prim
    root = next((item for item in context.lookdev.layers if item.identifier == context.stage.root_layer), None)
    passed = not required or bool(root and root.default_prim)
    return result(USD_ROOT_LAYER_DEFAULT_PRIM_AUTHORED, "Root Layer Default Prim Authored", "Layers", runtime_context, passed, f"Root-layer defaultPrim authored: {bool(root and root.default_prim)}.", details={"required": required, "default_prim": root.default_prim if root else ""})
