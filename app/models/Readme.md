# Models

The `models` directory contains the data models and schemas used throughout the application. These models define the structure and validation rules for various data entities and inputs.

## distances.py

The `distances.py` file defines the data models related to distance calculations. It includes:
- `DistanceType`: An enumeration of supported distance types (e.g., Levenshtein, cosine, Jaccard).
- `ModelConfig`: A model representing the configuration of an embedding model, including the model ID and distance prefix.
- `StringPair`: A model representing a pair of strings for distance calculation.
- `DistanceInput`: A model for the input data required for distance calculations, including string pairs, distance type, embedding model, tokenization settings, and processing options.
- `SingleListInput`: A model for input data consisting of a single list of strings for distance calculations.
- `TwoListsInput`: A model for input data consisting of two lists of strings for distance calculations.
- `CSVDistanceInput`: A comprehensive model for input configuration when calculating distances from a CSV file. It includes field selection, blocking keys, distance types, embedding models, tokenization settings, processing options, clustering options, and visualization settings.

These models provide a structured way to define and validate the input data for distance calculation endpoints. They ensure that the required information is provided and help in maintaining data integrity.

## embeddings.py

The `embeddings.py` file contains the models related to embedding functionality. It includes:
- `EmbeddingModelRegistry`: A class for managing multiple embedding models.
- `BaseEmbeddingModel`: An abstract base class defining the interface for embedding models.
- `SentenceTransformerModel` and `HuggingFaceModel`: Concrete implementations of embedding models using the SentenceTransformer and Hugging Face libraries, respectively.

These models provide a unified interface for working with different embedding models and facilitate the integration of new embedding models into the application.

### Usage

The models defined in this directory are used throughout the application to ensure data consistency and validation. They are typically used in the following scenarios:
- Defining input schemas for API endpoints to validate and parse incoming requests.
- Structuring data within the application to maintain a consistent format.
- Providing type hints and documentation for better code readability and maintainability.

By utilizing these models, the application can enforce data integrity, handle different types of inputs, and provide a clear structure for data exchange between different components.

It's important to keep the models up to date and in sync with the evolving requirements of the application. Whenever new data entities or input formats are introduced, corresponding models should be created or updated to accommodate those changes.

The use of Pydantic models, as seen in the code, allows for easy validation, serialization, and deserialization of data. It provides a declarative way to define data structures and enables automatic validation and parsing of input data based on the defined schemas.

Overall, the models directory plays a crucial role in maintaining data consistency, validating inputs, and providing a structured foundation for the application's data handling.