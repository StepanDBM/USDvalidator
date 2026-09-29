# Storage Providers

S-USDv service code depends on the provider-neutral `ObjectStorage` contract. The default provider is `local` and preserves the existing filesystem behavior.

## Configuration

```text
S_USDV_STORAGE_PROVIDER=local
S_USDV_STORAGE_ROOT=.s_usdv_data/storage
S_USDV_TEMPORARY_ROOT=.s_usdv_data/temp
S_USDV_STORAGE_CHUNK_SIZE=1048576
```

Unknown providers fail during dependency creation with a configuration error instead of silently falling back to local storage.

## Provider contract

A provider must implement streaming writes and reads, existence checks, metadata lookup, deletion, key enumeration, and health checks. Writes must enforce the optional byte limit, clean incomplete content after failure, and promote completed content atomically from the application's perspective.

`resolve_local_path()` is optional. Cloud providers should return `None`; service code must use `open()` rather than assuming that an object is a local file.

## Adding Azure Blob Storage later

An Azure adapter can register itself as `azure` through `register_storage_provider()` and implement the same contract with `azure-storage-blob`. Expected configuration belongs in environment variables or a secret manager, not source control. The existing service routes, file lifecycle, and reconciliation services should not require provider-specific changes.

## Contract tests

`tests/service/test_storage_provider_contract.py` is the shared behavioral suite. Add a fixture entry for every provider. A provider is not supported until the complete contract passes.
