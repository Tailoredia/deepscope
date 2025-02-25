from typing import List, Set
from collections import Counter

def tokenize(text: str, method: str = "words") -> List[str]:
    """
    Tokenize text using different methods.

    Args:
        text: Input text to tokenize
        method: Tokenization method ("words", "chars", "ngrams")

    Returns:
        List of tokens
    """
    if method == "words":
        return text.lower().split()
    elif method == "chars":
        return list(text.lower())
    elif method == "ngrams":
        # Generate character n-grams (n=3)
        text = text.lower()
        return [text[i:i+3] for i in range(len(text)-2)]
    else:
        raise ValueError(f"Unknown tokenization method: {method}")

def calculate_jaccard_distance(text1: str, text2: str, tokenization: str = "words") -> float:
    """
    Calculate normalized Jaccard distance between two strings.

    Args:
        text1: First text
        text2: Second text
        tokenization: Tokenization method to use

    Returns:
        Normalized Jaccard distance (0-1)
    """
    tokens1 = set(tokenize(text1, tokenization))
    tokens2 = set(tokenize(text2, tokenization))

    if not tokens1 and not tokens2:
        return 0.0

    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))

    return 1 - (intersection / union)

def calculate_cosine_token_distance(text1: str, text2: str, tokenization: str = "words") -> float:
    """
    Calculate normalized cosine distance using token frequencies.

    Args:
        text1: First text
        text2: Second text
        tokenization: Tokenization method to use

    Returns:
        Normalized cosine distance (0-1)
    """
    tokens1 = Counter(tokenize(text1, tokenization))
    tokens2 = Counter(tokenize(text2, tokenization))

    # Get all unique tokens
    all_tokens = set(tokens1.keys()).union(tokens2.keys())

    # Calculate dot product and magnitudes
    dot_product = sum(tokens1.get(token, 0) * tokens2.get(token, 0) for token in all_tokens)
    magnitude1 = sum(count * count for count in tokens1.values()) ** 0.5
    magnitude2 = sum(count * count for count in tokens2.values()) ** 0.5

    if magnitude1 == 0 and magnitude2 == 0:
        return 0.0
    elif magnitude1 == 0 or magnitude2 == 0:
        return 1.0

    similarity = dot_product / (magnitude1 * magnitude2)
    return 1 - similarity

def calculate_token_distance(
        text1: str,
        text2: str,
        distance_type: str = "jaccard",
        tokenization: str = "words"
) -> dict:
    """
    Calculate token-based distance between two strings.

    Args:
        text1: First text
        text2: Second text
        distance_type: Type of distance ("jaccard" or "cosine_token")
        tokenization: Tokenization method to use

    Returns:
        Dictionary with distance information
    """
    if distance_type == "jaccard":
        distance = calculate_jaccard_distance(text1, text2, tokenization)
    elif distance_type == "cosine_token":
        distance = calculate_cosine_token_distance(text1, text2, tokenization)
    else:
        raise ValueError(f"Unknown distance type: {distance_type}")

    return {
        "string1": text1,
        "string2": text2,
        "distance": distance,
        "distance_type": f"{distance_type}_{tokenization}"
    }