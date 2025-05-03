from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Any, List

from app.api.deps import get_current_active_user, get_db
from app.db.models import Task, TaskCompletion, User
from app.schemas.routine import TaskCompletion as TaskCompletionSchema, TaskCompletionCreate
from app.schemas.api_docs import UserStatsResponse
from app.services.gamification import gamification_service

router = APIRouter()

@router.post("/tasks/{task_id}/complete", response_model=TaskCompletionSchema)
def complete_task(
    task_id: int = Path(..., gt=0),
    completion_in: TaskCompletionCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if the task belongs to a routine owned by the current user
    if task.routine.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to complete this task")
    
    completion = TaskCompletion(
        task_id=task_id,
        user_id=current_user.id,
        notes=completion_in.notes if completion_in else None,
    )
    db.add(completion)
    
    # Award points to the user
    current_user.points += task.points
    db.add(current_user)
    
    db.commit()
    db.refresh(completion)
    
    # Check for new achievements
    gamification_service.check_achievements(db, current_user.id)
    
    return completion

@router.get("/tasks/{task_id}/completions", response_model=List[TaskCompletionSchema])
def get_task_completions(
    task_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if the task belongs to a routine owned by the current user
    if task.routine.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task's completions")
    
    completions = db.query(TaskCompletion).filter(
        TaskCompletion.task_id == task_id, TaskCompletion.user_id == current_user.id
    ).all()
    
    return completions

@router.get("/completions", response_model=List[TaskCompletionSchema])
def get_user_completions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    completions = db.query(TaskCompletion).filter(
        TaskCompletion.user_id == current_user.id
    ).order_by(TaskCompletion.completed_at.desc()).all()
    
    return completions

@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get statistics for the current user including:
    - Points
    - Completed tasks count
    - Missed tasks count
    - Completion rate
    - Current streak
    - Recent achievements
    """
    stats = gamification_service.get_user_stats(db, current_user.id)
    return stats