# DeepScope: Fast Manifold Visualization and Analysis Platform

The Manifold Visualization and Analysis Platform is a powerful and intuitive tool designed to simplify the exploration and understanding of complex datasets. With its advanced algorithms and interactive visualizations, this platform empowers users to gain deep insights, uncover hidden patterns, and make data-driven decisions effortlessly.

## Features

- **Distance Calculation**: Calculate various distance metrics between data points or strings, including Levenshtein, cosine using any sentence-transformer / HF model, and token-based distances.
- **Dimensionality Reduction**: Visualize high-dimensional data in 2D or 3D using the t-SNE algorithm, preserving local structure and revealing patterns.
- **Clustering**: Perform hierarchical clustering and visualize dendrograms to understand data groupings and similarities.
- **Embedding Analysis**: Explore and compare different embedding models, measure neighborhood stability, and visualize embeddings.
- **Outlier Detection**: Identify anomalies and outliers in datasets using state-of-the-art techniques such as Z-score, Isolation Forest, and Local Outlier Factor.
- **Interactive Visualization**: Engage with data through interactive plots, allowing for zooming, panning, and hovering to gain detailed insights.
- **Flexible Data Input**: Support for various data formats, including CSV files, with options for field selection, filtering, and preprocessing.
- **Scalability**: Designed to handle small-medium datasets efficiently, with optimized algorithms and parallel processing capabilities.
- **Extensibility**: Modular architecture and well-defined interfaces enable easy integration of new algorithms, models, and visualizations.

## Getting Started

### Prerequisites

- Python 3.7+
- FastAPI
- NumPy
- SciPy
- Scikit-learn
- Matplotlib
- Plotly
- Pandas

### Local Installation

1. Clone the repository:
   ```shell
   git clone https://github.com/Tailoredia/deepscope.git
   ```

2. Install the dependencies:
   ```shell
   pip install -r requirements.txt
   ```

3. Set up the necessary configurations in the `config/constants.py` file.

4. Run the application:
   ```shell
   uvicorn web.main:app --reload
   ```

### Installation with Docker
1. Just do:
   ```shell
   docker compose up --build
   ```

5. Access the application in your web browser at `http://localhost:8000`.

## Usage

1. Prepare your dataset in a supported format (e.g., CSV).

2. Place the dataset in the `data` folder.

3. Select the desired analysis and visualization options, such as distance metrics, outlier detection methods, and dimensionality reduction techniques. More examples on the [test](test) directory.

4. Explore the generated visualizations, interact with the plots, and gain insights into your data.

5. Export the results, including visualizations and analysis reports, for further use or sharing.

## DeepScope Readme Index

## Project Documentation

### Root Level Documentation
- [Main Project Readme](../Readme.md)
- [Technical Architecture Overview](app/Readme.md)
- [Short High Level Report](app/Report.md)

### [Data Structures, Registries and Validation](app/models/Readme.md)

### [URLs and Routing](app/urls/Readme.md)
 
### [Service Module Documentation](app/services/distances/Readme.md)
1. [Distances Service Readme](app/services/distances/Readme.md)
   - Core distance calculation functionality
   - Multiple distance metrics
   - Embedding model support

2. [Analytics Service Readme](app/services/analytics/Readme.md)
   - Outlier detection
   - Data visualization
   - Advanced analytical tools

3. [t-SNE Visualization Service Readme](app/services/tsnes/Readme.md)
   - Dimensionality reduction
   - Visualization techniques
   - Grid-based projections

## Contact
For more information, please contact the project maintainer.

## Examples

The repository includes sample datasets and example clients `test` directory to demonstrate the usage and capabilities of the Deepscope. These example datasets cover objects like cars, interviews, air quality or demographics data.

## Contributing

We welcome contributions to the Manifold Visualization and Analysis Platform! If you'd like to contribute, please follow these guidelines:

### Gitflow Workflow

We follow the stable main gitflow workflow for managing contributions:

1. Fork the repository and clone it locally.
2. Create a new branch from the `develop` or `main` branch for your feature or bug fix respectively:
   ```shell
   git checkout -b feature/your-feature-name main
   ```
   or
   ```shell
   git checkout -b bugfix/your-bug-fix-name main
   ```
3. Implement your changes, ensuring that the code is properly tested and documented.
4. Commit your changes with descriptive commit messages:
   ```shell
   git commit -m "Add feature X" 
   ```
5. Push your branch to your forked repository:
   ```shell
   git push origin feature/your-feature-name
   ```
6. Open a pull request against the `main` branch of the original repository.

### Pull Request Checklist

Before submitting a pull request, please ensure that your contribution meets the following criteria:

- [ ] The code follows the project's coding style and conventions.
- [ ] All existing tests pass successfully.
- [ ] New tests are added to cover the changes introduced by your contribution.
- [ ] The code is properly documented, including docstrings for functions and classes.
- [ ] The CI/CD pipeline passes all checks and builds successfully.
- [ ] The documentation is updated to reflect any changes or additions.

### Continuous Integration and Deployment

We have a CI/CD pipeline set up to automatically build, test, and deploy the application when changes are merged into the `main` branch. Please ensure that your contributions pass all CI/CD checks before submitting a pull request.

### Documentation

Maintaining up-to-date and comprehensive documentation is crucial for the project's usability and maintainability. When contributing, please update the relevant documentation files, including:

- Readme.md: Update the main Readme file if your contribution introduces new features, changes existing functionality, or requires additional setup instructions.
- API Documentation: If your contribution modifies the API endpoints or request/response formats, update the `urls` and `web` documentation accordingly.
- Code Comments: Ensure that your code is well-commented, explaining the purpose, inputs, and outputs of functions and classes.

We appreciate your contributions and look forward to collaborating with you to make the Manifold Visualization and Analysis Platform even better!

If you have any questions or need further assistance, please don't hesitate to reach out to the project maintainers.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions, suggestions, or collaborations, please contact the project maintainer at [Andres Fernandez](mailto:fernandrez@gmail.com).

Let's unlock the power of data together with Deep Scope, the Manifold Visualization and Analysis Platform!