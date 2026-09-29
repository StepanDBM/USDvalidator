from enum import StrEnum


class ValidationJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


TERMINAL_JOB_STATUSES = frozenset(
    {ValidationJobStatus.CANCELLED.value, ValidationJobStatus.SUCCEEDED.value, ValidationJobStatus.FAILED.value}
)
