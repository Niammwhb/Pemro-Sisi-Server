from ninja import Router
from django.utils import timezone
from courses.models import (
    User,
    Course,
    Category,
    Lesson,
    Enrollment,
    Progress,
    Announcement,
)

router = Router(tags=["Dashboard"])


@router.get("/")
def dashboard(request):
    return {
        "project": "Final Project LMS Backend",
        "developer": "Muhammad Ni'am Mawahib",
        "generated_at": timezone.now(),

        "users": {
            "total": User.objects.count(),
            "admin": User.objects.filter(role="admin").count(),
            "instructor": User.objects.filter(role="instructor").count(),
            "student": User.objects.filter(role="student").count(),
        },

        "courses": {
            "total": Course.objects.count(),
        },

        "categories": {
            "total": Category.objects.count(),
        },

        "lessons": {
            "total": Lesson.objects.count(),
        },

        "announcements": {
            "total": Announcement.objects.count(),
        },

        "enrollments": {
            "total": Enrollment.objects.count(),
        },

        "progress": {
            "total": Progress.objects.count(),
            "completed": Progress.objects.filter(
                is_completed=True
            ).count(),
            "not_completed": Progress.objects.filter(
                is_completed=False
            ).count(),
        }
    }