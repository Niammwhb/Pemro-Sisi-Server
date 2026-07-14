from ninja import Router
from lms.models import Course
from .jwt_utils import decode_token
from .permissions import get_user_from_token
from django.shortcuts import get_object_or_404

router = Router()


@router.get("/")
def list_courses(request, limit: int = 10, offset: int = 0):
    qs = Course.objects.all()[offset:offset+limit]

    data = []
    for c in qs:
        data.append({
            "id": c.id,
            "title": c.title,
            "instructor": c.instructor.username
        })

    return {
        "count": Course.objects.count(),
        "results": data
    }


@router.post("/")
def create_course(request, title: str, description: str):
    user = get_user_from_token(request, decode_token)

    if not user:
        return {"error": "Unauthorized"}

    if user.role != "instructor":
        return {"error": "Only instructor"}

    course = Course.objects.create(
        title=title,
        description=description,
        instructor=user
    )

    return {"id": course.id, "title": course.title}


@router.patch("/{course_id}")
def update_course(request, course_id: int, title: str = None, description: str = None):
    user = get_user_from_token(request, decode_token)

    if not user:
        return {"error": "Unauthorized"}

    course = get_object_or_404(Course, id=course_id)

    # 🔥 Ownership check
    if course.instructor != user and user.role != "admin":
        return {"error": "Not allowed"}

    if title is not None:
        course.title = title
    if description is not None:
        course.description = description

    course.save()

    return {"message": "Course updated"}


@router.delete("/{course_id}")
def delete_course(request, course_id: int):
    user = get_user_from_token(request, decode_token)

    if not user:
        return {"error": "Unauthorized"}

    if user.role != "admin":
        return {"error": "Only admin"}

    Course.objects.filter(id=course_id).delete()

    return {"message": "deleted"}
