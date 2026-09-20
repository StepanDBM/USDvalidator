import sqlite3
from pathlib import Path
from uuid import UUID

database_path = Path(".s_usd_data/s_usd.db")
database = sqlite3.connect(database_path)
database.row_factory = sqlite3.Row


def format_uuid(value):
    return str(UUID(value)) if value else None


def format_row(row, uuid_fields=()):
    result = dict(row)

    for field in uuid_fields:
        result[field] = format_uuid(result[field])

    return result


print(f"Database: {database_path.resolve()}")
print(f"Size: {database_path.stat().st_size} bytes")

tables = database.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""").fetchall()

print("\nTables:")

for table in tables:
    print(f"  {table['name']}")

print("\nProjects:")

for row in database.execute("SELECT * FROM projects ORDER BY code"):
    print(format_row(row, ("id",)))

print("\nAssets:")

for row in database.execute("SELECT * FROM assets ORDER BY code"):
    print(format_row(row, ("id", "project_id")))

print("\nStreams:")

for row in database.execute("SELECT * FROM streams ORDER BY name"):
    print(format_row(row, ("id", "asset_id")))

print("\nVersions:")

for row in database.execute("""
    SELECT *
    FROM versions
    ORDER BY stream_id, number DESC
"""):
    print(format_row(row, ("id", "stream_id")))

database.close()