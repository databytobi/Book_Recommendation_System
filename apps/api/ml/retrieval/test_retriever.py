# pyrefly: ignore [missing-import]
from faiss_retriever import retriever


print("\n")
print("=" * 60)
print("SEMANTIC SEARCH")
print("=" * 60)

results = retriever.search_books(
    "harry potter wizard magic",
    top_k=5
)

for i, book in enumerate(results, start=1):

    print(
        f"{i}. "
        f"{book['title']} "
        f"({book['score']:.4f})"
    )


print("\n")
print("=" * 60)
print("SIMILAR BOOKS")
print("=" * 60)

isbn = "043935806X"

results = retriever.similar_books(
    isbn,
    top_k=5
)

for i, book in enumerate(results, start=1):

    print(
        f"{i}. "
        f"{book['title']} "
        f"({book['score']:.4f})"
    )