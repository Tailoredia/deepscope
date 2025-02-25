# DeepScope: Technical Architecture Overview

## Backend Architecture

### Core Components

#### CSV Processing [`csvs.py`](services/csvs.py)
- Advanced CSV parsing and preprocessing
- Supports:
    - Field selection
    - Blocking strategies
    - Multimodal distance calculations
- Unified map generation
- Clustering and dimensionality reduction

#### Distance Calculation Services [`README.md`](services/distances/README.md)
- **Base Distance Calculations** [`base.py`](services/distances/base.py)
    - Supports multiple distance metrics:
        - Levenshtein distance
        - Cosine distance
        - Token-based distances
    - Async processing with multiprocessing support
    - Flexible embedding model integration

#### Analytics Module [`README.md`](services/analytics/README.md)
- Outlier detection methods
- Distance metric visualization
- Comprehensive data analysis tools
- E-commerce specific insights

#### t-SNE Visualization [`README.md`](services/tsnes/README.md)
- Dimensionality reduction techniques
- t-SNE and UMAP implementations
- Grid-based visualization
- Metadata generation for high-dimensional data

### API Endpoints

#### Distance Calculation Endpoints [`distances.py`](urls/distances.py)
- `/calculate-distances/pairs`
- `/calculate-distances/single-list`
- `/calculate-distances/two-lists`
- `/calculate-distances/from-csv`

#### Visualization Endpoints [`viz.py`](urls/viz.py)
- Dynamic visualization rendering
- JSON file handling
- t-SNE visualization generation

### Core Libraries and Dependencies
- FastAPI for API development
- Polars for efficient data processing
- NumPy for numerical computations
- Scikit-learn for machine learning algorithms
- SciPy for scientific computing
- Sentence Transformers for embeddings

## Frontend Architecture

### Core JavaScript Modules

#### State Management [`state.js`](static/js/state.js)
- Centralized application state
- Reactive state updates
- Persistent configuration handling

#### Filtering System [`filter-handler.js`](static/js/filter-handler.js)
- Dynamic categorical filtering
- Color-based legend interactions
- Efficient marker filtering

#### Visualization Processors [`processors.js`](static/js/processors.js)
- Marker creation
- Clustering logic
- Point metadata generation

#### Color Management [`color-updater.js`](static/js/color-updater.js)
- Dynamic color mapping
- Legend generation
- Color field selection

### Visualization Technologies
- Leaflet.js for interactive mapping
- D3.js for advanced visualizations
- PapaParse for CSV processing

## Key Workflow

1. Data Ingestion
    - CSV/JSON file upload
    - Preprocessing and parsing
    - Metadata extraction

2. Distance Calculation
    - Multiple distance metrics
    - Embedding transformations
    - Parallel processing

3. Dimensionality Reduction
    - t-SNE/UMAP projections
    - Outlier detection
    - Clustering analysis

4. Interactive Visualization
    - Dynamic filtering
    - Color-coded representations
    - Detailed point interactions

## Performance Optimizations
- Chunked marker processing
- Efficient state management
- Caching mechanisms
- Parallel computation strategies

## Extension Points
- Pluggable embedding models
- Customizable distance metrics
- Modular visualization components

## Development Recommendations
- Maintain type hints
- Use async processing
- Implement comprehensive logging
- Write extensive unit tests

## Potential Improvements
- Add more embedding models
- Implement additional distance metrics
- Enhance outlier detection algorithms
- Create more visualization options
