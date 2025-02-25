# URL Configuration

The URL configuration defines the routes and endpoints for different parts of the application. It uses FastAPI routers to organize and modularize the URL handling logic.

## viz.py

The `viz.py` file contains the route definitions for the visualization-related endpoints. It includes:
- `/viz/`: The home endpoint for visualization routes, returning a JSON response indicating the status of the Visualization API.
- `/viz/tsne/{file_path:path}`: The endpoint for rendering t-SNE visualizations based on the provided file path. It uses the `render_tsne` function to process the file and render the visualization using the `leaflet_custom.html` template.

The `viz_router` is an instance of `APIRouter` that groups these visualization routes together.

## distances.py

The `distances.py` file defines the routes for distance calculation endpoints. It includes:
- `/distances/calculate-distances/pairs`: Endpoint for calculating distances between specified pairs of strings using `calculate_distances_pairs`.
- `/distances/calculate-distances/single-list`: Endpoint for calculating distances between all pairs in a single list of strings using `calculate_distances_single_list`.
- `/distances/calculate-distances/two-lists`: Endpoint for calculating distances between pairs from two lists of strings using `calculate_distances_two_lists`.
- `/distances/calculate-distances/from-csv`: Endpoint for calculating distance metrics between concatenated fields from CSV rows using `calculate_distances_from_csv`. It accepts a CSV file and a configuration JSON string.

The `distances_router` is an instance of `APIRouter` that groups these distance calculation routes together.

## browser.py

The `browser.py` file contains the route definitions for the file browsing functionality. It includes:
- `/{bname}{path:path}`: Endpoint for browsing directory contents with authentication support using `browse_directory`. It renders the `browser.html` template with the directory listing and file information.
- `/`: The root endpoint that redirects to the `browse_directory_base` endpoint for the default directory.

The `browser_router` is an instance of `APIRouter` that groups these file browsing routes together.

## main.py

The `main.py` file serves as the main entry point for the application. It creates an instance of the FastAPI application, mounts static directories based on the configuration defined in `constants.py`, and includes the routers from `viz.py`, `distances.py`, and `browser.py`.

It also defines the root endpoint `/` that redirects to the `browse_directory_base` endpoint.

### URL Prefixes

The routers are included with specific URL prefixes to organize the endpoints:
- `viz_router` is included with the prefix `/viz/`
- `distances_router` is included with the prefix `/distances/`
- `browser_router` is included with the prefix `/browser/`

These prefixes help in grouping related endpoints and providing a clear structure to the API.

The URL configuration plays a crucial role in defining the structure and organization of the application's API endpoints. It allows for modular and maintainable code by separating the route handling logic into different files and routers. This makes it easier to manage and extend the application's functionality over time.