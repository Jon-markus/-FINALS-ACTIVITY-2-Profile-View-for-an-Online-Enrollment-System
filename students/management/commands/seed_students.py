"""Load fictional sample data so the Students page has something to show.

Usage:
    python manage.py seed_students            # only if there are no students yet
    python manage.py seed_students --reset    # wipe students, classes and programs first
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from students.models import (
    Course,
    Enrollment,
    FamilyMember,
    PreviousSchool,
    Program,
    Student,
    SubjectGrade,
)

SUBJECTS = [
    "Oral Communication",
    "General Mathematics",
    "Earth and Life Science",
    "Understanding Culture, Society and Politics",
    "Empowerment Technologies",
    "Physical Education and Health",
]

BSIT = "Bachelor of Science in Information Technology"
ELS = "Bachelor of Arts in English Language Studies"
COMM = "Bachelor of Arts in Communication"
CE = "Bachelor of Science in Civil Engineering"
FASHION = "Bachelor of Arts Major in Fashion Design and Merchandising"

STUDENTS = [
    dict(
        number="026A-10021", first="Maria Angelica", middle="Santos", last="Dela Cruz",
        sex="Female", dob="2007-03-14", pob="Calamba, Laguna", religion="Roman Catholic", tongue="Tagalog",
        email="angelica.delacruz@example.com", phone="0917 555 0142", siblings=2,
        address="Blk 4 Lot 12, Mabuhay St., Brgy. Real, Calamba City, Laguna 4027",
        program=BSIT, section="A", status="active", attendance=100,
        father=("Ramon Dela Cruz", "Electrician", "0918 555 0177"),
        mother=("Cristina S. Dela Cruz", "Teacher", "0917 555 0142"),
        guardian=("Cristina S. Dela Cruz", "Mother", "0917 555 0142"),
        emergency=("Lourdes Santos", "Aunt", "0920 555 0113"),
        prev=("Calamba Integrated School", "2025-2026", "Grade 12", "94.20", "With High Honors"),
        grades=[93, 95, 92, 96, 94, 95],
        enr=("enrolled", "new", "2026-06-02", "quarterly", "36500.00"),
        docs=[1, 1, 1, 1, 1], notes="Member of the campus paper staff.",
    ),
    dict(
        number="026A-10034", first="John Paul", middle="Reyes", last="Bautista",
        sex="Male", dob="2007-08-02", pob="Los Baños, Laguna", religion="Iglesia ni Cristo", tongue="Tagalog",
        email="jp.bautista@example.com", phone="0927 555 0188", siblings=1,
        address="22 Rizal Ave., Brgy. Batong Malake, Los Baños, Laguna 4030",
        program=COMM, section="A", status="active", attendance=98,
        father=("Eduardo Bautista", "Driver", "0927 555 0188"),
        mother=("Marites R. Bautista", "Vendor", "0928 555 0109"),
        guardian=("Eduardo Bautista", "Father", "0927 555 0188"),
        emergency=("Alfredo Reyes", "Grandfather", "0939 555 0121"),
        prev=("Los Baños National High School", "2025-2026", "Grade 12", "88.60", ""),
        grades=[88, 86, 90, 89, 88, 91],
        enr=("pending", "transferee", "2026-06-03", "monthly", "8000.00"),
        docs=[1, 1, 0, 1, 0], notes="Awaiting Good Moral Certificate and Medical Certificate.",
    ),
    dict(
        number="026A-10047", first="Kristine Joy", middle="Villanueva", last="Aquino",
        sex="Female", dob="2006-12-21", pob="Santa Rosa, Laguna", religion="Roman Catholic", tongue="Tagalog",
        email="kj.aquino@example.com", phone="0916 555 0166", siblings=0,
        address="88 Sampaguita St., Brgy. Pulong Santa Cruz, Santa Rosa, Laguna 4026",
        program=CE, section="A", status="active", attendance=100,
        father=("Benjamin Aquino", "Engineer", "0916 555 0166"),
        mother=("Jocelyn V. Aquino", "Nurse", "0917 555 0190"),
        guardian=("Benjamin Aquino", "Father", "0916 555 0166"),
        emergency=("Fe Villanueva", "Grandmother", "0918 555 0134"),
        prev=("Santa Rosa Science High School", "2025-2026", "Grade 12", "97.10", "With Highest Honors"),
        grades=[96, 98, 99, 98, 95, 96],
        enr=("enrolled", "new", "2026-05-20", "full", "36500.00"),
        docs=[1, 1, 1, 1, 1], notes="Academic scholar. Discount to be confirmed with Accounting.",
    ),
    dict(
        number="026A-10052", first="Miguel Antonio", middle="Garcia", last="Fernandez",
        sex="Male", dob="2007-01-09", pob="Biñan, Laguna", religion="Roman Catholic", tongue="Tagalog",
        email="miguel.fernandez@example.com", phone="0905 555 0155", siblings=3,
        address="15 Acacia Lane, Brgy. Canlalay, Biñan, Laguna 4024",
        program=ELS, section="B", status="active", attendance=86,
        father=("Antonio Fernandez", "Accountant", "0905 555 0155"),
        mother=("Elena G. Fernandez", "Homemaker", "0906 555 0171"),
        guardian=("Antonio Fernandez", "Father", "0905 555 0155"),
        emergency=("Raul Garcia", "Uncle", "0915 555 0128"),
        prev=("Biñan City Central School", "2025-2026", "Grade 12", "90.30", "With Honors"),
        grades=[89, 91, 90, 92, 90, 90],
        enr=("enrolled", "new", "2026-06-01", "quarterly", "18250.00"),
        docs=[1, 1, 1, 1, 1], notes="",
    ),
    dict(
        number="026A-10068", first="Shaira Mae", middle="Pascual", last="Lopez",
        sex="Female", dob="2007-05-27", pob="Cabuyao, Laguna", religion="Born Again Christian", tongue="Tagalog",
        email="shaira.lopez@example.com", phone="0936 555 0144", siblings=1,
        address="7 Mahogany Rd., Brgy. Banay-Banay, Cabuyao, Laguna 4025",
        program=FASHION, section="B", status="active", attendance=83,
        father=None,
        mother=("Rowena P. Lopez", "Call center agent", "0936 555 0144"),
        guardian=("Rowena P. Lopez", "Mother", "0936 555 0144"),
        emergency=("Teresita Pascual", "Grandmother", "0917 555 0102"),
        prev=("Cabuyao Academy", "2025-2026", "Grade 12", "91.80", "With Honors"),
        grades=[92, 93, 89, 91, 92, 94],
        enr=("requirements", "transferee", "2026-06-10", "monthly", "0.00"),
        docs=[0, 1, 1, 0, 0], notes="Needs PSA Birth Certificate, 2x2 photo and Medical Certificate.",
    ),
    dict(
        number="026A-10071", first="Daniel", middle="Cruz", last="Mendoza",
        sex="Male", dob="2006-10-30", pob="Calamba, Laguna", religion="Roman Catholic", tongue="Tagalog",
        email="daniel.mendoza@example.com", phone="0919 555 0183", siblings=2,
        address="31 Narra St., Brgy. Parian, Calamba City, Laguna 4027",
        program=BSIT, section="A", status="inactive", attendance=32,
        father=("Jose Mendoza", "Security guard", "0919 555 0183"),
        mother=("Lilibeth C. Mendoza", "Seamstress", "0920 555 0147"),
        guardian=("Jose Mendoza", "Father", "0919 555 0183"),
        emergency=("Noel Cruz", "Uncle", "0921 555 0116"),
        prev=("Calamba Integrated School", "2025-2026", "Grade 12", "85.40", ""),
        grades=[85, 84, 83, 86, 87, 88],
        enr=("enrolled", "new", "2026-05-30", "monthly", "9125.00"),
        docs=[1, 1, 1, 1, 1], notes="On leave of absence this term.",
    ),
    dict(
        number="026A-10085", first="Bea Nicole", middle="Ramos", last="Castillo",
        sex="Female", dob="2007-07-16", pob="San Pedro, Laguna", religion="Roman Catholic", tongue="Tagalog",
        email="bea.castillo@example.com", phone="0917 555 0129", siblings=1,
        address="54 Ilang-Ilang St., Brgy. Landayan, San Pedro, Laguna 4023",
        program=COMM, section="A", status="active", attendance=100,
        father=("Victor Castillo", "Seafarer (OFW)", "0917 555 0129"),
        mother=("Grace R. Castillo", "Bookkeeper", "0918 555 0152"),
        guardian=("Grace R. Castillo", "Mother", "0918 555 0152"),
        emergency=("Dante Ramos", "Uncle", "0922 555 0139"),
        prev=("San Pedro Relocation Center NHS", "2025-2026", "Grade 12", "93.00", "With High Honors"),
        grades=[93, 94, 91, 93, 92, 95],
        enr=("pending", "new", "2026-06-12", "quarterly", "9125.00"),
        docs=[1, 1, 1, 1, 0], notes="Medical Certificate to be submitted next week.",
    ),
]


class Command(BaseCommand):
    help = "Create fictional sample students for the Students page."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing students, classes and programs first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Student.objects.all().delete()  # cascades to enrollments, grades, etc.
            Course.objects.all().delete()
            Program.objects.all().delete()
        elif Student.objects.exists():
            self.stdout.write(self.style.WARNING("Students already exist. Use --reset to replace them."))
            return

        course = Course.objects.create(
            name="IT 101 – Introduction to Computing",
            term="1st Semester, A.Y. 2026-2027",
            instructor="Prof. L. Mercado",
        )

        for d in STUDENTS:
            program, _ = Program.objects.get_or_create(name=d["program"])
            student = Student.objects.create(
                student_number=d["number"], first_name=d["first"], middle_name=d["middle"], last_name=d["last"],
                sex=d["sex"], date_of_birth=date.fromisoformat(d["dob"]), place_of_birth=d["pob"],
                religion=d["religion"], mother_tongue=d["tongue"], email=d["email"], phone=d["phone"],
                address=d["address"], siblings=d["siblings"], notes=d["notes"],
                program=program, section=d["section"], status=d["status"], attendance_rate=d["attendance"],
            )

            for rel in ("father", "mother"):
                person = d[rel]
                if person:
                    FamilyMember.objects.create(
                        student=student, relationship=rel, name=person[0], occupation=person[1], phone=person[2]
                    )
            for rel in ("guardian", "emergency"):
                name, label, phone = d[rel]
                FamilyMember.objects.create(
                    student=student, relationship=rel, name=name, relation_label=label, phone=phone
                )

            school, year, grade, avg, honors = d["prev"]
            PreviousSchool.objects.create(
                student=student, school_name=school, school_year=year, grade_completed=grade,
                general_average=Decimal(avg), honors=honors,
            )
            SubjectGrade.objects.bulk_create(
                [SubjectGrade(student=student, subject=s, grade=g) for s, g in zip(SUBJECTS, d["grades"])]
            )

            status, stype, enrolled_on, plan, paid = d["enr"]
            Enrollment.objects.create(
                student=student, course=course, status=status, student_type=stype,
                date_enrolled=date.fromisoformat(enrolled_on), payment_plan=plan, amount_paid=Decimal(paid),
            )

            # Student.save() already created the default requirement rows; mark the submitted ones.
            for requirement, submitted in zip(student.requirements.all(), d["docs"]):
                requirement.is_submitted = bool(submitted)
                requirement.save(update_fields=["is_submitted"])

        User = get_user_model()
        if not User.objects.exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin12345")
            self.stdout.write(self.style.WARNING("Created dev login: admin / admin12345 (change this)."))

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(STUDENTS)} sample students."))
