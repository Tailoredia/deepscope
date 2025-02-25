# Analytics Module

The Analytics module provides functionality for advanced analysis of data, focusing on extracting insights and detecting patterns. It includes submodules for specific analytical tasks.

## charts.py

The `charts.py` module contains functions for generating various types of charts and visualizations, such as:
- Saving dendrograms for hierarchical clustering results (`save_dendrogram`)
- Analyzing and visualizing distance metrics and their correlations (`analyze_distance_metrics`, `visualize_distance_correlation`, `visualize_distance_distributions`)
- Analyzing and visualizing neighborhood stability in embeddings (`analyze_neighborhood_stability`, `visualize_neighborhood_stability`)

These charting capabilities can be used to gain visual insights into data relationships, clustering structures, and embedding spaces. The module utilizes libraries such as Matplotlib and Seaborn for creating informative and visually appealing charts.

## outliers.py

The `outliers.py` module provides functions for detecting outliers in data using different methods, including:
- Z-score based outlier detection
- Isolation Forest outlier detection
- Local Outlier Factor (LOF) outlier detection

The main function `detect_outliers` takes a condensed distance matrix, a list of data points, and preserved field information to identify outliers using the specified method. It returns detailed outlier information, including outlier scores, indices, and field statistics.

The module also includes functions to enhance data points with outlier information (`enhance_points_with_outlier_info`) and calculate cluster outlier metrics (`calculate_cluster_outlier_metrics`).

Additionally, it provides a function `enhance_visualization_for_ecommerce` that enhances the visualization with e-commerce specific insights, such as price anomalies, potential duplicate products, and category clusters.

### Use Cases

- Detecting fraudulent transactions in financial datasets
- Identifying defective products in manufacturing quality control
- Discovering novel or unusual user behavior in e-commerce clickstreams
- Finding anomalous sensor readings in IoT monitoring systems

By leveraging the Analytics module, developers and data scientists can gain deeper insights into their data, uncover hidden patterns, and make data-driven decisions. The module's integration with visualization libraries allows for effective communication and exploration of analytical results.