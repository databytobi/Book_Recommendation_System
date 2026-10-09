from pathlib import Path
import pickle

import faiss
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize


BASE_DIR = Path(__file__).resolve().parents[1]

ARTIFACT_DIR = (
    BASE_DIR
    / "apps"
    / "api"
    / "ml"
    / "artifacts"
)

MODEL_NAME = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)


class FaissRetriever:
    """
    Production retrieval service.
    Loads artifacts once and serves search requests.
    """

    def __init__(self):

        self.books = None
        self.index = None
        self.metadata = None
        self.model = None

        self._load_artifacts()

    def _load_artifacts(self):

        print("=" * 60)
        print("LOADING RETRIEVAL ARTIFACTS")
        print("=" * 60)

        books_path = (
            ARTIFACT_DIR
            / "semantic_books.parquet"
        )

        index_path = (
            ARTIFACT_DIR
            / "books_faiss.index"
        )

        metadata_path = (
            ARTIFACT_DIR
            / "embedding_metadata.pkl"
        )

        self.books = pd.read_parquet(
            books_path
        )

        self.index = faiss.read_index(
            str(index_path)
        )

        with open(
            metadata_path,
            "rb"
        ) as file:
            self.metadata = pickle.load(
                file
            )

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        print(
            f"Books loaded: "
            f"{len(self.books):,}"
        )

        print(
            f"Vectors loaded: "
            f"{self.index.ntotal:,}"
        )

    def _embed_query(
        self,
        query: str
    ):

        embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        embedding = normalize(
            embedding,
            norm="l2"
        )

        return embedding.astype(
            "float32"
        )

    def search_books(
        self,
        query: str,
        top_k: int = 10
    ):

        query_embedding = (
            self._embed_query(query)
        )

        scores, indices = (
            self.index.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for idx, score in zip(
            indices[0],
            scores[0]
        ):

            if idx < 0:
                continue

            book = self.books.iloc[idx]

            results.append(
                {
                    "isbn": book["isbn"],
                    "title": book["title"],
                    "authors": book["authors"],
                    "publisher": book["publisher"],
                    "score": float(score)
                }
            )

        return results

    def similar_books(
        self,
        isbn: str,
        top_k: int = 10
    ):

        matches = self.books[
            self.books["isbn"] == isbn
        ]

        if matches.empty:
            return []

        book_index = matches.index[0]

        query_vector = (
            self.index.reconstruct(
                int(book_index)
            )
        )

        query_vector = np.expand_dims(
            query_vector,
            axis=0
        )

        scores, indices = (
            self.index.search(
                query_vector,
                top_k + 1
            )
        )

        results = []

        for idx, score in zip(
            indices[0],
            scores[0]
        ):

            if idx == book_index:
                continue

            book = self.books.iloc[idx]

            results.append(
                {
                    "isbn": book["isbn"],
                    "title": book["title"],
                    "authors": book["authors"],
                    "score": float(score)
                }
            )

        return results[:top_k]

    def recommend_by_book(
        self,
        isbn: str,
        top_k: int = 10
    ):

        return self.similar_books(
            isbn,
            top_k
        )


retriever = FaissRetriever()