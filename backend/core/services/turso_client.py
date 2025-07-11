import httpx

TURSO_DB_URL = "https://your-database.turso.io"
TURSO_AUTH_TOKEN = "your_auth_token_here"

def run_turso_query(query, params=None):
    headers = {
        "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "statement": query,
        "args": params or []
    }

    response = httpx.post(f"{TURSO_DB_URL}/v1/query", json=data, headers=headers)
    response.raise_for_status()
    result = response.json()
    return result.get("results", [{}])[0].get("rows", [])
