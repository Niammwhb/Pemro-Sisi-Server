from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit

from .models import (
    Course,
    Enrollment,
    Announcement,
)
from .auth import JWTAuth, require_role
from .mongo_utils import log_activity, log_learning_analytics

from .tasks import (
    send_enrollment_email,
    generate_certificate,
    update_course_statistics,
    export_course_report,
)

router = Router()


# ========================
# SCHEMAS
# ========================

class CourseOutSchema(Schema):
    id: int
    title: str
    description: str


class CourseCreateSchema(Schema):
    title: str
    description: str


class CourseUpdateSchema(Schema):
    title: str = None
    description: str = None


class EnrollmentOutSchema(Schema):
    message: str
    course_id: int
    student_id: int


# ========================
# LIST COURSE
# ========================

@router.get("/")
@ratelimit(key="ip", rate="60/m", block=True)
def list_courses(
    request,
    search: str = None,
    category_id: int = None,
    instructor_id: int = None,
    sort: str = "title",
):
    courses = Course.objects.for_listing()

    if search:
        courses = courses.filter(
            title__icontains=search
        )

    if category_id:
        courses = courses.filter(
            category_id=category_id
        )

    if instructor_id:
        courses = courses.filter(
            instructor_id=instructor_id
        )

    if sort == "title":
        courses = courses.order_by("title")

    elif sort == "-title":
        courses = courses.order_by("-title")

    elif sort == "newest":
        courses = courses.order_by("-id")

    elif sort == "oldest":
        courses = courses.order_by("id")

    return {
        "success": True,
        "message": "Courses retrieved successfully",
        "total": courses.count(),
        "data": list(
            courses.values(
                "id",
                "title",
                "description",
                "category_id",
                "instructor_id",
            )
        ),
    }

# ========================
# HEALTH CHECK
# ========================
@router.get("/health")
def health_check(request):

    try:
        Course.objects.exists()
        db_status = "connected"
    except Exception:
        db_status = "error"

    try:
        cache.set("health_check", "ok", 5)
        cache.get("health_check")
        cache_status = "connected"
    except Exception:
        cache_status = "error"

    return {
        "success": True,
        "status": "healthy",
        "database": db_status,
        "cache": cache_status,
        "celery": "running",
    }

# ========================
# DETAIL COURSE
# ========================

@router.get("/{course_id}")
@ratelimit(key="ip", rate="60/m", block=True)
def get_course(request, course_id: int):

    cache_key = f"course_detail_{course_id}"

    cached = cache.get(cache_key)

    if cached:
        return {
            "success": True,
            "message": "Course retrieved successfully",
            "source": "redis_cache",
            "data": cached,
        }

    course = (
        Course.objects
        .filter(id=course_id)
        .values(
            "id",
            "title",
            "description",
            "category_id",
            "instructor_id",
        )
        .first()
    )

    if not course:
        return {
            "success": False,
            "message": "Course not found",
        }

    cache.set(cache_key, course, timeout=300)

    return {
        "success": True,
        "message": "Course retrieved successfully",
        "source": "database",
        "data": course,
    }


# ========================
# CREATE COURSE
# ========================

@router.post("/", auth=JWTAuth())
@require_role(["instructor"])
def create_course(request, data: CourseCreateSchema):

    user = request.auth

    course = Course.objects.create(
        title=data.title,
        description=data.description,
        instructor=user,
    )

    log_activity(
        user_id=user.id,
        action="CREATE_COURSE",
        detail=f"Course '{course.title}' created",
    )

    log_learning_analytics(
        user_id=user.id,
        course_id=course.id,
        event_type="COURSE_CREATED",
        progress=0,
    )

    cache.clear()

    update_course_statistics.delay()

    return {
        "success": True,
        "message": "Course created successfully",
        "data": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
        },
    }

# ========================
# UPDATE COURSE
# ========================
@router.patch("/{course_id}", auth=JWTAuth())
@require_role(["instructor"])
def update_course(request, course_id: int, data: CourseUpdateSchema):
    user = request.auth
    course = get_object_or_404(Course, id=course_id)

    if course.instructor != user:
        return {
            "success": False,
            "message": "You are not the owner of this course",
        }

    if data.title is not None:
        course.title = data.title

    if data.description is not None:
        course.description = data.description

    course.save()

    log_activity(
        user_id=user.id,
        action="UPDATE_COURSE",
        detail=f"Course ID {course.id} updated",
    )

    cache.clear()
    cache.delete(f"course_detail_{course.id}")

    update_course_statistics.delay()

    return {
        "success": True,
        "message": "Course updated successfully",
        "data": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
        },
    }


# ========================
# DELETE COURSE
# ========================
@router.delete("/{course_id}", auth=JWTAuth())
@require_role(["admin"])
def delete_course(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    log_activity(
        user_id=request.auth.id,
        action="DELETE_COURSE",
        detail=f"Course ID {course.id} deleted",
    )

    course.delete()

    cache.clear()
    cache.delete(f"course_detail_{course_id}")

    return {
        "success": True,
        "message": "Course deleted successfully",
    }


# ========================
# EXPORT REPORT
# ========================
@router.post("/{course_id}/export", auth=JWTAuth())
@require_role(["admin", "instructor"])
def export_report(request, course_id: int):

    get_object_or_404(Course, id=course_id)

    export_course_report.delay(course_id)

    return {
        "success": True,
        "message": "Export report task submitted",
    }


# ========================
# ENROLL COURSE
# ========================
@router.post(
    "/{course_id}/enroll",
    auth=JWTAuth(),
    response=EnrollmentOutSchema,
)
@require_role(["student"])
def enroll_course(request, course_id: int):

    user = request.auth

    course = get_object_or_404(
        Course,
        id=course_id,
    )

    enrollment, created = Enrollment.objects.get_or_create(
        student=user,
        course=course,
    )

    if not created:
        return {
            "message": "You are already enrolled in this course",
            "course_id": course.id,
            "student_id": user.id,
        }

    log_activity(
        user_id=user.id,
        action="ENROLL_COURSE",
        detail=f"Student enrolled in Course ID {course.id}",
    )

    log_learning_analytics(
        user_id=user.id,
        course_id=course.id,
        event_type="COURSE_ENROLLED",
        progress=0,
    )

    send_enrollment_email.delay(
        user.email,
        course.title,
    )

    generate_certificate.delay(
        user.id,
        course.id,
    )

    cache.clear()

    return {
        "message": "Successfully enrolled",
        "course_id": course.id,
        "student_id": user.id,
    }


# ========================
# ANNOUNCEMENT SCHEMAS
# ========================

class AnnouncementSchema(Schema):
    title: str
    message: str


class AnnouncementOutSchema(Schema):
    id: int
    title: str
    message: str


# ========================
# CREATE ANNOUNCEMENT
# ========================

@router.post("/{course_id}/announcement", auth=JWTAuth())
@require_role(["instructor"])
def create_announcement(
    request,
    course_id: int,
    data: AnnouncementSchema,
):
    course = get_object_or_404(
        Course,
        id=course_id,
    )

    if course.instructor != request.auth:
        return {
            "success": False,
            "message": "Not your course",
        }

    announcement = Announcement.objects.create(
        course=course,
        instructor=request.auth,
        title=data.title,
        message=data.message,
    )

    log_activity(
        user_id=request.auth.id,
        action="CREATE_ANNOUNCEMENT",
        detail=f"Announcement created for Course {course.id}",
    )

    return {
        "success": True,
        "message": "Announcement created successfully",
        "data": {
            "id": announcement.id,
            "title": announcement.title,
            "message": announcement.message,
        },
    }


# ========================
# LIST ANNOUNCEMENTS
# ========================

@router.get(
    "/{course_id}/announcements",
    response=list[AnnouncementOutSchema],
)
def list_announcements(
    request,
    course_id: int,
):
    get_object_or_404(
        Course,
        id=course_id,
    )

    return Announcement.objects.filter(
        course_id=course_id
    ).order_by("-created_at")


# ========================
# DELETE ANNOUNCEMENT
# ========================

@router.delete(
    "/announcement/{announcement_id}",
    auth=JWTAuth(),
)
@require_role(["instructor"])
def delete_announcement(
    request,
    announcement_id: int,
):
    announcement = get_object_or_404(
        Announcement,
        id=announcement_id,
    )

    if announcement.instructor != request.auth:
        return {
            "success": False,
            "message": "Not your announcement",
        }

    announcement.delete()

    return {
        "success": True,
        "message": "Announcement deleted successfully",
    }