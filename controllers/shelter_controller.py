"""
Controller: ShelterController
จัดการ logic สำหรับหน้าจัดสรรที่พัก

Business Rules
  1. ศูนย์พักพิงที่เต็มแล้วไม่สามารถรับเพิ่มได้
  2. เด็ก (อายุ < 15) และผู้สูงอายุ (อายุ >= 60) ได้รับการจัดสรรก่อน
  3. ผู้มีความเสี่ยงด้านสุขภาพ (chronic/critical) ต้องถูกจัดไปยังศูนย์ที่มีความเสี่ยงต่ำ (risk_level <= 2)
  4. ประชาชนหนึ่งคนลงทะเบียนได้เพียงครั้งเดียว (handled in CitizenModel)
"""
from models.citizen_model import CitizenModel
from models.shelter_model import ShelterModel
from models.assignment_model import AssignmentModel
from views.shelter_view import ShelterView


class ShelterController:
    """Bridges Models ↔ ShelterView with business logic."""

    def __init__(self):
        self.view = ShelterView

    def run(self):
        """Main loop for shelter allocation page."""
        while True:
            choice = self.view.show_menu()

            if choice == "1":
                self._show_shelters()
            elif choice == "2":
                self._auto_assign()
            elif choice == "3":
                self._manual_assign()
            elif choice == "0":
                break
            else:
                self.view.show_error("กรุณาเลือก 0-3")

    # ══════════════════════════════════════════
    #  Show shelters with occupancy
    # ══════════════════════════════════════════
    def _show_shelters(self):
        shelters = ShelterModel.get_all()
        for s in shelters:
            s["current_occupancy"] = AssignmentModel.count_by_shelter(s["shelter_id"])
        self.view.show_all_shelters(shelters)

    # ══════════════════════════════════════════
    #  Helper: get shelters enriched with occupancy
    # ══════════════════════════════════════════
    @staticmethod
    def _get_shelters_with_occupancy():
        shelters = ShelterModel.get_all()
        for s in shelters:
            s["current_occupancy"] = AssignmentModel.count_by_shelter(s["shelter_id"])
            s["available"] = s["max_capacity"] - s["current_occupancy"]
        return shelters

    # ══════════════════════════════════════════
    #  Helper: get unassigned citizens
    # ══════════════════════════════════════════
    @staticmethod
    def _get_unassigned_citizens():
        all_citizens = CitizenModel.get_all()
        assigned_ids = AssignmentModel.get_assigned_citizen_ids()
        return [c for c in all_citizens if c["citizen_id"] not in assigned_ids]

    # ══════════════════════════════════════════
    #  Business Rule: priority sorting
    #  เด็ก/ผู้สูงอายุ → กลุ่มเสี่ยง → VIP → ทั่วไป
    #  ภายในกลุ่ม: สุขภาพแย่กว่าได้ก่อน
    # ══════════════════════════════════════════
    @staticmethod
    def _priority_sort(citizens):
        """
        Sort citizens by allocation priority (highest first).
        Priority logic:
          - children (age < 15) and elderly (age >= 60) first
          - then by citizen_type: risk_group > vip > general
          - then by health: critical > chronic > healthy
          - then by registration date (earlier = higher priority)
        """
        def sort_key(c):
            # Priority 1: age group (children & elderly first)
            is_priority_age = 0 if (c["age"] < 15 or c["age"] >= 60) else 1

            # Priority 2: citizen type
            type_order = {"risk_group": 0, "vip": 1, "general": 2}
            type_rank = type_order.get(c["citizen_type"], 3)

            # Priority 3: health severity
            health_order = {"critical": 0, "chronic": 1, "healthy": 2}
            health_rank = health_order.get(c["health_status"], 3)

            # Priority 4: registration date (earlier first)
            reg_date = c.get("registered_date", "9999-99-99")

            return (is_priority_age, type_rank, health_rank, reg_date)

        return sorted(citizens, key=sort_key)

    # ══════════════════════════════════════════
    #  Business Rule: find best shelter for citizen
    #  ผู้มีปัญหาสุขภาพ → ศูนย์ risk_level ≤ 2
    # ══════════════════════════════════════════
    @staticmethod
    def _find_best_shelter(citizen, shelters):
        """
        Find the best available shelter for a citizen.
        - If health is chronic/critical → must be risk_level ≤ 2
        - Otherwise → any available shelter, prefer lower risk
        Returns shelter dict or None.
        """
        needs_low_risk = citizen["health_status"] in ("chronic", "critical")

        # Filter available shelters
        candidates = [s for s in shelters if s["available"] > 0]

        if needs_low_risk:
            # Business Rule: health risk → low risk shelter only
            candidates = [s for s in candidates if s["risk_level"] <= 2]

        if not candidates:
            return None

        # Sort by risk_level ascending (safest first), then by available descending
        candidates.sort(key=lambda s: (s["risk_level"], -s["available"]))
        return candidates[0]

    # ══════════════════════════════════════════
    #  Auto-Assign: allocate all unassigned
    # ══════════════════════════════════════════
    def _auto_assign(self):
        unassigned = self._get_unassigned_citizens()
        if not unassigned:
            self.view.show_info("ไม่มีประชาชนที่รอจัดสรร")
            return

        # Sort by priority
        sorted_citizens = self._priority_sort(unassigned)

        # Get live shelter data
        shelters = self._get_shelters_with_occupancy()

        results = []
        for citizen in sorted_citizens:
            best_shelter = self._find_best_shelter(citizen, shelters)
            c_name = f"{citizen['first_name']} {citizen['last_name']}"

            if best_shelter is None:
                # Determine reason
                if citizen["health_status"] in ("chronic", "critical"):
                    reason = "ศูนย์ความเสี่ยงต่ำเต็มหมด (ต้องการ risk ≤ 2)"
                else:
                    reason = "ศูนย์พักพิงเต็มทุกแห่ง"

                results.append({
                    "citizen_id": citizen["citizen_id"],
                    "citizen_name": c_name,
                    "shelter_id": "-",
                    "shelter_name": "-",
                    "status": "fail",
                    "reason": reason,
                })
            else:
                # Assign
                success, _ = AssignmentModel.add(citizen["citizen_id"], best_shelter["shelter_id"])
                if success:
                    # Update local available count
                    best_shelter["available"] -= 1
                    best_shelter["current_occupancy"] += 1

                    results.append({
                        "citizen_id": citizen["citizen_id"],
                        "citizen_name": c_name,
                        "shelter_id": best_shelter["shelter_id"],
                        "shelter_name": best_shelter["name"],
                        "status": "ok",
                        "reason": "",
                    })
                else:
                    results.append({
                        "citizen_id": citizen["citizen_id"],
                        "citizen_name": c_name,
                        "shelter_id": "-",
                        "shelter_name": "-",
                        "status": "fail",
                        "reason": "เกิดข้อผิดพลาด",
                    })

        self.view.show_assignment_results(results)

    # ══════════════════════════════════════════
    #  Manual-Assign: single citizen
    # ══════════════════════════════════════════
    def _manual_assign(self):
        unassigned = self._get_unassigned_citizens()
        shelters = self._get_shelters_with_occupancy()
        available_shelters = [s for s in shelters if s["available"] > 0]

        citizen_id, shelter_id = self.view.manual_assign_form(unassigned, available_shelters)
        if citizen_id is None:
            return

        # ── Validate citizen ──
        citizen = CitizenModel.get_by_id(citizen_id)
        if not citizen:
            self.view.show_error(f"ไม่พบประชาชนรหัส {citizen_id}")
            return

        if AssignmentModel.get_by_citizen(citizen_id):
            self.view.show_error("ประชาชนคนนี้ได้รับที่พักแล้ว")
            return

        # ── Validate shelter ──
        shelter = None
        for s in shelters:
            if s["shelter_id"] == shelter_id:
                shelter = s
                break

        if not shelter:
            self.view.show_error(f"ไม่พบศูนย์พักพิงรหัส {shelter_id}")
            return

        # Business Rule: shelter full
        if shelter["available"] <= 0:
            self.view.show_error(f"ศูนย์ {shelter['name']} เต็มแล้ว (ความจุ {shelter['max_capacity']})")
            return

        # Business Rule: health risk → low risk shelter
        if citizen["health_status"] in ("chronic", "critical") and shelter["risk_level"] > 2:
            self.view.show_error(
                f"ผู้มีปัญหาสุขภาพ ({citizen['health_status']}) "
                f"ต้องจัดไปศูนย์ที่มีความเสี่ยง ≤ 2 "
                f"(ศูนย์นี้ risk_level = {shelter['risk_level']})"
            )
            return

        # ── Assign ──
        success, result = AssignmentModel.add(citizen_id, shelter_id)
        if success:
            self.view.show_success(
                f"จัดสรรสำเร็จ: {citizen['first_name']} {citizen['last_name']} → {shelter['name']}"
            )
        else:
            self.view.show_error(result)
