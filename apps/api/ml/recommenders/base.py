
from abc import ABC, abstractmethod
from typing import Optional, Union, List, Dict, Any
from pathlib import Path
import pandas as pd

class BaseRecommender(ABC):
    """
    Base recommender interface.
    
    All recommenders in the system must inherit from this class.
    This abstract base class defines the contract that all recommendation
    algorithms must follow.
    
    Attributes
    ----------
    model : Any
        The trained model object
    is_fitted : bool
        Flag indicating whether the model has been trained
    """
    
    def __init__(self):
        """Initialize the base recommender."""
        self.model = None
        self.is_fitted = False
    
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> None:
        """
        Train recommender on dataset.
        
        Parameters
        ----------
        data : pd.DataFrame
            The training dataset containing user-item interactions.
            Expected columns: user_id, item_id, rating (optional)
        
        Raises
        ------
        ValueError
            If the data is empty or missing required columns
        """
        pass
    
    @abstractmethod
    def recommend(
        self,
        user_id: Optional[int] = None,
        item_id: Optional[str] = None,
        top_k: int = 10,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate recommendations.
        
        Parameters
        ----------
        user_id : int, optional
            User identifier for user-based recommendations.
            If provided, generates personalized recommendations.
            
        item_id : str, optional
            Book ISBN for item-based recommendations.
            If provided, generates similar item recommendations.
            
        top_k : int, default=10
            Number of recommendations to return.
            
        **kwargs
            Additional algorithm-specific parameters.
        
        Returns
        -------
        pd.DataFrame
            DataFrame containing top-K recommendations with columns:
            - item_id: Recommended book ISBN
            - score: Recommendation score or predicted rating
            - rank: Ranking position (1 to top_k)
        
        Raises
        ------
        ValueError
            If neither user_id nor item_id is provided
        RuntimeError
            If the model hasn't been fitted yet
        """
        pass
    
    @abstractmethod
    def save_model(self, path: Union[str, Path]) -> None:
        """
        Save trained recommender to disk.
        
        Parameters
        ----------
        path : str or Path
            File path where the model will be saved.
            Should include the file extension (e.g., .pkl, .joblib).
        
        Raises
        ------
        RuntimeError
            If the model hasn't been fitted yet
        IOError
            If unable to write to the specified path
        """
        pass
    
    @abstractmethod
    def load_model(self, path: Union[str, Path]) -> None:
        """
        Load trained recommender from disk.
        
        Parameters
        ----------
        path : str or Path
            File path from which to load the model.
        
        Raises
        ------
        FileNotFoundError
            If the specified file doesn't exist
        IOError
            If unable to read from the specified path
        """
        pass
    
    def get_recommendations_batch(
        self,
        user_ids: List[int],
        top_k: int = 10
    ) -> Dict[int, pd.DataFrame]:
        """
        Generate recommendations for multiple users.
        
        Parameters
        ----------
        user_ids : List[int]
            List of user IDs to generate recommendations for.
        top_k : int, default=10
            Number of recommendations per user.
        
        Returns
        -------
        Dict[int, pd.DataFrame]
            Dictionary mapping user_id to their recommendations DataFrame.
        """
        results = {}
        for user_id in user_ids:
            results[user_id] = self.recommend(user_id=user_id, top_k=top_k)
        return results
    
    def __repr__(self) -> str:
        """String representation of the recommender."""
        return f"{self.__class__.__name__}(is_fitted={self.is_fitted})"

