from s_usd_desktop.cache import CacheLocation, CacheManager, VerifiedDownloader
from s_usd_desktop.client import FileClient, SUsdvApiClient


file_id = "PASTE-STORED-FILE-UUID" #ex: "599a77dc-6d89-4b79-a063-d70e1d730b1c"

with SUsdvApiClient() as api:
    files = FileClient(api)
    stored_file = files.get_file(file_id)
    downloader = VerifiedDownloader(files, CacheManager())

    entry = downloader.download(
        stored_file,
        CacheLocation(
            project_code="EXP",
            asset_code="probe",
            stream_name="model",
            version_number=1
        ),
        progress=lambda sent, total: print(
            f"\r{sent:,} / {total:,} bytes",
            end=""
        )
    )

print()
print("Downloaded:", entry.local_path)
print("Status:", entry.status.value)
print("SHA-256:", entry.sha256)