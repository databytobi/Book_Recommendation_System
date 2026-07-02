# manual_clean.py
import sys
from pathlib import Path

api_dir = Path(__file__).resolve().parent / "apps" / "api"
sys.path.insert(0, str(api_dir))

# pyrefly: ignore [missing-import]
from app.core.database import engine
# pyrefly: ignore [missing-import]
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE"))
    conn.execute(text("CREATE SCHEMA public"))
    conn.commit()
    print("✅ Schema reset")

# Now create tables
# pyrefly: ignore [missing-import]
from app.core.database import Base
# pyrefly: ignore [missing-import]
from app.models import *
Base.metadata.create_all(bind=engine)
print("✅ Tables created")