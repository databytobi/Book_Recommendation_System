Milestone Explanation: Implementing Reading Style End-to-End

This milestone wasn't just about adding a new field called Reading Style. It was about extending the application across every layer of the software architecture while keeping the database, API, business logic, and frontend synchronized.

Think of it as adding one new feature that had to travel through the entire system.

1. The problem we were solving

Originally, your onboarding collected:

Favorite genres

Favorite authors

Favorite books

Reading goal

Language

Theme

But it didn't know how the user reads.

We introduced four reading styles:

Style
Meaning
quick
Short, easy-to-finish books
balanced
Mix of entertainment and depth
deep
Long, intellectually rich books
explorer
Likes discovering unusual books

This becomes another personalization signal for recommendations.

When a user clicks one card:

const [selected, setSelected] = useState<number | null>(null);

onClick={() => setSelected(style.id)}

The component doesn't save anything itself. It only returns the selected value to the parent through:

onContinue(selectedStyle);

This is good component design because the UI is separated from the business logic.

3. API contract (Pydantic Schema)

The frontend sends JSON to FastAPI.

We extended OnboardingRequest.

Before:

reading_goal: Optional[ReadingGoal]

After:

class ReadingStyle(str, Enum):
    QUICK = "quick"
    BALANCED = "balanced"
    DEEP = "deep"
    EXPLORER = "explorer"

reading_style: Optional[ReadingStyle] = Field(
    default=ReadingStyle.BALANCED
)

This is important because Enums guarantee valid values.

Valid:

{
  "reading_style": "deep"
}

Invalid:

{
  "reading_style": "super_reader"
}

FastAPI rejects the second request automatically.

4. Why we used Alembic

A common beginner mistake is manually editing PostgreSQL.

For example:

ALTER TABLE user_profiles
ADD COLUMN reading_style VARCHAR(20);

That changes the database, but the project loses its history.

Instead we use Alembic, which is database version control.

Think of Git, but for PostgreSQL.

Database version timeline

Every migration has a unique revision ID.

Your project now has:

Revision

	

Purpose




941fd45aea84

	

Initial database




bfbffd008889

	

Added reading_style

That means anyone cloning your project can recreate the exact same database.

5. Updating the SQLAlchemy model

Alembic compares models with database structure.

So we first modified:

class UserProfile(Base):

We added:

reading_style = Column(
    String(20),
    default="balanced",
    nullable=False,
    index=True
)

This tells SQLAlchemy:

Store text

Maximum length = 20

Default = balanced

Cannot be NULL

Create an index

Without this change Alembic would never detect anything.

6. Creating the migration

We generated the migration with:

alembic revision --autogenerate \
    -m "add reading style to user profiles"

Alembic inspected:

SQLAlchemy models

PostgreSQL tables

It detected:

Detected added column:
user_profiles.reading_style

and generated:

def upgrade():
    op.add_column(
        "user_profiles",
        sa.Column(
            "reading_style",
            sa.String(20),
            nullable=False
        )
    )

    op.create_index(
        "ix_user_profiles_reading_style",
        "user_profiles",
        ["reading_style"]
    )

This file becomes a permanent record of the database change.

7. Applying the migration

Creating a migration does not change the database.

We then executed:

alembic upgrade head

Output:

Running upgrade
941fd45aea84
→
bfbffd008889

Now PostgreSQL actually contained the new column.

We verified it with SQLAlchemy Inspector:

inspect(engine).get_columns("user_profiles")

Result:

reading_style
VARCHAR(20)
nullable=False

This is much safer than manually checking pgAdmin because it verifies it through Python.

8. Service layer

The service is where business logic lives.

Originally it saved:

profile.reading_goals = ...
profile.preferred_language = ...

We added:

profile.reading_style = ...

Now every onboarding completion persists the user's reading style.

This is the only layer allowed to write profile preferences.

9. The bug we discovered

The most valuable lesson of this milestone was integration testing.

Everything looked correct:

Schema

Model

Migration

Database

But the API failed.

Error:

'str' object has no attribute 'value'

Why?

Your validator converted Enum objects into strings.

Example:

Language.ENGLISH

became

"en"

Then the route tried:

request.preferred_language.value

Strings don't have .value.

The fix

Instead of assuming Enum:

request.preferred_language.value

we safely handled both:

request.preferred_language.value
if hasattr(request.preferred_language, "value")
else request.preferred_language

This made the endpoint compatible with both Enum objects and validated strings.

This is a classic example of an integration bug—each individual layer worked, but they disagreed on the data type.

10. API testing strategy

We didn't stop at unit testing.

We tested four different layers.

Test

	

Purpose




Schema test

	

Validate Enum




Database test

	

Verify column exists




Service test

	

Verify persistence




HTTP API test

	

Verify complete flow

Schema test

We instantiated the Pydantic model:

OnboardingRequest(reading_style="deep")

Result:

ReadingStyle.DEEP

This confirmed validation.

Service test

We created a temporary user.

user = User(...)

Then called:

service.complete_onboarding(...)

Finally queried PostgreSQL.

Output:

REQUEST STYLE: deep
STORED STYLE: deep
MATCH: True

That proved persistence worked.

Afterward we deleted the temporary user to keep the database clean.

HTTP API test

Finally we used Swagger.

Request:

{
  "reading_style": "deep",
  "reading_goal": "moderate",
  "preferred_language": "en"
}

Backend log:

POST /api/v1/onboarding/onboarding/complete

201 Created

This confirmed the entire production flow works exactly as the frontend will use it.


Milestone: Building the Book Catalog Infrastructure
Objective

The goal of this milestone was to transform our processed book dataset from a static Parquet file into a fully searchable PostgreSQL database that the FastAPI backend can query in real time.

Before this milestone, the recommendation system had user tables (users, profiles, preferences, interactions) but no book catalog inside PostgreSQL. The books only existed as machine learning artifacts.


he important limitation was that FastAPI could not query books from PostgreSQL because the books table did not exist.

That meant features like:

Personalized recommendations

Genre filtering

Author filtering

Pagination

Search

could not be implemented efficiently.

Step 1 — Creating the Book SQLAlchemy Model

We created a new model:

apps/api/app/models/book.py

This model defines the structure of the books table using SQLAlchemy.

Instead of manually writing SQL, we described the table in Python:

class Book(Base):
    __tablename__ = "books"

    isbn = Column(String(13), primary_key=True)
    title = Column(Text)
    authors = Column(Text)
    genre = Column(Text)
    average_rating = Column(Float)
    ratings_count = Column(Integer)
Why SQLAlchemy?

SQLAlchemy is the Object Relational Mapper (ORM) that connects Python objects with PostgreSQL tables.

Python

	

PostgreSQL




Book.title

	

books.title




Book.genre

	

books.genre




Book.average_rating

	

books.average_rating

This allows us to write:

db.query(Book).filter(Book.genre == "Fantasy")

instead of raw SQL.

Step 2 — Registering the model

Creating the model alone does not tell SQLAlchemy it exists.

We registered it inside:

app/models/__init__.py

by importing:

from app.models.book import Book

This makes the model part of SQLAlchemy's metadata.

Without this step, Alembic would never detect the table.

Step 3 — Using Alembic to generate the migration

Alembic compares:

SQLAlchemy models (Python)

PostgreSQL database (current schema)

We ran:

alembic revision --autogenerate -m "create books table"

Alembic detected:

Detected added table 'books'
Detected added index 'ix_books_title'
Detected added index 'ix_books_genre'
Detected added index 'ix_books_average_rating'
What Alembic actually generated

It produced a migration file containing:

op.create_table(
    "books",
    ...
)

This is essentially a Python version of SQL's CREATE TABLE.

Alembic also generated indexes automatically.

Step 4 — Applying the migration

Generating a migration does not modify the database.

We executed:

alembic upgrade head

This applied the migration to PostgreSQL.

Our migration history became:

Initial Migration
        │
        ▼
Add reading_style
        │
        ▼
Create books table

At this point PostgreSQL contained an empty books table.

Step 5 — Importing the Parquet dataset into PostgreSQL

This was the biggest part of the milestone.

What is a Parquet file?

A Parquet file is a columnar data storage format optimized for analytics and machine learning.

Our file:

apps/api/ml/artifacts/semantic_books.parquet

contained:

Dataset

	

Records




Books

	

248,176

Unlike CSV, Parquet preserves data types and loads much faster.

Reading the dataset

We used pandas:

df = pd.read_parquet(PARQUET_PATH)

Result:

Loaded 248,176 books

The DataFrame became the in-memory representation of our catalog.

Step 6 — Converting DataFrame rows into SQLAlchemy objects

Every row in the DataFrame was converted into a Book object.

Conceptually:

DataFrame

	

SQLAlchemy




row["title"]

	

Book(title=...)




row["authors"]

	

Book(authors=...)




row["genre"]

	

Book(genre=...)

Example:

Book(
    isbn=row["isbn"],
    title=row["title"],
    authors=row["authors"],
)

We repeated this for all 248,176 books.

Step 7 — Handling missing values (NaN)

During the import we encountered an error:

ValueError: cannot convert float NaN to integer
Why it happened

Pandas stores missing numeric values as NaN, not None.

Example:

Value

	

Python type




125

	

int




4.5

	

float




NaN

	

float

Trying to do:

int(float("nan"))

raises an exception.

The solution

We used:

pd.isna(value)

Example:

ratings_count = (
    0 if pd.isna(row["ratings_count"])
    else int(row["ratings_count"])
)

This safely converts missing values into database defaults.

This is a common ETL (Extract–Transform–Load) practice.

Step 8 — Bulk inserting into PostgreSQL

Instead of inserting one book at a time, we used:

db.bulk_save_objects(books)
db.commit()
Why bulk insertion?

Individual inserts

	

Bulk insert




248,176 SQL statements

	

Single optimized transaction




Slow

	

Much faster




Higher overhead

	

Production approach

This is the recommended method when importing large datasets.

Step 9 — Verifying the import

We confirmed the import using SQLAlchemy:

db.query(Book).count()

Output:

Books: 248176

We also retrieved the first record:

Classical Mythology
Author: Mark P. O. Morford

This verified that:

The table exists

Data was imported

SQLAlchemy can query it successfully


What we achieved

You have now connected your trained embedding model to the backend.

The recommendation pipeline is officially:

User favorites → Taste vector

FAISS → Top 250 semantically similar books

PostgreSQL → Fetch full book records

Hybrid scoring → Genre + Author + Popularity + Reading Style

API → Return the best 20 books

Milestone Hybrid Recommendation API

Built a production-style recommendation endpoint that combines semantic search, user preferences, popularity ranking, and reading behavior into personalized book recommendations.

Technical achievements

Designed RecommendationRequest and RecommendationResponse schemas.

Built RecommendationService as the recommendation engine.

Connected the trained FAISS index (248,176 embeddings).

Imported 248,176 books into PostgreSQL from Parquet.

Implemented hybrid scoring using author, genre, popularity, and reading style.

Exposed GET /api/v1/recommendations through FastAPI.

Successfully tested the endpoint in Swagger with JWT authentication.

Milestone achieved: Discover Page
What we accomplished

Backend

Built a production BookService layer.

Added GET /api/v1/books with pagination.

Cached the 248,176-book dataset using @lru_cache.

Kept /books/search intact without breaking existing functionality.

Frontend

Replaced mock books with the real Books API.

Created /dashboard/discover.

Reused your existing BookCard component.

Rendered real cover images from PostgreSQL.

Added pagination with Load More.

Architecture now
PostgreSQL (248,176 books)
          │
   BookService (FastAPI)
          │
GET /api/v1/books
          │
 book.service.ts
          │
 /dashboard/discover
          │
     BookCard UI


Performance improvement

Endpoint                    Before        After collaborative fix              After cache

Login                      1.4 s           0.6 s                                 0.31 s

Book search                5.9 s           5.9 s                                 1.81 s

Recommendations (1st call)  389 s         28.3 s                                 13.15 s

Recommendations (warm)  389 s           27.1 s                                 9.76 s

Auth / Favorites / History ~0.3 s         ~0.3 s                                 0.08 s

You've cut recommendations from 389 seconds to under 10 seconds on warm requests—that's about a 97.5% improvement.     

But 28 seconds is still too slow for release

The remaining bottleneck is in your constructor:

self.faiss_index = faiss.read_index(...)
self.embeddings = np.load(...)
self.semantic_books = pd.read_parquet(...)

Every request is reloading three large artifacts from disk:

FAISS index (~397 MB)

Embeddings (~397 MB)

Parquet (~34 MB)

That's over 800 MB being read on every recommendation request.
then i created a cache in memory (ml/artifacts/cache.py). it loads from the shared cache instead of reading the files every request.