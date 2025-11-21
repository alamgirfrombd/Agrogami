import os
import psycopg2
import urllib.parse as urlparse

def get_connection():
    try:
        # Render uses DATABASE_URL
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            raise Exception("❌ DATABASE_URL not found. Set it in Render Environment Variables.")

        urlparse.uses_netloc.append("postgres")
        url = urlparse.urlparse(db_url)

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            sslmode="require"
        )
        return conn

    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)
        raise
