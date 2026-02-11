import json
import os
from typing import List, Dict, Any, Optional

LAYOUTS_DIR = "layouts"
SCRIPTS_DIR = "scripts"


def ensure_directories():
    """Ensure layouts and scripts directories exist."""
    os.makedirs(LAYOUTS_DIR, exist_ok=True)
    os.makedirs(SCRIPTS_DIR, exist_ok=True)


def list_layouts() -> List[str]:
    """Return a list of available layout filenames (without .json extension)."""
    ensure_directories()
    files = [f for f in os.listdir(LAYOUTS_DIR) if f.endswith(".json")]
    return [os.path.splitext(f)[0] for f in files]


def load_layout(name: str) -> Dict[str, Any]:
    """Load a layout by name."""
    path = os.path.join(LAYOUTS_DIR, f"{name}.json")
    if not os.path.exists(path):
        # Return default structure if file doesn't exist
        return create_default_layout(name)

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading layout {name}: {e}")
        return create_default_layout(name)


def save_layout(name: str, layout_data: Dict[str, Any]) -> bool:
    """Save a layout to disk."""
    ensure_directories()
    path = os.path.join(LAYOUTS_DIR, f"{name}.json")
    try:
        with open(path, "w") as f:
            json.dump(layout_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving layout {name}: {e}")
        return False


def create_default_layout(name: str) -> Dict[str, Any]:
    """Create a default empty layout structure."""
    return {
        "name": name,
        "rows": 4,
        "cols": 3,
        "buttons": {},  # Keyed by "row-col", e.g. "0-0": { ... }
    }


def list_scripts() -> List[str]:
    """List available executable scripts."""
    ensure_directories()
    return [
        f
        for f in os.listdir(SCRIPTS_DIR)
        if os.path.isfile(os.path.join(SCRIPTS_DIR, f))
        and os.access(os.path.join(SCRIPTS_DIR, f), os.X_OK)
    ]
