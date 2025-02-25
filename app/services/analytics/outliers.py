import numpy as np
from scipy.stats import zscore
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from typing import List, Dict, Optional

def detect_outliers(
        distances: np.ndarray,
        texts: List[str],
        preserved_fields: Dict[str, List],
        method: str = "zscore"
) -> Dict[str, List]:
    """
    Detect outliers in the distance data using various methods.

    Args:
        distances: Condensed distance matrix
        texts: List of strings corresponding to points
        preserved_fields: Dictionary of preserved field values
        method: Outlier detection method ("zscore", "isolation_forest", "lof")

    Returns:
        Dictionary with outlier information
    """
    n_points = len(texts)

    # Create full distance matrix from condensed form
    dist_matrix = np.zeros((n_points, n_points))
    idx = 0
    for i in range(n_points):
        for j in range(i + 1, n_points):
            dist_matrix[i, j] = distances[idx]
            dist_matrix[j, i] = distances[idx]
            idx += 1

    # Calculate outlier scores based on specified method
    if method == "zscore":
        # Use Z-score on average distances
        avg_distances = np.mean(dist_matrix, axis=1)
        scores = np.abs(zscore(avg_distances))
        is_outlier = scores > 2.5  # Threshold for Z-score

    elif method == "isolation_forest":
        # Use Isolation Forest
        clf = IsolationForest(contamination=0.05, random_state=42)
        # Use row-wise distances as features
        scores = -clf.fit(dist_matrix).score_samples(dist_matrix)
        is_outlier = clf.fit_predict(dist_matrix) == -1

    elif method == "lof":
        # Local Outlier Factor
        clf = LocalOutlierFactor(n_neighbors=min(20, n_points//2), contamination=0.05)
        is_outlier = clf.fit_predict(dist_matrix) == -1
        scores = clf.negative_outlier_factor_ * -1

    else:
        raise ValueError(f"Unknown outlier detection method: {method}")

    # Create results
    outliers = []
    field_names = list(preserved_fields.keys())

    for i in range(n_points):
        if is_outlier[i]:
            outlier_info = {
                "text": texts[i],
                "score": float(scores[i]),
                "index": i,
                "fields": {field: preserved_fields[field][i] for field in field_names}
            }
            outliers.append(outlier_info)

    # Sort outliers by score (descending)
    outliers.sort(key=lambda x: x["score"], reverse=True)

    # Calculate statistics for field values among outliers
    field_stats = {}
    for field in field_names:
        field_values = [o["fields"][field] for o in outliers]
        try:
            # Try to calculate frequency distribution
            value_counts = {}
            for val in field_values:
                if val in value_counts:
                    value_counts[val] += 1
                else:
                    value_counts[val] = 1

            field_stats[field] = {
                "unique_values": len(value_counts),
                "most_common": sorted(
                    value_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5],
                "distribution": value_counts
            }
        except:
            # If values are not hashable, skip stats
            field_stats[field] = {"error": "Could not calculate statistics"}

    return {
        "outliers": outliers,
        "total_outliers": len(outliers),
        "outlier_percentage": len(outliers) / n_points * 100,
        "method": method,
        "field_statistics": field_stats
    }
