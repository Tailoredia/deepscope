import glob
import json
import os
import traceback

import requests

from app.config.constants import OUTPUT_FIGS, OUTPUT_JSONS, DISTANCES, OUTPUT_DISTANCES_URL
from app.config.loggers import get_and_set_logger

logger = get_and_set_logger(__name__)

class TestAPIClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.endpoints = {
            "pairs": f"{OUTPUT_DISTANCES_URL}/calculate-distances/pairs",
            "single_list": f"{OUTPUT_DISTANCES_URL}/calculate-distances/single-list",
            "two_lists": f"{OUTPUT_DISTANCES_URL}/calculate-distances/two-lists",
            "csv": f"/{DISTANCES}/calculate-distances/from-csv"
        }

    def _prepare_embedding_models(self, embedding_models):
        """Helper method to prepare embedding model configurations"""
        if embedding_models is None:
            return [{"model_id": "minilm", "distance_prefix": "minilm_cosine"}]

        if isinstance(embedding_models, list):
            return [
                {
                    "model_id": model if isinstance(model, str) else model.get("model_id"),
                    "distance_prefix": (
                        f"{model}_cosine" if isinstance(model, str)
                        else model.get("distance_prefix", f"{model['model_id']}_cosine")
                    )
                }
                for model in embedding_models
            ]
        return []

    def calculate_csv_distances(
            self,
            csv_path=None,
            csv_content=None,
            fields=None,
            blocking_keys=None,
            separator=" ",
            output_dir=None,
            distance_types=None,
            embedding_models=None,
            tokenization="words",
            compare_mode="all_pairs",
            batch_size=32,
            use_worker=True,
            clustering=True,
            outlier_detection_method="zscore",
            linkage_method="ward",
            dimensionality_reduction='umap',
            reduction_perplexity=30,
            reduction_n_neighbors=15,
            reduction_min_dist=0.1,
            timeout=300
    ):
        """Calculate distances from a CSV file with support for multiple embedding models"""
        # Convert Path objects to strings
        if hasattr(output_dir, '__fspath__'):
            output_dir = str(output_dir)

        if csv_path and hasattr(csv_path, '__fspath__'):
            csv_path = str(csv_path)

        # Convert fields and blocking_keys Paths to strings if needed
        if fields:
            fields = [str(f) if hasattr(f, '__fspath__') else f for f in fields]
        if blocking_keys:
            blocking_keys = [str(k) if hasattr(k, '__fspath__') else k for k in blocking_keys]

        # Set default distance types if none provided
        if distance_types is None:
            distance_types = ["levenshtein", "cosine"]

        # Prepare embedding models configuration
        prepared_models = self._prepare_embedding_models(embedding_models)

        # Prepare the config
        config = {
            "fields": fields,
            "blocking_keys": blocking_keys,
            "separator": separator,
            "distance_types": distance_types,
            "embedding_models": prepared_models,
            "tokenization": tokenization,
            "compare_mode": compare_mode,
            "batch_size": batch_size,
            "use_worker": use_worker,
            "clustering": clustering,
            "outlier_detection_method": outlier_detection_method,
            "linkage_method": linkage_method,
            "dimensionality_reduction": dimensionality_reduction,
            "reduction_perplexity": reduction_perplexity,
            "reduction_n_neighbors": reduction_n_neighbors,
            "reduction_min_dist": reduction_min_dist,
            "output_dir": output_dir
        }

        # Remove None values from config
        config = {k: v for k, v in config.items() if v is not None}

        logger.info(f"Prepared config: {config}")

        try:
            # Prepare CSV content
            if csv_path:
                with open(csv_path, 'rb') as f:
                    csv_content = f.read()
            elif csv_content and isinstance(csv_content, str):
                csv_content = csv_content.encode('utf-8')
            elif not csv_content:
                raise ValueError("Either csv_path or csv_content must be provided")

            # Prepare multipart form data
            files = {'file': ('data.csv', csv_content)}
            data = {'config': json.dumps(config)}

            # Make the request with timeout
            response = requests.post(
                f"{self.base_url}{self.endpoints['csv']}",
                files=files,
                data=data,
                timeout=timeout
            )

            # Check response
            response.raise_for_status()

            # Verify content type
            if 'application/json' not in response.headers.get('content-type', ''):
                raise ValueError("Expected JSON response")

            result = response.json()

            # Handle empty response
            if not result:
                logger.warning(f"Empty response for {csv_path or 'provided content'}")
                return {
                    'summary': {'num_rows': 0, 'num_comparisons': 0},
                    'total_pairs': 0,
                    'used_fields': [],
                    'distances': []
                }

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response content: {e.response.text}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON response for {csv_path or 'provided content'}")
            return {
                'summary': {'num_rows': 0, 'num_comparisons': 0},
                'total_pairs': 0,
                'used_fields': [],
                'distances': []
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

def process_csv_directory(directory='data', **kwargs):
    """Process all CSV files in a given directory"""
    csv_files = glob.glob(os.path.join(directory, '*.csv'))
    csv_files.sort()
    client = TestAPIClient()

    all_results = {
        'total_results': [],
        'file_summaries': []
    }

    for csv_file in csv_files:
        logger.info(f"Processing file: {csv_file}")

        try:
            result = client.calculate_csv_distances(csv_path=csv_file, **kwargs)

            if not result or not isinstance(result, dict):
                logger.warning(f"No valid results for {csv_file}")
                continue

            all_results['total_results'].append(result)

            # Calculate statistics from the actual result structure
            total_pairs = result.get('total_pairs', 0)
            used_fields = result.get('used_fields', [])
            distances = result.get('distances', [])

            # Calculate average distances
            distance_stats = {}
            if distances:
                for dist_type in result.get('distance_types', ['levenshtein', 'cosine']):
                    values = []
                    for d in distances:
                        if 'distances' in d and dist_type in d['distances']:
                            values.append(float(d['distances'][dist_type]))
                    if values:
                        distance_stats[f'avg_{dist_type}_distance'] = sum(values) / len(values)
                    else:
                        distance_stats[f'avg_{dist_type}_distance'] = 0.0

            # Create file summary using actual available data
            file_summary = {
                'filename': os.path.basename(csv_file),
                'total_pairs': total_pairs,
                'used_fields': used_fields,
                'num_unique_strings': len(set(
                    d['string1'] for d in distances
                ) | set(
                    d['string2'] for d in distances
                )),
                **distance_stats
            }

            all_results['file_summaries'].append(file_summary)
            print_results(result)

        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Error for {csv_file}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response content: {e.response.text}")
        except Exception as e:
            logger.error(f"Error processing {csv_file}: {e}")
            logger.error(traceback.format_exc())

    print_aggregate_summary(all_results, csv_files)
    return all_results

def print_results(result):
    """Pretty print the distance calculation results"""
    if not isinstance(result, dict):
        logger.error("Invalid result format")
        return

    logger.info(f"Total Pairs: {result.get('total_pairs', 0)}")
    logger.info(f"Used Fields: {', '.join(result.get('used_fields', []))}")

    # Print distance types and models used
    logger.info(f"Distance Types: {', '.join(result.get('distance_types', []))}")
    embedding_models = result.get('embedding_models', [])
    if embedding_models:
        logger.info("Embedding Models:")
        for model in embedding_models:
            logger.info(f"  - {model.get('model_id')} ({model.get('distance_prefix')})")

    # Print sample distances
    distances = result.get('distances', [])
    if distances:
        logger.info("\nSample Distances (first 5):")
        for dist in distances[:5]:
            logger.info(f"  {dist.get('string1', '')} <-> {dist.get('string2', '')}:")
            for dtype, value in dist.get('distances', {}).items():
                logger.info(f"    {dtype}: {value:.4f}")

    # Print clustering results if available
    clustering_results = result.get('clustering_results', [])
    if clustering_results:
        logger.info("\nClustering Results:")
        for cluster in clustering_results:
            logger.info(f"  Block Index: {cluster.get('block_index', 0)}")
            if 'metrics' in cluster:
                metrics = cluster['metrics']
                logger.info(f"  Metrics:")
                logger.info(f"    Median Distance: {metrics.get('median', 0.0):.4f}")
                logger.info(f"    Distribution: {metrics.get('distribution', {})}")

def print_aggregate_summary(all_results, csv_files):
    """Print aggregate summary of all processed files"""
    logger.info("\n=== Overall Summary ===")

    file_summaries = all_results.get('file_summaries', [])

    total_pairs = sum(summary.get('total_pairs', 0) for summary in file_summaries)
    unique_fields = set()
    for summary in file_summaries:
        unique_fields.update(summary.get('used_fields', []))

    # Calculate overall average distances
    all_distances = {
        'cosine': [],
        'levenshtein': []
    }

    for result in all_results.get('total_results', []):
        for dist in result.get('distances', []):
            if 'distances' in dist:
                for dist_type, values in all_distances.items():
                    if dist_type in dist['distances']:
                        values.append(float(dist['distances'][dist_type]))

    avg_distances = {}
    for dist_type, values in all_distances.items():
        if values:
            avg_distances[f'avg_{dist_type}'] = sum(values) / len(values)
        else:
            avg_distances[f'avg_{dist_type}'] = 0.0

    logger.info(f"Total Files Processed: {len(csv_files)}")
    logger.info(f"Total Pairs Processed: {total_pairs}")
    logger.info(f"Unique Fields Used: {', '.join(sorted(unique_fields))}")
    logger.info(f"Average Distances:")
    for dist_type, avg in avg_distances.items():
        logger.info(f"  {dist_type}: {avg:.4f}")

def save_results(results, output_dir=OUTPUT_JSONS):
    """Save results to JSON files"""
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'full_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(output_dir, 'file_summaries.json'), 'w') as f:
        json.dump(results.get('file_summaries', []), f, indent=2)

def main():
    """Main entry point for processing CSV files"""
    results = process_csv_directory(
        directory='../app/data',
        clustering=True,
        compare_mode='all_pairs',
        batch_size=8,
        use_worker=True,
        dimensionality_reduction='umap',  # or 'umap'
        reduction_perplexity=30,  # for t-SNE
        reduction_n_neighbors=15,  # for UMAP
        reduction_min_dist=0.1  # for UMAP
    )
    save_results(results)

if __name__ == "__main__":
    main()