# Deep Scope: A Comprehensive Analysis of Data Visualization and Manifold Learning

## Project Overview

### Architecture and Repository Structure

The project is a sophisticated data visualization and analysis platform designed to explore high-dimensional data through multiple lenses:
- Dimensionality Reduction
- Distance Calculation
- Outlier Detection
- Interactive Visualization

#### Repository Composition
Despite being a deep application, the project maintains a remarkably compact and modular codebase:

```
project/
├── app/
│   ├── config/
│   ├── data/
│   ├── models/
│   ├── services/
│   └── static/
│   └── urls/
│   └── web/
├── test/
```

**Key Observation:** The entire application is implemented in approximately 40 core files, making it highly maintainable. We acknowledge there is room for improvement, and architectural feedback is both welcome and encouraged.

### Technological Stack
- **Backend:** Python (FastAPI)
- **Frontend:** JavaScript (Vanilla JS with D3.js, Leaflet)
- **Core Libraries:**
    - **Dimensionality Reduction:** scikit-learn (t-SNE, UMAP)
    - **Distance Metrics:** RapidFuzz, NumPy
    - **Embedding:** Sentence Transformers
    - **Clustering:** SciPy Hierarchical Clustering

## Manifold Learning and Outlier Detection: Deep Dive

### Manifold Interpretation: The "Cinnamon Roll" Hypothesis

The project's approach to manifold learning can be conceptualized as unrolling a complex, potentially non-linear "cinnamon roll" data space:

1. **Topological Transformation**
    - High-dimensional data is compressed into a 2D representation
    - Preserves local and global data relationships
    - **t-SNE and UMAP are both available** for dimensionality reduction

2. **Distance-Based Manifold Characterization**
    - Multiple distance metrics are used:
        * Levenshtein
        * Cosine
        * Token-based distances
    - This allows for multiple perspectives on data structure

### Outlier Detection Techniques

The project implements sophisticated, multi-method outlier detection:

#### 1. Statistical Z-Score Method
```python
def detect_outliers(distances, texts, method="zscore"):
    avg_distances = np.mean(dist_matrix, axis=1)
    scores = np.abs(zscore(avg_distances))
    is_outlier = scores > 2.5  # Threshold-based identification
```

#### 2. Isolation Forest Algorithm
```python
def detect_outliers(distances, method="isolation_forest"):
    clf = IsolationForest(contamination=0.05, random_state=42)
    scores = -clf.fit(dist_matrix).score_samples(dist_matrix)
    is_outlier = clf.fit_predict(dist_matrix) == -1
```

#### 3. Local Outlier Factor (LOF)
```python
def detect_outliers(distances, method="lof"):
    clf = LocalOutlierFactor(
        n_neighbors=min(20, n_points//2),
        contamination=0.05
    )
    is_outlier = clf.fit_predict(dist_matrix) == -1
```

### Outlier Aggregation Strategy

1. **Multi-Method Scoring**
    - Run multiple outlier detection algorithms
    - Aggregate and cross-validate results
    - Provide comprehensive anomaly insights

2. **Field-Level Analysis**
    - Analyze outliers across different data dimensions
    - Identify systematic vs. sporadic anomalies

### Visualization and Interaction

The frontend provides interactive exploration:
- Color-coded markers
- Cluster-based visualization
- Dynamic filtering
- Outlier highlighting

## Technological Innovation

### Key Architectural Innovations
- Chunked processing for large datasets
- Dynamic color generation
- Adaptive visualization techniques

## Conclusion

The project represents a sophisticated approach to high-dimensional data exploration, seamlessly integrating advanced machine learning techniques with interactive visualization.

### Future Work
- Enhance manifold learning by optimizing t-SNE and UMAP configurations
- Develop more nuanced outlier detection techniques
- Create domain-specific visualization modules

---

