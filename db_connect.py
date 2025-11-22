import os
import psycopg2
import urllib.parse as urlparse
from dotenv import load_dotenv
from pathlib import Path

def get_connection():
    try:
        # ✅ 1️⃣ Try Render DATABASE_URL (RECOMMENDED)
        db_url = os.getenv("DATABASE_URL")

        if db_url and db_url.startswith("postgres"):
            urlparse.uses_netloc.append("postgres")
            url = urlparse.urlparse(db_url)

            return psycopg2.connect(
                database=url.path.lstrip("/"),
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port,
                sslmode="require"   # ✅ required for Render
            )

        # ✅ 2️⃣ Try local dbinfo.env
        env_path = Path(__file__).resolve().parent / "dbinfo.env"
        if env_path.exists():
            load_dotenv(env_path, override=True)

        host = os.getenv("DB_HOST", "localhost")
        name = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        port = os.getenv("DB_PORT", "5432")

        # ✅ 3️⃣ Local connection support
        if host and name and user and password:
            return psycopg2.connect(
                host=host,
                port=port,
                database=name,
                user=user,
                password=password
            )

        # ✅ 4️⃣ Nothing worked
        raise Exception("DATABASE_URL and local DB settings missing")

    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)
        raise
