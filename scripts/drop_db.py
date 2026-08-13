import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.config import get_settings

def drop_and_create_db():
    settings = get_settings()
    url = settings.database_url
    
    # We must connect to the server without specifying the database
    # Assuming URL is like mysql+pymysql://user:pass@host:port/dbname
    from sqlalchemy.engine.url import make_url
    parsed_url = make_url(url)
    db_name = parsed_url.database
    
    server_url = parsed_url.set(database='')
    
    engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        print(f"Dropping database {db_name}...")
        conn.execute(text(f"DROP DATABASE IF EXISTS `{db_name}`;"))
        print(f"Creating database {db_name}...")
        conn.execute(text(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
    print("Database recreated successfully.")

if __name__ == "__main__":
    drop_and_create_db()
