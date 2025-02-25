import logging
logging.basicConfig(level=logging.ERROR)

import asyncio
import time
from itertools import combinations
from typing import List, Optional, Dict

import polars as pl
from app.models.distances import StringPair, CSVDistanceInput, ModelConfig
from app.models.embeddings import model_registry, get_model
from app.services.csvs import process_csv_for_distances, process_csv_distances



def clear_embedding_caches():
    """Clear the cache of all registered embedding models."""
    print("Clearing embedding caches...")
    for model_id in model_registry.list_models():
        model = get_model(model_id)
        if hasattr(model, 'cache') and isinstance(model.cache, dict):
            model.cache.clear()
            print(f"Cleared cache for model: {model_id}")

async def benchmark_distances(
        df: pl.DataFrame,
        fields: Optional[List[str]] = None,
        batch_sizes: List[int] = [32, 64, 128],
        use_workers: List[bool] = [False, True],
        embedding_models: List[str] = ["minilm"]
) -> Dict:
    """
    Benchmark distance calculations with different configurations

    Args:
        df (pl.DataFrame): Input DataFrame to process
        fields (Optional[List[str]]): Fields to use for text generation
        batch_sizes (List[int]): Batch sizes to test
        use_workers (List[bool]): Whether to use worker processes
        embedding_models (List[str]): List of embedding models to test

    Returns:
        Dict with benchmark results
    """
    results = {}

    # Create base input configuration
    input_config = CSVDistanceInput(
        fields=fields,
        distance_types=["levenshtein", "cosine", "jaccard_words"],
        unified_map=False,
        separator=" ",
        tokenization="words"
    )

    # Prepare texts and get pairs
    texts, preserved_fields, string_counts = process_csv_for_distances(
        df,
        fields=fields,
        separator=" "
    )

    pairs = [
        StringPair(string1=s1, string2=s2)
        for s1, s2 in combinations(texts, 2)
    ]

    for model_name in embedding_models:
        results[f"model_{model_name}"] = {}

        for use_worker in use_workers:
            results[f"model_{model_name}"][f"worker_{use_worker}"] = {}

            for batch_size in batch_sizes:
                # Clear caches before each batch size test
                clear_embedding_caches()
                # Update configuration
                input_config.batch_size = batch_size
                input_config.use_worker = use_worker
                input_config.embedding_models = [
                    ModelConfig(model_id=model_name)
                ]

                start_time = time.time()

                # Process distances
                distances = await process_csv_distances(df, input_config)

                end_time = time.time()

                results[f"model_{model_name}"][f"worker_{use_worker}"][batch_size] = {
                    "total_time": end_time - start_time,
                    "num_pairs": len(pairs),
                    "avg_time_per_pair": (end_time - start_time) / len(pairs),
                    "total_pairs_processed": distances.get("total_pairs", 0)
                }

    return results

def generate_test_dataframe(num_rows: int, num_fields: int = 3) -> pl.DataFrame:
    """
    Generate a synthetic DataFrame with diverse text data for testing

    Args:
        num_rows (int): Number of rows to generate
        num_fields (int): Number of text fields to generate

    Returns:
        pl.DataFrame with synthetic data
    """
    # Sample words to create more diverse text
    subjects = ["customer", "user", "client", "patient", "student", "employee", "visitor"]
    actions = ["requested", "purchased", "submitted", "reviewed", "accessed", "modified", "created"]
    objects = ["document", "report", "application", "record", "file", "account", "profile"]
    locations = ["office", "store", "branch", "department", "unit", "region", "center"]

    import random

    data = {}
    for i in range(num_fields):
        data[f"field_{i}"] = []
        for _ in range(num_rows):
            # Generate a unique combination for each row
            text = f"{random.choice(subjects)} {random.choice(actions)} {random.choice(objects)} "
            text += f"at {random.choice(locations)} {random.randint(1, 100)}"
            data[f"field_{i}"].append(text)

    return pl.DataFrame(data)

async def run_benchmarks():
    """
    Run benchmarks for different DataFrame sizes
    """
    row_sizes = [10, 100, 1000]  # Adjusted sizes for quicker testing
    embedding_models = ["minilm"]  # Using available model

    for rows in row_sizes:
        # Clear embedding caches before each test
        clear_embedding_caches()
        print(f"\n--- Benchmarking with {rows} rows ---")
        df = generate_test_dataframe(rows)

        benchmark_results = await benchmark_distances(
            df,
            fields=None,  # Use all fields
            batch_sizes=[32, 64, 128],
            use_workers=[False, True],
            embedding_models=embedding_models
        )

        print("Benchmark Results:")
        for model, worker_configs in benchmark_results.items():
            print(f"\n{model}:")
            for worker_config, batch_configs in worker_configs.items():
                print(f"\n{worker_config}:")
                for batch_size, metrics in batch_configs.items():
                    print(f"  Batch Size {batch_size}:")
                    print(f"    Total Time: {metrics['total_time']:.4f} seconds")
                    print(f"    Pairs Processed: {metrics['total_pairs_processed']}")
                    print(f"    Avg Time per Pair: {metrics['avg_time_per_pair']:.6f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())