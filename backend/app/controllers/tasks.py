from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.dependencies import CurrentUser, TaskServiceDep
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

# AUTH: every route depends on CurrentUser. Swapping X-User-Id for OAuth2 bearer tokens
# happens in app/core/security.py only (see the design notes there).
router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    user: CurrentUser,
    tasks: TaskServiceDep,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
):
    return tasks.list_for_user(user.id, status_filter)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate, user: CurrentUser, tasks: TaskServiceDep):
    return tasks.create(user.id, body)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, user: CurrentUser, tasks: TaskServiceDep):
    return tasks.get(user.id, task_id)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, body: TaskUpdate, user: CurrentUser, tasks: TaskServiceDep):
    return tasks.update(user.id, task_id, body)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, user: CurrentUser, tasks: TaskServiceDep):
    tasks.delete(user.id, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
