# debug_author.py
import sys
sys.path.insert(0, '.')
sys.path.insert(0, './apps/api')

# pyrefly: ignore [missing-import]
from app.core.database import SessionLocal
# pyrefly: ignore [missing-import]
from app.models.author import Author
# pyrefly: ignore [missing-import]
from app.api.v1.authors.schemas import AuthorResponse

def test_conversion():
    db = SessionLocal()
    author = db.query(Author).first()
    
    if author:
        print(f"Author: {author.name}")
        print(f"Type: {type(author)}")
        
        # Try to convert
        try:
            response = AuthorResponse.model_validate(author)
            print(f"✅ Conversion successful: {response}")
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            print(f"Author dict: {author.__dict__}")

if __name__ == "__main__":
    test_conversion()