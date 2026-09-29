# Durable Validation Jobs

S-USDv persists remote validation work independently of the HTTP request that submitted it.

## State machine

```text
pending -> running -> succeeded
                  -> pending (bounded retry)
                  -> failed
pending -> cancelled
running -> cancelling -> cancelled
```

The terminal states are `cancelled`, `succeeded`, and `failed`.

## Configuration

```text
S_USDV_VALIDATION_WORKER_ENABLED=true
S_USDV_VALIDATION_WORKER_POLL_SECONDS=1.0
S_USDV_VALIDATION_JOB_MAXIMUM_ATTEMPTS=3
S_USDV_VALIDATION_JOB_RETRY_DELAY_SECONDS=5
```

Run one in-process worker per deployment for v0.2. Multiple service replicas require a database-specific atomic claim implementation before they may all enable their worker.

## Idempotency

An idempotency key is unique for the combination of workspace, requesting user, and key. Repeating a submission returns the original job instead of scheduling duplicate work.

## Recovery

At startup, abandoned `running` jobs return to `pending` while attempts remain. `cancelling` jobs become `cancelled`. Jobs that exhausted attempts become `failed`.

## Execution

The worker reconstructs the complete version in a temporary directory through the provider-neutral storage interface, validates the root layer, persists exactly one `ValidationRun`, and links it from the successful job.
