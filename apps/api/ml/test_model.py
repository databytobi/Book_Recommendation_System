import pickle
from pathlib import Path

# Load the model
model_path = Path("apps/ml/models/popularity_recommender.pkl")
with open(model_path, "rb") as f:
    recommender = pickle.load(f)

# Get recommendations
recommendations = recommender.recommend(top_k=5)
print("Top 5 Recommendations:")
print(recommendations[['title', 'category', 'adjusted_score']])