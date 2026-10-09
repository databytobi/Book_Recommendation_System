"""
Derived genre classification for the book catalog.

WHY THIS EXISTS
---------------
Neither raw data source carries a genre column:

* Book-Crossing `Books.csv` -> ISBN, Book-Title, Book-Author,
  Year-Of-Publication, Publisher, Image-URL-S/M/L.
* Goodreads `books.csv`    -> bookID, title, authors, average_rating, isbn,
  isbn13, language_code, num_pages, ratings_count, text_reviews_count,
  publication_date, publisher.

So `Book.genre` is NULL for all 248,176 rows, and every genre-dependent
feature silently degrades: the browse/search API returns `genre: null`, and
the recommendations service had to delete its genre scoring term entirely
(see `recommendations/service.py`) because the term was a constant zero.

This module derives a genre at read time from the signals the catalog DOES
have: the title, the author, and the publisher imprint. Nothing is written
back to the data files or the database.

HONEST LIMITS
-------------
This is a heuristic, not authoritative metadata. Measured coverage over the
full 248,176-row catalog is roughly 32%, so about two thirds of the catalog
resolves to `None`. That is a genuine improvement over 0% but it means
`genre` must still be treated as "may be unknown":

* Keep `genre` nullable everywhere. Do NOT make it a required field, and do
  not let a recommendation score depend on it unless the candidate actually
  has a genre -- re-introducing an always-zero term is the exact bug that was
  removed from `recommendations/service.py`.
* For real coverage the catalog would need an external join (e.g. Open Library
  bulk edition dumps keyed by ISBN-13, which requires normalising the mostly
  ISBN-10 Book-Crossing identifiers first).

TWO DEFECTS THIS FIXES
----------------------
The previous inline classifier in
`ml/popularity/popularity_recommender.py::_extract_categories`:

1. Used plain substring matching, which produced large false-positive
   buckets -- `'ya'` matched 3,992 rows as a substring but only 42 as a whole
   word (matching "the *ya*wning heights" and "life of pi" by *Yann* Martel),
   and `'war'` matched 8,430 rows but only 2,335 at word boundaries (matching
   the author Robert Penn *War*ren). Word-boundary matching is used here.
2. Declared a 'Thriller' category that was unreachable dead code, because
   'Mystery' was tested first and already claimed the words "thriller" and
   "suspense". Categories are ordered most-specific-first below.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Dict, List, Optional, Pattern, Tuple

import pandas as pd

# ---------------------------------------------------------------------------
# Title / author keyword rules
# ---------------------------------------------------------------------------
#
# Ordered most-specific-first; the first matching rule wins. Every keyword is
# matched on whole-word boundaries so short tokens cannot fire inside longer
# words. Multi-word phrases still match normally under \b.
#
# Ordering notes:
#   * Young Adult precedes Children so "young adult" titles are not swallowed.
#   * Mystery precedes Thriller, so Thriller keywords must NOT be a subset of
#     Mystery's. "mystery"/"detective" live under Mystery; "thriller" words
#     that Mystery does not claim are listed separately. Because Mystery is
#     checked first, any word shared between them resolves to Mystery, which is
#     why Thriller lists only words Mystery does not use.
CATEGORY_KEYWORDS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "Fantasy",
        (
            "harry potter", "lord of the rings", "fantasy", "wizard", "magic",
            "dragon", "hobbit", "wheel of time", "mistborn", "stormlight",
            "chronicles of narnia", "game of thrones", "sword of truth",
            "earthsea", "discworld", "shannara", "belgariad",
        ),
    ),
    (
        "Science Fiction",
        (
            "science fiction", "sci-fi", "sci fi", "dune", "foundation",
            "cyberpunk", "fahrenheit 451", "brave new world", "ender",
            "space opera", "starship", "robot", "android", "time machine",
            "hitchhiker", "neuromancer", "snow crash",
        ),
    ),
    (
        "Classic",
        (
            "to kill a mockingbird", "pride and prejudice", "great gatsby",
            "jane austen", "moby dick", "moby-dick", "war and peace",
            "crime and punishment", "ulysses", "dickens", "charles dickens",
            "sense and sensibility", "emma", "wuthering heights", "jane eyre",
            "heart of darkness", "don quixote", "odyssey", "iliad",
            "anna karenina", "brothers karamazov", "les miserables",
            "scarlet letter", "tale of two cities", "animal farm",
            "of mice and men", "romeo and juliet", "hamlet", "macbeth",
            "lord of the flies", "catcher in the rye", "grapes of wrath",
        ),
    ),
    (
        "Mystery",
        (
            "mystery", "detective", "sherlock", "whodunit", "agatha christie",
            "p.d. james", "murder", "crime", "suspense",
        ),
    ),
    (
        # Deliberately excludes "mystery"/"detective"/"suspense"/"crime",
        # which Mystery claims first.
        "Thriller",
        ("thriller", "espionage", "spy", "assassin", "conspiracy"),
    ),
    (
        "Romance",
        (
            "romance", "bridget jones", "romantic", "chick lit",
            "harlequin", "courtship", "true love", "love story",
        ),
    ),
    (
        "Horror",
        (
            "horror", "stephen king", "ghost", "haunting", "terror", "creepy",
            "supernatural", "paranormal", "vampire", "zombie", "werewolf",
            "dracula", "frankenstein", "lovecraft",
        ),
    ),
    (
        "Young Adult",
        (
            "young adult", "teen fiction", "teen", "hunger games", "divergent",
            "ya fantasy", "coming of age",
        ),
    ),
    (
        "Children",
        (
            "children", "childrens", "picture book", "dr. seuss", "dr seuss",
            "curious george", "winnie-the-pooh", "winnie the pooh", "kids",
            "early reader", "bedtime", "fairy tale", "mother goose",
            "charlotte's web", "matilda", "paddington", "peter rabbit",
        ),
    ),
    (
        "Biography",
        (
            # "life of" / "story of" / "my life" were removed: they are far too
            # greedy on fiction ("Life of Pi" -> Biography). These remaining
            # terms are specific enough to be reliable.
            "biography", "autobiography", "memoir", "memoirs", "biographical",
            "journals", "diaries", "an autobiography", "a memoir",
        ),
    ),
    (
        "History",
        (
            "history", "historical", "civilization", "ancient", "world war",
            "middle ages", "renaissance", "revolution", "empire", "crusade",
            "that changed the world", "chronicle of",
        ),
    ),
    (
        "Adventure",
        ("adventure", "quest", "expedition", "exploration", "treasure island", "castaway"),
    ),
    (
        "Self Help",
        (
            "self help", "self-help", "personal development", "motivation",
            "codependency", "habits", "how to win friends", "chicken soup",
            "getting better",
        ),
    ),
    (
        "Business",
        (
            "business", "leadership", "entrepreneurship", "economics", "finance",
            "investing", "marketing", "management", "startup",
        ),
    ),
    (
        "Philosophy",
        (
            "philosophy", "stoic", "existentialism", "ethics", "plato",
            "aristotle", "socrates", "meditations", "republic and other works",
        ),
    ),
    (
        "Religion",
        (
            "bible", "christian", "gospel", "devotional", "prophet", "prayer",
            "spiritual", "faith", "buddhism", "islam", "judaism", "quran",
        ),
    ),
)

# ---------------------------------------------------------------------------
# Publisher / imprint rules
# ---------------------------------------------------------------------------
#
# Specialist imprints publish essentially one category, so the publisher field
# recovers books whose titles carry no keyword at all. Matched as substrings
# against the lowercased publisher, since imprints appear with inconsistent
# suffixes ("Harlequin Books", "Harlequin Enterprises").
PUBLISHER_KEYWORDS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("Romance", ("harlequin", "silhouette", "mills & boon", "mills and boon", "zebra", "avon books", "leisure books")),
    ("Science Fiction", ("tor books", "del rey", "baen", "daw books", "ace books", "orbit", "roc books")),
    ("Children", ("scholastic", "puffin", "yearling", "disney press", "little golden")),
    ("Religion", ("zondervan", "tyndale", "bethany house", "thomas nelson", "baker books", "multnomah")),
    ("Mystery", ("mysterious press", "minotaur books")),
)


def _build_patterns() -> List[Tuple[str, Pattern[str]]]:
    """Compile one word-boundary alternation per category, preserving order."""
    compiled = []
    for category, keywords in CATEGORY_KEYWORDS:
        # re.escape each keyword so punctuation like "sci-fi" is literal.
        alternation = "|".join(re.escape(k) for k in keywords)
        compiled.append((category, re.compile(rf"\b(?:{alternation})\b")))
    return compiled


@lru_cache(maxsize=1)
def _title_patterns() -> List[Tuple[str, Pattern[str]]]:
    return _build_patterns()


@lru_cache(maxsize=1)
def _publisher_patterns() -> List[Tuple[str, Pattern[str]]]:
    compiled = []
    for category, keywords in PUBLISHER_KEYWORDS:
        alternation = "|".join(re.escape(k) for k in keywords)
        compiled.append((category, re.compile(alternation)))
    return compiled


def _as_text(value: object) -> str:
    """
    Coerce one catalog field to a lowercase string.

    Pandas represents missing string data as NaN (a float). `value or ""` does
    NOT guard against it, because NaN is truthy -- which previously produced
    `AttributeError: 'float' object has no attribute 'lower'` on books with a
    missing publisher. Explicitly treat null-like values as empty.
    """
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value).lower()
    text = str(value)
    # Guard against the literal "nan" that str() produces for np.nan.
    if text.lower() in ("nan", "none", "<na>"):
        return ""
    return text.lower()


def classify_genre(
    title: Optional[str],
    authors: Optional[str] = None,
    publisher: Optional[str] = None,
) -> Optional[str]:
    """
    Derive a single genre label for one book.

    Title/author keywords are consulted first because they are the most
    specific signal; the publisher imprint is the fallback. Returns None when
    nothing matches -- "unknown" is a real state, not a genre.

    Returns `None` rather than a synthetic "Other" bucket so that downstream
    code can distinguish "definitely no signal" from a genuine label.
    """
    title_text = _as_text(title)
    author_text = _as_text(authors)
    publisher_text = _as_text(publisher)

    text = f"{title_text} {author_text}".strip()

    if text:
        for category, pattern in _title_patterns():
            if pattern.search(text):
                return category

    if publisher_text:
        for category, pattern in _publisher_patterns():
            if pattern.search(publisher_text):
                return category

    return None


def add_genre_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a copy of `df` with a derived `genre` column.

    A pre-existing `genre` column is overwritten only where it is null, so any
    authoritative genre data added later takes precedence over this heuristic.
    """
    out = df.copy()

    titles = out["title"].tolist() if "title" in out.columns else [None] * len(out)
    authors = out["authors"].tolist() if "authors" in out.columns else [None] * len(out)
    publishers = (
        out["publisher"].tolist() if "publisher" in out.columns else [None] * len(out)
    )

    derived = [
        classify_genre(t, a, p)
        for t, a, p in zip(titles, authors, publishers)
    ]

    series = pd.Series(derived, index=out.index, dtype="object")

    if "genre" in out.columns:
        out["genre"] = out["genre"].where(out["genre"].notna(), series)
    else:
        out["genre"] = series

    return out