from urllib.parse import urlencode

from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Course, Student

TABS = [
    ("personal", "Personal Info"),
    ("contact", "Contact"),
    ("background", "Family Background"),
    ("academic", "Academic"),
    ("enrollment", "Enrollment & Fees"),
    ("documents", "Documents"),
]
TAB_KEYS = {key for key, _ in TABS}
STATUS_FILTERS = {"all", "active", "inactive"}


def _params(request):
    """The list-page state (class, search, filter, layout) that links carry along."""
    out = {}
    for key in ("course", "q", "status", "view"):
        value = request.GET.get(key, "").strip()
        if value:
            out[key] = value
    return out


def _current_course(courses, course_id):
    if course_id.isdigit():
        for course in courses:
            if course.pk == int(course_id):
                return course
    return courses[0] if courses else None


def student_list(request):
    """Dashboard: summary cards and a searchable, filterable class list."""
    params = _params(request)
    courses = list(Course.objects.all())
    course = _current_course(courses, params.get("course", ""))

    q = params.get("q", "")
    status = params.get("status", "all")
    if status not in STATUS_FILTERS:
        status = "all"
    view = "list" if params.get("view") == "list" else "grid"

    class_students = Student.objects.select_related("program", "enrollment")
    class_students = class_students.filter(enrollment__course=course) if course else class_students.none()

    agg = class_students.aggregate(
        total=Count("id"),
        active=Count("id", filter=Q(status=Student.Status.ACTIVE)),
        programs=Count("program", distinct=True),
        attendance=Avg("attendance_rate"),
    )
    stats = {
        "total": agg["total"],
        "active": agg["active"],
        "programs": agg["programs"],
        "attendance": round(agg["attendance"]) if agg["attendance"] is not None else None,
    }

    students = class_students
    if status != "all":
        students = students.filter(status=status)
    if q:
        students = students.filter(
            Q(first_name__icontains=q)
            | Q(middle_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(student_number__icontains=q)
            | Q(program__name__icontains=q)
        )
    students = students.order_by("last_name", "first_name")

    def link(**override):
        merged = {k: v for k, v in {**params, **override}.items() if v}
        qs = urlencode(merged)
        return request.path + ("?" + qs if qs else "")

    status_tabs = [
        {"label": "All", "href": link(status=""), "active": status == "all"},
        {"label": "Active", "href": link(status="active"), "active": status == "active"},
        {"label": "Inactive", "href": link(status="inactive"), "active": status == "inactive"},
    ]

    return render(
        request,
        "students/student_list.html",
        {
            "courses": courses,
            "course": course,
            "students": students,
            "stats": stats,
            "q": q,
            "status": status,
            "view": view,
            "status_tabs": status_tabs,
            "grid_href": link(view=""),
            "list_href": link(view="list"),
            "keep": urlencode(params),
        },
    )


def student_detail(request, pk):
    """One student's full record, split into tabs."""
    student = get_object_or_404(
        Student.objects.select_related("program", "previous_school", "enrollment__course"),
        pk=pk,
    )
    tab = request.GET.get("tab", "personal")
    if tab not in TAB_KEYS:
        tab = "personal"

    requirements = list(student.requirements.all())
    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "tab": tab,
            "tabs": TABS,
            "family": {m.relationship: m for m in student.family.all()},
            "grades": student.grades.all(),
            "requirements": requirements,
            "missing_count": sum(1 for r in requirements if not r.is_submitted),
            "keep": urlencode(_params(request)),
        },
    )
