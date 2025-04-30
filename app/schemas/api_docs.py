"""
Pydantic models specifically for API documentation.
These models are used to provide clean request/response documentation in Swagger UI.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

from app.db.models import RoastIntensity

# ------ Auth Models ------

class LoginRequest(BaseModel):
    """Request model for user login."""
    username: str = Field(..., description="User's email address used as username for login")
    password: str = Field(..., description="User's password")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "strongpassword123"
            }
        }

class TokenResponse(BaseModel):
    """Response model for successful authentication."""
    access_token: str = Field(..., description="JWT access token for authenticated requests")
    token_type: str = Field(..., description="Type of token, typically 'bearer'")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

# ------ User Models ------

class UserCreateRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="User's email address, must be unique")
    username: str = Field(..., description="User's chosen username, must be unique")
    password: str = Field(..., description="User's password")
    whatsapp_opt_in: bool = Field(False, description="Whether the user opts in to WhatsApp notifications")
    roast_intensity: RoastIntensity = Field(RoastIntensity.MEDIUM, description="Intensity level for accountability roasts")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "accountability_master",
                "password": "securepassword123",
                "whatsapp_number": "+1234567890",
            }
        }

class UserUpdateRequest(BaseModel):
    """Request model for updating user profile."""
    email: Optional[EmailStr] = Field(None, description="User's new email address")
    whatsapp_number: Optional[str] = Field(None, description="User's new WhatsApp number")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "whatsapp_number": "+1234567890",
            }
        }

class UserResponse(BaseModel):
    """Response model for user data."""
    id: int = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    is_active: bool = Field(..., description="Whether the user account is active")
    whatsapp_number: Optional[str] = Field(None, description="User's WhatsApp number")
    points: int = Field(..., description="User's total achievement points")
    created_at: datetime = Field(..., description="When the user account was created")
    updated_at: datetime = Field(..., description="When the user account was last updated")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "accountability_master",
                "is_active": True,
                "whatsapp_number": "+1234567890",
                "points": 150,
                "created_at": "2025-04-20T10:30:00Z",
                "updated_at": "2025-04-28T16:45:00Z"
            }
        }

# ------ Routine Models ------

class RoutineCreateRequest(BaseModel):
    """Request model for creating a new routine."""
    title: str = Field(..., description="Title of the routine")
    description: Optional[str] = Field(None, description="Detailed description of the routine")
    is_active: bool = Field(True, description="Whether the routine is active")
    start_date: Optional[datetime] = Field(None, description="When the routine should start")
    end_date: Optional[datetime] = Field(None, description="When the routine should end (optional)")

    class Config:
        schema_extra = {
            "example": {
                "title": "Morning Workout",
                "description": "Daily morning exercise routine",
                "is_active": True,
                "start_date": "2025-05-01T00:00:00Z",
                "end_date": "2025-06-01T00:00:00Z"
            }
        }

class RoutineUpdateRequest(BaseModel):
    """Request model for updating a routine."""
    title: Optional[str] = Field(None, description="New title for the routine")
    description: Optional[str] = Field(None, description="New description for the routine")
    is_active: Optional[bool] = Field(None, description="Update active status")
    start_date: Optional[datetime] = Field(None, description="Update start date")
    end_date: Optional[datetime] = Field(None, description="Update end date")

    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Workout Routine",
                "is_active": False,
                "end_date": "2025-05-15T00:00:00Z"
            }
        }

# ------ Task Models ------

class TaskFrequencyEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"
class TaskCreateRequest(BaseModel):
    """Request model for creating a new task within a routine."""
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    points: int = Field(1, description="Points awarded for completing this task")
    is_active: bool = Field(True, description="Whether the task is active")
    frequency: TaskFrequencyEnum = Field(TaskFrequencyEnum.DAILY, description="Frequency of the task")
    frequency_config: Dict[str, Any] = Field({}, description="Configuration for task frequency")

    class Config:
        schema_extra = {
            "example": {
                "title": "30 Pushups",
                "description": "Complete 30 pushups in good form",
                "points": 5,
                "is_active": True,
                "frequency": "daily",
                "frequency_config": {
                    "time": "08:00:00"
                }
            }
        }

class TaskUpdateRequest(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(None, description="New title for the task")
    description: Optional[str] = Field(None, description="New description for the task")
    points: Optional[int] = Field(None, description="Update points value")
    is_active: Optional[bool] = Field(None, description="Update active status")
    frequency: Optional[TaskFrequencyEnum] = Field(None, description="Update task frequency")
    frequency_config: Optional[Dict[str, Any]] = Field(None, description="Update frequency configuration")

    class Config:
        schema_extra = {
            "example": {
                "title": "50 Pushups",
                "points": 10,
                "frequency": "weekly",
                "frequency_config": {
                    "days": [1, 3, 5],  # Monday, Wednesday, Friday
                    "time": "08:00:00"
                }
            }
        }

# ------ Task Completion Models ------

class TaskCompletionCreateRequest(BaseModel):
    """Request model for marking a task as complete."""
    notes: Optional[str] = Field(None, description="Optional notes about the task completion")

    class Config:
        schema_extra = {
            "example": {
                "notes": "Completed with good form, felt great!"
            }
        }

class TaskCompletionResponse(BaseModel):
    """Response model for task completion data."""
    id: int = Field(..., description="Unique identifier for this completion")
    task_id: int = Field(..., description="ID of the completed task")
    user_id: int = Field(..., description="ID of the user who completed the task")
    completed_at: datetime = Field(..., description="When the task was marked complete")
    notes: Optional[str] = Field(None, description="User notes about the completion")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 42,
                "task_id": 5,
                "user_id": 1,
                "completed_at": "2025-04-29T08:45:30Z",
                "notes": "Completed with good form, felt great!"
            }
        }

# ------ Statistics and Gamification Models ------

class UserStatsResponse(BaseModel):
    """Response model for user statistics."""
    username: str = Field(..., description="User's username")
    points: int = Field(..., description="Total points earned")
    tasks_completed: int = Field(..., description="Tasks completed this week")
    tasks_missed: int = Field(..., description="Tasks missed this week")
    completion_rate: float = Field(..., description="Weekly completion rate percentage")
    current_streak: int = Field(..., description="Current streak of days with task completions")
    achievements: List[Dict[str, Any]] = Field(..., description="Recent achievements earned")

    class Config:
        schema_extra = {
            "example": {
                "username": "accountability_master",
                "points": 450,
                "tasks_completed": 28,
                "tasks_missed": 2,
                "completion_rate": 93.3,
                "current_streak": 12,
                "achievements": [
                    {
                        "name": "7-Day Streak",
                        "description": "Complete at least one task per day for 7 days",
                        "points": 50
                    },
                    {
                        "name": "Consistency Champion",
                        "description": "Complete 90% of your tasks in a week",
                        "points": 100
                    }
                ]
            }
        }

class LeaderboardEntryResponse(BaseModel):
    """Response model for a leaderboard entry."""
    user_id: int = Field(..., description="User's ID")
    username: str = Field(..., description="User's username")
    points: int = Field(..., description="Total points earned")
    achievements_count: int = Field(..., description="Number of achievements earned")

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "username": "accountability_master",
                "points": 450,
                "achievements_count": 5
            }
        }

# ------ WhatsApp Webhook Models ------

class WebhookVerifyResponse(BaseModel):
    """Response for webhook verification request."""
    hub_challenge: int = Field(..., description="Challenge value to return for verification")

class WebhookResponse(BaseModel):
    """Response for webhook message processing."""
    status: str = Field(..., description="Status of the webhook processing")

    class Config:
        schema_extra = {
            "example": {
                "status": "success"
            }
        }