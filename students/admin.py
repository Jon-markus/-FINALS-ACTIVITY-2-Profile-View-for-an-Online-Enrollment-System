from django.contrib import admin

from .models import (
    Course,
    Enrollment,
    FamilyMember,
    PreviousSchool,
    Program,
    Requirement,
    Student,
    SubjectGrade,
)


class EnrollmentInline(admin.StackedInline):
    model = Enrollment
    extra = 1
    max_num = 1


class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 0


class PreviousSchoolInline(admin.StackedInline):
    model = PreviousSchool
    extra = 0
    max_num = 1


class SubjectGradeInline(admin.TabularInline):
    model = SubjectGrade
    extra = 0


class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 0


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_number", "last_name", "first_name", "program", "section", "status", "attendance_rate")
    list_filter = ("status", "program", "section")
    search_fields = ("student_number", "first_name", "middle_name", "last_name")
    inlines = [
        EnrollmentInline,
        FamilyMemberInline,
        PreviousSchoolInline,
        SubjectGradeInline,
        RequirementInline,
    ]


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "term", "instructor")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "status", "student_type", "amount_paid")
    list_filter = ("course", "status", "student_type")
