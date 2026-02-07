"""
Model: AssignmentModel
ดูแลข้อมูลการจัดสรรที่พักพิง (assignments.csv)
"""
import csv
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, "assignments.csv")

FIELDS = ["assignment_id", "citizen_id", "shelter_id", "assigned_date", "status"]


class AssignmentModel:
    """Data access for assignments table."""

    # ──────────── READ ────────────
    @staticmethod
    def get_all():
        assignments = []
        with open(ASSIGNMENTS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("assignment_id"):  # skip blank rows
                    assignments.append(row)
        return assignments

    @staticmethod
    def get_active():
        """Return only active (not discharged) assignments."""
        return [a for a in AssignmentModel.get_all() if a["status"] == "active"]

    @staticmethod
    def get_by_citizen(citizen_id):
        """Check if a citizen already has an active assignment."""
        for a in AssignmentModel.get_active():
            if a["citizen_id"] == citizen_id:
                return a
        return None

    @staticmethod
    def count_by_shelter(shelter_id):
        """Count active occupants in a shelter."""
        return sum(1 for a in AssignmentModel.get_active() if a["shelter_id"] == shelter_id)

    @staticmethod
    def get_assigned_citizen_ids():
        """Return set of citizen_ids that have active assignments."""
        return {a["citizen_id"] for a in AssignmentModel.get_active()}

    # ──────────── WRITE ────────────
    @staticmethod
    def _write_all(assignments):
        with open(ASSIGNMENTS_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(assignments)

    @staticmethod
    def add(citizen_id, shelter_id):
        """
        Create a new assignment.
        Returns (True, assignment_dict) or (False, error_msg).
        """
        assignments = AssignmentModel.get_all()

        # Check duplicate
        for a in assignments:
            if a["citizen_id"] == citizen_id and a["status"] == "active":
                return False, "ประชาชนคนนี้ได้รับการจัดสรรแล้ว (Already assigned)"

        # Auto-generate ID
        if assignments:
            max_num = max(int(a["assignment_id"][1:]) for a in assignments)
            new_id = f"A{max_num + 1:03d}"
        else:
            new_id = "A001"

        new_assignment = {
            "assignment_id": new_id,
            "citizen_id": citizen_id,
            "shelter_id": shelter_id,
            "assigned_date": str(date.today()),
            "status": "active",
        }

        assignments.append(new_assignment)
        AssignmentModel._write_all(assignments)
        return True, new_assignment
