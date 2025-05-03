from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set
from sqlalchemy.orm import Session

from app.db.models import Task, Routine, TaskCompletion, User, TaskFrequency

class TaskService:
    @staticmethod
    def get_missed_tasks_by_user(db: Session) -> Dict[int, List[Tuple[Task, int]]]:
        """
        Get all missed tasks for today grouped by user, with count of days missed.
        
        Returns a dictionary with user_id as key and a list of tuples (task, days_missed) as value.
        """
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        active_tasks = db.query(Task).join(Routine).filter(
            Routine.is_active == True,
            Task.is_active == True
        ).all()
        
        # Determine which tasks are due today
        due_tasks = []
        for task in active_tasks:
            is_due = False
            
            if task.frequency == TaskFrequency.DAILY:
                is_due = True
            elif task.frequency == TaskFrequency.WEEKLY:
                day_of_week = today.weekday()
                try:
                    config = task.frequency_config
                    if isinstance(config, str):
                        import json
                        config = json.loads(config)
                    if 'days' in config and day_of_week in config['days']:
                        is_due = True
                except:
                    pass
            
            if is_due:
                due_tasks.append(task)
        
        # Get all completions for today
        completions = db.query(TaskCompletion).filter(
            TaskCompletion.completed_at >= today_start,
            TaskCompletion.completed_at <= today_end
        ).all()
        
        # Create a set of (user_id, task_id) pairs for completed tasks
        completed_pairs = {(c.user_id, c.task_id) for c in completions}
        
        # Build a dictionary of missed tasks by user
        missed_by_user = {}
        for task in due_tasks:
            user_id = task.routine.user_id
            if (user_id, task.id) not in completed_pairs:
                # Calculate how many days in a row this task has been missed
                days_missed = 1
                
                # Check previous days (up to 7 days back)
                for days_back in range(1, 8):
                    check_date = today - timedelta(days=days_back)
                    check_start = datetime.combine(check_date, datetime.min.time())
                    check_end = datetime.combine(check_date, datetime.max.time())
                    
                    # Check if the task was due on this day
                    was_due = False
                    if task.frequency == TaskFrequency.DAILY:
                        was_due = True
                    elif task.frequency == TaskFrequency.WEEKLY:
                        day_of_week = check_date.weekday()
                        try:
                            config = task.frequency_config
                            if isinstance(config, str):
                                import json
                                config = json.loads(config)
                            if 'days' in config and day_of_week in config['days']:
                                was_due = True
                        except:
                            pass
                    
                    if not was_due:
                        break
                    
                    # Check if the task was completed on this day
                    completion = db.query(TaskCompletion).filter(
                        TaskCompletion.task_id == task.id,
                        TaskCompletion.user_id == user_id,
                        TaskCompletion.completed_at >= check_start,
                        TaskCompletion.completed_at <= check_end
                    ).first()
                    
                    if completion:
                        break
                    
                    days_missed += 1
                
                if user_id not in missed_by_user:
                    missed_by_user[user_id] = []
                missed_by_user[user_id].append((task, days_missed))
        
        return missed_by_user
    
    @staticmethod
    def build_roast_context(user: User, missed_tasks: List[Tuple[Task, int]]) -> Dict:
        """
        Build a context dictionary for the AI roast generator.
        """
        context = {
            "username": user.username,
            "routine_name": missed_tasks[0][0].routine.title if missed_tasks else "",
            "missed_tasks": [
                {
                    "title": task.title, 
                    "description": task.description,
                    "days_missed": days_missed
                } 
                for task, days_missed in missed_tasks
            ],
            "roast_intensity": getattr(user, 'roast_intensity', 'medium'),
        }
        
        return context

task_service = TaskService()