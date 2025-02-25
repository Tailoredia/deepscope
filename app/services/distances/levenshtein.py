from rapidfuzz.distance import Levenshtein

from ...config.loggers import get_and_set_logger

logger = get_and_set_logger(__name__)

def calculate_levenshtein_distance(args):
    """Calculate Levenshtein distance between two strings."""
    string1, string2 = args
    # Calculate raw Levenshtein distance
    raw_dist = Levenshtein.distance(string1, string2)

    # Calculate normalized distance
    max_length = max(len(string1), len(string2))
    normalized_dist = raw_dist / max_length if max_length > 0 else 0.0

    return {
        "string1": string1,
        "string2": string2,
        "distances": {
            "levenshtein": normalized_dist,
            "levenshtein_raw": raw_dist
        }
    }