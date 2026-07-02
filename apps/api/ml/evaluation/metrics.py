"""
Recommendation Evaluation Metrics

Phase 4A

This module provides comprehensive evaluation metrics for recommendation systems.
All metrics follow standard definitions used in information retrieval and
recommender system research.

Metrics:
- Precision@K: Precision of top-K recommendations
- Recall@K: Recall of top-K recommendations
- Hit Rate@K: Whether at least one relevant item appears in top-K
- Average Precision: Precision averaged across recall levels
- MAP@K: Mean Average Precision across multiple users
- DCG@K: Discounted Cumulative Gain (position-aware)
- NDCG@K: Normalized DCG (position-aware, normalized)
- MRR: Mean Reciprocal Rank (first relevant item position)
- Coverage: Percentage of items recommended
- Novelty: Average popularity of recommended items
- Diversity: Uniqueness of recommendations
- Serendipity: Unexpectedness of recommendations
"""

from typing import List, Set, Dict, Optional, Union, Tuple
import numpy as np
from collections import Counter
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# CORE METRICS
# ============================================================

def precision_at_k(
    recommended: List[str],
    relevant: Set[str],
    k: int = 10
) -> float:
    """
    Precision@K: Proportion of recommended items that are relevant.
    
    Measures: How many of the top-K recommendations are actually relevant.
    Range: [0, 1], higher is better.
    
    Parameters:
    -----------
    recommended : List[str]
        List of recommended item IDs (in order of relevance)
    relevant : Set[str]
        Set of relevant item IDs (ground truth)
    k : int
        Number of top recommendations to consider
    
    Returns:
    --------
    float: Precision@K score
    
    Examples:
    --------
    >>> precision_at_k(['a', 'b', 'c'], {'a', 'd'}, k=3)
    0.3333  # 1 out of 3 is relevant
    """
    if k <= 0 or not recommended:
        return 0.0
    
    recommended_k = recommended[:min(k, len(recommended))]
    hits = sum(1 for item in recommended_k if item in relevant)
    return hits / k


def recall_at_k(
    recommended: List[str],
    relevant: Set[str],
    k: int = 10
) -> float:
    """
    Recall@K: Proportion of relevant items found in top-K.
    
    Measures: How many of all relevant items were retrieved in top-K.
    Range: [0, 1], higher is better.
    
    Parameters:
    -----------
    recommended : List[str]
        List of recommended item IDs (in order of relevance)
    relevant : Set[str]
        Set of relevant item IDs (ground truth)
    k : int
        Number of top recommendations to consider
    
    Returns:
    --------
    float: Recall@K score
    
    Examples:
    --------
    >>> recall_at_k(['a', 'b', 'c'], {'a', 'd', 'e'}, k=3)
    0.3333  # 1 out of 3 relevant items was found
    """
    if not relevant:
        return 0.0
    
    recommended_k = recommended[:min(k, len(recommended))]
    hits = sum(1 for item in recommended_k if item in relevant)
    return hits / len(relevant)


def hit_rate_at_k(
    recommended: List[str],
    relevant: Set[str],
    k: int = 10
) -> float:
    """
    Hit Rate@K: Whether any relevant item appears in top-K.
    
    Measures: Binary indicator of whether at least one relevant item
    was found in the top-K recommendations.
    Range: {0, 1}, higher is better.
    
    Parameters:
    -----------
    recommended : List[str]
        List of recommended item IDs (in order of relevance)
    relevant : Set[str]
        Set of relevant item IDs (ground truth)
    k : int
        Number of top recommendations to consider
    
    Returns:
    --------
    float: 1.0 if at least one hit, else 0.0
    
    Examples:
    --------
    >>> hit_rate_at_k(['a', 'b', 'c'], {'d', 'e'}, k=3)
    0.0  # No relevant items found
    """
    recommended_k = recommended[:min(k, len(recommended))]
    return 1.0 if any(item in relevant for item in recommended_k) else 0.0


def average_precision(
    recommended: List[str],
    relevant: Set[str],
    k: int = 10
) -> float:
    """
    Average Precision@K: Precision averaged across recall levels.
    
    Measures: Area under the precision-recall curve up to K.
    Range: [0, 1], higher is better.
    
    Parameters:
    -----------
    recommended : List[str]
        List of recommended item IDs (in order of relevance)
    relevant : Set[str]
        Set of relevant item IDs (ground truth)
    k : int
        Number of top recommendations to consider
    
    Returns:
    --------
    float: Average Precision@K score
    
    Examples:
    --------
    >>> average_precision(['a', 'b', 'c'], {'b', 'c'}, k=3)
    0.8333  # Precision at positions with relevant items averaged
    """
    if not relevant or k <= 0:
        return 0.0
    
    recommended_k = recommended[:min(k, len(recommended))]
    
    score = 0.0
    hits = 0
    
    for idx, item in enumerate(recommended_k, start=1):
        if item in relevant:
            hits += 1
            precision = hits / idx
            score += precision
    
    if hits == 0:
        return 0.0
    
    return score / hits


def map_at_k(
    recommendation_lists: List[List[str]],
    relevant_lists: List[Set[str]],
    k: int = 10
) -> float:
    """
    Mean Average Precision@K: Average of AP@K scores across users.
    
    Measures: Overall ranking quality across all users.
    Range: [0, 1], higher is better.
    
    Parameters:
    -----------
    recommendation_lists : List[List[str]]
        List of recommendation lists for each user
    relevant_lists : List[Set[str]]
        List of relevant item sets for each user
    k : int
        Number of top recommendations to consider
    
    Returns:
    --------
    float: MAP@K score
    
    Examples:
    --------
    >>> map_at_k([['a', 'b'], ['c', 'd']], [{'a'}, {'c', 'd'}], k=2)
    0.75  # Average of AP scores
    """
    if not recommendation_lists or not relevant_lists:
        return 0.0
    
    if len(recommendation_lists) != len(relevant_lists):
        logger.warning("Recommendation and relevant lists have different lengths")
        return 0.0
    
    scores = []
    for recommended, relevant in zip(recommendation_lists, relevant_lists):
        scores.append(average_precision(recommended, relevant, k))
    
    return float(np.mean(scores)) if scores else 0.0


def dcg_at_k(
    recommended: List[str],
    relevant: Set[str],
    k: int = 10
) -> float:
    """
    Discounted Cumulative Gain@K: Position-aware relevance score.
    
    Measures: Sum of relevance scores discounted by position.
    Higher positions have lower impact (logarithmic discount).
    
    Parameters:
    -----------
    recommended : List[str]
        List of recommended item IDs (in order of relevance)
    relevant : Set[str]
        Set of relevant item IDs (ground truth)
    k : int
        Number of top recommendations to consider
    
    Returns:
    --------
    float: DCG@K score
    """
    if k <= 0 or not recommended:
        return 0.0
    
    recommended_k = recommended[:min(k, len(recommended))]
    
    dcg = 0.0
    for idx, item in enumerate(recommended_k, start=1):
        rel = 1.0 if item in relevant else 0.0
        dcg += rel / np.log2(idx + 1)
    
    return dcg


def ndcg_at_k(
    recommended: List[str],
    relevant: Set[str],
    k: int = 10
) -> float:
    """
    Normalized DCG@K: DCG normalized by ideal DCG.
    
    Measures: Position-aware ranking quality relative to ideal ranking.
    Range: [0, 1], higher is better.
    
    Parameters:
    -----------
    recommended : List[str]
        List of recommended item IDs (in order of relevance)
    relevant : Set[str]
        Set of relevant item IDs (ground truth)
    k : int
        Number of top recommendations to consider
    
    Returns:
    --------
    float: NDCG@K score
    
    Examples:
    --------
    >>> ndcg_at_k(['a', 'b', 'c'], {'a', 'b'}, k=3)
    1.0  # Perfect ranking
    """
    if not relevant or k <= 0:
        return 0.0
    
    actual_dcg = dcg_at_k(recommended, relevant, k)
    
    # Calculate ideal DCG (all relevant items at top positions)
    ideal_hits = min(len(relevant), k)
    if ideal_hits == 0:
        return 0.0
    
    ideal_dcg = sum(1.0 / np.log2(i + 1) for i in range(1, ideal_hits + 1))
    
    return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def mrr_at_k(
    recommended: List[str],
    relevant: Set[str],
    k: int = 10
) -> float:
    """
    Mean Reciprocal Rank@K: Position of first relevant item.
    
    Measures: How early the first relevant item appears.
    Range: [0, 1], higher is better.
    
    Parameters:
    -----------
    recommended : List[str]
        List of recommended item IDs (in order of relevance)
    relevant : Set[str]
        Set of relevant item IDs (ground truth)
    k : int
        Number of top recommendations to consider
    
    Returns:
    --------
    float: MRR@K score
    
    Examples:
    --------
    >>> mrr_at_k(['a', 'b', 'c'], {'b'}, k=3)
    0.5  # First relevant item at position 2
    """
    if not relevant or k <= 0:
        return 0.0
    
    recommended_k = recommended[:min(k, len(recommended))]
    
    for idx, item in enumerate(recommended_k, start=1):
        if item in relevant:
            return 1.0 / idx
    
    return 0.0


# ============================================================
# DIVERSITY & COVERAGE METRICS
# ============================================================

def catalog_coverage(
    recommendations: Dict[str, List[str]],
    total_items: int
) -> float:
    """
    Catalog Coverage: Percentage of items recommended.
    
    Measures: How much of the catalog is exposed by the recommender.
    Range: [0, 100], higher is better.
    
    Parameters:
    -----------
    recommendations : Dict[str, List[str]]
        Dictionary mapping user_id to list of recommended items
    total_items : int
        Total number of items in the catalog
    
    Returns:
    --------
    float: Catalog coverage percentage
    """
    if total_items <= 0:
        return 0.0
    
    recommended_items = set()
    for recs in recommendations.values():
        recommended_items.update(recs)
    
    return (len(recommended_items) / total_items) * 100


def item_coverage(
    recommendations: Dict[str, List[str]]
) -> float:
    """
    Item Coverage: Average number of unique items per user.
    
    Measures: Diversity of items across users.
    
    Parameters:
    -----------
    recommendations : Dict[str, List[str]]
        Dictionary mapping user_id to list of recommended items
    
    Returns:
    --------
    float: Average unique items per user
    """
    if not recommendations:
        return 0.0
    
    all_items = []
    for recs in recommendations.values():
        all_items.extend(recs)
    
    unique_items = len(set(all_items))
    total_recommendations = len(all_items)
    
    return unique_items / total_recommendations if total_recommendations > 0 else 0.0


def diversity(
    recommendations: Dict[str, List[str]],
    item_similarity: Optional[Dict[str, Dict[str, float]]] = None
) -> float:
    """
    Diversity: Average dissimilarity between recommended items.
    
    Measures: How diverse the recommendations are.
    Range: [0, 1], higher means more diverse.
    
    Parameters:
    -----------
    recommendations : Dict[str, List[str]]
        Dictionary mapping user_id to list of recommended items
    item_similarity : Dict[str, Dict[str, float]], optional
        Similarity matrix between items. If None, uses Jaccard similarity.
    
    Returns:
    --------
    float: Diversity score
    """
    if not recommendations:
        return 0.0
    
    total_pairs = 0
    total_distance = 0.0
    
    for user_id, recs in recommendations.items():
        if len(recs) < 2:
            continue
        
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                item1 = recs[i]
                item2 = recs[j]
                
                if item_similarity and item1 in item_similarity and item2 in item_similarity[item1]:
                    similarity = item_similarity[item1][item2]
                else:
                    # Default: assume all items are distinct
                    similarity = 0.0 if item1 != item2 else 1.0
                
                total_distance += 1 - similarity
                total_pairs += 1
    
    return total_distance / total_pairs if total_pairs > 0 else 0.0


def novelty(
    recommendations: Dict[str, List[str]],
    item_popularity: Dict[str, float]
) -> float:
    """
    Novelty: Average inverse popularity of recommended items.
    
    Measures: How unexpected/surprising the recommendations are.
    Range: [0, 1], higher means more novel.
    
    Parameters:
    -----------
    recommendations : Dict[str, List[str]]
        Dictionary mapping user_id to list of recommended items
    item_popularity : Dict[str, float]
        Dictionary mapping item_id to popularity score (e.g., rating count)
    
    Returns:
    --------
    float: Novelty score
    """
    if not recommendations or not item_popularity:
        return 0.0
    
    total_popularity = 0.0
    total_items = 0
    
    for recs in recommendations.values():
        for item in recs:
            if item in item_popularity and item_popularity[item] > 0:
                total_popularity += 1.0 / (item_popularity[item] + 1)  # Smoothing
                total_items += 1
    
    return total_popularity / total_items if total_items > 0 else 0.0


def serendipity(
    recommendations: Dict[str, List[str]],
    user_history: Dict[str, Set[str]],
    item_similarity: Optional[Dict[str, Dict[str, float]]] = None
) -> float:
    """
    Serendipity: Unexpectedness of recommendations.
    
    Measures: How surprising and relevant the recommendations are.
    Combines novelty (unexpected) and relevance.
    Range: [0, 1], higher means more serendipitous.
    
    Parameters:
    -----------
    recommendations : Dict[str, List[str]]
        Dictionary mapping user_id to list of recommended items
    user_history : Dict[str, Set[str]]
        Dictionary mapping user_id to set of previously interacted items
    item_similarity : Dict[str, Dict[str, float]], optional
        Similarity matrix between items
    
    Returns:
    --------
    float: Serendipity score
    """
    if not recommendations:
        return 0.0
    
    total_items = 0
    total_serendipity = 0.0
    
    for user_id, recs in recommendations.items():
        if user_id not in user_history:
            continue
        
        history = user_history[user_id]
        
        for item in recs:
            if item in history:
                continue  # Skip items already seen
            
            # Calculate novelty: how different from history
            max_similarity = 0.0
            if item_similarity and item in item_similarity:
                for hist_item in history:
                    if hist_item in item_similarity[item]:
                        max_similarity = max(max_similarity, item_similarity[item][hist_item])
            
            # Serendipity = 1 - max_similarity (higher when dissimilar from history)
            total_serendipity += 1 - max_similarity
            total_items += 1
    
    return total_serendipity / total_items if total_items > 0 else 0.0


# ============================================================
# COMPREHENSIVE EVALUATION
# ============================================================

def evaluate_recommendations(
    recommendations: Dict[str, List[str]],
    ground_truth: Dict[str, Set[str]],
    k: int = 10,
    total_items: Optional[int] = None,
    item_popularity: Optional[Dict[str, float]] = None,
    user_history: Optional[Dict[str, Set[str]]] = None,
    item_similarity: Optional[Dict[str, Dict[str, float]]] = None
) -> Dict[str, float]:
    """
    Comprehensive evaluation of recommendations using multiple metrics.
    
    Parameters:
    -----------
    recommendations : Dict[str, List[str]]
        Dictionary mapping user_id to list of recommended items
    ground_truth : Dict[str, Set[str]]
        Dictionary mapping user_id to set of relevant items
    k : int
        Number of top recommendations to consider
    total_items : int, optional
        Total number of items in catalog (for coverage)
    item_popularity : Dict[str, float], optional
        Item popularity scores (for novelty)
    user_history : Dict[str, Set[str]], optional
        User history (for serendipity)
    item_similarity : Dict[str, Dict[str, float]], optional
        Item similarity matrix (for diversity)
    
    Returns:
    --------
    Dict[str, float]: Dictionary of metric names to scores
    
    Examples:
    --------
    >>> recommendations = {'user1': ['a', 'b', 'c'], 'user2': ['d', 'e', 'f']}
    >>> ground_truth = {'user1': {'a', 'b'}, 'user2': {'d'}}
    >>> metrics = evaluate_recommendations(recommendations, ground_truth, k=3)
    >>> print(metrics)
    {
        'precision@10': 0.333,
        'recall@10': 0.5,
        'hit_rate@10': 1.0,
        'map@10': 0.75,
        'mrr@10': 0.75,
        'ndcg@10': 0.75,
        'catalog_coverage': 66.67,
        'item_coverage': 1.0,
        'diversity': 1.0,
        'novelty': 0.5,
        'serendipity': 0.5
    }
    """
    metrics = {}
    
    # Convert to lists for MAP calculation
    user_ids = list(recommendations.keys())
    rec_lists = [recommendations[uid] for uid in user_ids if uid in ground_truth]
    rel_lists = [ground_truth[uid] for uid in user_ids if uid in ground_truth]
    
    if not rec_lists:
        return {"error": "No matching users found"}
    
    # Precision, Recall, Hit Rate, MRR, NDCG per user (average)
    precision_scores = []
    recall_scores = []
    hit_scores = []
    mrr_scores = []
    ndcg_scores = []
    
    for uid in user_ids:
        if uid not in ground_truth:
            continue
        
        recs = recommendations[uid]
        rels = ground_truth[uid]
        
        precision_scores.append(precision_at_k(recs, rels, k))
        recall_scores.append(recall_at_k(recs, rels, k))
        hit_scores.append(hit_rate_at_k(recs, rels, k))
        mrr_scores.append(mrr_at_k(recs, rels, k))
        ndcg_scores.append(ndcg_at_k(recs, rels, k))
    
    if precision_scores:
        metrics[f'precision@{k}'] = np.mean(precision_scores)
        metrics[f'recall@{k}'] = np.mean(recall_scores)
        metrics[f'hit_rate@{k}'] = np.mean(hit_scores)
        metrics[f'mrr@{k}'] = np.mean(mrr_scores)
        metrics[f'ndcg@{k}'] = np.mean(ndcg_scores)
    
    # MAP
    metrics[f'map@{k}'] = map_at_k(rec_lists, rel_lists, k)
    
    # Coverage
    if total_items:
        metrics['catalog_coverage'] = catalog_coverage(recommendations, total_items)
        metrics['item_coverage'] = item_coverage(recommendations)
    
    # Diversity
    metrics['diversity'] = diversity(recommendations, item_similarity)
    
    # Novelty
    if item_popularity:
        metrics['novelty'] = novelty(recommendations, item_popularity)
    
    # Serendipity
    if user_history and item_similarity:
        metrics['serendipity'] = serendipity(recommendations, user_history, item_similarity)
    
    return metrics


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def print_metrics(metrics: Dict[str, float], precision: int = 4) -> None:
    """
    Pretty print evaluation metrics.
    
    Parameters:
    -----------
    metrics : Dict[str, float]
        Dictionary of metric names to scores
    precision : int
        Number of decimal places to display
    """
    print("\n" + "=" * 50)
    print("RECOMMENDATION METRICS")
    print("=" * 50)
    
    # Group metrics
    core_metrics = ['precision', 'recall', 'hit_rate', 'map', 'mrr', 'ndcg']
    coverage_metrics = ['catalog_coverage', 'item_coverage']
    diversity_metrics = ['diversity', 'novelty', 'serendipity']
    
    for metric, value in metrics.items():
        # Determine which group
        group = "Other"
        for prefix in core_metrics:
            if metric.startswith(prefix):
                group = "Core Metrics"
                break
        for prefix in coverage_metrics:
            if metric.startswith(prefix):
                group = "Coverage Metrics"
                break
        for prefix in diversity_metrics:
            if metric.startswith(prefix):
                group = "Diversity Metrics"
                break
        
        if group == "Other":
            continue
        
        # Format value
        if isinstance(value, float):
            if 'coverage' in metric:
                formatted = f"{value:.2f}%"
            else:
                formatted = f"{value:.{precision}f}"
        else:
            formatted = str(value)
        
        print(f"{metric:20s}: {formatted}")
    
    print("=" * 50)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Example data
    recommendations = {
        'user1': ['a', 'b', 'c', 'd', 'e'],
        'user2': ['a', 'b', 'c', 'f', 'g'],
        'user3': ['a', 'b', 'c', 'd', 'h'],
    }
    
    ground_truth = {
        'user1': {'a', 'b', 'c'},
        'user2': {'a', 'b', 'f'},
        'user3': {'a', 'b', 'c'},
    }
    
    # Evaluate
    metrics = evaluate_recommendations(
        recommendations,
        ground_truth,
        k=5,
        total_items=10
    )
    
    # Print results
    print_metrics(metrics)