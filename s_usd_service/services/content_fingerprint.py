import hashlib
import json


class VersionContentFingerprint:
    @staticmethod
    def calculate(files):
        records = [
            {
                "role": item.role,
                "relative_path": item.relative_path,
                "size_bytes": int(item.size_bytes),
                "sha256": item.sha256.lower(),
                "status": item.status
            }
            for item in sorted(files, key=lambda value: value.relative_path)
        ]
        payload = json.dumps(
            records,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
