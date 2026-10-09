| Risk              | Impact | Solution              |
| ----------------- | ------ | --------------------- |
| Deployment issues | High   | Test early            |
| API bugs          | Medium | Add integration tests |
| Performance       | High   | Profile endpoints     |


hy is genre null?

You probably noticed this:

"genre": null

This is not a bug.

The Book-Crossing dataset doesn't contain a genre column. During your semantic integration, many books were enriched with ratings and language, but genre metadata was largely unavailable.

Your recommender still works because it relies on:

Author

Semantic embeddings

Popularity

Reading style

Later, we can enrich genres from Goodreads or Open Library.