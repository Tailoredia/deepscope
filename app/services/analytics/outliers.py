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

def enhance_points_with_outlier_info(
        points: List[Dict],
        outlier_results: Dict[str, List]
) -> List[Dict]:
    """
    Enhance visualization points with outlier information.

    Args:
        points: List of point dictionaries for visualization
        outlier_results: Results from outlier detection

    Returns:
        Enhanced points with outlier flags and scores
    """
    # Create index map for outliers
    outlier_indices = {o["index"]: o["score"] for o in outlier_results["outliers"]}

    # Enhance points
    for point in points:
        point_id = point["id"]
        if point_id in outlier_indices:
            point["is_outlier"] = True
            point["outlier_score"] = outlier_indices[point_id]
            point["outlier_severity"] = "high" if outlier_indices[point_id] > 3 else "medium"
        else:
            point["is_outlier"] = False
            point["outlier_score"] = 0

    return points

def calculate_cluster_outlier_metrics(
        distances: np.ndarray,
        Z: np.ndarray,
        texts: List[str],
        preserved_fields: Dict[str, List]
) -> Dict:
    """
    Calculate cluster metrics including outlier information.

    Args:
        distances: Condensed distance matrix
        Z: Hierarchical clustering linkage matrix
        texts: List of strings corresponding to points
        preserved_fields: Dictionary of preserved field values

    Returns:
        Dictionary with cluster metrics and outlier information
    """
    from scipy.stats import kurtosis, skew

    # Standard cluster metrics
    c_distances = Z[:, 2]
    buckets = np.array(c_distances * 10 // 10 + 1)

    unique, counts = np.unique(buckets, return_counts=True)
    dist_dict = {float(k): int(v) for k, v in zip(unique, counts)}

    # Run outlier detection with multiple methods for comparison
    outlier_methods = ["zscore", "isolation_forest", "lof"]
    outlier_results = {}

    for method in outlier_methods:
        try:
            outlier_results[method] = detect_outliers(
                distances, texts, preserved_fields, method
            )
        except Exception as e:
            outlier_results[method] = {"error": str(e)}

    return {
        'distribution': dist_dict,
        'num': int(len(distances)),
        'median': float(np.median(c_distances)),
        'mean': float(np.mean(c_distances)),
        'std': float(np.std(c_distances)),
        'kurt': float(kurtosis(c_distances)),
        'skew': float(skew(c_distances)),
        'outlier_analysis': outlier_results
    }

def add_outlier_detection_to_process_clustering(
        texts: List[str],
        results: List[Dict],
        distance_matrix: np.ndarray,
        Z: np.ndarray,
        preserved_fields: Dict[str, List]
) -> Dict:
    """
    Add outlier detection to clustering results.

    Args:
        texts: List of strings corresponding to points
        results: Existing distance results
        distance_matrix: Full distance matrix
        Z: Hierarchical clustering linkage matrix
        preserved_fields: Dictionary of preserved field values

    Returns:
        Dict with outlier results
    """
    # Calculate condensed distances from upper triangular part of distance matrix
    n = len(texts)
    condensed_dist = distance_matrix[np.triu_indices(n, k=1)]

    # Calculate metrics including outlier analysis
    metrics = calculate_cluster_outlier_metrics(
        condensed_dist, Z, texts, preserved_fields
    )

    # Get the best outlier detection method (prefer Isolation Forest)
    preferred_method = "isolation_forest"
    if preferred_method in metrics['outlier_analysis']:
        outlier_results = metrics['outlier_analysis'][preferred_method]
    else:
        # Fallback to any available method
        for method in metrics['outlier_analysis']:
            if 'error' not in metrics['outlier_analysis'][method]:
                outlier_results = metrics['outlier_analysis'][method]
                break
        else:
            outlier_results = {"outliers": [], "error": "All methods failed"}

    return {
        'metrics': metrics,
        'outlier_results': outlier_results
    }

# Enhanced visualization for e-commerce data
def enhance_visualization_for_ecommerce(
        points: List[Dict],
        preserved_fields: Dict[str, List],
        outlier_results: Dict
) -> Dict:
    """
    Enhance visualization with e-commerce specific insights.

    Args:
        points: List of point dictionaries for visualization
        preserved_fields: Dictionary of preserved field values
        outlier_results: Results from outlier detection

    Returns:
        Dictionary with enhanced visualization insights
    """
    # E-commerce field detection
    potential_ecommerce_fields = [
        'price', 'product_name', 'category', 'brand', 'sales',
        'revenue', 'sku', 'inventory', 'rating', 'discount'
    ]

    # Detect available e-commerce fields
    ecommerce_fields = {}
    for field in preserved_fields:
        field_lower = field.lower()
        if any(e_field in field_lower for e_field in potential_ecommerce_fields):
            ecommerce_fields[field] = preserved_fields[field]

    # Look for price anomalies
    price_anomalies = []
    price_fields = [f for f in ecommerce_fields if 'price' in f.lower()]

    if price_fields and 'outliers' in outlier_results:
        for outlier in outlier_results['outliers']:
            for price_field in price_fields:
                try:
                    price = float(outlier['fields'][price_field])
                    if price > 0:  # Valid price
                        price_anomalies.append({
                            'text': outlier['text'],
                            'price': price,
                            'score': outlier['score'],
                            'fields': outlier['fields']
                        })
                except (ValueError, TypeError):
                    # Not a valid price value
                    pass

    # Generate insights
    insights = {
        'ecommerce_fields_detected': list(ecommerce_fields.keys()),
        'price_anomalies': price_anomalies,
        'potential_duplicate_products': [],
        'category_clusters': {}
    }

    # Look for potential duplicate products
    for i, point1 in enumerate(points):
        for j, point2 in enumerate(points[i+1:], i+1):
            # Skip if either is an outlier (we want similar non-outlier products)
            if point1.get('is_outlier', False) or point2.get('is_outlier', False):
                continue

            # Calculate similarity score (invert the distance)
            try:
                similarity = 1 - point1.get('distances', {}).get('levenshtein', 0.5)
                if similarity > 0.8:  # Highly similar products
                    insights['potential_duplicate_products'].append({
                        'product1': point1['label'],
                        'product2': point2['label'],
                        'similarity': similarity,
                        'fields1': {k: point1.get(k) for k in ecommerce_fields},
                        'fields2': {k: point2.get(k) for k in ecommerce_fields}
                    })
            except:
                pass

    # Generate category clusters if category field exists
    category_fields = [f for f in ecommerce_fields if 'category' in f.lower()]
    if category_fields:
        category_field = category_fields[0]
        categories = {}

        for point in points:
            cat = point.get(category_field, 'Unknown')
            if cat not in categories:
                categories[cat] = {
                    'count': 0,
                    'outlier_count': 0,
                    'avg_distance': 0,
                    'prodpucts': []
                }

            categories[cat]['count'] += 1
            if point.get('is_outlier', False):
                categories[cat]['outlier_count'] += 1

            categories[cat]['products'].append(point['label'])

        insights['category_clusters'] = categories

    return insights