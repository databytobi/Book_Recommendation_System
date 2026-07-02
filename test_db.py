# test_db.py
import sys
from pathlib import Path

api_dir = Path(__file__).resolve().parent / "apps" / "api"
sys.path.insert(0, str(api_dir))

# pyrefly: ignore [missing-import]
from app.core.database import engine
# pyrefly: ignore [missing-import]
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version}")
        
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"✅ Database: {db_name}")
        
        result = conn.execute(text("SELECT current_schema()"))
        schema = result.fetchone()[0]
        print(f"✅ Schema: {schema}")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")