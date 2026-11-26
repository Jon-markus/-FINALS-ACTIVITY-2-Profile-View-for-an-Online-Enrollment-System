from datetime import date
from decimal import Decimal

from django.core.validators import MaxValueValidator
from django.db import models

DEFAULT_REQUIREMENTS = [
    "PSA Birth Certificate",
    "Form 138 (Report Card)",
    "Good Moral Certificate",
    "2x2 ID Photo",
    "Medical Certificate",
]


class Program(models.Model):
    """A degree program, for example Bachelor of Science in Information Technology."""

    name = models.CharField(max_length=160, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Course(models.Model):
    """A class that students enroll in. The Students page lists one class at a time."""

    name = models.CharField(max_length=160)
    term = models.CharField(max_length=60, default="1st Semester, A.Y. 2026-2027")
    instructor = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("name", "term")]

    def __str__(self):
        return self.name


class Student(models.Model):
    class Sex(models.TextChoices):
        FEMALE = "Female", "Female"
        MALE = "Male", "Male"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    # Identity
    student_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80)
    sex = models.CharField(max_length=6, choices=Sex.choices)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=120, blank=True)
    nationality = models.CharField(max_length=60, default="Filipino")
    religion = models.CharField(max_length=80, blank=True)
    mother_tongue = models.CharField(max_length=60, blank=True)
    siblings = models.PositiveSmallIntegerField(default=0)

    # Placement
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name="students")
    section = models.CharField(max_length=10, default="A")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    attendance_rate = models.PositiveSmallIntegerField(
        default=100, validators=[MaxValueValidator(100)], help_text="Percent of sessions attended."
    )

    # Contact
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)

    # Registrar
    notes = models.TextField("Registrar notes", blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating:
            Requirement.objects.bulk_create(
                [Requirement(student=self, name=n) for n in DEFAULT_REQUIREMENTS]
            )

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)

    @property
    def initials(self):
        return (self.first_name[:1] + self.last_name[:1]).upper()

    @property
    def avatar_tone(self):
        return (self.pk or 0) % 5

    @property
    def attendance_class(self):
        return "ok" if self.attendance_rate >= 90 else "bad"

    @property
    def age(self):
        today = date.today()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years


class FamilyMember(models.Model):
    class Relationship(models.TextChoices):
        FATHER = "father", "Father"
        MOTHER = "mother", "Mother"
        GUARDIAN = "guardian", "Legal guardian"
        EMERGENCY = "emergency", "Emergency contact"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="family")
    relationship = models.CharField(max_length=10, choices=Relationship.choices)
    name = models.CharField(max_length=120)
    relation_label = models.CharField(
        max_length=60, blank=True, help_text="For guardians and emergency contacts, e.g. Aunt."
    )
    occupation = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        unique_together = [("student", "relationship")]

    def __str__(self):
        return f"{self.get_relationship_display()}: {self.name}"


class PreviousSchool(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="previous_school")
    school_name = models.CharField(max_length=160)
    school_year = models.CharField(max_length=9)
    grade_completed = models.CharField(max_length=30)
    general_average = models.DecimalField(max_digits=5, decimal_places=2)
    honors = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"{self.school_name} ({self.school_year})"


class SubjectGrade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grades")
    subject = models.CharField(max_length=80)
    grade = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.subject}: {self.grade}"

    @property
    def passed(self):
        return self.grade >= 75


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        PENDING = "pending", "Pending"
        REQUIREMENTS = "requirements", "For Requirements"

    class StudentType(models.TextChoices):
        NEW = "new", "New"
        CONTINUING = "continuing", "Continuing"
        TRANSFEREE = "transferee", "Transferee"

    class PaymentPlan(models.TextChoices):
        FULL = "full", "Full payment"
        QUARTERLY = "quarterly", "Quarterly"
        MONTHLY = "monthly", "Monthly"

    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="enrollment")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="enrollments")
    status = models.CharField(max_length=14, choices=Status.choices, default=Status.PENDING)
    student_type = models.CharField(max_length=12, choices=StudentType.choices, default=StudentType.NEW)
    date_enrolled = models.DateField(default=date.today)
    payment_plan = models.CharField(max_length=10, choices=PaymentPlan.choices, default=PaymentPlan.MONTHLY)

    tuition = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("28000.00"))
    misc_fees = models.DecimalField("Miscellaneous", max_digits=10, decimal_places=2, default=Decimal("6000.00"))
    books_fees = models.DecimalField("Books and ID", max_digits=10, decimal_places=2, default=Decimal("2500.00"))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.student} → {self.course} ({self.get_status_display()})"

    @property
    def total_fees(self):
        return self.tuition + self.misc_fees + self.books_fees

    @property
    def balance(self):
        return self.total_fees - self.amount_paid

    @property
    def status_class(self):
        return {"enrolled": "ok", "pending": "warn"}.get(self.status, "bad")


class Requirement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="requirements")
    name = models.CharField(max_length=120)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]
        unique_together = [("student", "name")]

    def __str__(self):
        return f"{self.name} ({'submitted' if self.is_submitted else 'missing'})"
