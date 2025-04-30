from datetime import datetime, time
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, validator, root_validator
from enum import Enum

# Add TaskFrequency enum
class TaskFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    CUSTOM = "custom"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    points: int = 1
    is_active: bool = True
    frequency: TaskFrequency = TaskFrequency.DAILY
    frequency_config: Dict[str, Any] = {}

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    points: Optional[int] = None
    is_active: Optional[bool] = None
    frequency: Optional[TaskFrequency] = None
    frequency_config: Optional[Dict[str, Any]] = None

class TaskInDBBase(TaskBase):
    id: int
    routine_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Task(TaskInDBBase):
    pass

class RoutineBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RoutineCreate(RoutineBase):
    pass

class RoutineUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RoutineInDBBase(RoutineBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Routine(RoutineInDBBase):
    tasks: List[Task] = []