# Online Enrollment System: Students page and profiles

A Django app for reviewing the students in a class. There is no login page: the site opens straight to the Students page.

- **Students page:** four summary cards (total, active, programs, average attendance), a search box, All / Active / Inactive filters, and a grid or list layout. Each student is a card showing status, program, section and attendance.
- **Student profile:** click a card to open a full record with tabs for Personal Info, Contact, Family Background, Academic, Enrollment & Fees, and Documents.
- **Add and edit:** the "Add student", "Edit record" and "Manage records" buttons open the Django admin site, which keeps its own built-in login.

## Run it

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations students
python manage.py migrate
python manage.py seed_students    # fictional sample data + admin account
python manage.py runserver
```

Open http://127.0.0.1:8000/. The Students page needs no username or password.

To add or edit students, use the admin buttons. They ask you to log in at `/admin/` with `admin` / `admin12345` (created by the seed command; change it before using this for anything real).

If you ran an earlier version of this project, delete `db.sqlite3` and the `students/migrations/` folder first.

## Who can see what

Anyone who can reach the site can view every student's record, because the Students page and profiles are public. That is fine for a local demo or class activity. Before putting real student data online, add login protection back (for example Django's `login_required` on the two views in `students/views.py`).

## Project layout

```
config/                      Settings and root URLs
students/
  models.py                  Program, Course, Student, FamilyMember, PreviousSchool,
                             SubjectGrade, Enrollment, Requirement
  views.py                   student_list and student_detail
  admin.py                   Admin with inlines for every related record
  templates/students/        base, shell (sidebar), student_list, student_detail
  static/students/style.css  Styles (light and dark)
  management/commands/seed_students.py
```

## How it works

- The class, search text, status filter and layout live in the query string, so the back link from a profile returns you to the same filtered list.
- Everything is server-rendered. The only JavaScript is an `onchange` that submits the class picker when there is more than one class.
- Attendance is a percentage stored on each student (green at 90% and above, red below). Edit it in the admin.
- "Active" (attending) is separate from the enrollment status on the profile (Enrolled, Pending, For Requirements).

## Changing it

- **New field on the profile:** add it to `Student` (or a related model), run `makemigrations` and `migrate`, then add a `<div><dt>…</dt><dd>…</dd></div>` in `student_detail.html`.
- **New tab:** add `("key", "Label")` to `TABS` in `views.py` and an `{% elif tab == "key" %}` block in `student_detail.html`.
- **More classes:** add a Course in the admin and set it on each student's Enrollment. A class picker appears on the Students page once there are two or more.
- **Different fees or requirements:** fee defaults are on `Enrollment`; the default document checklist is `DEFAULT_REQUIREMENTS` at the top of `models.py`.
