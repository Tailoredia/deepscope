from ..config.loggers import get_and_set_logger
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


logger = get_and_set_logger(__name__)


DistanceType = Literal[
    "levenshtein",
    "cosine",
    "jaccard_words",
    "jaccard_chars",
    "jaccard_ngrams",
    "cosine_token_words",
    "cosine_token_chars",
    "cosine_token_ngrams"
]

class ModelConfig(BaseModel):
    model_id: str
    distance_prefix: Optional[str] = None  # If not provided, will use model_id as prefix

    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "minilm",
                "distance_prefix": "minilm_cosine"
            }
        }

class StringPair(BaseModel):
    string1: str
    string2: str

class DistanceInput(BaseModel):
    pairs: List[StringPair]
    distance_type: DistanceType = "levenshtein"
    model_id: Optional[str] = Field(
        default=None,
        description="Embedding model to use for cosine distance"
    )
    tokenization: Optional[str] = Field(
        default="words",
        description="Tokenization method for token-based distances"
    )
    use_worker: bool = False
    batch_size: int = 32

class SingleListInput(BaseModel):
    strings: List[str]
    distance_type: Literal["levenshtein", "cosine"] = "levenshtein"
    model_name: Optional[str] = Field(
        default="sentence-transformers/all-mpnet-base-v2"
    )
    use_worker: bool = False
    batch_size: int = 32

class TwoListsInput(BaseModel):
    list1: List[str]
    list2: List[str]
    distance_type: Literal["levenshtein", "cosine"] = "levenshtein"
    model_name: Optional[str] = Field(
        default="sentence-transformers/all-mpnet-base-v2"
    )
    use_worker: bool = False
    batch_size: int = 32

class CSVDistanceInput(BaseModel):
    """Input configuration for CSV distance calculations."""

    # Field selection
    fields: Optional[List[str]] = Field(
        default=None,
        description="Fields to use for comparison. If None, uses all fields."
    )
    blocking_keys: Optional[List[str]] = Field(
        default=None,
        description="Keys to use for blocking comparisons."
    )
    separator: str = Field(
        default=" ",
        description="Separator for concatenating field values."
    )

    # Distance configuration
    distance_types: List[DistanceType] = Field(
        default_factory=lambda: ["levenshtein","cosine","jaccard_words"],
        description="Distance metrics to calculate."
    )
    embedding_models: Optional[List[ModelConfig]] = Field(
        default=None,
        description="Embedding models to use for cosine distances."
    )
    tokenization: str = Field(
        default="words",
        description="Tokenization method for token-based distances."
    )

    # Processing options
    compare_mode: Literal["all_pairs", "consecutive"] = Field(
        default="all_pairs",
        description="How to compare rows."
    )
    batch_size: int = Field(
        default=32,
        description="Batch size for processing."
    )
    use_worker: bool = Field(
        default=False,
        description="Use multiprocessing for calculations."
    )

    # Clustering options
    clustering: bool = Field(
        default=False,
        description="Generate clustering metrics and visualizations."
    )
    linkage_method: Literal["ward", "complete", "average", "single"] = Field(
        default="ward",
        description="Method for hierarchical clustering."
    )
    outlier_detection_method: str = Field(
        default="isolation_forest",
        description="Prefix for the unified map JSON file."
    )

    dimensionality_reduction: Literal["tsne", "umap"] = Field(
        default="tsne",
        description="Method for dimensionality reduction (t-SNE or UMAP)"
    )
    reduction_perplexity: Optional[int] = Field(
        default=None,
        description="Perplexity for t-SNE (ignored for UMAP). Defaults to min(30, n_samples - 1)"
    )
    reduction_n_neighbors: Optional[int] = Field(
        default=15,
        description="Number of neighbors for UMAP (ignored for t-SNE)"
    )
    reduction_min_dist: Optional[float] = Field(
        default=0.1,
        description="Minimum distance for UMAP (ignored for t-SNE)"
    )

    # VIz options
    unified_map: bool = Field(
        default=False,
        description="Generate a unified map visualization with blocks in a grid."
    )
    grid_size: int = Field(
        default=4,
        description="Number of blocks per row in the unified map grid."
    )
    unified_map_prefix: str = Field(
        default="unified_map",
        description="Prefix for the unified map JSON file."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "fields": ["name", "description"],
                "blocking_keys": ["category"],
                "separator": " ",
                "distance_types": ["levenshtein", "cosine"],
                "embedding_models": [
                    {"model_id": "minilm", "distance_prefix": "minilm_cosine"},
                    {"model_id": "mpnet", "distance_prefix": "mpnet_cosine"}
                ],
                "tokenization": "words",
                "compare_mode": "all_pairs",
                "batch_size": 32,
                "use_worker": True,
                "clustering": True,
                "linkage_method": "ward"
            }
        }