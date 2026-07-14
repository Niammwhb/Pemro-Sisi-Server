from ninja import Router
from lms.models import Course, Enrollment, Progress, Lesson
from .jwt_utils import decode_token
from .permissions import get_user_from_token
from django.shortcuts import get_object_or_404

router = Router()


@router.post("/")
def enroll(request, course_id: int):
    user = get_user_from_token(request, decode_token)

    if not user:
        return {"error": "Unauthorized"}

    if user.role != "student":
        return {"error": "Only student can enroll"}

    course = Course.objects.get(id=course_id)

    Enrollment.objects.create(
        student=user,
        course=course
    )

    return {"message": "enrolled"}


@router.get("/my-courses")
def my_courses(request):
    user = get_user_from_token(request, decode_token)

    if not user:
        return {"error": "Unauthorized"}

    enrollments = Enrollment.objects.filter(student=user)

    return [
        {
            "course": e.course.title
        }
        for e in enrollments
    ]


@router.post("/{enroll_id}/progress")
def mark_progress(request, enroll_id: int, lesson_id: int):
    user = get_user_from_token(request, decode_token)

    if not user:
        return {"error": "Unauthorized"}

    # Cek apakah enrollment milik user yang sedang login
    enrollment = get_object_or_404(Enrollment, id=enroll_id, student=user)

    # Cek apakah lesson ada
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Validasi tambahan: apakah lesson termasuk dalam course yang di-enroll?
    if lesson.course != enrollment.course:
        return {"error": "Lesson not part of enrolled course"}

    # Buat atau update progress
    progress, created = Progress.objects.get_or_create(
        student=user,
        lesson=lesson
    )

    progress.completed = True
    progress.save()

    return {"message": "Progress updated", "lesson": lesson.title, "completed": progress.completed}
