import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from controllers.citizen_controller import CitizenController
from controllers.shelter_controller import ShelterController
from controllers.report_controller import ReportController


def print_banner():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║                                                                    ║
║         Emergency Shelter Allocation System                        ║
║                                                                    ║
║                                                                    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝""")


def main_menu():
    print()
    print("═" * 50)
    print("  📌  เมนูหลัก (Main Menu)")
    print("═" * 50)
    print("  1) 📋  หน้าลงทะเบียนประชาชน      (View 1)")
    print("  2) 🏠  หน้าจัดสรรที่พัก            (View 2)")
    print("  3) 📊  หน้ารายงานผล               (View 3)")
    print("  0) 🚪  ออกจากโปรแกรม")
    print("═" * 50)
    return input("  เลือก: ").strip()


def main():
    print_banner()

    # Initialize controllers
    citizen_ctrl = CitizenController()
    shelter_ctrl = ShelterController()
    report_ctrl = ReportController()

    while True:
        choice = main_menu()

        if choice == "1":
            citizen_ctrl.run()
        elif choice == "2":
            shelter_ctrl.run()
        elif choice == "3":
            report_ctrl.run()
        elif choice == "0":
            print("\n  👋  ขอบคุณที่ใช้งานระบบ\n")
            break
        else:
            print("  ❌  กรุณาเลือก 0-3")


if __name__ == "__main__":
    main()
