import json
import traceback
from datetime import datetime
from typing import Optional, List, Dict, Tuple

import numpy as np
import polars as pl
from fastapi import HTTPException
from scipy.cluster.hierarchy import linkage

from .analytics.outliers import detect_outliers
from .tsnes.grid import process_unified_map
from ..config.constants import OUTPUT_DEEPSCOPES
from ..config.loggers import get_and_set_logger
from ..models.distances import StringPair, CSVDistanceInput, ModelConfig
from ..services.analytics.charts import save_dendrogram
from ..services.distances.base import calculate_all_distances, calculate_cluster_metrics
from ..services.tsnes.core import process_block_dimred

logger = get_and_set_logger(__name__)


def generate_string_pairs(texts: List[str], compare_mode: str = "all_pairs") -> List[StringPair]:
    """Generate pairs efficiently."""
    if compare_mode == "all_pairs":
        # Pre-allocate the list for better performance
        n = len(texts)
        num_pairs = (n * (n - 1)) // 2
        pairs = []
        pairs.extend(
            StringPair(string1=texts[i], string2=texts[j])
            for i in range(n-1)
            for j in range(i + 1, n)
        )
        return pairs
    else:  # consecutive mode
        # One-shot list creation for consecutive pairs
        return [
            StringPair(string1=texts[i], string2=texts[i+1])
            for i in range(len(texts) - 1)
        ]

def process_csv_for_distances(
        df: pl.DataFrame,
        fields: Optional[List[str]] = None,
        separator: str = " "
) -> Tuple[List[str], Dict[str, List], Dict[str, int]]:
    """Process CSV fields and return strings with preserved field values and counts.

    Args:
        df: Input DataFrame
        fields: Fields to use for text generation (if None, uses all fields)
        separator: Separator for concatenating field values

    Returns:
        Tuple containing:
        - List of unique concatenated strings
        - Dictionary mapping field names to their values
        - Dictionary mapping each unique string to its count in original data
    """
    if fields is None:
        fields = df.columns

    try:
        # Process the dataframe efficiently with Polars
        df_subset = df.select(fields).fill_null("")
        df_subset = df_subset.with_columns([
            pl.col(col).cast(pl.Utf8).fill_null("") for col in df_subset.columns
        ])

        # Create concatenated strings from selected fields
        df = df.with_columns([
            pl.concat_str(pl.col(fields), separator=separator).alias("_concat_text")
        ])

        # Create a unique identifier using all fields to properly identify duplicates
        all_fields_concat = pl.concat_str(
            [pl.col(col) for col in df.columns if col != "_concat_text"],
            separator="||"
        ).alias("_all_fields_key")

        df = df.with_columns([all_fields_concat])

        # Get unique rows based on all fields
        unique_rows = df.unique(subset=["_all_fields_key"])

        # Create dictionaries for text counts and preserved fields
        text_counts = {}  # Track counts of each text based on concatenated selected fields
        preserved_fields = {field: [] for field in df.columns if field not in ["_concat_text", "_all_fields_key"]}
        unique_texts = []
        text_to_idx = {}

        # Process each unique row
        for row in unique_rows.iter_rows(named=True):
            text = row["_concat_text"]
            if text:
                # Count occurrences in original dataframe
                count = df.filter(pl.col("_concat_text") == text).height

                if text not in text_to_idx:
                    text_to_idx[text] = len(unique_texts)
                    unique_texts.append(text)
                    text_counts[text] = count

                    # Store values for all fields from the row
                    for field in preserved_fields:
                        preserved_fields[field].append(row[field])

        # Clean up temporary columns from DataFrame
        df = df.drop(["_concat_text", "_all_fields_key"])

        logger.info(f"Processed {df.height} rows into {len(unique_texts)} unique strings")
        logger.debug(f"Generated text_counts: {text_counts}")
        logger.debug(f"Unique texts: {unique_texts}")

        return unique_texts, preserved_fields, text_counts

    except Exception as e:
        logger.error(f"Error processing CSV fields: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error processing CSV fields: {str(e)}"
        )

def setup_blocks(df: pl.DataFrame, blocking_keys: Optional[List[str]]) -> List[pl.DataFrame]:
    """Set up data blocks based on blocking keys."""
    if not blocking_keys:
        return [df]

    missing_keys = [key for key in blocking_keys if key not in df.columns]
    if missing_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Blocking keys not found: {', '.join(missing_keys)}"
        )

    blocks = df.partition_by(blocking_keys)
    logger.info(f"Created {len(blocks)} blocks using keys: {blocking_keys}")
    return blocks

def get_block_id(block_df: pl.DataFrame, block_idx: int, blocking_keys: Optional[List[str]]) -> Tuple[str, Optional[List[str]]]:
    """Generate block ID and values from blocking keys."""
    if not blocking_keys:
        return f"block_{block_idx}", None

    block_values = [str(block_df.select(key).row(0)[0]) for key in blocking_keys]
    block_id = "_".join(str(val).strip().replace(" ", "_") for val in block_values)
    return block_id, block_values

async def process_distances(
        pairs: List[StringPair],
        input_data: CSVDistanceInput,
        block_info: Optional[Dict] = None
) -> List[Dict]:
    """Calculate distances for pairs with specified configuration."""
    results = await calculate_all_distances(
        pairs=pairs,
        distance_types=input_data.distance_types,
        embedding_models=input_data.embedding_models,
        use_worker=input_data.use_worker,
        batch_size=input_data.batch_size,
        tokenization=input_data.tokenization
    )

    if block_info:
        for result in results:
            result['block'] = block_info

    return results

def create_distance_matrix(
        results: List[Dict],
        texts: List[str],
        embedding_models: Optional[List[ModelConfig]]
) -> np.ndarray:
    """Create distance matrix from results."""
    n = len(texts)
    distance_matrix = np.zeros((n, n))
    string_to_idx = {s: i for i, s in enumerate(texts)}

    # Use the first available embedding model's distance
    first_model_prefix = None
    if embedding_models:
        model_config = embedding_models[0]
        first_model_prefix = model_config.distance_prefix or f"{model_config.model_id}_cosine"

    for result in results:
        i = string_to_idx[result["string1"]]
        j = string_to_idx[result["string2"]]
        if first_model_prefix and first_model_prefix in result["distances"]:
            distance = float(result["distances"][first_model_prefix])
        else:
            distance = float(result["distances"].get("cosine", 0.0))
        distance_matrix[i, j] = distance
        distance_matrix[j, i] = distance

    return distance_matrix
def add_field_information(
        results: List[Dict],
        texts: List[str],
        preserved_fields: Dict[str, List]
) -> None:
    """Add preserved field information to results."""
    for result in results:
        str1_idx = texts.index(result["string1"])
        str2_idx = texts.index(result["string2"])
        result["fields1"] = {f: preserved_fields[f][str1_idx] for f in preserved_fields}
        result["fields2"] = {f: preserved_fields[f][str2_idx] for f in preserved_fields}

def create_response(
        all_results: List[Dict],
        df: pl.DataFrame,
        input_data: CSVDistanceInput,
        all_cluster_results: List[Dict],
        unified_map_blocks: Optional[List[Dict]]
) -> Dict:
    """Create final response with all results."""
    response = {
        "total_pairs": len(all_results),
        "used_fields": [str(f) for f in df.columns],
        "blocking_keys": input_data.blocking_keys,
        "distance_types": input_data.distance_types,
        "embedding_models": [
            {
                "model_id": model.model_id,
                "distance_prefix": model.distance_prefix or f"{model.model_id}_cosine"
            }
            for model in (input_data.embedding_models or [])
        ],
        "distances": all_results
    }

    if input_data.clustering:
        response["clustering_results"] = all_cluster_results

    # Add unified TSNE information if enabled
    if input_data.unified_map and unified_map_blocks:
        unified_results = []
        for block in unified_map_blocks:
            if "unified_map" in block:
                unified_results.append({
                    "block_id": block["block_id"],
                    "unified_map": block["unified_map"]
                })
        if unified_results:
            response["unified_map_results"] = unified_results

    return response

def process_clustering(
        texts: List[str],
        results: List[Dict],
        input_data: CSVDistanceInput,
        block_id: str,
        block_values: Optional[List[str]],
        string_counts: Dict[str, int],
        preserved_fields: Dict[str, List],
        unified_map_blocks: Optional[List[Dict]] = None
) -> Optional[Dict]:
    """Process clustering and visualization for a block."""
    try:
        n = len(texts)
        distance_matrix = create_distance_matrix(results, texts, input_data.embedding_models)
        condensed_dist = distance_matrix[np.triu_indices(n, k=1)]

        # Calculate linkage
        Z = linkage(condensed_dist, method=input_data.linkage_method)
        metrics = calculate_cluster_metrics(condensed_dist, Z)

        outlier_results = detect_outliers(
            distances=condensed_dist,
            texts=texts,
            preserved_fields=preserved_fields,
            method=input_data.outlier_detection_method
        )

        # Create cluster result with outlier info
        cluster_result = {
            'block_id': block_id,
            'block_values': block_values,
            'Z': Z.tolist(),
            'metrics': metrics,
            'labels': texts,
            'dendro_path': save_dendrogram(Z, texts, block_id) if len(texts) < 500 else None,
            'outlier_analysis': outlier_results  # Add the outlier results
        }

        # Generate TSNE visualization
        tsne_results = process_block_dimred(
            strings=texts,
            distances=condensed_dist,
            block_id=",".join(block_values) if block_values else block_id,
            string_counts=string_counts,
            preserved_fields=preserved_fields,
            outlier_results=outlier_results,
            unified_map=input_data.unified_map,
            dimensionality_reduction = input_data.dimensionality_reduction,
            reduction_perplexity = input_data.reduction_perplexity,
            reduction_n_neighbors = input_data.reduction_n_neighbors,
            reduction_min_dist = input_data.reduction_min_dist,
            unified_blocks=unified_map_blocks
        )

        if tsne_results and tsne_results.get("tsne_coordinates"):
            cluster_result["tsne"] = tsne_results

        return cluster_result

    except Exception as e:
        logger.error(f"Clustering failed for block {block_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def process_csv_distances(
        df: pl.DataFrame,
        input_data: CSVDistanceInput
) -> Dict:
    """Process CSV for distances with preserved field values."""
    logger.info("Starting process_csv_distances")

    if df is None or df.height == 0:
        return {
            "total_pairs": 0,
            "used_fields": input_data.fields or df.columns,
            "summary": {},
            "distances": []
        }

    try:
        # Setup blocks and results containers
        blocks = setup_blocks(df, input_data.blocking_keys)
        all_results = []
        all_cluster_results = []
        unified_map_blocks = [] if input_data.unified_map else None

        # Process each block
        for block_idx, block_df in enumerate(blocks):
            if block_df.height < 2:
                continue

            try:
                # Process block data
                block_id, block_values = get_block_id(block_df, block_idx, input_data.blocking_keys)
                texts, preserved_fields, string_counts = process_csv_for_distances(
                    block_df, input_data.fields, input_data.separator
                )

                if len(texts) < 2:
                    continue

                # Generate and process pairs
                pairs = generate_string_pairs(texts, input_data.compare_mode)
                if not pairs:
                    continue

                # Calculate distances
                block_info = dict(zip(input_data.blocking_keys, block_values)) if input_data.blocking_keys else None
                results = await process_distances(pairs, input_data, block_info)

                if not results:
                    continue

                # Handle clustering if requested
                if input_data.clustering and len(pairs) > 1:
                    cluster_result = process_clustering(
                        texts=texts,
                        results=results,
                        input_data=input_data,
                        block_id=block_id,
                        block_values=block_values,
                        string_counts=string_counts,
                        preserved_fields=preserved_fields,
                        unified_map_blocks=unified_map_blocks
                    )
                    if cluster_result:
                        all_cluster_results.append(cluster_result)

                # Add field information and collect results
                add_field_information(results, texts, preserved_fields)
                all_results.extend(results)

            except Exception as e:
                logger.error(f"Error processing block {block_idx}: {str(e)}")
                logger.error(traceback.format_exc())
                continue

        # Create response
        response = create_response(all_results, df, input_data, all_cluster_results, unified_map_blocks)

        # Process unified visualization if requested
        if input_data.unified_map and unified_map_blocks:
            unified_data = process_unified_map(unified_map_blocks, input_data.grid_size)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{input_data.unified_map_prefix}_{timestamp}.json"
            filepath = OUTPUT_DEEPSCOPES / filename

            with open(filepath, 'w') as f:
                json.dump(unified_data, f, indent=2)

            response["unified_map"] = {
                "filepath": str(filepath),
                "total_blocks": len(unified_map_blocks),
                "grid_dimensions": unified_data["metadata"]["grid_dimensions"]
            }

        return response

    except Exception as e:
        logger.error(f"Fatal error in process_csv_distances: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "total_pairs": 0,
            "error": str(e),
            "distances": []
        }