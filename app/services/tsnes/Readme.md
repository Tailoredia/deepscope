# t-SNE Module

The t-SNE (t-Distributed Stochastic Neighbor Embedding) module provides functionality for dimensionality reduction and visualization of high-dimensional data using the t-SNE algorithm. It allows for creating 2D or 3D representations of complex datasets while preserving local structure.

## core.py

The `core.py` module contains the core functions for performing t-SNE calculations and visualizations, including:
- Computing t-SNE coordinates from distance matrices with `compute_tsne`
- Creating block metadata for visualizations with `create_block_metadata`
- Saving t-SNE visualizations to file using `save_visualization`
- Processing t-SNE for individual data blocks with `process_block_tsne`, supporting unified visualizations

These functions provide a high-level interface for applying t-SNE to datasets and generating informative visualizations. They handle the integration with the t-SNE algorithm, coordinate computation, metadata creation, and file saving.

## grid.py

The `grid.py` module focuses on creating unified t-SNE visualizations by arranging multiple data blocks in a grid layout. It provides the `process_unified_map` function for processing and combining t-SNE results from individual blocks to create a comprehensive visualization.

The unified t-SNE visualization allows for exploring large datasets by organizing them into a grid of subplots, where each subplot represents a subset of the data. This enables users to gain an overview of the entire dataset while still being able to inspect individual blocks in detail.

## utils.py

The `utils.py` module contains utility functions used by the t-SNE module, such as:
- Creating distance matrices from condensed distance representations with `make_distance_matrix`
- Generating point metadata for visualizations using `create_point_metadata`
- Calculating bounding boxes for t-SNE coordinates with `calculate_bounds`
- Sanitizing filenames for saving visualizations using `sanitize_filename`

These utility functions support the core t-SNE functionality and help in preparing data for visualization. They handle tasks such as converting distance representations, creating metadata, calculating plot boundaries, and ensuring valid filenames.

### Use Cases

- Visualizing high-dimensional datasets to identify clusters or patterns
- Exploring large collections of images, documents, or customer data
- Analyzing gene expression data or single-cell sequencing results
- Visualizing embeddings learned by deep learning models
- Creating interactive data explorers for domain experts

The t-SNE module empowers data scientists and researchers to create compelling visualizations of complex datasets, enabling them to gain insights, communicate findings, and make data-driven decisions. Its ability to handle large datasets and create unified visualizations makes it valuable for exploratory data analysis in various domains, such as bioinformatics, customer segmentation, or natural language processing.