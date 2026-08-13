from fastapi import APIRouter
from app.models import UserDTO

router = APIRouter()

@router.get("/users/{user_id}", response_model=UserDTO)
def get_user(user_id: int):
    return UserDTO(id=user_id, username="veda_developer")
