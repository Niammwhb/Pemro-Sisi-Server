from django.core.management.base import BaseCommand

from courses.models import (
    User,
    Course,
    Enrollment,
    Announcement,
)


class Command(BaseCommand):
    help = "Generate demo data for Simple LMS"

    def handle(self, *args, **kwargs):

        # =====================
        # ADMIN
        # =====================
        admin, _ = User.objects.get_or_create(
            username="admin_demo",
            defaults={
                "email": "admin@example.com",
                "role": "admin",
            },
        )

        admin.set_password("admin123")
        admin.save()

        self.stdout.write(
            self.style.SUCCESS("Admin created")
        )

        # =====================
        # INSTRUCTOR
        # =====================
        instructors = []

        for i in range(1, 3):

            instructor, _ = User.objects.get_or_create(
                username=f"instructor{i}",
                defaults={
                    "email": f"instructor{i}@example.com",
                    "role": "instructor",
                },
            )

            instructor.set_password("123456")
            instructor.save()

            instructors.append(instructor)

        self.stdout.write(
            self.style.SUCCESS("Instructors created")
        )

        # =====================
        # STUDENTS
        # =====================
        students = []

        for i in range(1, 6):

            student, _ = User.objects.get_or_create(
                username=f"student{i}",
                defaults={
                    "email": f"student{i}@example.com",
                    "role": "student",
                },
            )

            student.set_password("123456")
            student.save()

            students.append(student)

        self.stdout.write(
            self.style.SUCCESS("Students created")
        )

        # =====================
        # COURSES
        # =====================
        courses = []

        for i in range(1, 11):

            course, _ = Course.objects.get_or_create(
                title=f"Demo Course {i}",
                defaults={
                    "description": f"Description Course {i}",
                    "instructor": instructors[i % 2],
                },
            )

            courses.append(course)

        self.stdout.write(
            self.style.SUCCESS("Courses created")
        )

        # =====================
        # ENROLLMENTS
        # =====================
        for student in students:
            for course in courses[:3]:

                Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                )

        self.stdout.write(
            self.style.SUCCESS("Enrollments created")
        )

        # =====================
        # ANNOUNCEMENTS
        # =====================
        for course in courses:

            Announcement.objects.get_or_create(
                course=course,
                instructor=course.instructor,
                title="Welcome",
                defaults={
                    "message": "Welcome to this course!"
                },
            )

        self.stdout.write(
            self.style.SUCCESS("Announcements created")
        )

        self.stdout.write(
            self.style.SUCCESS(
                "\nDemo data generated successfully!"
            )
        )