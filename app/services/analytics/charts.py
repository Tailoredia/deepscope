import os
from datetime import datetime
from typing import List, Dict

import numpy as np
from matplotlib import pyplot as plt
from scipy.cluster import hierarchy
from sklearn.neighbors import NearestNeighbors

from app.config.constants import OUTPUT_FIGS


def save_dendrogram(Z: np.ndarray, labels: List[str], block_id: str) -> str:
    """Save dendrogram visualization to the figures directory."""
    label_height = 0.3
    min_height = 8
    calculated_height = max(min_height, len(labels) * label_height)

    plt.figure(figsize=(12, calculated_height))
    dendrogram = hierarchy.dendrogram(
        Z,
        labels=labels,
        orientation='left',
        leaf_font_size=10,
        leaf_rotation=0,
        distance_sort='ascending'
    )

    plt.margins(x=0.1)
    plt.tight_layout(pad=1.5)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dendrogram_{block_id}_{timestamp}.png"
    filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    filepath = OUTPUT_FIGS / filename

    plt.savefig(filepath, format='png', dpi=300, bbox_inches='tight')
    plt.close()

    return str(filepath)


