
import asyncio
import multiprocessing
import traceback
from typing import Optional, List, Dict

import numpy as np
from rapidfuzz.distance import Levenshtein
from scipy.stats import kurtosis, skew

from .embeddings import calculate_cosine_distance
from .levenshtein import calculate_levenshtein_distance
from .tokens import calculate_token_distance
from ...models.embeddings import get_model
from ...config.loggers import get_and_set_logger
from ...models.distances import StringPair, DistanceType, ModelConfig

logger = get_and_set_logger(__name__)


async def calculate_distances(
        pairs: List[StringPair],
        distance_type: DistanceType,
        model_id: Optional[str] = None,
        distance_prefix: Optional[str] = None,
        tokenization: str = "words",
        use_worker: bool = False,
        batch_size: int = 32
) -> List[Dict]:
    """
    Calculate distances between pairs of strings using various methods.
    Now supports proper prefix handling for multiple models.
    """
    logger.info(f"Starting distance calculation: {distance_type}, model: {model_id}, prefix: {distance_prefix}")

    if distance_type == "levenshtein":
        pair_inputs = [(pair.string1, pair.string2) for pair in pairs]

        if use_worker and len(pairs) > 1000:
            try:
                with multiprocessing.Pool() as pool:
                    results = pool.map(calculate_levenshtein_distance, pair_inputs)
                    logger.info(f"Multiprocessing completed with {len(results)} results")
                return results
            except Exception as e:
                logger.error(f"Multiprocessing failed: {e}")
                logger.info("Falling back to sequential processing")

        results = [calculate_levenshtein_distance(pair) for pair in pair_inputs]
        logger.info(f"Sequential processing completed with {len(results)} results")
        return results

    elif distance_type == "cosine":
        # Use embedding model for cosine distance with proper prefix
        model = get_model(model_id)
        prefix = distance_prefix or f"{model_id}_cosine"
        return calculate_cosine_distance(pairs, model, batch_size, prefix)

    elif distance_type.startswith(("jaccard_", "cosine_token_")):
        # Handle token-based distances with proper prefixing
        results = []
        for pair in pairs:
            result = calculate_token_distance(
                pair.string1,
                pair.string2,
                distance_type.split("_")[0],
                tokenization
            )
            # Convert to new format with distances dict
            results.append({
                "string1": result["string1"],
                "string2": result["string2"],
                "distances": {
                    f"{distance_type}": result["distance"]
                }
            })
        return results

    else:
        raise ValueError(f"Unknown distance type: {distance_type}")


async def calculate_all_distances(
        pairs: List[StringPair],
        distance_types: List[DistanceType],
        embedding_models: Optional[List[ModelConfig]] = None,
        use_worker: bool = False,
        batch_size: int = 32,
        tokenization: str = "words"
) -> List[Dict]:
    """Calculate distances using multiple models with proper prefixing."""
    logger.info(f"Starting calculate_all_distances with {len(pairs)} pairs")
    logger.info(f"Calculating distance types: {distance_types}")

    try:
        distance_tasks = []

        for dist_type in distance_types:
            if dist_type == "levenshtein":
                distance_tasks.append(
                    calculate_distances(
                        pairs, "levenshtein",
                        distance_prefix="levenshtein",
                        use_worker=use_worker,
                        batch_size=batch_size
                    )
                )
            elif dist_type == "cosine":
                # Handle multiple embedding models for cosine distance
                if embedding_models:
                    for model_config in embedding_models:
                        distance_tasks.append(
                            calculate_distances(
                                pairs,
                                "cosine",
                                model_id=model_config.model_id,
                                distance_prefix=model_config.distance_prefix or f"{model_config.model_id}_cosine",
                                use_worker=use_worker,
                                batch_size=batch_size
                            )
                        )
                else:
                    logger.warning("Cosine distance requested but no embedding models provided")
            else:
                # Handle token-based distances with proper prefix
                distance_tasks.append(
                    calculate_distances(
                        pairs,
                        dist_type,
                        distance_prefix=dist_type,
                        tokenization=tokenization,
                        use_worker=use_worker,
                        batch_size=batch_size
                    )
                )

        if not distance_tasks:
            logger.error("No valid distance calculations to perform")
            return []

        # Run all distance calculations concurrently
        all_results = await asyncio.gather(*distance_tasks)

        # Combine results for each pair
        combined_results = []
        for pair_idx in range(len(pairs)):
            combined_distances = {}
            pair_info = None

            for result_set in all_results:
                if result_set and len(result_set) > pair_idx:
                    result = result_set[pair_idx]
                    if not pair_info:
                        pair_info = {
                            "string1": result["string1"],
                            "string2": result["string2"]
                        }

                    # Merge distances dictionaries
                    if "distances" in result:
                        combined_distances.update(result["distances"])

            if combined_distances and pair_info:
                combined_results.append({
                    **pair_info,
                    "distances": combined_distances
                })

        return combined_results

    except Exception as e:
        logger.error(f"Error in calculate_all_distances: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def calculate_cluster_metrics(distances: np.ndarray, Z: np.ndarray) -> Dict:
    c_distances = Z[:, 2]
    buckets = np.array(c_distances * 10 // 10 + 1)

    unique, counts = np.unique(buckets, return_counts=True)
    dist_dict = {float(k): int(v) for k, v in zip(unique, counts)}

    return {
        'distribution': dist_dict,
        'num': int(len(distances)),
        'median': float(np.median(c_distances)),
        'mean': float(np.mean(c_distances)),
        'std': float(np.std(c_distances)),
        'kurt': float(kurtosis(c_distances)),
        'skew': float(skew(c_distances))
    }