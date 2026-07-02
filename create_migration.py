# add_account_status.py
import sys
from pathlib import Path

# Add the API directory to path
api_dir = Path(__file__).resolve().parent / "apps" / "api"
sys.path.insert(0, str(api_dir))

import logging
# pyrefly: ignore [missing-import]
from app.core.database import engine
# pyrefly: ignore [missing-import]
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_account_status_column():
    """Add account_status column to users table if it doesn't exist."""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'account_status'
            """))
            
            if result.fetchone():
                logger.info("✅ account_status column already exists")
                return
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN account_status VARCHAR(20) DEFAULT 'pending_verification'
            """))
            conn.commit()
            logger.info("✅ Added account_status column to users table")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    add_account_status_column()