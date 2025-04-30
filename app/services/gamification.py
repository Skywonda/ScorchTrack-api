from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Tuple

from app.db.models import Routine, User, Task, TaskCompletion, Achievement, UserAchievement

class GamificationService:
    def award_points(self, db: Session, user_id: int, points: int) -> None:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.points += points
            db.add(user)
            db.commit()
    
    def check_achievements(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        earned_achievements = []
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return earned_achievements
        
        existing_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        existing_achievement_ids = [a.achievement_id for a in existing_achievements]
        
        total_completions = db.query(func.count(TaskCompletion.id)).filter(
            TaskCompletion.user_id == user_id
        ).scalar()
        
        first_task_achievement = db.query(Achievement).filter(
            Achievement.name == "First Task Completed"
        ).first()
        
        if first_task_achievement and first_task_achievement.id not in existing_achievement_ids and total_completions >= 1:
            self._award_achievement(db, user_id, first_task_achievement.id)
            earned_achievements.append({
                "name": first_task_achievement.name,
                "description": first_task_achievement.description,
                "points": first_task_achievement.points
            })
        
        ten_tasks_achievement = db.query(Achievement).filter(
            Achievement.name == "10 Tasks Completed"
        ).first()
        
        if ten_tasks_achievement and ten_tasks_achievement.id not in existing_achievement_ids and total_completions >= 10:
            self._award_achievement(db, user_id, ten_tasks_achievement.id)
            earned_achievements.append({
                "name": ten_tasks_achievement.name,
                "description": ten_tasks_achievement.description,
                "points": ten_tasks_achievement.points
            })
        
        streak_achievement = db.query(Achievement).filter(
            Achievement.name == "7-Day Streak"
        ).first()
        
        if streak_achievement and streak_achievement.id not in existing_achievement_ids:
            streak_days = self._calculate_streak(db, user_id)
            if streak_days >= 7:
                self._award_achievement(db, user_id, streak_achievement.id)
                earned_achievements.append({
                    "name": streak_achievement.name,
                    "description": streak_achievement.description,
                    "points": streak_achievement.points
                })
        
        return earned_achievements
    
    def _award_achievement(self, db: Session, user_id: int, achievement_id: int) -> None:
        achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
        if not achievement:
            return
        
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id
        )
        db.add(user_achievement)
        
        self.award_points(db, user_id, achievement.points)
        
        db.commit()
    
    def _calculate_streak(self, db: Session, user_id: int) -> int:
        today = datetime.utcnow().date()
        streak = 0
        
        for day_offset in range(30):  # Check up to 30 days back
            check_date = today - timedelta(days=day_offset)
            next_date = today - timedelta(days=day_offset-1) if day_offset > 0 else None
            
            day_start = datetime.combine(check_date, datetime.min.time())
            day_end = datetime.combine(check_date, datetime.max.time())
            
            completions = db.query(TaskCompletion).filter(
                TaskCompletion.user_id == user_id,
                TaskCompletion.completed_at >= day_start,
                TaskCompletion.completed_at <= day_end
            ).count()
            
            if completions > 0:
                streak += 1
            else:
                # Streak broken
                break
        
        return streak
    
    def get_leaderboard(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        users = db.query(
            User.id,
            User.username,
            User.points,
            func.count(UserAchievement.id).label("achievements_count")
        ).outerjoin(
            UserAchievement, User.id == UserAchievement.user_id
        ).group_by(
            User.id
        ).order_by(
            User.points.desc()
        ).limit(limit).all()
        
        return [
            {
                "user_id": user.id,
                "username": user.username,
                "points": user.points,
                "achievements_count": user.achievements_count
            }
            for user in users
        ]
    
    def get_user_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        recent_achievements = db.query(
            Achievement
        ).join(
            UserAchievement
        ).filter(
            UserAchievement.user_id == user_id
        ).order_by(
            UserAchievement.awarded_at.desc()
        ).limit(5).all()
        
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        
        week_completions = db.query(func.count(TaskCompletion.id)).filter(
            TaskCompletion.user_id == user_id,
            TaskCompletion.completed_at >= week_start_dt
        ).scalar()
        
        user_tasks = db.query(Task).join(
            Routine, Task.routine_id == Routine.id
        ).filter(
            Routine.user_id == user_id,
            Routine.is_active == True,
            Task.is_active == True
        ).all()
        
        total_weekly_tasks = len(user_tasks) * 7  
        
        current_streak = self._calculate_streak(db, user_id)
        
        return {
            "username": user.username,
            "points": user.points,
            "tasks_completed": week_completions,
            "tasks_missed": max(0, total_weekly_tasks - week_completions),
            "completion_rate": round(week_completions / max(1, total_weekly_tasks) * 100, 1),
            "current_streak": current_streak,
            "achievements": [
                {
                    "name": achievement.name,
                    "description": achievement.description,
                    "points": achievement.points
                }
                for achievement in recent_achievements
            ]
        }

gamification_service = GamificationService()