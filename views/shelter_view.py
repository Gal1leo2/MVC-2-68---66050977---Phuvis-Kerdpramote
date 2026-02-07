"""
View 2: ShelterView (หน้าจัดสรรที่พัก)
─ แสดงรายละเอียดที่พัก
─ แสดงจำนวนคนที่พักในปัจจุบัน
─ จัดสรรที่พักให้ประชาชน
"""

RISK_LABELS = {
    1: "★☆☆☆☆ ต่ำมาก",
    2: "★★☆☆☆ ต่ำ",
    3: "★★★☆☆ ปานกลาง",
    4: "★★★★☆ สูง",
    5: "★★★★★ สูงมาก",
}


class ShelterView:
    """Terminal UI for shelter allocation page."""

    @staticmethod
    def _line(char="═", width=100):
        print(char * width)

    @staticmethod
    def _header(title):
        print()
        ShelterView._line("═")
        print(f"  🏠  {title}")
        ShelterView._line("═")

    # ════════════════════════════════════════════
    #  Sub-menu
    # ════════════════════════════════════════════
    @staticmethod
    def show_menu():
        print()
        ShelterView._line("─")
        print("  [ หน้าจัดสรรที่พัก ]")
        ShelterView._line("─")
        print("  1) แสดงรายละเอียดศูนย์พักพิงทั้งหมด")
        print("  2) จัดสรรที่พักอัตโนมัติ (Auto-Assign)")
        print("  3) จัดสรรที่พักรายบุคคล (Manual-Assign)")
        print("  0) กลับเมนูหลัก")
        ShelterView._line("─")
        return input("  เลือก: ").strip()

    # ════════════════════════════════════════════
    #  Display: shelter table with occupancy
    # ════════════════════════════════════════════
    @staticmethod
    def show_all_shelters(shelters_with_occupancy):
        """
        shelters_with_occupancy = list of dicts:
            {shelter_id, name, max_capacity, risk_level, current_occupancy, available}
        """
        ShelterView._header("รายละเอียดศูนย์พักพิงทั้งหมด")

        fmt = "  {:<8} {:<32} {:>6} {:>8} {:>8}  {:<18}"
        print(fmt.format(
            "รหัส", "ชื่อศูนย์", "ความจุ", "ปัจจุบัน", "ว่าง", "ระดับความเสี่ยง"
        ))
        ShelterView._line("─")

        total_cap = 0
        total_occ = 0

        for s in shelters_with_occupancy:
            occ = s["current_occupancy"]
            cap = s["max_capacity"]
            avail = cap - occ
            risk = RISK_LABELS.get(s["risk_level"], str(s["risk_level"]))
            status_bar = "█" * occ + "░" * avail

            total_cap += cap
            total_occ += occ

            print(fmt.format(
                s["shelter_id"],
                s["name"][:32],
                cap,
                occ,
                avail,
                risk,
            ))
            print(f"           [{status_bar}] {occ}/{cap}")

        ShelterView._line("─")
        print(f"  รวม: ความจุทั้งหมด {total_cap} | เข้าพัก {total_occ} | ว่าง {total_cap - total_occ}")
        ShelterView._line("─")

    # ════════════════════════════════════════════
    #  Display: assignment result log
    # ════════════════════════════════════════════
    @staticmethod
    def show_assignment_results(results):
        """
        results = list of dicts:
            {citizen_id, citizen_name, shelter_id, shelter_name, status, reason}
        """
        ShelterView._header("ผลการจัดสรรที่พัก")

        ok_count = sum(1 for r in results if r["status"] == "ok")
        fail_count = sum(1 for r in results if r["status"] == "fail")

        fmt = "  {:<8} {:<22} {:<8} {:<30} {}"
        print(fmt.format("รหัส", "ชื่อ-สกุล", "ศูนย์", "ชื่อศูนย์", "สถานะ"))
        ShelterView._line("─")

        for r in results:
            icon = "✅" if r["status"] == "ok" else "❌"
            shelter_id = r.get("shelter_id", "-")
            shelter_name = r.get("shelter_name", "-")
            reason = r.get("reason", "")
            detail = f"{icon} {reason}" if reason else icon
            print(fmt.format(
                r["citizen_id"],
                r["citizen_name"][:22],
                shelter_id,
                shelter_name[:30],
                detail,
            ))

        ShelterView._line("─")
        print(f"  สรุป: จัดสรรสำเร็จ {ok_count} คน | ไม่สำเร็จ {fail_count} คน")

    # ════════════════════════════════════════════
    #  Form: manual assignment
    # ════════════════════════════════════════════
    @staticmethod
    def manual_assign_form(unassigned_citizens, available_shelters):
        ShelterView._header("จัดสรรที่พักรายบุคคล")

        if not unassigned_citizens:
            print("  ไม่มีประชาชนที่รอจัดสรร")
            return None, None

        if not available_shelters:
            print("  ศูนย์พักพิงเต็มทุกแห่ง")
            return None, None

        print("\n  ── ประชาชนที่ยังไม่ได้ที่พัก ──")
        for c in unassigned_citizens:
            print(f"    {c['citizen_id']}  {c['first_name']} {c['last_name']}  "
                  f"อายุ {c['age']}  สุขภาพ: {c['health_status']}  ประเภท: {c['citizen_type']}")

        print("\n  ── ศูนย์พักพิงที่ยังว่าง ──")
        for s in available_shelters:
            avail = s["max_capacity"] - s["current_occupancy"]
            print(f"    {s['shelter_id']}  {s['name']}  "
                  f"ว่าง: {avail}/{s['max_capacity']}  ความเสี่ยง: {s['risk_level']}")

        print()
        cid = input("  รหัสประชาชน (เช่น C001) หรือ 'q' ยกเลิก: ").strip()
        if cid.lower() == "q":
            return None, None
        sid = input("  รหัสศูนย์ (เช่น S001)                   : ").strip()
        if sid.lower() == "q":
            return None, None

        return cid, sid

    # ════════════════════════════════════════════
    #  Messages
    # ════════════════════════════════════════════
    @staticmethod
    def show_success(msg):
        print(f"\n  ✅  {msg}")

    @staticmethod
    def show_error(msg):
        print(f"\n  ❌  {msg}")

    @staticmethod
    def show_info(msg):
        print(f"\n  ℹ️   {msg}")
