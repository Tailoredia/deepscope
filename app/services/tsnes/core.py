import json
import traceback
from datetime import datetime
from typing import List, Dict, Optional

import numpy as np
from sklearn.manifold import TSNE
from umap import UMAP

from .utils import make_distance_matrix, calculate_bounds, sanitize_filename
from ...config.constants import OUTPUT_DEEPSCOPES
from ...config.loggers import get_and_set_logger

logger = get_and_set_logger(__name__)

def save_visualization(
        data: Dict,
        filename: str
) -> str:
    """Save visualization data to file."""
    filepath = OUTPUT_DEEPSCOPES / sanitize_filename(filename)
    OUTPUT_DEEPSCOPES.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    logger.info(f"Saved visualization to {filepath}")
    return filepath.name

def compute_dimensionality_reduction(
        distances: np.ndarray,
        n_points: int,
        method: str = 'tsne',
        perplexity: Optional[int] = None,
        n_neighbors: Optional[int] = None,
        min_dist: Optional[float] = None
) -> np.ndarray:
    """
    Compute dimensionality reduction using either t-SNE or UMAP.

    Args:
        distances: Condensed distance matrix
        n_points: Number of points
        method: Reduction method ('tsne' or 'umap')
        perplexity: Perplexity for t-SNE
        n_neighbors: Number of neighbors for UMAP
        min_dist: Minimum distance for UMAP

    Returns:
        Numpy array of 2D coordinates
    """
    # Determine perplexity for t-SNE
    if perplexity is None:
        perplexity = min(30, n_points - 1)

    # Create full distance matrix from condensed form
    dist_matrix = make_distance_matrix(distances.tolist(), n_points)

    # Choose reduction method
    if method == 'tsne':
        reducer = TSNE(
            n_components=2,
            metric='precomputed',
            init='random',
            random_state=42,
            perplexity=perplexity
        )
    elif method == 'umap':
        # Set default values if not provided
        n_neighbors = n_neighbors or min(15, n_points - 1)
        min_dist = min_dist or 0.1

        reducer = UMAP(
            n_components=2,
            metric='precomputed',
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            random_state=42
        )
    else:
        raise ValueError(f"Unsupported dimensionality reduction method: {method}")

    # Fit and transform
    return reducer.fit_transform(dist_matrix)

def process_block_dimred(
        strings: List[str],
        distances: np.ndarray,
        block_id: str,
        string_counts: Dict[str, int],
        preserved_fields: Dict[str, List],
        outlier_results: Optional[Dict] = None,
        unified_map: bool = False,
        unified_blocks: Optional[List[Dict]] = None,
        dimensionality_reduction: str = 'tsne',
        reduction_perplexity: Optional[int] = None,
        reduction_n_neighbors: Optional[int] = None,
        reduction_min_dist: Optional[float] = None
) -> Dict:
    """
    Process dimensionality reduction visualization for a block with enhanced compatibility.

    Adds support for both t-SNE and UMAP reduction methods.
    """
    try:
        n_points = len(strings)
        if n_points < 2:
            logger.warning(f"Not enough points for dimensionality reduction in block {block_id}")
            return {
                "tsne_coordinates": [],
                "point_count": n_points,
                "error": "Not enough points for dimensionality reduction"
            }

        # Use the new compute_dimensionality_reduction function
        coords = compute_dimensionality_reduction(
            distances,
            n_points,
            method=dimensionality_reduction,
            perplexity=reduction_perplexity,
            n_neighbors=reduction_n_neighbors,
            min_dist=reduction_min_dist
        )
        bounds = calculate_bounds(coords)

        # Rest of the function remains the same as in the original implementation
        points = []
        for i in range(n_points):
            point = {
                "lat": float(coords[i, 0]),
                "lng": float(coords[i, 1]),
                "labelstr": strings[i],
                "total_count": string_counts.get(strings[i], 1),
                "block_id": str(block_id)
            }

            # Add preserved field values
            for field, values in preserved_fields.items():
                point[field] = values[i]

            # Add outlier information
            if outlier_results and 'outliers' in outlier_results:
                is_outlier = False
                outlier_score = 0.0

                for outlier in outlier_results['outliers']:
                    if outlier['text'] == strings[i]:
                        is_outlier = True
                        outlier_score = outlier['score']
                        break

                point['is_outlier'] = is_outlier
                point['outlier_score'] = outlier_score
            else:
                point['is_outlier'] = False
                point['outlier_score'] = 0.0

            points.append(point)

        # Create base block result
        block_result = {
            "tsne_coordinates": points,
            "labels": strings,
            "bounds": bounds,
            "point_count": n_points,
            "block_id": block_id,
            "metadata": {
                "total_points": sum(string_counts.values()),
                "unique_points": len(points),
                "available_fields": list(preserved_fields.keys()),
                "embedded_fields": sorted(preserved_fields.keys()),
                "reduction_method": dimensionality_reduction
            }
        }

        # Rest of the function remains the same as in the original implementation
        if unified_map and unified_blocks is not None:
            unified_blocks.append(block_result)
            return block_result
        else:
            # Existing saving logic...
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            field_names = "_".join(sorted(preserved_fields.keys()))
            filename = f"{dimensionality_reduction}_{field_names}_{block_id}_{timestamp}.json"

            # Prepare data for saving
            save_data = {
                "points": points,
                "bounds": bounds,
                "metadata": block_result["metadata"]
            }

            # Save visualization
            filepath = save_visualization(save_data, filename)

            # Add filename to result
            block_result["json_filename"] = filepath

            return block_result

    except Exception as e:
        logger.error(f"Error in dimensionality reduction for block {block_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "tsne_coordinates": [],
            "point_count": 0,
            "error": str(e)
        }