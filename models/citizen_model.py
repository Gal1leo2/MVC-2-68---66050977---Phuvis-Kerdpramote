"""
Model: CitizenModel
ดูแลข้อมูลประชาชน (citizens.csv)
"""
import csv
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CITIZENS_FILE = os.path.join(DATA_DIR, "citizens.csv")

FIELDS = [
    "citizen_id", "national_id", "first_name", "last_name",
    "age", "health_status", "citizen_type", "registered_date", "phone"
]


class CitizenModel:
    """Data access for citizens table."""

    # ──────────── READ ────────────
    @staticmethod
    def get_all():
        """Return list of all citizens as dicts."""
        citizens = []
        with open(CITIZENS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["age"] = int(row["age"])
                citizens.append(row)
        return citizens

    @staticmethod
    def get_by_id(citizen_id):
        for c in CitizenModel.get_all():
            if c["citizen_id"] == citizen_id:
                return c
        return None

    @staticmethod
    def get_by_national_id(national_id):
        for c in CitizenModel.get_all():
            if c["national_id"] == national_id:
                return c
        return None

    @staticmethod
    def get_by_type(citizen_type):
        """Filter citizens by type: general, risk_group, vip."""
        return [c for c in CitizenModel.get_all() if c["citizen_type"] == citizen_type]

    # ──────────── WRITE ────────────
    @staticmethod
    def _write_all(citizens):
        """Overwrite entire CSV with updated list."""
        with open(CITIZENS_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(citizens)

    @staticmethod
    def add(citizen_data):
        """
        Add a new citizen. Auto-generates citizen_id.
        Returns (True, citizen_dict) on success, (False, error_msg) on failure.
        """
        citizens = CitizenModel.get_all()

        # Business Rule หลักตือ ประชาชนหนึ่งคนลงทะเบียนได้เพียงครั้งเดียว
        for c in citizens:
            if c["national_id"] == citizen_data["national_id"]:
                return False, "เลขบัตรประชาชนนี้ลงทะเบียนแล้ว (Duplicate national ID)"

        # Auto-generate next citizen_id
        if citizens:
            max_num = max(int(c["citizen_id"][1:]) for c in citizens)
            new_id = f"C{max_num + 1:03d}"
        else:
            new_id = "C001"

        new_citizen = {
            "citizen_id": new_id,
            "national_id": citizen_data["national_id"],
            "first_name": citizen_data["first_name"],
            "last_name": citizen_data["last_name"],
            "age": citizen_data["age"],
            "health_status": citizen_data["health_status"],
            "citizen_type": citizen_data["citizen_type"],
            "registered_date": str(date.today()),
            "phone": citizen_data.get("phone", "-"),
        }

        citizens.append(new_citizen)
        CitizenModel._write_all(citizens)
        return True, new_citizen

    @staticmethod
    def count():
        return len(CitizenModel.get_all())
