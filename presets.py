"""
Default crosshair config, built-in preset library, and disk persistence for
user-saved presets and the "last used" crosshair.
"""

import os
import json
import re

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_DIR = os.path.join(APP_DIR, "presets")
LAST_USED_PATH = os.path.join(APP_DIR, "current_crosshair.json")

os.makedirs(PRESETS_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "name": "Custom",
    "color": "#39ff14",
    "opacity": 100,
    "crossEnabled": True,
    "thickness": 2,
    "length": 10,
    "gap": 3,
    "tShape": False,
    "rotation": 0,
    "centerDot": False,
    "dotSize": 2,
    "dotOpacity": 100,
    "circleEnabled": False,
    "circleRadius": 20,
    "circleThickness": 1,
    "outlineEnabled": True,
    "outlineColor": "#000000",
    "outlineWidth": 1,
    "outlineOpacity": 100,
}

BUILTIN_PRESETS = [
    {"name": "Classic Cross", "color": "#39ff14", "thickness": 2, "length": 10, "gap": 3},
    {"name": "Micro Dot", "color": "#ffffff", "crossEnabled": False, "centerDot": True, "dotSize": 2, "dotOpacity": 100},
    {"name": "Duty Cross", "color": "#3fe0d0", "thickness": 1, "length": 8, "gap": 5},
    {"name": "Operator", "color": "#ff7a1a", "thickness": 3, "length": 12, "gap": 2, "centerDot": True, "dotSize": 3, "outlineWidth": 2},
    {"name": "Sniper Ring", "color": "#ffffff", "crossEnabled": False, "centerDot": True, "dotSize": 2, "circleEnabled": True, "circleRadius": 26, "circleThickness": 1},
    {"name": "T-Rex", "color": "#ffd400", "thickness": 3, "length": 14, "gap": 4, "tShape": True, "outlineWidth": 2},
    {"name": "Ring & Cross", "color": "#39ff14", "thickness": 1, "length": 9, "gap": 8, "circleEnabled": True, "circleRadius": 18, "circleThickness": 1},
    {"name": "Pixel Precision", "color": "#39ff14", "thickness": 1, "length": 5, "gap": 1, "outlineEnabled": False},
    {"name": "Phantom X", "color": "#ff4b5c", "thickness": 2, "length": 11, "gap": 3, "rotation": 45},
    {"name": "Ghost", "color": "#ffffff", "opacity": 35, "thickness": 2, "length": 22, "gap": 6, "outlineEnabled": False},
    {"name": "Vector", "color": "#3fe0d0", "thickness": 1, "length": 28, "gap": 0},
    {"name": "Bracket", "color": "#ffffff", "thickness": 2, "length": 6, "gap": 10, "centerDot": True, "dotSize": 2, "circleEnabled": True, "circleRadius": 14, "circleThickness": 1},
]


def make_config(overrides=None):
    cfg = DEFAULT_CONFIG.copy()
    if overrides:
        cfg.update(overrides)
    return cfg


def load_last_used():
    if os.path.exists(LAST_USED_PATH):
        try:
            with open(LAST_USED_PATH, "r") as f:
                data = json.load(f)
            return make_config(data)
        except Exception:
            pass
    return make_config()


def save_last_used(cfg):
    try:
        with open(LAST_USED_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def _slugify(name):
    slug = re.sub(r"[^a-z0-9\-_]+", "_", name.strip().lower())
    return slug or "preset"


def list_user_presets():
    """Returns list of (display_name, filepath) for every saved preset on disk."""
    items = []
    for fname in sorted(os.listdir(PRESETS_DIR)):
        if fname.endswith(".json"):
            path = os.path.join(PRESETS_DIR, fname)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                items.append((data.get("name", fname[:-5]), path))
            except Exception:
                continue
    return items


def save_user_preset(cfg):
    name = cfg.get("name") or "Preset"
    path = os.path.join(PRESETS_DIR, _slugify(name) + ".json")
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)
    return path


def delete_user_preset(path):
    try:
        os.remove(path)
    except Exception:
        pass


def load_preset_file(path):
    with open(path, "r") as f:
        data = json.load(f)
    return make_config(data)
