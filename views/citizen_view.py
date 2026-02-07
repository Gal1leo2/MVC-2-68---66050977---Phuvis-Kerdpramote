"""
View 1: CitizenView (หน้าลงทะเบียนประชาชน)
─ แสดงประชาชนทั้งหมด
─ แยกตามประเภทประชาชน
─ ฟอร์มลงทะเบียนใหม่
"""

# ─── Mapping ภาษาไท ───
TYPE_LABELS = {
    "general": "ทั่วไป",
    "risk_group": "กลุ่มเสี่ยง",
    "vip": "VIP",
}
HEALTH_LABELS = {
    "healthy": "สุขภาพดี",
    "chronic": "โรคเรื้อรัง",
    "critical": "วิกฤต",
}


class CitizenView:
    """Terminal UI for citizen registration page."""

    # ════════════════════════════════════════════
    #  draw horizontal line
    # ════════════════════════════════════════════
    @staticmethod
    def _line(char="═", width=100):
        print(char * width)

    @staticmethod
    def _header(title):
        print()
        CitizenView._line("═")
        print(f"  📋  {title}")
        CitizenView._line("═")

    # ════════════════════════════════════════════
    #  Sub-menu for this view
    # ════════════════════════════════════════════
    @staticmethod
    def show_menu():
        print()
        CitizenView._line("─")
        print("  [ หน้าลงทะเบียนประชาชน ]")
        CitizenView._line("─")
        print("  1) แสดงประชาชนทั้งหมด")
        print("  2) แสดงแยกตามประเภท (ทั่วไป / กลุ่มเสี่ยง / VIP)")
        print("  3) ลงทะเบียนประชาชนใหม่")
        print("  0) กลับเมนูหลัก")
        CitizenView._line("─")
        return input("  เลือก: ").strip()

    # ════════════════════════════════════════════
    #  Display: all citizens table
    # ════════════════════════════════════════════
    @staticmethod
    def show_all_citizens(citizens):
        CitizenView._header(f"รายชื่อประชาชนทั้งหมด ({len(citizens)} คน)")
        if not citizens:
            print("  (ไม่มีข้อมูล)")
            return

        # Table header
        fmt = "  {:<8} {:<15} {:<20} {:>5}  {:<12} {:<12} {:<12}"
        print(fmt.format(
            "รหัส", "เลขบัตรฯ", "ชื่อ-สกุล", "อายุ",
            "สุขภาพ", "ประเภท", "วันที่ลงทะเบียน"
        ))
        CitizenView._line("─")

        for c in citizens:
            full_name = f"{c['first_name']} {c['last_name']}"
            health = HEALTH_LABELS.get(c["health_status"], c["health_status"])
            ctype = TYPE_LABELS.get(c["citizen_type"], c["citizen_type"])
            print(fmt.format(
                c["citizen_id"],
                c["national_id"][-4:].rjust(13, "*"),  # mask national id
                full_name[:20],
                c["age"],
                health,
                ctype,
                c["registered_date"],
            ))
        CitizenView._line("─")

    # ════════════════════════════════════════════
    #  Display: citizens filtered by type
    # ════════════════════════════════════════════
    @staticmethod
    def show_by_type(citizens_by_type):
        """citizens_by_type = {'general': [...], 'risk_group': [...], 'vip': [...]}"""
        for ctype in ["risk_group", "vip", "general"]:
            group = citizens_by_type.get(ctype, [])
            label = TYPE_LABELS.get(ctype, ctype)
            CitizenView._header(f"ประเภท: {label}  ({len(group)} คน)")
            if not group:
                print("  (ไม่มีข้อมูล)")
                continue

            fmt = "  {:<8} {:<20} {:>5}  {:<12} {:<12}"
            print(fmt.format("รหัส", "ชื่อ-สกุล", "อายุ", "สุขภาพ", "วันที่ลงทะเบียน"))
            CitizenView._line("─")
            for c in group:
                full_name = f"{c['first_name']} {c['last_name']}"
                health = HEALTH_LABELS.get(c["health_status"], c["health_status"])
                print(fmt.format(
                    c["citizen_id"],
                    full_name[:20],
                    c["age"],
                    health,
                    c["registered_date"],
                ))
            CitizenView._line("─")

    # ════════════════════════════════════════════
    #  Form: register new citizen
    # ════════════════════════════════════════════
    @staticmethod
    def registration_form():
        CitizenView._header("ลงทะเบียนประชาชนใหม่")
        print("  (พิมพ์ 'q' เพื่อยกเลิก)\n")

        national_id = input("  เลขบัตรประชาชน (13 หลัก) : ").strip()
        if national_id.lower() == "q":
            return None

        first_name = input("  ชื่อ                       : ").strip()
        if first_name.lower() == "q":
            return None

        last_name = input("  นามสกุล                    : ").strip()
        if last_name.lower() == "q":
            return None

        age_str = input("  อายุ                       : ").strip()
        if age_str.lower() == "q":
            return None

        print("  สุขภาพ: 1) สุขภาพดี  2) โรคเรื้อรัง  3) วิกฤต")
        health_choice = input("  เลือก (1/2/3)              : ").strip()
        health_map = {"1": "healthy", "2": "chronic", "3": "critical"}

        print("  ประเภท: 1) ทั่วไป  2) กลุ่มเสี่ยง  3) VIP")
        type_choice = input("  เลือก (1/2/3)              : ").strip()
        type_map = {"1": "general", "2": "risk_group", "3": "vip"}

        phone = input("  เบอร์โทร (หรือ Enter ข้าม) : ").strip() or "-"

        # A basic validation
        try:
            age = int(age_str)
        except ValueError:
            return {"error": "อายุต้องเป็นตัวเลข"}

        if len(national_id) != 13 or not national_id.isdigit():
            return {"error": "เลขบัตรประชาชนต้องเป็นตัวเลข 13 หลัก"}

        return {
            "national_id": national_id,
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "health_status": health_map.get(health_choice, "healthy"),
            "citizen_type": type_map.get(type_choice, "general"),
            "phone": phone,
        }

    # ════════════════════════════════════════════
    #  Messages
    # ════════════════════════════════════════════
    @staticmethod
    def show_success(msg):
        print(f"\n  ✅  {msg}")

    @staticmethod
    def show_error(msg):
        print(f"\n  ❌  {msg}")
