import numpy as np
from typing import List, Dict, Tuple

def get_all_strings(results: List[Dict]) -> List[str]:
    """Get all strings from results in order of appearance."""
    all_strings = []
    for r in results:
        all_strings.append(r["string1"])
        all_strings.append(r["string2"])
    return all_strings

def make_distance_matrix(distances: List[float], size: int) -> np.ndarray:
    """Create a distance matrix from pairwise distances."""
    matrix = np.zeros((size, size))
    idx = 0
    for i in range(size):
        for j in range(i + 1, size):
            if idx < len(distances):
                matrix[i][j] = distances[idx]
                matrix[j][i] = distances[idx]
                idx += 1
    return matrix

def create_point_metadata(
        coords: np.ndarray,
        strings: List[str],
        string_counts: Dict[str, int],
        preserved_fields: Dict[str, List],
        block_id: str = None
) -> List[Dict]:
    """Create point metadata from coordinates and fields."""
    points = []
    for i in range(len(strings)):
        text = strings[i]
        point = {
            "id": i,
            "lat": float(coords[i,0]),
            "lng": float(coords[i,1]),
            "label": text,
            "labelstr": text,
            "occurrence_count": string_counts.get(text, 1),
            **{
                field: values[i] for field, values in preserved_fields.items()
            }
        }
        if block_id:
            point["block_id"] = block_id
        points.append(point)
    return points

def calculate_bounds(coords: np.ndarray, padding: float = 0.1) -> Dict[str, float]:
    """Calculate bounds with padding for visualization."""
    min_lat, min_lng = coords.min(axis=0)
    max_lat, max_lng = coords.max(axis=0)

    lat_padding = (max_lat - min_lat) * padding
    lng_padding = (max_lng - min_lng) * padding

    return {
        "min_lat": float(min_lat - lat_padding),
        "max_lat": float(max_lat + lat_padding),
        "min_lng": float(min_lng - lng_padding),
        "max_lng": float(max_lng + lng_padding)
    }

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing problematic characters."""
    return "".join(c for c in filename if c.isalnum() or c in "._-")