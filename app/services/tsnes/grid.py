import traceback
from typing import List, Dict, Tuple, NamedTuple
import numpy as np

from ...config.loggers import get_and_set_logger

logger = get_and_set_logger(__name__)

def calculate_optimal_grid_layout(num_blocks: int, grid_size: int = 4) -> Dict:
    """
    Calculate an optimal grid layout with clear cell boundaries.

    Args:
        num_blocks (int): Total number of blocks to place
        grid_size (int): Maximum number of columns

    Returns:
        Dict with grid layout parameters
    """
    # Calculate grid rows and columns
    grid_rows = (num_blocks + grid_size - 1) // grid_size
    grid_cols = min(num_blocks, grid_size)

    # Define base cell dimensions
    base_cell_width = 15.0
    base_cell_height = 15.0

    # Increased padding between cells for clearer boundaries
    padding_ratio = 0.4  # Increased from 0.2
    h_padding = base_cell_width * padding_ratio
    v_padding = base_cell_height * padding_ratio

    # Calculate total grid dimensions
    total_width = grid_cols * base_cell_width + (grid_cols - 1) * h_padding
    total_height = grid_rows * base_cell_height + (grid_rows - 1) * v_padding

    return {
        "grid_rows": grid_rows,
        "grid_cols": grid_cols,
        "cell_width": base_cell_width,
        "cell_height": base_cell_height,
        "h_padding": h_padding,
        "v_padding": v_padding,
        "total_width": total_width,
        "total_height": total_height
    }

def calculate_block_center(block_idx: int, grid_layout: Dict) -> Tuple[float, float]:
    """
    Calculate the center coordinates for a specific block in the grid.

    Args:
        block_idx (int): Index of the block
        grid_layout (Dict): Grid layout parameters

    Returns:
        Tuple of (center_x, center_y)
    """
    grid_cols = grid_layout["grid_cols"]
    cell_width = grid_layout["cell_width"]
    cell_height = grid_layout["cell_height"]
    h_padding = grid_layout["h_padding"]
    v_padding = grid_layout["v_padding"]
    total_width = grid_layout["total_width"]
    total_height = grid_layout["total_height"]

    # Calculate grid position
    grid_row = block_idx // grid_cols
    grid_col = block_idx % grid_cols

    # Calculate block center with more separation
    center_x = (grid_col * (cell_width + h_padding)) - (total_width / 2) + (cell_width / 2)
    center_y = (total_height / 2) - (grid_row * (cell_height + v_padding)) - (cell_height / 2)

    return center_x, center_y

def normalize_block_points(points: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Normalize points within a block to utilize most of cell space.

    Args:
        points (List[Dict]): Points in a block

    Returns:
        Tuple of (normalized points, block_min, block_range)
    """
    # Extract point coordinates
    block_points = np.array([[p.get('lat', 0), p.get('lng', 0)] for p in points])

    # Calculate block scaling
    block_min = block_points.min(axis=0)
    block_max = block_points.max(axis=0)
    block_range = block_max - block_min

    # Ensure non-zero range to avoid division by zero
    block_range = np.where(block_range == 0, 1, block_range)

    return block_points, block_min, block_range

def process_unified_map(blocks: List[Dict], grid_size: int = 4) -> Dict:
    """
    Process blocks into a unified TSNE visualization with clear cell boundaries.

    Args:
        blocks (List[Dict]): Input blocks with TSNE coordinates
        grid_size (int): Maximum number of columns in the grid

    Returns:
        Dict with processed visualization data
    """
    # Handle empty input
    if not blocks:
        return {
            "points": [],
            "bounds": {
                "min_lat": 0,
                "max_lat": 0,
                "min_lng": 0,
                "max_lng": 0
            },
            "metadata": {
                "grid_dimensions": [0, 0],
                "total_blocks": 0,
                "points_per_block": [],
            }
        }

    # Calculate optimal grid layout
    grid_layout = calculate_optimal_grid_layout(len(blocks), grid_size)

    # Prepare for processing
    unified_points = []
    points_per_block = []
    global_bounds = {
        "min_lat": float('inf'),
        "max_lat": float('-inf'),
        "min_lng": float('inf'),
        "max_lng": float('-inf')
    }

    # Collect all possible field names
    all_fields = set()
    for block in blocks:
        coordinates = block.get('tsne_coordinates', [])
        if coordinates:
            for point in coordinates:
                all_fields.update(point.keys())

    # Remove system-related keys
    system_keys = {'lat', 'lng', 'block_lat', 'block_lng', 'block_id', 'tsne_coordinates'}
    available_fields = list(all_fields - system_keys)

    # Process each block
    for block_idx, block in enumerate(blocks):
        # Find TSNE coordinates
        coordinates = block.get('tsne_coordinates', [])
        if not coordinates:
            points_per_block.append(0)
            continue

        # Calculate block center
        center_x, center_y = calculate_block_center(block_idx, grid_layout)

        # Normalize block points
        block_points, block_min, block_range = normalize_block_points(coordinates)

        # Prepare transformed points
        transformed_points = []
        cell_width = grid_layout["cell_width"]
        cell_height = grid_layout["cell_height"]

        for point_idx, point in enumerate(coordinates):
            # Create a new point dictionary
            new_point = point.copy()

            # Normalize point coordinates within the block with 0.8 scaling factor to leave some space
            normalized_lat = ((point.get('lat', 0) - block_min[0]) / block_range[0] - 0.5) * cell_height * 0.8
            normalized_lng = ((point.get('lng', 0) - block_min[1]) / block_range[1] - 0.5) * cell_width * 0.8

            # Set coordinates
            new_point['block_lat'] = point.get('lat', 0)
            new_point['block_lng'] = point.get('lng', 0)
            new_point['lat'] = center_x + normalized_lat
            new_point['lng'] = center_y + normalized_lng

            # Ensure block_id is set
            new_point['block_id'] = str(block.get('block_id', f'block_{block_idx}'))

            # Track global bounds
            global_bounds["min_lat"] = min(global_bounds["min_lat"], new_point['lat'])
            global_bounds["max_lat"] = max(global_bounds["max_lat"], new_point['lat'])
            global_bounds["min_lng"] = min(global_bounds["min_lng"], new_point['lng'])
            global_bounds["max_lng"] = max(global_bounds["max_lng"], new_point['lng'])

            transformed_points.append(new_point)

        # Add block points to unified points
        unified_points.extend(transformed_points)
        points_per_block.append(len(transformed_points))

    # Add padding to bounds
    def add_padding(bounds):
        lat_range = bounds["max_lat"] - bounds["min_lat"]
        lng_range = bounds["max_lng"] - bounds["min_lng"]

        bounds["min_lat"] -= lat_range * 0.1
        bounds["max_lat"] += lat_range * 0.1
        bounds["min_lng"] -= lng_range * 0.1
        bounds["max_lng"] += lng_range * 0.1

        return bounds

    global_bounds = add_padding(global_bounds)

    # Prepare metadata
    metadata = {
        "grid_dimensions": [grid_layout["grid_cols"], grid_layout["grid_rows"]],
        "total_blocks": len(blocks),
        "points_per_block": points_per_block,
        "cell_width": grid_layout["cell_width"],
        "cell_height": grid_layout["cell_height"],
        "h_padding": grid_layout["h_padding"],
        "v_padding": grid_layout["v_padding"],
        "available_fields": available_fields,
        "embedded_fields": available_fields
    }

    return {
        "points": unified_points,
        "bounds": global_bounds,
        "metadata": metadata
    }