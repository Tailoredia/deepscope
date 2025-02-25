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



def analyze_distance_metrics(results: List[dict]) -> Dict:
    """
    Analyze the distribution and correlation of distance metrics
    """
    cosine_distances = [float(r["distances"]["cosine"]) for r in results]
    levenshtein_distances = [float(r["distances"]["levenshtein"]) for r in results]

    hist_cosine = np.histogram(cosine_distances, bins=50)
    hist_levenshtein = np.histogram(levenshtein_distances, bins=50)

    stats = {
        'cosine': {
            'mean': float(np.mean(cosine_distances)),
            'std': float(np.std(cosine_distances)),
            'min': float(np.min(cosine_distances)),
            'max': float(np.max(cosine_distances)),
            'histogram': {
                'counts': [int(x) for x in hist_cosine[0]],
                'bins': [float(x) for x in hist_cosine[1]]
            }
        },
        'levenshtein': {
            'mean': float(np.mean(levenshtein_distances)),
            'std': float(np.std(levenshtein_distances)),
            'min': float(np.min(levenshtein_distances)),
            'max': float(np.max(levenshtein_distances)),
            'histogram': {
                'counts': [int(x) for x in hist_levenshtein[0]],
                'bins': [float(x) for x in hist_levenshtein[1]]
            }
        }
    }

    correlation = float(np.corrcoef(cosine_distances, levenshtein_distances)[0, 1])
    stats['correlation'] = correlation

    return stats

def visualize_distance_correlation(results: List[dict], output_dir: str) -> str:
    """
    Create scatter plot showing correlation between distance metrics
    """
    cosine_distances = [float(r["distances"]["cosine"]) for r in results]
    levenshtein_distances = [float(r["distances"]["levenshtein"]) for r in results]

    plt.figure(figsize=(10, 10))
    plt.scatter(
        cosine_distances,
        levenshtein_distances,
        alpha=0.3,
        s=50
    )

    correlation = float(np.corrcoef(cosine_distances, levenshtein_distances)[0, 1])

    plt.xlabel('Cosine Distance')
    plt.ylabel('Levenshtein Distance')
    plt.title('Correlation between Distance Metrics')
    plt.text(
        0.05, 0.95,
        f'Correlation: {correlation:.3f}',
        transform=plt.gca().transAxes,
        fontsize=12,
        bbox=dict(facecolor='white', alpha=0.8)
    )

    # Add trend line
    z = np.polyfit(cosine_distances, levenshtein_distances, 1)
    p = np.poly1d(z)
    plt.plot(
        sorted(cosine_distances),
        p(sorted(cosine_distances)),
        "r--",
        alpha=0.8,
        label=f'Trend line (y = {z[0]:.2f}x + {z[1]:.2f})'
    )
    plt.legend()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"distance_correlation_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    plt.savefig(filepath, format='png', dpi=300, bbox_inches='tight')
    plt.close()

    return filepath

def visualize_distance_distributions(results: List[dict], output_dir: str) -> str:
    """
    Create violin plots showing distribution of distances
    """
    distances = {
        'Cosine': [float(r["distances"]["cosine"]) for r in results],
        'Levenshtein': [float(r["distances"]["levenshtein"]) for r in results]
    }

    plt.figure(figsize=(10, 6))

    parts = plt.violinplot(
        [distances['Cosine'], distances['Levenshtein']],
        positions=[1, 2],
        showmeans=True,
        showmedians=True
    )

    for pc in parts['bodies']:
        pc.set_facecolor('#3498db')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)

    parts['cmeans'].set_color('red')
    parts['cmedians'].set_color('black')

    plt.xticks([1, 2], ['Cosine', 'Levenshtein'])
    plt.ylabel('Distance')
    plt.title('Distribution of Distance Metrics')

    for i, (name, dist) in enumerate(distances.items(), 1):
        stats_text = (
            f'Mean: {np.mean(dist):.3f}\n'
            f'Std: {np.std(dist):.3f}\n'
            f'Median: {np.median(dist):.3f}'
        )
        plt.text(
            i + 0.3,
            plt.ylim()[0] + (plt.ylim()[1] - plt.ylim()[0]) * 0.1,
            stats_text,
            fontsize=10,
            bbox=dict(facecolor='white', alpha=0.8)
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"distance_distributions_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    plt.savefig(filepath, format='png', dpi=300, bbox_inches='tight')
    plt.close()

    return filepath

def analyze_and_visualize_distances(
        results: List[dict],
        output_dir: str = OUTPUT_FIGS
) -> Dict:
    """
    Perform comprehensive analysis of distance metrics and generate visualizations
    """
    stats = analyze_distance_metrics(results)
    correlation_plot = visualize_distance_correlation(results, output_dir)
    distribution_plot = visualize_distance_distributions(results, output_dir)

    return {
        'statistics': stats,
        'visualizations': {
            'correlation_plot': correlation_plot,
            'distribution_plot': distribution_plot
        }
    }

def analyze_neighborhood_stability(
        embeddings: np.ndarray,
        k: int = 5
) -> Dict:
    """
    Analyze how stable neighborhoods are across different distance metrics
    """
    knn_cosine = NearestNeighbors(n_neighbors=k, metric='cosine')
    knn_euclidean = NearestNeighbors(n_neighbors=k, metric='euclidean')

    neighbors_cosine = knn_cosine.fit(embeddings).kneighbors(return_distance=False)
    neighbors_euclidean = knn_euclidean.fit(embeddings).kneighbors(return_distance=False)

    overlaps = np.array([
        len(set(neighbors_cosine[i]) & set(neighbors_euclidean[i])) / k
        for i in range(len(embeddings))
    ])

    hist_data = np.histogram(overlaps, bins=10)
    stability_stats = {
        'mean_overlap': float(np.mean(overlaps)),
        'std_overlap': float(np.std(overlaps)),
        'min_overlap': float(np.min(overlaps)),
        'max_overlap': float(np.max(overlaps)),
        'histogram': {
            'counts': [int(x) for x in hist_data[0]],
            'bins': [float(x) for x in hist_data[1]]
        }
    }

    return stability_stats

def visualize_neighborhood_stability(
        stability_stats: Dict,
        output_dir: str = OUTPUT_FIGS
) -> str:
    """
    Create visualization of neighborhood stability distribution
    """
    plt.figure(figsize=(10, 6))

    hist_data = stability_stats['histogram']
    plt.bar(
        (hist_data['bins'][:-1] + hist_data['bins'][1:]) / 2,
        hist_data['counts'],
        width=np.diff(hist_data['bins']),
        alpha=0.7,
        color='#3498db'
    )

    plt.xlabel('Neighborhood Overlap Ratio')
    plt.ylabel('Count')
    plt.title('Distribution of Neighborhood Stability')

    stats_text = (
        f"Mean Overlap: {stability_stats['mean_overlap']:.3f}\n"
        f"Std Dev: {stability_stats['std_overlap']:.3f}\n"
        f"Range: [{stability_stats['min_overlap']:.3f}, {stability_stats['max_overlap']:.3f}]"
    )
    plt.text(
        0.95, 0.95,
        stats_text,
        transform=plt.gca().transAxes,
        verticalalignment='top',
        horizontalalignment='right',
        bbox=dict(facecolor='white', alpha=0.8)
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"neighborhood_stability_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    plt.savefig(filepath, format='png', dpi=300, bbox_inches='tight')
    plt.close()

    return filepath
