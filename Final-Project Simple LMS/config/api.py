from ninja import NinjaAPI

from courses.auth import auth_router
from courses.api import router as courses_router
from courses.dashboard import router as dashboard_router

api = NinjaAPI()

api.add_router("/auth", auth_router)
api.add_router("/courses", courses_router)
api.add_router("/dashboard", dashboard_router)