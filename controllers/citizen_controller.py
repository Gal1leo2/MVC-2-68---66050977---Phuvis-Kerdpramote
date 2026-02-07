"""
Controller: CitizenController
จัดการ logic สำหรับหน้าลงทะเบียนประชาชน
"""
from models.citizen_model import CitizenModel
from views.citizen_view import CitizenView


class CitizenController:
    """Bridges CitizenModel ↔ CitizenView."""

    def __init__(self):
        self.model = CitizenModel
        self.view = CitizenView

    def run(self):
        """Main loop for citizen registration page."""
        while True:
            choice = self.view.show_menu()

            if choice == "1":
                self._show_all()
            elif choice == "2":
                self._show_by_type()
            elif choice == "3":
                self._register_new()
            elif choice == "0":
                break
            else:
                self.view.show_error("กรุณาเลือก 0-3")

    # ──────── internal actions ────────

    def _show_all(self):
        citizens = self.model.get_all()
        self.view.show_all_citizens(citizens)

    def _show_by_type(self):
        all_citizens = self.model.get_all()
        by_type = {}
        for c in all_citizens:
            by_type.setdefault(c["citizen_type"], []).append(c)
        self.view.show_by_type(by_type)

    def _register_new(self):
        form_data = self.view.registration_form()

        if form_data is None:
            self.view.show_info("ยกเลิกการลงทะเบียน")
            return

        if "error" in form_data:
            self.view.show_error(form_data["error"])
            return

        success, result = self.model.add(form_data)

        if success:
            self.view.show_success(
                f"ลงทะเบียนสำเร็จ: {result['citizen_id']} "
                f"{result['first_name']} {result['last_name']}"
            )
        else:
            self.view.show_error(result)
