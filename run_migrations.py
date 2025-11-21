import os
import psycopg2
import glob

def run_migrations():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("❌ DATABASE_URL not found! Migration skipped.")
        return

    print("🔄 Running migrations...")

    try:
        conn = psycopg2.connect(db_url, sslmode="require")
        cur = conn.cursor()

        sql_files = sorted(glob.glob("migrations/*.sql"))

        for file in sql_files:
            print(f"📄 Applying migration: {file}")
            with open(file, "r", encoding="utf-8") as f:
                sql = f.read()
                cur.execute(sql)
                conn.commit()

        cur.close()
        conn.close()
        print("✅ All migrations applied successfully!")

    except Exception as e:
        print("❌ Migration failed:", e)


if __name__ == "__main__":
    run_migrations()
