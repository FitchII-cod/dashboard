from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

PROFILES = {
    "bastian": {
        "label": "バスチャン",
        "birthdays_csv": DATA_DIR / "birthdays" / "bastian.csv",
        # tu pourrais plus tard ajouter ville météo, etc.
    },
    "axelle": {
        "label": "アクセル",
        "birthdays_csv": DATA_DIR / "birthdays" / "axelle.csv",
    },
}
DEFAULT_PROFILE = "bastian"

TZ = "Europe/Paris"
