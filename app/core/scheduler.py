from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Dict, Any, List

from app.config import settings
from app.db.database import SessionLocal
from app.db.models import TaskFrequency, User, Routine, Task, TaskCompletion
from app.services.greenapi_whatsapp import whatsapp_service
from app.services.ai import ai_service
from app.services.gamification import gamification_service

class TaskScheduler:
    def __init__(self):
        self.scheduler = None
        
    def start(self):
        if self.scheduler and self.scheduler.running:
            return
            
        self.scheduler = AsyncIOScheduler()
        
        self.scheduler.add_job(
            self.send_daily_group_update,
            CronTrigger(hour=20, minute=0),  # 8 PM daily
            id="daily_group_update"
        )
        
        self.scheduler.add_job(
            self.send_daily_roast,
            CronTrigger(hour=12, minute=0),  # 12 PM daily
            id="daily_roast"
        )
        
        self.scheduler.add_job(
            self.send_daily_motivation,
            CronTrigger(hour=6, minute=0),  # 6 AM daily
            id="daily_motivation"
        )
        
        self.scheduler.add_job(
            self.send_weekly_group_report,
            CronTrigger(day_of_week="sun", hour=18, minute=0),
            id="weekly_reports"
        )
        
        self.scheduler.start()
        print("Scheduler started")
    
    def stop(self):
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            print("Scheduler stopped")
            
        
    async def send_daily_motivation(self):
        try:
            motivation_content = await ai_service.generate_daily_motivation()
            
            message = "🌟 *Daily Motivation* 🌟\n\n" + motivation_content
            
            await whatsapp_service.send_group_message(message)
        
        except Exception as e:
            print(f"Error sending daily motivation: {str(e)}")
            
    async def send_daily_roast(self):
        try:
            roast_content = await ai_service.generate_daily_roast()
            
            message = "🔥 *Daily Accountability Roast* 🔥\n\n" + roast_content
            
            await whatsapp_service.send_group_message(message)
        
        except Exception as e:
            print(f"Error sending daily roast: {str(e)}")
    
    async def send_daily_group_update(self):
        db = SessionLocal()
        try:
            users = db.query(User).filter(User.is_active == True).all()
            
            total_tasks = db.query(Task).count()
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            completed_tasks = db.query(TaskCompletion).filter(
                TaskCompletion.completed_at >= today_start,
                TaskCompletion.completed_at <= today_end
            ).count()
            
            user_tasks = db.query(Task).all()
            missed_tasks = []
            for task in user_tasks:
                completed = db.query(TaskCompletion).filter(
                    TaskCompletion.task_id == task.id,
                    TaskCompletion.completed_at >= today_start,
                    TaskCompletion.completed_at <= today_end
                ).first()
                
                if not completed:
                    missed_tasks.append(task)
            
            message = "📊 *Daily Accountability Check* 🔍\n\n"
            message += f"*Total Tasks Today:* {total_tasks}\n"
            message += f"*Completed Tasks:* {completed_tasks}\n"
            message += f"*Completion Rate:* {round(completed_tasks/max(1,total_tasks)*100, 1)}%\n\n"
            
            if missed_tasks:
                message += "*Tasks Left Behind:*\n"
                for task in missed_tasks[:5]:  # Limit to 5 tasks
                    message += f"- {task.title} (Task #{task.id})\n"
                
                if len(missed_tasks) > 5:
                    message += f"\n*... and {len(missed_tasks)-5} more*"
            
            if len(missed_tasks) > (total_tasks / 2):
                roast_context = {
                    "missed_tasks": [{"title": task.title} for task in missed_tasks],
                    "streak_breaks": len(missed_tasks),
                    "missed_days": 1
                }
                
                roast_user = users[0] if users else None
                
                if roast_user:
                    try:
                        roast_content = await ai_service.generate_roast(roast_user, roast_context)
                        message += f"\n🔥 *Group Roast:* {roast_content}"
                    except Exception as e:
                        print(f"Error generating group roast: {str(e)}")
            
            await whatsapp_service.send_group_message(message)
        
        except Exception as e:
            print(f"Error in daily group update: {str(e)}")
        finally:
            db.close()
    
    async def send_weekly_group_report(self):
        db = SessionLocal()
        try:
            total_users = db.query(User).count()
            total_points = db.query(func.sum(User.points)).scalar() or 0
            total_tasks = db.query(Task).count()
            
            today = datetime.utcnow().date()
            week_start = today - timedelta(days=today.weekday())
            week_start_dt = datetime.combine(week_start, datetime.min.time())
            
            weekly_completions = db.query(TaskCompletion).filter(
                TaskCompletion.completed_at >= week_start_dt
            ).count()
            
            top_performers = db.query(User).order_by(User.points.desc()).limit(3).all()
            
            message = "🏆 *Weekly Accountability Report* 🏆\n\n"
            message += f"*Total Users:* {total_users}\n"
            message += f"*Total Group Points:* {total_points}\n"
            message += f"*Total Tasks:* {total_tasks}\n"
            message += f"*Tasks Completed This Week:* {weekly_completions}\n"
            message += f"*Completion Rate:* {round(weekly_completions/max(1,total_tasks)*100, 1)}%\n\n"
            
            message += "*Top Performers:*\n"
            for i, user in enumerate(top_performers, 1):
                message += f"{i}. {user.username} - {user.points} pts\n"
            
            message += "\nKeep pushing, team! Every task counts! 💪🔥"
            
            await whatsapp_service.send_group_message(message)
        
        except Exception as e:
            print(f"Error in weekly group report: {str(e)}")
        finally:
            db.close()
            
    async def check_due_tasks(self):
        """Check for tasks that are due and notify users if they haven't completed them"""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            today = now.date()
            day_of_week = today.weekday()  # 0-6, Monday is 0
            day_of_month = today.day  # 1-31
            
            # Get all active tasks
            active_tasks = db.query(Task).join(Routine).filter(
                Routine.is_active == True,
                Task.is_active == True,
                or_(
                    Routine.end_date.is_(None), 
                    Routine.end_date >= today
                ),
                Routine.start_date <= today
            ).all()
            
            due_tasks = []
            
            for task in active_tasks:
                is_due = False
                config = task.frequency_config
                
                # Check if task is due based on frequency
                if task.frequency == TaskFrequency.DAILY:
                    # Task is due daily
                    is_due = True
                    
                elif task.frequency == TaskFrequency.WEEKLY:
                    # Check if task is due on this day of the week
                    if 'days' in config and day_of_week in config['days']:
                        is_due = True
                        
                elif task.frequency == TaskFrequency.MONTHLY:
                    # Check if task is due on this day of the month
                    if 'days' in config and day_of_month in config['days']:
                        is_due = True
                        
                elif task.frequency == TaskFrequency.CUSTOM:
                    # Handle custom frequency logic
                    if 'dates' in config:
                        date_strings = config['dates']
                        for date_str in date_strings:
                            due_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            if due_date == today:
                                is_due = True
                                break
                
                # If task is due, check if it's been completed
                if is_due:
                    completed_today = db.query(TaskCompletion).filter(
                        TaskCompletion.task_id == task.id,
                        TaskCompletion.completed_at >= datetime.combine(today, datetime.min.time()),
                        TaskCompletion.completed_at <= datetime.combine(today, datetime.max.time())
                    ).first()
                    
                    if not completed_today:
                        due_tasks.append(task)
            
            # If there are due tasks, send reminders
            if due_tasks:
                message = "🔔 *Tasks Due Today* 🔔\n\n"
                for task in due_tasks:
                    message += f"• {task.title} (Task #{task.id})\n"
                
                await whatsapp_service.send_group_message(message)
        
        except Exception as e:
            print(f"Error checking due tasks: {str(e)}")
        finally:
            db.close()

scheduler = TaskScheduler()