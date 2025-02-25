import os
from pathlib import Path

# Base paths from environment variables
DATA_HOME = os.environ.get("DATA_HOME", "./data")

# Core application paths
BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT = "output"
STATIC = "static"
JSONS = "jsons"
FIGS = "figs"
DEEPSCOPE = "ds"

VIZ = "viz"
BROWSER = "browser"
DISTANCES = "distances"

OUTPUT_DIR = BASE_DIR / OUTPUT
STATIC_HOME = BASE_DIR / STATIC
OUTPUT_FIGS = OUTPUT_DIR / FIGS
OUTPUT_JSONS = OUTPUT_DIR / JSONS
OUTPUT_DEEPSCOPES = OUTPUT_DIR / DEEPSCOPE

# URL prefixes
STATIC_URL = f"/{STATIC}"
OUTPUT_FIGS_URL = f"/{FIGS}"
OUTPUT_JSONS_URL = f"/{JSONS}"
OUTPUT_DEEPSCOPES_URL = f"/{DEEPSCOPE}"


OUTPUT_BROWSER_URL = f"/{BROWSER}"
OUTPUT_DISTANCES_URL = f"/{DISTANCES}"
OUTPUT_VIZ_URL = f"/{VIZ}"

# Directory configurations using the above constants
DIRECTORY_CONFIG = {
    STATIC: {
        "path": STATIC_HOME,
        "url_prefix": STATIC_URL,
        "requires_auth": False,
        "description": "Public static files",
        "mount_name": STATIC
    },
    FIGS: {
        "path": OUTPUT_FIGS,
        "url_prefix": OUTPUT_FIGS_URL,
        "requires_auth": False,
        "description": "Fixed figures and charts for checks",
        "mount_name": FIGS
    },
    JSONS: {
        "path": OUTPUT_JSONS,
        "url_prefix": OUTPUT_JSONS_URL,
        "requires_auth": False,
        "description": "Json summaries and process metrics",
        "mount_name": JSONS
    },
    DEEPSCOPE: {
        "path": OUTPUT_DEEPSCOPES,
        "url_prefix": OUTPUT_DEEPSCOPES_URL,
        "requires_auth": False,
        "description": "Specific MapLike Structures to navigate data",
        "mount_name": DEEPSCOPE
    }
}