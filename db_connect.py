import os
import psycopg2
import urllib.parse as urlparse
from dotenv import load_dotenv
from pathlib import Path

def get_connection():
    try:
        # 1️⃣ FIRST: Try Render DATABASE_URL
        db_url = os.getenv("DATABASE_URL")

        if db_url:
            urlparse.uses_netloc.append("postgres")
            url = urlparse.urlparse(db_url)

            return psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port,
                sslmode="require"
            )

        # 2️⃣ SECOND: Try Local PC .env
        env_path = Path(__file__).resolve().parent / "dbinfo.env"

        if env_path.exists():
            load_dotenv(env_path, override=True)

        host = os.getenv("DB_HOST")
        name = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        port = os.getenv("DB_PORT")

        if host and name and user and password:
            return psycopg2.connect(
                host=host,
                port=port,
                database=name,
                user=user,
                password=password
            )

        # 3️⃣ NOTHING FOUND → raise error
        raise Exception("❌ Local DB_HOST not found and Render DATABASE_URL missing.")

    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)
        raise
