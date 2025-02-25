import multiprocessing
from typing import Optional, List, Dict

import numpy as np
from rapidfuzz.distance import Levenshtein

from .tokens import calculate_token_distance
from ...models.embeddings import get_model
from ...config.loggers import get_and_set_logger
from ...models.distances import StringPair, DistanceType

logger = get_and_set_logger(__name__)

def calculate_cosine_distance(pairs: List[StringPair], model, batch_size: int, distance_prefix: str = "cosine") -> List[Dict]:
    """Calculate cosine distance using embeddings with proper prefix."""
    # Get unique strings and create mapping
    unique_strings = list({pair.string1 for pair in pairs} | {pair.string2 for pair in pairs})
    string_to_idx = {s: i for i, s in enumerate(unique_strings)}

    # Get embeddings
    embeddings = model.get_embeddings(unique_strings, batch_size)

    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized_embeddings = embeddings / norms

    # Calculate distances
    results = []
    for pair in pairs:
        i = string_to_idx[pair.string1]
        j = string_to_idx[pair.string2]
        similarity = np.dot(normalized_embeddings[i], normalized_embeddings[j])
        distance = max(float(1 - similarity), 0)

        results.append({
            "string1": pair.string1,
            "string2": pair.string2,
            "distances": {distance_prefix: distance}
        })

    return results

