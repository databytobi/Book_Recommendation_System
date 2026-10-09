"""
Artifact Validator

Validates that all required ML artifacts exist and are accessible.
Provides detailed error messages and guidance for missing files.

Phase: Core Validation
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class ArtifactInfo:
    """Information about an artifact."""
    name: str
    path: Path
    exists: bool
    size_bytes: Optional[int] = None
    last_modified: Optional[datetime] = None
    error: Optional[str] = None
    required: bool = True


@dataclass
class ValidationResult:
    """Result of artifact validation."""
    all_present: bool = False
    present: List[ArtifactInfo] = field(default_factory=list)
    missing: List[ArtifactInfo] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        missing_files=None,
        artifacts=None,
        errors=None,
        warnings=None
    ):
        """Factory method to create ValidationResult."""
        
        missing_files = missing_files or []
        artifacts = artifacts or {}

        return cls(
            all_present=len(missing_files) == 0,
            missing=[
                artifact
                for artifact in artifacts.values()
                if not artifact.exists and artifact.required
            ],
            present=[
                artifact
                for artifact in artifacts.values()
                if artifact.exists
            ],
            errors=errors or [],
            warnings=warnings or []
        )

    @property
    def missing_files(self) -> List[str]:
        """Return names of missing required artifacts."""
        return [artifact.name for artifact in self.missing]


# ============================================================
# ARTIFACT VALIDATOR
# ============================================================

class ArtifactValidator:
    """
    Validates ML artifacts for the recommendation system.
    
    Features:
    - Checks existence of required files
    - Validates file sizes and integrity
    - Provides detailed error reporting
    - Offers guidance for fixing issues
    """
    
    # Required artifacts for different components
    REQUIRED_ARTIFACTS = {
        # Collaborative filtering
        "als_model.pkl": "Collaborative ALS model",
        "book_encoder.pkl": "Book encoder for collaborative filtering",
        "user_encoder.pkl": "User encoder for collaborative filtering",
        "interaction_matrix.npz": "User-item interaction matrix",
        "train_ratings.parquet": "Training ratings data",
        "collaborative_metadata.pkl": "Collaborative model metadata",
        
        # Content-based recommendations
        "book_embeddings.npy": "Book embeddings for content-based recommendations",
        "books_faiss.index": "FAISS index for semantic search",
        "semantic_books.parquet": "Semantic book metadata",
        "embedding_metadata.pkl": "Embedding model metadata",
        
        # Popularity recommendations
        "popularity_scores.parquet": "Popularity scores for books",
    }
    
    # Optional artifacts (won't raise errors if missing)
    OPTIONAL_ARTIFACTS = {
        "interaction_matrix_sample.csv": "Sample interaction matrix for debugging",
        "matrix_stats.txt": "Matrix statistics",
        "evaluation_results_popularity.csv": "Evaluation results",
    }
    
    def __init__(self, artifacts_dir: Optional[Path] = None):
        """
        Initialize the artifact validator.
        
        Parameters:
        -----------
        artifacts_dir : Path, optional
            Directory containing artifacts. Defaults to settings.ARTIFACTS_DIR.
        """
        self.artifacts_dir = Path(artifacts_dir or settings.ARTIFACTS_DIR)
        self._results_cache: Optional[ValidationResult] = None
    
    def validate(self, raise_on_missing: bool = False) -> ValidationResult:
        """
        Validate all required artifacts.
        
        Parameters:
        -----------
        raise_on_missing : bool
            Whether to raise an exception if artifacts are missing
        
        Returns:
        --------
        ValidationResult: Validation results
        
        Raises:
        --------
        RuntimeError: If raise_on_missing is True and artifacts are missing
        """
        if self._results_cache is not None:
            return self._results_cache
        
        logger.info(f"🔍 Validating artifacts in: {self.artifacts_dir}")
        
        result = ValidationResult()
        
        # Check if directory exists
        if not self.artifacts_dir.exists():
            result.errors.append(f"Artifacts directory does not exist: {self.artifacts_dir}")
            result.all_present = False
            return result
        
        # Validate required artifacts
        for file_name, description in self.REQUIRED_ARTIFACTS.items():
            artifact_info = self._check_artifact(file_name, description, required=True)
            if artifact_info.exists:
                result.present.append(artifact_info)
            else:
                result.missing.append(artifact_info)
        
        # Validate optional artifacts (just for information)
        for file_name, description in self.OPTIONAL_ARTIFACTS.items():
            artifact_info = self._check_artifact(file_name, description, required=False)
            if artifact_info.exists:
                result.present.append(artifact_info)
        
        # Check for any missing files
        result.all_present = len(result.missing) == 0
        
        # Add warnings for missing optional files (if any were checked)
        # Optional files are already in present list if they exist
        
        self._results_cache = result
        self._log_results(result)
        
        if raise_on_missing and not result.all_present:
            raise RuntimeError(self.format_error_message(result))
        
        return result
    
    def _check_artifact(
        self,
        file_name: str,
        description: str,
        required: bool = True
    ) -> ArtifactInfo:
        """
        Check a single artifact.
        
        Parameters:
        -----------
        file_name : str
            Name of the artifact file
        description : str
            Description of the artifact
        required : bool
            Whether this artifact is required
        
        Returns:
        --------
        ArtifactInfo: Information about the artifact
        """
        file_path = self.artifacts_dir / file_name
        
        if file_path.exists():
            try:
                size_bytes = file_path.stat().st_size
                last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                return ArtifactInfo(
                    name=file_name,
                    path=file_path,
                    exists=True,
                    size_bytes=size_bytes,
                    last_modified=last_modified,
                    required=required
                )
            except Exception as e:
                return ArtifactInfo(
                    name=file_name,
                    path=file_path,
                    exists=False,
                    error=f"Error accessing file: {str(e)}",
                    required=required
                )
        else:
            return ArtifactInfo(
                name=file_name,
                path=file_path,
                exists=False,
                required=required
            )
    
    def _log_results(self, result: ValidationResult) -> None:
        """
        Log validation results.
        
        Parameters:
        -----------
        result : ValidationResult
            Validation results
        """
        if result.all_present:
            logger.info("✅ All required artifacts are present!")
            logger.info(f"   Total artifacts: {len(result.present)}")
            
            # Log sizes
            total_size = 0
            for artifact in result.present:
                if artifact.size_bytes:
                    total_size += artifact.size_bytes
                    size_mb = artifact.size_bytes / 1024 / 1024
                    logger.debug(f"   {artifact.name}: {size_mb:.2f} MB")
            
            logger.info(f"   Total size: {total_size / 1024 / 1024:.2f} MB")
        
        else:
            logger.warning(f"⚠️ Missing {len(result.missing)} required artifacts:")
            for artifact in result.missing:
                logger.warning(f"   ❌ {artifact.name}")
    
    def format_error_message(self, result: ValidationResult) -> str:
        """
        Format a detailed error message for missing artifacts.
        
        Parameters:
        -----------
        result : ValidationResult
            Validation results
        
        Returns:
        --------
        str: Formatted error message
        """
        if result.all_present:
            return "All artifacts are present"
        
        lines = [
            "=" * 60,
            "MISSING ML ARTIFACTS",
            "=" * 60,
            "",
            f"Directory: {self.artifacts_dir}",
            "",
            f"Missing {len(result.missing)} required artifacts:",
            ""
        ]
        
        for artifact in result.missing:
            description = self.REQUIRED_ARTIFACTS.get(artifact.name, "Unknown artifact")
            lines.append(f"  ❌ {artifact.name}")
            lines.append(f"     Description: {description}")
            
            # Add guidance for specific artifacts
            guidance = self._get_guidance(artifact.name)
            if guidance:
                lines.append(f"     💡 {guidance}")
            lines.append("")
        
        lines.extend([
            "=" * 60,
            "HOW TO FIX",
            "=" * 60,
            "",
            "To generate missing artifacts, run the following pipelines:",
            "",
            "1. Collaborative filtering artifacts:",
            "   python apps/api/ml/collaborative/train_collaborative.py",
            "",
            "2. Content-based artifacts:",
            "   python apps/api/ml/features/embedding_pipeline.py",
            "",
            "3. Popularity artifacts:",
            "   python apps/api/ml/train_popularity.py",
            "",
            "4. Train the hybrid recommender:",
            "   python apps/api/ml/hybrid/train_hybrid.py",
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    def _get_guidance(self, file_name: str) -> Optional[str]:
        """
        Get guidance for a specific missing artifact.
        
        Parameters:
        -----------
        file_name : str
            Name of the missing artifact
        
        Returns:
        --------
        Optional[str]: Guidance string
        """
        guidance = {
            "als_model.pkl": "Run: python apps/api/ml/collaborative/train_collaborative.py",
            "user_encoder.pkl": "Run: python apps/api/ml/collaborative/train_collaborative.py",
            "book_encoder.pkl": "Run: python apps/api/ml/collaborative/train_collaborative.py",
            "interaction_matrix.npz": "Run: python apps/api/ml/collaborative/train_collaborative.py",
            "train_ratings.parquet": "Run: python apps/api/ml/collaborative/train_collaborative.py",
            "collaborative_metadata.pkl": "Run: python apps/api/ml/collaborative/train_collaborative.py",
            "book_embeddings.npy": "Run: python apps/api/ml/features/embedding_pipeline.py",
            "books_faiss.index": "Run: python apps/api/ml/features/embedding_pipeline.py",
            "semantic_books.parquet": "Run: python apps/api/ml/features/embedding_pipeline.py",
            "embedding_metadata.pkl": "Run: python apps/api/ml/features/embedding_pipeline.py",
            "popularity_scores.parquet": "Run: python apps/api/ml/train_popularity.py",
        }
        return guidance.get(file_name)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get a status summary of all artifacts.
        
        Returns:
        --------
        Dict[str, Any]: Status summary
        """
        result = self.validate()
        
        total_required = len(self.REQUIRED_ARTIFACTS)
        total_present = len(result.present)
        
        return {
            "directory": str(self.artifacts_dir),
            "valid": result.all_present,
            "total_required": total_required,
            "total_present": total_present,
            "total_missing": len(result.missing),
            "present": [a.name for a in result.present if a.required],
            "missing": [a.name for a in result.missing],
            "optional_present": [a.name for a in result.present if not a.required],
            "errors": result.errors
        }


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def validate_artifacts(raise_on_missing: bool = False) -> ValidationResult:
    """
    Validate all required artifacts.
    
    Parameters:
    -----------
    raise_on_missing : bool
        Whether to raise an exception if artifacts are missing
    
    Returns:
    --------
    ValidationResult: Validation results
    
    Raises:
    --------
    RuntimeError: If raise_on_missing is True and artifacts are missing
    """
    validator = ArtifactValidator()
    return validator.validate(raise_on_missing=raise_on_missing)


def get_artifact_status() -> Dict[str, Any]:
    """
    Get a status summary of all artifacts.
    
    Returns:
    --------
    Dict[str, Any]: Status summary
    """
    validator = ArtifactValidator()
    return validator.get_status()


def ensure_artifacts() -> None:
    """
    Ensure all artifacts exist. Raises an error if any are missing.
    
    Raises:
    --------
    RuntimeError: If any required artifacts are missing
    """
    
    validate_artifacts(raise_on_missing=True)


# ============================================================
# FASTAPI DEPENDENCY
# ============================================================

from fastapi import HTTPException, status

async def require_artifacts():
    """
    FastAPI dependency to ensure artifacts are present.
    
    Usage:
    ```python
    @app.get("/recommendations")
    async def get_recommendations(
        _: None = Depends(require_artifacts)
    ):
    """