"""
Recommendation API Routes

This module defines the API endpoints for the recommendation system.
Includes endpoints for user recommendations, similar books, semantic search,
trending books, and admin operations.

Phase: API Routes
"""

import logging
import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np

# FIXED: Correct import paths
from app.api.v1.recommendation.schemas import (
    RecommendationRequest,
    SimilarBookRequest,
    SearchRequest,
    TrendingRequest,
    WeightsUpdateRequest,
    RecommendationResponse,
    SimilarBooksResponse,
    SearchResponse,
    TrendingResponse,
    ErrorResponse,
    BookRecommendation,
    create_recommendation_response,
    create_error_response
)

# FIXED: Correct import paths for dependencies
from app.api.v1.recommendation.dependencies import (
    get_hybrid_recommender,
    get_health_status,
    get_recommender_stats,
    reload_hybrid_recommender
)

# ============================================================
# MONITORING IMPORTS - ADD THESE
# ============================================================

from app.services.recommendation_metrics import (
    track_endpoint,
    track_recommendations,
    record_recommendation
)
from app.services.monitoring import log_recommendation
from app.services.recommendation_monitor import get_monitor

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/recommendation",
    tags=["recommendations"]
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_int(value) -> Optional[int]:
    """
    Safely convert a value to int, handling NaN and None.
    """
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    return None


def safe_float(value) -> Optional[float]:
    """
    Safely convert a value to float, handling NaN and None.
    """
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_str(value) -> str:
    """
    Safely convert a value to string, handling NaN and None.
    """
    if value is None:
        return ""
    if isinstance(value, float) and np.isnan(value):
        return ""
    return str(value)


# ============================================================
# ERROR HANDLING
# ============================================================

def handle_exception(e: Exception, endpoint: str = "unknown") -> HTTPException:
    """
    Handle exceptions and return appropriate HTTP exceptions.
    """
    logger.error(f"Error in {endpoint}: {str(e)}", exc_info=True)
    
    if isinstance(e, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    elif isinstance(e, KeyError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found: {str(e)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# ============================================================
# USER RECOMMENDATIONS
# ============================================================

@router.post(
    "/user",
    response_model=RecommendationResponse,
    summary="Get user recommendations",
    description="Generate personalized recommendations for a specific user"
)
@track_endpoint("/api/v1/recommendation/user", "POST")
@track_recommendations("user")
async def recommend_for_user(
    request: RecommendationRequest,
    recommender = Depends(get_hybrid_recommender),
) -> RecommendationResponse:
    """
    Generate personalized recommendations for a user.
    """
    start_time = time.time()
    user_id = str(request.user_id)
    
    try:
        logger.info(f"Generating recommendations for user {request.user_id}")
        
        # Get recommendations
        recommendations = recommender.recommend_for_user(
            user_id=request.user_id,
            top_k=request.top_k,
            min_score=request.min_score if hasattr(request, 'min_score') else 0.0,
            exclude_authors=request.exclude_authors if hasattr(request, 'exclude_authors') else None
        )
        
        # Calculate processing time
        duration_ms = (time.time() - start_time) * 1000
        count = len(recommendations) if not recommendations.empty else 0
        
        # Calculate average score
        avg_score = 0.0
        if not recommendations.empty and 'score' in recommendations.columns:
            avg_score = recommendations['score'].mean()
        
        # Log to monitoring
        log_recommendation(
            user_id=user_id,
            recommendation_type="user",
            count=count,
            duration_ms=duration_ms,
            status="success"
        )
        
        # Record to monitor
        monitor = get_monitor()
        monitor.record_recommendation(
            rec_type="user",
            count=count,
            score=avg_score,
            latency_ms=duration_ms,
            cache_hit=False,
            user_id=user_id
        )
        
        # Record to Prometheus metrics
        record_recommendation(
            rec_type="user",
            count=count,
            duration=duration_ms / 1000,  # Convert to seconds
            status="success"
        )
        
        # Convert to response format
        if recommendations.empty:
            return RecommendationResponse(
                count=0,
                recommendations=[],
                user_id=request.user_id,
                recommender_type="hybrid",
                processing_time_ms=duration_ms
            )
        
        return create_recommendation_response(
            recommendations=recommendations.to_dict(orient="records"),
            user_id=request.user_id,
            recommender_type="hybrid",
            processing_time_ms=duration_ms
        )
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        # Log error to monitoring
        log_recommendation(
            user_id=user_id,
            recommendation_type="user",
            count=0,
            duration_ms=duration_ms,
            status="error",
            error=str(e)
        )
        
        # Record error to Prometheus
        record_recommendation(
            rec_type="user",
            count=0,
            duration=duration_ms / 1000,
            status="error"
        )
        
        raise handle_exception(e, "recommend_for_user")


@router.get(
    "/user/{user_id}",
    response_model=RecommendationResponse,
    summary="Get user recommendations (GET)",
    description="Alternative GET endpoint for user recommendations"
)
@track_endpoint("/api/v1/recommendation/user", "GET")
async def recommend_for_user_get(
    user_id: int = Path(..., description="User ID", gt=0),
    top_k: int = Query(10, description="Number of recommendations", ge=1, le=100),
    recommender = Depends(get_hybrid_recommender),
) -> RecommendationResponse:
    """
    GET endpoint for user recommendations.
    """
    request = RecommendationRequest(user_id=user_id, top_k=top_k)
    return await recommend_for_user(request, recommender)


# ============================================================
# SIMILAR BOOKS
# ============================================================

@router.post(
    "/similar",
    response_model=SimilarBooksResponse,
    summary="Find similar books",
    description="Find books similar to a given ISBN"
)
@track_endpoint("/api/v1/recommendation/similar", "POST")
@track_recommendations("similar")
async def similar_books(
    request: SimilarBookRequest,
    recommender = Depends(get_hybrid_recommender),
) -> SimilarBooksResponse:
    """
    Find books similar to a given ISBN.
    """
    start_time = time.time()
    isbn = request.isbn
    
    try:
        logger.info(f"Finding similar books for ISBN: {request.isbn}")
        
        # Get similar books
        recommendations = recommender.recommend_similar_books(
            isbn=request.isbn,
            top_k=request.top_k,
            min_score=request.min_similarity if hasattr(request, 'min_similarity') else 0.0
        )
        
        # Calculate processing time
        duration_ms = (time.time() - start_time) * 1000
        count = len(recommendations) if not recommendations.empty else 0
        
        # Calculate average score
        avg_score = 0.0
        if not recommendations.empty and 'score' in recommendations.columns:
            avg_score = recommendations['score'].mean()
        
        # Log to monitoring
        log_recommendation(
            user_id=isbn,
            recommendation_type="similar",
            count=count,
            duration_ms=duration_ms,
            status="success",
            isbn=isbn
        )
        
        # Record to monitor
        monitor = get_monitor()
        monitor.record_recommendation(
            rec_type="similar",
            count=count,
            score=avg_score,
            latency_ms=duration_ms,
            cache_hit=False,
            isbn=isbn
        )
        
        # Record to Prometheus metrics
        record_recommendation(
            rec_type="similar",
            count=count,
            duration=duration_ms / 1000,
            status="success"
        )
        
        # Get query book info
        query_title = None
        try:
            if hasattr(recommender, 'content_service'):
                book_info = recommender.content_service.get_book_info(request.isbn)
                if book_info:
                    query_title = book_info.get('title')
        except Exception as e:
            logger.debug(f"Could not get query book info: {e}")
        
        # Convert to response format
        if recommendations.empty:
            return SimilarBooksResponse(
                query_isbn=request.isbn,
                query_title=query_title,
                count=0,
                similar_books=[]
            )
        
        books = []
        for _, row in recommendations.iterrows():
            publication_year = safe_int(row.get('publication_year'))
            isbn_val = safe_str(row.get('isbn', ''))
            title = safe_str(row.get('title', 'Unknown'))
            author = safe_str(row.get('authors'))
            publisher = safe_str(row.get('publisher'))
            category = safe_str(row.get('category'))
            
            score = row.get('score', 0.0) or row.get('similarity', 0.0)
            if isinstance(score, float) and np.isnan(score):
                score = 0.0
            
            books.append(
                BookRecommendation(
                    isbn=isbn_val,
                    title=title,
                    author=author if author else None,
                    publisher=publisher if publisher else None,
                    publication_year=publication_year,
                    category=category if category else None,
                    score=float(score)
                )
            )
        
        return SimilarBooksResponse(
            query_isbn=request.isbn,
            query_title=query_title,
            count=len(books),
            similar_books=books
        )
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        log_recommendation(
            user_id=isbn,
            recommendation_type="similar",
            count=0,
            duration_ms=duration_ms,
            status="error",
            error=str(e)
        )
        
        record_recommendation(
            rec_type="similar",
            count=0,
            duration=duration_ms / 1000,
            status="error"
        )
        
        raise handle_exception(e, "similar_books")


# ============================================================
# SEMANTIC SEARCH
# ============================================================

@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Semantic search",
    description="Search for books using natural language queries"
)
@track_endpoint("/api/v1/recommendation/search", "POST")
@track_recommendations("search")
async def semantic_search(
    request: SearchRequest,
    recommender = Depends(get_hybrid_recommender),
) -> SearchResponse:
    """
    Search for books using natural language queries.
    """
    start_time = time.time()
    query = request.query[:50]  # Truncate for logging
    
    try:
        logger.info(f"Semantic search for: '{request.query[:50]}...'")
        
        # Perform search
        results = recommender.search_and_recommend(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score if hasattr(request, 'min_score') else 0.0
        )
        
        # Calculate processing time
        duration_ms = (time.time() - start_time) * 1000
        count = len(results) if not results.empty else 0
        
        # Calculate average score
        avg_score = 0.0
        if not results.empty and 'score' in results.columns:
            avg_score = results['score'].mean()
        
        # Log to monitoring
        log_recommendation(
            user_id=f"search:{query}",
            recommendation_type="search",
            count=count,
            duration_ms=duration_ms,
            status="success",
            query=request.query
        )
        
        # Record to monitor
        monitor = get_monitor()
        monitor.record_recommendation(
            rec_type="search",
            count=count,
            score=avg_score,
            latency_ms=duration_ms,
            cache_hit=False,
            query=request.query
        )
        
        # Record to Prometheus metrics
        record_recommendation(
            rec_type="search",
            count=count,
            duration=duration_ms / 1000,
            status="success"
        )
        
        # Convert to response format
        if results.empty:
            return SearchResponse(
                query=request.query,
                count=0,
                results=[]
            )
        
        books = []
        for _, row in results.iterrows():
            publication_year = safe_int(row.get('publication_year'))
            isbn_val = safe_str(row.get('isbn', ''))
            title = safe_str(row.get('title', 'Unknown'))
            author = safe_str(row.get('authors'))
            publisher = safe_str(row.get('publisher'))
            category = safe_str(row.get('category'))
            
            score = row.get('score', 0.0) or row.get('similarity', 0.0) or row.get('hybrid_score', 0.0)
            if isinstance(score, float) and np.isnan(score):
                score = 0.0
            
            books.append(
                BookRecommendation(
                    isbn=isbn_val,
                    title=title,
                    author=author if author else None,
                    publisher=publisher if publisher else None,
                    publication_year=publication_year,
                    category=category if category else None,
                    score=float(score)
                )
            )
        
        return SearchResponse(
            query=request.query,
            count=len(books),
            results=books
        )
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        log_recommendation(
            user_id=f"search:{query}",
            recommendation_type="search",
            count=0,
            duration_ms=duration_ms,
            status="error",
            error=str(e)
        )
        
        record_recommendation(
            rec_type="search",
            count=0,
            duration=duration_ms / 1000,
            status="error"
        )
        
        raise handle_exception(e, "semantic_search")


# ============================================================
# TRENDING BOOKS (Add tracking here too)
# ============================================================

@router.get(
    "/trending",
    response_model=TrendingResponse,
    summary="Get trending books",
    description="Get popular and trending books"
)
@track_endpoint("/api/v1/recommendation/trending", "GET")
@track_recommendations("trending")
async def get_trending(
    top_k: int = Query(20, description="Number of trending books", ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category"),
    days: int = Query(30, description="Days to consider for trending", ge=1),
    recommender = Depends(get_hybrid_recommender),
) -> TrendingResponse:
    """
    Get trending books.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Getting trending books (top={top_k}, category={category})")
        
        # Get trending books
        trending = recommender.cold_start_recommendations(top_k=top_k)
        
        # Calculate processing time
        duration_ms = (time.time() - start_time) * 1000
        count = len(trending) if not trending.empty else 0
        
        # Calculate average score
        avg_score = 0.0
        if not trending.empty and 'adjusted_score' in trending.columns:
            avg_score = trending['adjusted_score'].mean()
        
        # Log to monitoring
        log_recommendation(
            user_id="trending",
            recommendation_type="trending",
            count=count,
            duration_ms=duration_ms,
            status="success"
        )
        
        # Record to monitor
        monitor = get_monitor()
        monitor.record_recommendation(
            rec_type="trending",
            count=count,
            score=avg_score,
            latency_ms=duration_ms,
            cache_hit=False
        )
        
        # Record to Prometheus metrics
        record_recommendation(
            rec_type="trending",
            count=count,
            duration=duration_ms / 1000,
            status="success"
        )
        
        # Filter by category if specified
        if category and 'category' in trending.columns:
            trending = trending[trending['category'].str.lower() == category.lower()]
            trending = trending.head(top_k)
        
        # Convert to response format
        if trending.empty:
            return TrendingResponse(
                period=f"Last {days} days",
                count=0,
                trending=[]
            )
        
        books = []
        for _, row in trending.iterrows():
            publication_year = safe_int(row.get('publication_year'))
            isbn_val = safe_str(row.get('isbn', ''))
            title = safe_str(row.get('title', 'Unknown'))
            author = safe_str(row.get('authors'))
            publisher = safe_str(row.get('publisher'))
            category_val = safe_str(row.get('category'))
            
            score = row.get('adjusted_score', 0.0) or row.get('score', 0.0)
            if isinstance(score, float) and np.isnan(score):
                score = 0.0
            
            books.append(
                BookRecommendation(
                    isbn=isbn_val,
                    title=title,
                    author=author if author else None,
                    publisher=publisher if publisher else None,
                    publication_year=publication_year,
                    category=category_val if category_val else None,
                    score=float(score)
                )
            )
        
        return TrendingResponse(
            period=f"Last {days} days",
            count=len(books),
            trending=books
        )
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        log_recommendation(
            user_id="trending",
            recommendation_type="trending",
            count=0,
            duration_ms=duration_ms,
            status="error",
            error=str(e)
        )
        
        record_recommendation(
            rec_type="trending",
            count=0,
            duration=duration_ms / 1000,
            status="error"
        )
        
        raise handle_exception(e, "get_trending")


# ============================================================
# RECOMMENDATION EXPLANATION
# ============================================================

@router.get(
    "/explain/{user_id}/{isbn}",
    summary="Explain a recommendation",
    description="Get an explanation for why a book was recommended"
)
async def explain_recommendation(
    user_id: int = Path(..., description="User ID", gt=0),
    isbn: str = Path(..., description="Book ISBN"),
    recommender = Depends(get_hybrid_recommender),
) -> Dict[str, Any]:
    """
    Explain why a specific book was recommended to a user.
    """
    try:
        logger.info(f"Explaining recommendation for user {user_id}, book {isbn}")
        
        # Get recommendations for the user
        recommendations = recommender.recommend_for_user(
            user_id=user_id,
            top_k=50
        )
        
        # Find the specific book
        book = recommendations[recommendations['isbn'] == isbn]
        
        if book.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book {isbn} not found in recommendations for user {user_id}"
            )
        
        # Extract explanation
        row = book.iloc[0]
        explanation = recommender.explain_recommendation(row)
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, "explain_recommendation")


# ============================================================
# HEALTH AND ADMIN
# ============================================================

@router.get(
    "/health",
    summary="Health check",
    description="Check the health of the recommendation service"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the recommendation service.
    """
    return get_health_status()


@router.get(
    "/stats",
    summary="Service statistics",
    description="Get statistics about the recommendation service"
)
async def get_stats() -> Dict[str, Any]:
    """
    Get statistics about the recommendation service.
    """
    return get_recommender_stats()


@router.post(
    "/reload",
    summary="Reload recommender",
    description="Reload the hybrid recommender (admin only)"
)
async def reload_recommender() -> Dict[str, str]:
    """
    Reload the hybrid recommender.
    """
    try:
        reload_hybrid_recommender()
        return {"status": "success", "message": "Recommender reloaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload recommender: {str(e)}"
        )


@router.put(
    "/weights",
    summary="Update recommendation weights",
    description="Update the hybrid recommender weights (admin only)"
)
async def update_weights(
    request: WeightsUpdateRequest,
    recommender = Depends(get_hybrid_recommender),
) -> Dict[str, Any]:
    """
    Update the recommendation weights for the hybrid recommender.
    """
    try:
        logger.info(f"Updating weights: {request.model_dump()}")
        
        # Update weights
        if hasattr(recommender, 'update_weights'):
            recommender.update_weights(
                collaborative_weight=request.collaborative_weight,
                content_weight=request.content_weight,
                popularity_weight=request.popularity_weight
            )
            return {
                "status": "success",
                "message": "Weights updated successfully",
                "weights": {
                    "collaborative": request.collaborative_weight,
                    "content": request.content_weight,
                    "popularity": request.popularity_weight
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Weight update not supported by this recommender"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_exception(e, "update_weights")


# ============================================================
# BATCH RECOMMENDATIONS
# ============================================================

@router.post(
    "/batch",
    summary="Batch recommendations",
    description="Get recommendations for multiple users"
)
async def batch_recommendations(
    user_ids: List[int] = Query(..., description="List of user IDs"),
    top_k: int = Query(10, description="Recommendations per user", ge=1, le=50),
    recommender = Depends(get_hybrid_recommender),
) -> Dict[str, Any]:
    """
    Get recommendations for multiple users in a single request.
    """
    try:
        logger.info(f"Batch recommendations for {len(user_ids)} users")
        
        results = {}
        errors = {}
        
        for user_id in user_ids:
            try:
                recommendations = recommender.recommend_for_user(
                    user_id=user_id,
                    top_k=top_k
                )
                
                if not recommendations.empty:
                    results[str(user_id)] = recommendations.to_dict(orient="records")
                else:
                    results[str(user_id)] = []
                    
            except Exception as e:
                logger.error(f"Error for user {user_id}: {e}")
                errors[str(user_id)] = str(e)
                results[str(user_id)] = []
        
        return {
            "total_users": len(user_ids),
            "successful": len(user_ids) - len(errors),
            "errors": errors if errors else None,
            "results": results
        }
        
    except Exception as e:
        raise handle_exception(e, "batch_recommendations")