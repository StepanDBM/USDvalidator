from s_usd_core.rules.common import result
from s_usd_core.validation.check_ids import (
    USD_INSTANCE_COUNT_LIMIT,
    USD_INSTANCE_PROTOTYPES_VALID,
    USD_POINT_INSTANCE_COUNT_LIMIT,
    USD_POINT_INSTANCER_INDICES_VALID,
    USD_POINT_INSTANCER_PROTOTYPES_VALID,
)


def check_instance_count_limit(context, runtime_context):
    count = sum(item.instance for item in context.pipeline.instances)
    limit = runtime_context.config.instancing.maximum_instances
    return result(USD_INSTANCE_COUNT_LIMIT, "Instance Count Limit", "Instancing", runtime_context, count <= limit, f"Instance count {count}; allowed maximum {limit}.", details={"count": count, "limit": limit}, suggestion="Reduce instance count or override the limit.")


def check_point_instance_count_limit(context, runtime_context):
    count = sum(item.point_instance_count for item in context.pipeline.instances)
    limit = runtime_context.config.instancing.maximum_point_instances
    return result(USD_POINT_INSTANCE_COUNT_LIMIT, "Point Instance Count Limit", "Instancing", runtime_context, count <= limit, f"Point instance count {count}; allowed maximum {limit}.", details={"count": count, "limit": limit}, suggestion="Reduce point instances or override the limit.")


def check_point_instancer_prototypes_valid(context, runtime_context):
    required = runtime_context.config.instancing.require_valid_prototypes
    invalid = [item.path for item in context.pipeline.instances if item.point_instancer and required and item.prototype_count == 0]
    return result(USD_POINT_INSTANCER_PROTOTYPES_VALID, "Point Instancer Prototypes Valid", "Instancing", runtime_context, not invalid, f"Point instancers without prototypes: {len(invalid)}.", details={"paths": invalid}, suggestion="Author valid prototype targets.")


def check_point_instancer_indices_valid(context, runtime_context):
    invalid = {item.path: item.invalid_proto_indices for item in context.pipeline.instances if item.point_instancer and item.invalid_proto_indices}
    return result(USD_POINT_INSTANCER_INDICES_VALID, "Point Instancer Indices Valid", "Instancing", runtime_context, not invalid, f"Point instancers with invalid prototype indices: {len(invalid)}.", details={"instancers": invalid}, suggestion="Repair protoIndices to reference existing prototypes.")


def check_instance_prototypes_valid(context, runtime_context):
    required = runtime_context.config.instancing.require_valid_prototypes
    invalid = [item.path for item in context.pipeline.instances if item.instance and required and not item.prototype_path]
    return result(USD_INSTANCE_PROTOTYPES_VALID, "Instance Prototypes Valid", "Instancing", runtime_context, not invalid, f"Instances without valid prototypes: {len(invalid)}.", details={"paths": invalid}, suggestion="Repair broken instance prototypes.")
