import sqlite3
from pathlib import Path

database_path = Path(".s_usd_data/s_usd.db")
database = sqlite3.connect(database_path)
database.row_factory = sqlite3.Row

print(f"Database: {database_path.resolve()}")
print(f"Size: {database_path.stat().st_size} bytes")
print("\nTables:")

tables = database.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""").fetchall()

for table in tables:
    print(f"  {table['name']}")

print("\nProjects:")

for row in database.execute("SELECT * FROM projects ORDER BY code"):
    print(dict(row))

print("\nAssets:")

for row in database.execute("SELECT * FROM assets ORDER BY code"):
    print(dict(row))

print("\nStreams:")

for row in database.execute("SELECT * FROM streams ORDER BY name"):
    print(dict(row))

print("\nVersions:")

for row in database.execute("""
    SELECT *
    FROM versions
    ORDER BY stream_id, number DESC
"""):
    print(dict(row))

database.close()