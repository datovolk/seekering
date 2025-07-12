import asyncio
import sqlite3
from libsql_client import create_client
import os
# === Turso Remote Connection ===
TURSO_URL = "https://sqld-davitjibladze.aws-eu-west-1.turso.io"
TURSO_AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTIxMzA2OTQsImlkIjoiZTM2Y2RmMmItOWQzZS00MDkxLThkMjAtZTVkNWQwYzllNDJkIiwicmlkIjoiMjE5NDUzMzktYzE2Ny00Y2U2LWI3NzktNGQ3ZjFiYjIyZWQwIn0._g-BofzEf9MjGZ3-rwY2D5pKLBDT3mMeKzvhU8j1EvFv-CclVmNmSjD5oKUy85lXxnLNTIS6vuk0DvujqgHmBg"                # ← paste your token here


# === Tables to Sync ===
tables = ['hr_ge', 'jobs_ge', 'myjobs_ge']

script_dir = os.path.dirname(os.path.abspath(__file__))  # directory where the script is
db_path = os.path.join(script_dir, "main.db")




async def sync_data():
    # ✅ create_client is synchronous — no await needed
    turso_client = create_client(url=TURSO_URL, auth_token=TURSO_AUTH_TOKEN)

    # === Local SQLite Connection ===
    conn_local = sqlite3.connect(db_path)
    cursor_local = conn_local.cursor()

    for table in tables:
        print(f"\n🔄 Syncing table: {table}")

        # 1. Delete existing rows
        cursor_local.execute(f"DELETE FROM {table}")
        print(f"🗑️ Deleted from local.{table}")

        # 2. Fetch all rows from Turso (this is async)
        result = await turso_client.execute(f"SELECT * FROM {table}")
        rows = [tuple(row) for row in result.rows]


        # 3. Insert into local DB
        cursor_local.executemany(f"""
            INSERT OR IGNORE INTO {table}
            (id, position, company,  date,published_date, end_date, company_url,position_url )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)


        print(f"✅ Inserted {len(rows)} rows into local.{table}")

    # Finalize
    conn_local.commit()
    conn_local.close()
    print("\n✅ Sync complete!")

# Run the async main
asyncio.run(sync_data())

