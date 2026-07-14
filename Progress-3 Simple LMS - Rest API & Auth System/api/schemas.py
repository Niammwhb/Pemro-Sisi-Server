from ninja import Schema

# =====================
# AUTH
# =====================


class RegisterSchema(Schema):
    username: str
    password: str


class LoginSchema(Schema):
    username: str
    password: str


class TokenSchema(Schema):
    access: str
    refresh: str


# =====================
# COURSE
# =====================
class CourseCreateSchema(Schema):
    title: str
    description: str
    category_id: int  # opsional, bisa juga nullable


class CourseOut(Schema):
    id: int
    title: str
    description: str


# =====================
# ENROLLMENT
# =====================
class EnrollmentSchema(Schema):
    course_id: int


# =====================
# PROGRESS
# =====================
class ProgressSchema(Schema):
    lesson_id: int
    completed: bool = False


class ProgressOut(Schema):
    id: int
    student_id: int
    lesson_id: int
    lesson_title: str
    completed: bool


# =====================
# CATEGORY
# =====================
class CategorySchema(Schema):
    name: str
    parent_id: int = None


class CategoryOut(Schema):
    id: int
    name: str
    parent_id: int = None
    children: list = []


# =====================
# LESSON
# =====================
class LessonCreateSchema(Schema):
    title: str
    content: str
    order: int


class LessonOut(Schema):
    id: int
    title: str
    content: str
    order: int
    course_id: int


# =====================
# USER
# =====================
class UserOut(Schema):
    id: int
    username: str
    email: str = ""
    role: str


class UserCreateSchema(Schema):
    username: str
    password: str
    email: str = ""
    role: str = "student"  # default student
