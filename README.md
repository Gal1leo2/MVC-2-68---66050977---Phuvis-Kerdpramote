# ข้อ 2 - Emergency Shelter Allocation System

---

## Project Structure

```
shelter_mvc/
├── main.py                           ← จุดเริ่มต้นโปรแกรม (Entry Point)
│
├── data/                             ← ฐานข้อมูล CSV (Mock Database)
│   ├── shelters.csv                  ← ตาราง: ศูนย์พักพิง (7 แห่ง)
│   ├── citizens.csv                  ← ตาราง: ประชาชน (35 คน)
│   └── assignments.csv               ← ตาราง: การจัดสรรที่พัก
│
├── models/                           ← [M] Model Layer — Data Access
│   ├── __init__.py
│   ├── shelter_model.py              ← อ่าน/เขียน shelters.csv
│   ├── citizen_model.py              ← อ่าน/เขียน citizens.csv + validation
│   └── assignment_model.py           ← อ่าน/เขียน assignments.csv
│
├── views/                            ← [V] View Layer — Terminal GUI (3 หน้าจอแยกกัน)
│   ├── __init__.py
│   ├── citizen_view.py               ← View 1: หน้าลงทะเบียนประชาชน
│   ├── shelter_view.py               ← View 2: หน้าจัดสรรที่พัก
│   └── report_view.py                ← View 3: หน้ารายงานผล
│
├── controllers/                      ← [C] Controller Layer — Business Logic
│   ├── __init__.py
│   ├── citizen_controller.py         ← จัดการการลงทะเบียน
│   ├── shelter_controller.py         ← จัดการจัดสรร + กฎทางธุรกิจทั้งหมด
│   └── report_controller.py          ← จัดการสร้างรายงาน
│
└── README.md
```

---

## ฐานข้อมูล (Database — CSV)

| ตาราง | ไฟล์ | คอลัมน์ |
|---|---|---|
| **Shelters** | `data/shelters.csv` | shelter_id, name, max_capacity, risk_level |
| **Citizens** | `data/citizens.csv` | citizen_id, national_id, first_name, last_name, age, health_status, citizen_type, registered_date, phone |
| **Assignments** | `data/assignments.csv` | assignment_id, citizen_id, shelter_id, assigned_date, status |

---

## View

### View 1: หน้าลงทะเบียนประชาชน (`citizen_view.py`)
- แสดงประชาชนทั้งหมด
- แสดงแยกตามประเภท (ทั่วไป / กลุ่มเสี่ยง / VIP)
- ฟอร์มลงทะเบียนใหม่

### View 2: หน้าจัดสรรที่พัก (`shelter_view.py`)
- แสดงรายละเอียดศูนย์พักพิง + แท่งกราฟแสดงความจุ
- จัดสรรอัตโนมัติ (Auto-Assign)
- จัดสรรรายบุคคล (Manual-Assign)

### View 3: หน้ารายงานผล (`report_view.py`)
- รายงานภาพรวม (สถิติ)
- รายชื่อผู้ได้รับที่พัก
- รายชื่อผู้ตกค้าง
- รายงานแบบเต็ม (ทุกคน)

---

## Business Logic and Rules 

| กฎ | อธิบาย | ตรวจสอบใน |
|---|---|---|
| 1 | ศูนย์พักพิงที่เต็มแล้วไม่สามารถรับเพิ่มได้ | `shelter_controller.py` |
| 2 | เด็ก (อายุ < 15) และผู้สูงอายุ (อายุ ≥ 60) ได้รับการจัดสรรก่อน | `_priority_sort()` |
| 3 | ผู้มีความเสี่ยงด้านสุขภาพ (chronic/critical) จัดไปศูนย์ risk_level ≤ 2 | `_find_best_shelter()` |
| 4 | ประชาชนหนึ่งคนลงทะเบียนได้เพียงครั้งเดียว | `citizen_model.py` |

---

## Sample Data

- ศูนย์พักพิง **7** แห่ง (ความจุรวม 29 คน)
- ประชาชน **35** คน
- เมื่อ Auto-Assign: จัดสรรได้ 29 คน, **ตกค้าง 6 คน** ✓
- ลำดับความสำคัญในการจัดสรร: เด็ก/ผู้สูงอายุ → กลุ่มเสี่ยง → VIP → ทั่วไป

---

## MVC Flow

```
User Input → [Controller] → reads/writes → [Model/CSV]
                  ↓
             [View] → Terminal Display
```

Controller ทำหน้าที่ตัดสินใจตาม Business Rules แล้วส่งข้อมูลไปให้ View แสดงผล
Model ทำหน้าที่อ่าน/เขียนไฟล์ CSV โดยไม่มี business logic
View ทำหน้าที่แสดงผลอย่างเดียว ไม่มีการเข้าถึง Model โดยตรง
