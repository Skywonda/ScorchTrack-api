from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Any, List

from app.api.deps import get_current_active_user, get_db
from app.db.models import Routine, Task, User
from app.schemas.routine import (
    Routine as RoutineSchema,
    RoutineCreate,
    RoutineUpdate,
    Task as TaskSchema,
    TaskCreate,
    TaskUpdate,
)

router = APIRouter()

@router.post("/", response_model=RoutineSchema)
def create_routine(
    routine_in: RoutineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    routine = Routine(
        user_id=current_user.id,
        title=routine_in.title,
        description=routine_in.description,
        is_active=routine_in.is_active,
        start_date=routine_in.start_date or datetime.utcnow(),
        end_date=routine_in.end_date,
    )
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine

@router.put("/{routine_id}", response_model=RoutineSchema)
def update_routine(
    routine_id: int = Path(..., gt=0),
    routine_in: RoutineUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    routine = db.query(Routine).filter(
        Routine.id == routine_id, Routine.user_id == current_user.id
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    if routine_in.title is not None:
        routine.title = routine_in.title
    if routine_in.description is not None:
        routine.description = routine_in.description
    if routine_in.is_active is not None:
        routine.is_active = routine_in.is_active
    if routine_in.start_date is not None:
        routine.start_date = routine_in.start_date
    if routine_in.end_date is not None:
        routine.end_date = routine_in.end_date
    
    db.add(routine)
    db.commit()
    db.refresh(routine)
    return routine

@router.post("/{routine_id}/tasks", response_model=TaskSchema)
def create_task(
    routine_id: int = Path(..., gt=0),
    task_in: TaskCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    routine = db.query(Routine).filter(
        Routine.id == routine_id, Routine.user_id == current_user.id
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    task = Task(
        routine_id=routine_id,
        title=task_in.title,
        description=task_in.description,
        points=task_in.points,
        is_active=task_in.is_active,
        frequency=task_in.frequency,
        frequency_config=task_in.frequency_config,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.put("/{routine_id}/tasks/{task_id}", response_model=TaskSchema)
def update_task(
    routine_id: int = Path(..., gt=0),
    task_id: int = Path(..., gt=0),
    task_in: TaskUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    routine = db.query(Routine).filter(
        Routine.id == routine_id, Routine.user_id == current_user.id
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    task = db.query(Task).filter(
        Task.id == task_id, Task.routine_id == routine_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_in.title is not None:
        task.title = task_in.title
    if task_in.description is not None:
        task.description = task_in.description
    if task_in.points is not None:
        task.points = task_in.points
    if task_in.is_active is not None:
        task.is_active = task_in.is_active
    if task_in.frequency is not None:
        task.frequency = task_in.frequency
    if task_in.frequency_config is not None:
        task.frequency_config = task_in.frequency_config
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task