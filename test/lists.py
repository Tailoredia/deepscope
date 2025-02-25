import requests
from config.loggers import get_and_set_logger
from config.constants import DISTANCES, OUTPUT_DISTANCES_URL

logger = get_and_set_logger(__name__)

def test_single_list():
    """Test the single list endpoint"""
    url = f"http://localhost:8000{OUTPUT_DISTANCES_URL}/calculate-distances/single-list"

    # Test data
    data = {
        "strings": [
            "apple iphone 12 pro max",
            "iphone 12 pro max",
            "apple iphone 12",
            "samsung galaxy s21"
        ],
        "distance_type": "levenshtein",
        "model_name": "minilm",
        "batch_size": 32,
        "use_worker": True
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()

        results = response.json()
        print("\n=== Single List Results ===")
        print(f"Number of comparisons: {len(results)}")
        print("\nSample distances:")
        for i, result in enumerate(results[:3]):
            print(f"\nComparison {i+1}:")
            print(f"String 1: {result['string1']}")
            print(f"String 2: {result['string2']}")
            print(f"Distances: {result['distances']}")

    except Exception as e:
        logger.error(f"Error in single list test: {str(e)}")

def test_two_lists():
    """Test the two lists endpoint"""
    url = f"http://localhost:8000{OUTPUT_DISTANCES_URL}/calculate-distances/two-lists"

    # Test data
    data = {
        "list1": [
            "iphone 12 black",
            "samsung galaxy",
            "macbook pro"
        ],
        "list2": [
            "iphone 12 white",
            "samsung note",
            "macbook air"
        ],
        "distance_type": "cosine",
        "model_name": "minilm",
        "batch_size": 32,
        "use_worker": True
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()

        results = response.json()
        print("\n=== Two Lists Results ===")
        print(f"Number of comparisons: {len(results)}")
        print("\nAll comparisons:")
        for i, result in enumerate(results):
            print(f"\nComparison {i+1}:")
            print(f"String 1: {result['string1']}")
            print(f"String 2: {result['string2']}")
            print(f"Distances: {result['distances']}")

    except Exception as e:
        logger.error(f"Error in two lists test: {str(e)}")

def main():
    """Run all tests"""
    print("\nTesting single list endpoint...")
    test_single_list()

    print("\nTesting two lists endpoint...")
    test_two_lists()

if __name__ == "__main__":
    main()