"""
Model: ShelterModel
ดูแลข้อมูลศูนย์พักพิง (shelters.csv)
"""
import csv
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SHELTERS_FILE = os.path.join(DATA_DIR, "shelters.csv")


class ShelterModel:
    """Data access for shelters table."""

    FIELDS = ["shelter_id", "name", "max_capacity", "risk_level"]

    # ──────────── READ ────────────
    @staticmethod
    def get_all():
        """Return list of all shelters as dicts."""
        shelters = []
        with open(SHELTERS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["max_capacity"] = int(row["max_capacity"])
                row["risk_level"] = int(row["risk_level"])
                shelters.append(row)
        return shelters

    @staticmethod
    def get_by_id(shelter_id):
        """Return a single shelter dict or None."""
        for s in ShelterModel.get_all():
            if s["shelter_id"] == shelter_id:
                return s
        return None
