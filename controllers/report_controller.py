"""
Controller: ReportController
จัดการ logic สำหรับหน้ารายงานผล
"""
from models.citizen_model import CitizenModel
from models.shelter_model import ShelterModel
from models.assignment_model import AssignmentModel
from views.report_view import ReportView


class ReportController:
    """Bridges Models ↔ ReportView."""

    def __init__(self):
        self.view = ReportView

    def run(self):
        """Main loop for report page."""
        while True:
            choice = self.view.show_menu()

            if choice == "1":
                self._show_summary()
            elif choice == "2":
                self._show_assigned()
            elif choice == "3":
                self._show_unassigned()
            elif choice == "4":
                self._show_full_report()
            elif choice == "0":
                break
            else:
                print("  ❌ กรุณาเลือก 0-4")

    # ──────── helpers ────────

    def _build_data(self):
        """Build enriched data for all citizens."""
        all_citizens = CitizenModel.get_all()
        assignments = AssignmentModel.get_active()
        shelters = {s["shelter_id"]: s for s in ShelterModel.get_all()}

        # Map citizen_id → assignment
        assign_map = {}
        for a in assignments:
            assign_map[a["citizen_id"]] = a

        assigned_list = []
        unassigned_list = []
        full_list = []

        for c in all_citizens:
            a = assign_map.get(c["citizen_id"])
            if a:
                shelter = shelters.get(a["shelter_id"], {})
                item = {
                    "citizen": c,
                    "status": "assigned",
                    "shelter_name": shelter.get("name", "?"),
                    "assigned_date": a["assigned_date"],
                }
                assigned_list.append(item)
                full_list.append(item)
            else:
                unassigned_list.append(c)
                full_list.append({
                    "citizen": c,
                    "status": "unassigned",
                    "shelter_name": "-",
                    "assigned_date": "-",
                })

        return all_citizens, assigned_list, unassigned_list, full_list

    # ──────── actions ────────

    def _show_summary(self):
        all_citizens, assigned_list, unassigned_list, _ = self._build_data()
        shelters = ShelterModel.get_all()

        total_capacity = sum(s["max_capacity"] for s in shelters)
        total_occupancy = sum(AssignmentModel.count_by_shelter(s["shelter_id"]) for s in shelters)

        # By type breakdown
        by_type = {}
        assigned_ids = AssignmentModel.get_assigned_citizen_ids()
        for c in all_citizens:
            ct = c["citizen_type"]
            if ct not in by_type:
                by_type[ct] = {"total": 0, "assigned": 0, "unassigned": 0}
            by_type[ct]["total"] += 1
            if c["citizen_id"] in assigned_ids:
                by_type[ct]["assigned"] += 1
            else:
                by_type[ct]["unassigned"] += 1

        stats = {
            "total_citizens": len(all_citizens),
            "assigned_count": len(assigned_list),
            "unassigned_count": len(unassigned_list),
            "total_shelters": len(shelters),
            "total_capacity": total_capacity,
            "total_occupancy": total_occupancy,
            "by_type": by_type,
        }
        self.view.show_summary(stats)

    def _show_assigned(self):
        _, assigned_list, _, _ = self._build_data()
        self.view.show_assigned(assigned_list)

    def _show_unassigned(self):
        _, _, unassigned_list, _ = self._build_data()
        self.view.show_unassigned(unassigned_list)

    def _show_full_report(self):
        _, _, _, full_list = self._build_data()
        self.view.show_full_report(full_list)
