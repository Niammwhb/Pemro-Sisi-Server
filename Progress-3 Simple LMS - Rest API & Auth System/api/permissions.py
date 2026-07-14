from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_from_token(request, decode_token):
    token = request.headers.get("Authorization")

    if not token:
        return None

    token = token.replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        return None

    try:
        return User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return None


# =====================
# RBAC - ROLE BASED ACCESS CONTROL
# =====================

def is_admin(user):
    """Check if user has admin role"""
    if not user:
        return False
    return user.role == "admin"


def is_instructor(user):
    """Check if user has instructor role"""
    if not user:
        return False
    return user.role == "instructor"


def is_student(user):
    """Check if user has student role"""
    if not user:
        return False
    return user.role == "student"


def is_admin_or_instructor(user):
    """Check if user is admin or instructor"""
    if not user:
        return False
    return user.role in ["admin", "instructor"]


def has_course_access(user, course):
    """
    Check if user has access to manage a course
    - Admin can manage all courses
    - Instructor can manage only their own courses
    - Students cannot manage courses
    """
    if not user:
        return False

    if is_admin(user):
        return True

    if is_instructor(user) and course.instructor == user:
        return True

    return False


def can_enroll(user):
    """Check if user can enroll in courses (only students)"""
    if not user:
        return False
    return is_student(user)


def can_manage_progress(user):
    """Check if user can manage lesson progress (only students)"""
    if not user:
        return False
    return is_student(user)


def can_manage_lessons(user, course):
    """Check if user can manage lessons in a course"""
    if not user:
        return False

    if is_admin(user):
        return True

    if is_instructor(user) and course.instructor == user:
        return True

    return False
