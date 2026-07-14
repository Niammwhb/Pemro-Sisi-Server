from django.db import connection
from .models import Course


def run_demo():
    print("=== N+1 PROBLEM ===")
    connection.queries_log.clear()

    courses = Course.objects.all()
    for c in courses:
        print(c.instructor.username)

    print("Query count:", len(connection.queries))

    print("\n=== OPTIMIZED ===")
    connection.queries_log.clear()

    courses = Course.objects.select_related('instructor')
    for c in courses:
        print(c.instructor.username)

    print("Query count:", len(connection.queries))
