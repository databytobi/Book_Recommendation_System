import re
import pandas as pd
from typing import Optional, Union

def normalize_text(text: Union[str, float, None]) -> Optional[str]:
    """Normalize text by stripping whitespace and collapsing multiple spaces."""
    if pd.isna(text):
        return None
    
    # Convert to string and strip
    text = str(text).strip()
    
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    
    # Remove leading/trailing special characters
    text = text.strip(".,;:!?\"'")
    
    # Return None if empty after cleaning
    if not text:
        return None
    
    return text

def normalize_author(author: Union[str, float, None]) -> Optional[str]:
    """Normalize author names by cleaning and standardizing separators."""
    author = normalize_text(author)
    
    if author is None:
        return None
    
    # Replace slashes and other separators with commas
    author = author.replace("/", ", ")
    author = author.replace(";", ", ")
    author = author.replace("|", ", ")
    
    # Remove extra spaces after commas
    author = re.sub(r",\s+", ", ", author)
    
    # Capitalize first letter of each part (optional)
    parts = author.split(", ")
    parts = [part.strip().title() for part in parts]
    author = ", ".join(parts)
    
    return author

def clean_year(year: Union[str, int, float, None]) -> Optional[int]:
    """Clean and validate publication year."""
    try:
        # Convert to int
        year = int(float(str(year).strip()))
        
        # Check for reasonable range (books from 1450 to current year)
        if year < 1450 or year > 2026:
            return None
        
        return year
    
    except (ValueError, TypeError):
        return None

def clean_age(age: Union[str, int, float, None]) -> Optional[int]:
    """Clean and validate user age."""
    try:
        # Convert to int
        age = int(float(str(age).strip()))
        
        # Check for reasonable age range
        if age < 5 or age > 100:
            return None
        
        return age
    
    except (ValueError, TypeError):
        return None

def clean_isbn(isbn: Union[str, float, None]) -> Optional[str]:
    """Clean and standardize ISBN format."""
    if pd.isna(isbn):
        return None
    
    # Convert to string and clean
    isbn = str(isbn).strip().upper()
    
    # Remove any non-alphanumeric characters
    isbn = re.sub(r"[^0-9X]", "", isbn)
    
    # Remove ISBN prefix if present
    isbn = re.sub(r"^ISBN", "", isbn)
    
    # Return None if empty or invalid length
    if len(isbn) not in [10, 13]:
        return None
    
    return isbn

def clean_location(location: Union[str, float, None]) -> Optional[str]:
    """Clean and standardize location strings."""
    location = normalize_text(location)
    
    if location is None:
        return None
    
    # Convert to lowercase for consistency
    location = location.lower()
    
    # Standardize country names
    country_replacements = {
        r"\busa\b": "united states",
        r"\bu\.s\.a\.\b": "united states",
        r"\buk\b": "united kingdom",
        r"\bu\.k\.\b": "united kingdom",
        r"\bengland\b": "united kingdom",
    }
    
    for pattern, replacement in country_replacements.items():
        location = re.sub(pattern, replacement, location, flags=re.IGNORECASE)
    
    # Remove extra spaces
    location = re.sub(r"\s+", " ", location)
    
    return location

def clean_rating(rating: Union[str, int, float, None]) -> Optional[int]:
    """Clean and validate book rating."""
    try:
        # Convert to float first to handle decimals, then to int
        rating = float(str(rating).strip())
        rating = int(rating)
        
        # Check for valid rating range (0-10)
        if rating < 0 or rating > 10:
            return None
        
        return rating
    
    except (ValueError, TypeError):
        return None

# Example usage and testing
if __name__ == "__main__":
    # Test the cleaning functions
    test_data = {
        "text": "  Hello   World!  ",
        "author": "John / Jane Doe",
        "year": "2020",
        "age": "25",
        "isbn": "ISBN 978-3-16-148410-0",
        "location": "New York, NY, USA",
        "rating": "8.5"
    }
    
    print("Testing cleaning functions:")
    print(f"Original text: '{test_data['text']}' -> '{normalize_text(test_data['text'])}'")
    print(f"Original author: '{test_data['author']}' -> '{normalize_author(test_data['author'])}'")
    print(f"Original year: '{test_data['year']}' -> '{clean_year(test_data['year'])}'")
    print(f"Original age: '{test_data['age']}' -> '{clean_age(test_data['age'])}'")
    print(f"Original ISBN: '{test_data['isbn']}' -> '{clean_isbn(test_data['isbn'])}'")
    print(f"Original location: '{test_data['location']}' -> '{clean_location(test_data['location'])}'")
    print(f"Original rating: '{test_data['rating']}' -> '{clean_rating(test_data['rating'])}'")