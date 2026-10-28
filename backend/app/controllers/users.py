from fastapi import APIRouter, status

from app.dependencies import UserServiceDep
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(users: UserServiceDep):
    return users.list_all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, users: UserServiceDep):
    return users.create(body.name)
