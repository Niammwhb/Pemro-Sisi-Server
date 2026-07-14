from ninja import Router
from django.contrib.auth import authenticate, get_user_model
from .jwt_utils import create_access_token, create_refresh_token, decode_token

router = Router()

User = get_user_model()


@router.post("/register")
def register(request, username: str, password: str):
    user = User.objects.create_user(username=username, password=password)
    return {"message": "user created", "user_id": user.id}


@router.post("/login")
def login(request, username: str, password: str):
    user = authenticate(request, username=username, password=password)

    if not user:
        return {"error": "Invalid credentials"}

    return {
        "access": create_access_token(user.id),
        "refresh": create_refresh_token(user.id)
    }


@router.post("/refresh")
def refresh(request, refresh_token: str):
    payload = decode_token(refresh_token)

    if payload["type"] != "refresh":
        return {"error": "Invalid token"}

    return {
        "access": create_access_token(payload["user_id"])
    }


@router.get("/me")
def me(request):
    token = request.headers.get("Authorization")

    if not token:
        return {"error": "No token"}

    token = token.replace("Bearer ", "")
    payload = decode_token(token)

    user = User.objects.get(id=payload["user_id"])

    return {
        "id": user.id,
        "username": user.username
    }
