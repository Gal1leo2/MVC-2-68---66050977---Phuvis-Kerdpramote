"""
View 3: ReportView (หน้ารายงานผล)
─ แสดงรายละเอียดของประชาชนว่าใครได้หรือยังไม่ได้ที่พัก
"""

TYPE_LABELS = {"general": "ทั่วไป", "risk_group": "กลุ่มเสี่ยง", "vip": "VIP"}
HEALTH_LABELS = {"healthy": "สุขภาพดี", "chronic": "โรคเรื้อรัง", "critical": "วิกฤต"}


class ReportView:
    """Terminal UI for the results report page."""

    @staticmethod
    def _line(char="═", width=100):
        print(char * width)

    @staticmethod
    def _header(title):
        print()
        ReportView._line("═")
        print(f"  📊  {title}")
        ReportView._line("═")

    # ════════════════════════════════════════════
    #  Sub-menu
    # ════════════════════════════════════════════
    @staticmethod
    def show_menu():
        print()
        ReportView._line("─")
        print("  [ หน้ารายงานผล ]")
        ReportView._line("─")
        print("  1) รายงานภาพรวม (สรุปสถิติ)")
        print("  2) รายชื่อผู้ได้รับที่พัก")
        print("  3) รายชื่อผู้ตกค้าง (ยังไม่ได้ที่พัก)")
        print("  4) รายงานแบบเต็ม (ทุกคน)")
        print("  0) กลับเมนูหลัก")
        ReportView._line("─")
        return input("  เลือก: ").strip()

    # ════════════════════════════════════════════
    #  Report: overview statistics
    # ════════════════════════════════════════════
    @staticmethod
    def show_summary(stats):
        """
        stats = {
            total_citizens, assigned_count, unassigned_count,
            total_shelters, total_capacity, total_occupancy,
            by_type: {general: {total, assigned, unassigned}, ...}
        }
        """
        ReportView._header("รายงานภาพรวมระบบจัดสรรที่พักพิง")

        print(f"""
  ┌──────────────────────────────────────────┐
  │  ประชาชนทั้งหมด      : {stats['total_citizens']:>6} คน         │
  │  ✅ ได้รับที่พักแล้ว   : {stats['assigned_count']:>6} คน         │
  │  ❌ ยังตกค้าง          : {stats['unassigned_count']:>6} คน         │
  ├──────────────────────────────────────────┤
  │  ศูนย์พักพิงทั้งหมด   : {stats['total_shelters']:>6} แห่ง        │
  │  ความจุรวม            : {stats['total_capacity']:>6} คน         │
  │  เข้าพักแล้ว          : {stats['total_occupancy']:>6} คน         │
  │  ที่ว่างเหลือ          : {stats['total_capacity'] - stats['total_occupancy']:>6} คน         │
  └──────────────────────────────────────────┘""")

        # Breakdown by type
        print("\n  ── สถิติแยกตามประเภทประชาชน ──")
        fmt = "    {:<14} {:>6} คน  │ ได้ที่พัก {:>4}  │ ตกค้าง {:>4}"
        ReportView._line("─")
        for ctype in ["risk_group", "vip", "general"]:
            info = stats["by_type"].get(ctype, {"total": 0, "assigned": 0, "unassigned": 0})
            label = TYPE_LABELS.get(ctype, ctype)
            print(fmt.format(label, info["total"], info["assigned"], info["unassigned"]))
        ReportView._line("─")

    # ════════════════════════════════════════════
    #  Report: assigned citizens
    # ════════════════════════════════════════════
    @staticmethod
    def show_assigned(assigned_list):
        """
        assigned_list = [{citizen, shelter_name, assigned_date}, ...]
        """
        ReportView._header(f"ผู้ได้รับที่พัก ({len(assigned_list)} คน)")

        if not assigned_list:
            print("  (ยังไม่มีการจัดสรร)")
            return

        fmt = "  {:<8} {:<22} {:>5}  {:<12} {:<12} {:<30} {:<12}"
        print(fmt.format(
            "รหัส", "ชื่อ-สกุล", "อายุ", "ประเภท", "สุขภาพ", "ศูนย์พักพิง", "วันที่เข้าพัก"
        ))
        ReportView._line("─")

        for item in assigned_list:
            c = item["citizen"]
            name = f"{c['first_name']} {c['last_name']}"
            ctype = TYPE_LABELS.get(c["citizen_type"], c["citizen_type"])
            health = HEALTH_LABELS.get(c["health_status"], c["health_status"])
            print(fmt.format(
                c["citizen_id"], name[:22], c["age"], ctype, health,
                item["shelter_name"][:30], item["assigned_date"],
            ))
        ReportView._line("─")

    # ════════════════════════════════════════════
    #  Report: unassigned citizens
    # ════════════════════════════════════════════
    @staticmethod
    def show_unassigned(unassigned_list):
        """
        unassigned_list = [citizen_dict, ...]
        """
        ReportView._header(f"ผู้ตกค้าง – ยังไม่ได้ที่พัก ({len(unassigned_list)} คน)")

        if not unassigned_list:
            print("  🎉  ทุกคนได้รับที่พักแล้ว!")
            return

        fmt = "  {:<8} {:<22} {:>5}  {:<12} {:<12} {:<12}"
        print(fmt.format("รหัส", "ชื่อ-สกุล", "อายุ", "ประเภท", "สุขภาพ", "วันที่ลงทะเบียน"))
        ReportView._line("─")

        for c in unassigned_list:
            name = f"{c['first_name']} {c['last_name']}"
            ctype = TYPE_LABELS.get(c["citizen_type"], c["citizen_type"])
            health = HEALTH_LABELS.get(c["health_status"], c["health_status"])
            print(fmt.format(
                c["citizen_id"], name[:22], c["age"], ctype, health, c["registered_date"],
            ))
        ReportView._line("─")

    # ════════════════════════════════════════════
    #  Report: full (everyone with status)
    # ════════════════════════════════════════════
    @staticmethod
    def show_full_report(all_citizens_with_status):
        """
        all_citizens_with_status = [{citizen, status:'assigned'/'unassigned', shelter_name, assigned_date}]
        """
        ReportView._header(f"รายงานแบบเต็ม ({len(all_citizens_with_status)} คน)")

        fmt = "  {:<8} {:<22} {:>5}  {:<12} {:<12} {:<6} {:<26}"
        print(fmt.format(
            "รหัส", "ชื่อ-สกุล", "อายุ", "ประเภท", "สุขภาพ", "สถานะ", "ศูนย์พักพิง"
        ))
        ReportView._line("─")

        for item in all_citizens_with_status:
            c = item["citizen"]
            name = f"{c['first_name']} {c['last_name']}"
            ctype = TYPE_LABELS.get(c["citizen_type"], c["citizen_type"])
            health = HEALTH_LABELS.get(c["health_status"], c["health_status"])

            if item["status"] == "assigned":
                status_icon = "✅"
                shelter = item.get("shelter_name", "-")[:26]
            else:
                status_icon = "❌"
                shelter = "- รอจัดสรร -"

            print(fmt.format(
                c["citizen_id"], name[:22], c["age"], ctype, health, status_icon, shelter,
            ))
        ReportView._line("─")
