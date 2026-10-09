import pandas as pd
from pathlib import Path

# Fix: Use __file__ (double underscores) not **file**
BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "data" / "processed"

def load_datasets():
    print("=" * 60)
    print("LOADING INTEGRATED DATASETS")
    print("=" * 60)
    
    books = pd.read_parquet(
        DATA_DIR / "integrated" / "master_books.parquet"
    )
    
    ratings = pd.read_parquet(
        DATA_DIR / "ratings" / "ratings_cleaned.parquet"
    )
    
    users = pd.read_parquet(
        DATA_DIR / "users" / "users_cleaned.parquet"
    )
    
    print(f"✓ Books: {len(books):,}")
    print(f"✓ Ratings: {len(ratings):,}")
    print(f"✓ Users: {len(users):,}")
    
    return books, ratings, users

def validate_books(books):
    print("\n📚 BOOKS VALIDATION")
    print("-" * 40)
    
    duplicate_isbns = books["isbn"].duplicated().sum()
    print(f"Duplicate ISBNs: {duplicate_isbns:,}")
    
    missing_titles = books["title"].isna().sum()
    print(f"Missing titles: {missing_titles:,}")
    
    missing_authors = books["authors"].isna().sum()
    print(f"Missing authors: {missing_authors:,}")
    
    missing_publishers = books["publisher"].isna().sum()
    print(f"Missing publishers: {missing_publishers:,}")
    
    if "language_code" in books.columns:
        language_coverage = (books["language_code"].notna().mean()) * 100
        print(f"Language metadata coverage: {language_coverage:.2f}%")
    
    if "average_rating" in books.columns:
        avg_rating_coverage = (books["average_rating"].notna().mean()) * 100
        print(f"Average rating coverage: {avg_rating_coverage:.2f}%")
        print(f"Average rating (overall): {books['average_rating'].mean():.2f}")

def validate_ratings(ratings):
    print("\n⭐ RATINGS VALIDATION")
    print("-" * 40)
    
    duplicate_interactions = ratings[["user_id", "isbn"]].duplicated().sum()
    print(f"Duplicate interactions: {duplicate_interactions:,}")
    
    # Calculate sparsity
    n_users = ratings["user_id"].nunique()
    n_books = ratings["isbn"].nunique()
    total_possible = n_users * n_books
    sparsity = (1 - (len(ratings) / total_possible)) * 100
    print(f"Matrix sparsity: {sparsity:.5f}%")
    print(f"Unique users: {n_users:,}")
    print(f"Unique books rated: {n_books:,}")
    
    user_activity = ratings.groupby("user_id").size()
    print(f"Median interactions/user: {user_activity.median():.0f}")
    print(f"Mean interactions/user: {user_activity.mean():.1f}")
    print(f"Max interactions/user: {user_activity.max():,}")
    
    book_popularity = ratings.groupby("isbn").size()
    print(f"Median interactions/book: {book_popularity.median():.0f}")
    print(f"Mean interactions/book: {book_popularity.mean():.1f}")
    print(f"Most popular book interactions: {book_popularity.max():,}")
    
    # Rating distribution
    if "book_rating" in ratings.columns:
        print(f"\nRating distribution:")
        rating_counts = ratings['book_rating'].value_counts().sort_index()
        for rating, count in rating_counts.items():
            if rating > 0:
                pct = (count / len(ratings)) * 100
                print(f"  Rating {int(rating)}: {count:,} ({pct:.1f}%)")

def validate_users(users):
    print("\n👤 USERS VALIDATION")
    print("-" * 40)
    
    duplicate_users = users["user_id"].duplicated().sum()
    print(f"Duplicate users: {duplicate_users:,}")
    
    missing_ages = (users["age"].isna().mean()) * 100
    print(f"Missing age ratio: {missing_ages:.2f}%")
    
    if "age" in users.columns:
        valid_ages = users["age"].notna().sum()
        if valid_ages > 0:
            print(f"Average age: {users['age'].mean():.1f}")
            print(f"Median age: {users['age'].median():.1f}")
            print(f"Age range: {users['age'].min():.0f} - {users['age'].max():.0f}")
    
    if "country" in users.columns:
        countries = users["country"].nunique()
        print(f"Unique countries: {countries:,}")
        
        # Show top 10 countries
        print(f"\nTop 10 countries by user count:")
        country_counts = users['country'].value_counts().head(10)
        for country, count in country_counts.items():
            if pd.notna(country):
                pct = (count / len(users)) * 100
                print(f"  {country}: {count:,} ({pct:.1f}%)")
    
    if "location" in users.columns:
        missing_location = users["location"].isna().sum()
        print(f"Missing location: {missing_location:,} ({missing_location/len(users)*100:.1f}%)")

def overall_assessment(books, ratings, users):
    print("\n" + "=" * 60)
    print("SYSTEM READINESS ASSESSMENT")
    print("=" * 60)
    
    # Data quality scores
    score = 0
    max_score = 10
    
    print("\n📊 DATA QUALITY METRICS:")
    print("-" * 40)
    
    # Books quality
    if books["isbn"].duplicated().sum() == 0:
        print("✅ Books: No duplicate ISBNs")
        score += 1
    else:
        print("⚠️ Books: Duplicate ISBNs found")
    
    if books["title"].isna().sum() / len(books) < 0.05:
        print("✅ Books: High title coverage (>95%)")
        score += 1
    else:
        print("⚠️ Books: Low title coverage")
    
    # Ratings quality
    if len(ratings) > 0:
        print("✅ Ratings: Active interaction data present")
        score += 1
    
    if "book_rating" in ratings.columns:
        print("✅ Ratings: Explicit feedback available")
        score += 1
    
    # Users quality
    if users["user_id"].duplicated().sum() == 0:
        print("✅ Users: No duplicate users")
        score += 1
    else:
        print("⚠️ Users: Duplicate users found")
    
    if users["country"].notna().mean() > 0.9:
        print("✅ Users: Good country coverage (>90%)")
        score += 1
    else:
        print("⚠️ Users: Low country coverage")
    
    # Recommendations readiness
    print("\n🚀 RECOMMENDATION READINESS:")
    print("-" * 40)
    
    # Collaborative filtering readiness
    n_users = ratings["user_id"].nunique()
    n_books = ratings["isbn"].nunique()
    if n_users > 1000 and n_books > 1000:
        print("✅ Collaborative filtering: Sufficient user-item interactions")
        score += 1
    else:
        print("⚠️ Collaborative filtering: Limited interactions")
    
    # Content-based readiness
    if "authors" in books.columns and books["authors"].notna().mean() > 0.8:
        print("✅ Content-based: Rich metadata available")
        score += 1
    else:
        print("⚠️ Content-based: Limited metadata")
    
    # Hybrid recommendation readiness
    if score >= 7:
        print("\n🎯 RECOMMENDATION: System ready for hybrid recommendations")
    else:
        print("\n🎯 RECOMMENDATION: Consider additional data enrichment")
    
    print(f"\n📈 Quality Score: {score}/{max_score}")
    
    # Next steps
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. Feature Engineering
   → Create user-item interaction matrix
   → Extract temporal features from ratings
   → Build content features from book metadata

2. Popularity Recommender
   → Implement baseline popularity model
   → Evaluate with ranking metrics

3. Content Embeddings
   → Generate TF-IDF vectors from book titles/authors
   → Create item similarity matrix

4. Collaborative Filtering
   → Train ALS or SVD model
   → Generate user and item embeddings

5. Hybrid Ranking
   → Combine content and collaborative scores
   → Implement ranking pipeline
""")

def main():
    books, ratings, users = load_datasets()
    
    validate_books(books)
    validate_ratings(ratings)
    validate_users(users)
    
    overall_assessment(books, ratings, users)

if __name__ == "__main__":
    main()