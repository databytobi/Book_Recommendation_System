# final_fix.py
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
        # Drop the problematic index directly
        conn.execute(text("DROP INDEX IF EXISTS ix_authors_total_books"))
        conn.commit()
        print("✅ Dropped index ix_authors_total_books")
        
        # Now create tables
        # pyrefly: ignore [missing-import]
        from app.core.database import Base
        # pyrefly: ignore [missing-import]
        from app.models.user import User
        # pyrefly: ignore [missing-import]
        from app.models.author import Author
        # pyrefly: ignore [missing-import]
        from app.models.recommendation_click import RecommendationClick
        # pyrefly: ignore [missing-import]
        from app.models.recommendation_event import RecommendationEvent
        # pyrefly: ignore [missing-import]
        from app.models.search_history import SearchHistory
        # pyrefly: ignore [missing-import]
        from app.models.user_book_interaction import UserBookInteraction
        # pyrefly: ignore [missing-import]
        from app.models.user_favorite_book import UserFavoriteBook
        # pyrefly: ignore [missing-import]
        from app.models.user_followed_author import UserFollowedAuthor
        # pyrefly: ignore [missing-import]
        from app.models.user_preference import UserPreference
        # pyrefly: ignore [missing-import]
        from app.models.user_profile import UserProfile
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Verify
        # pyrefly: ignore [missing-import]
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Created tables: {', '.join(sorted(tables))}")
        
except Exception as e:
    print(f"❌ Error: {e}")