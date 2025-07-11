# core/turso_client.py

from libsql_client import create_client
from django.conf import settings

client = create_client(
    url=settings.TURSO_URL,
    auth_token=settings.TURSO_AUTH_TOKEN
)

def fetch_jobs(table_name):
    result = client.execute(f"SELECT * FROM {table_name}")
    jobs = []
    for row in result["rows"]:
        jobs.append(row)
    return jobs
