from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic_settings import BaseSettings
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional

from app.api.deps import get_db
from app.services.whatsapp import whatsapp_service
from app.db.models import User, Task, TaskCompletion
from app.services.gamification import gamification_service

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge"),
    db: Session = Depends(get_db),
) -> Any:
    if whatsapp_service.verify_webhook(mode, token):
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def process_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    data = await request.json()
    message_data = whatsapp_service.process_webhook(data)
    
    if not message_data:
        return {"status": "success"}
    
    message_body = message_data.get("message_body", "").strip().lower()
    mentions = message_data.get("mentions", [])
    
    is_bot_mentioned = any(
        mention.get('type') == 'MENTIONS' and 
        mention.get('mentioned_user_id') == settings.BOT_USER_ID 
        for mention in mentions
    )
    
    try:
        task_number = whatsapp_service.extract_task_number(message_body)
        if task_number:
            user = db.query(User).first()
            if user:
                await process_task_completion(db, user, task_number)
                
                await whatsapp_service.send_group_message(
                    f"✅ Task #{task_number} completed by {user.username}!"
                )
        
        elif is_bot_mentioned:
            if "stats" in message_body or "progress" in message_body:
                user = db.query(User).first()
                if user:
                    stats = gamification_service.get_user_stats(db, user.id)
                    await send_stats_to_group(stats)
            elif "help" in message_body:
                await send_help_to_group()
    
    except Exception as e:
        print(f"Error processing WhatsApp message: {str(e)}")
        await whatsapp_service.send_group_message(
            f"Oops! An error occurred while processing the message: {str(e)}"
        )
    
    return {"status": "success"}

async def process_task_completion(db: Session, user: User, task_id: int) -> None:
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        await whatsapp_service.send_group_message(
            f"Task #{task_id} not found."
        )
        return
    
    completion = TaskCompletion(
        task_id=task.id,
        user_id=user.id
    )
    db.add(completion)
    
    user.points += task.points
    db.add(user)
    
    db.commit()
    
    new_achievements = gamification_service.check_achievements(db, user.id)
    
    if new_achievements:
        achievement_msg = "\n🏆 New achievements:\n" + "\n".join(
            f"- {ach['name']} (+{ach['points']} points)" 
            for ach in new_achievements
        )
    else:
        achievement_msg = ""

async def send_stats_to_group(stats: Dict[str, Any]) -> None:
    message = f"*Weekly Progress Report* 📊\n\n" \
              f"*Points:* {stats.get('points', 0)}\n" \
              f"*Tasks Completed:* {stats.get('tasks_completed', 0)}\n" \
              f"*Tasks Missed:* {stats.get('tasks_missed', 0)}\n" \
              f"*Completion Rate:* {stats.get('completion_rate', 0)}%\n" \
              f"*Current Streak:* {stats.get('current_streak', 0)} days\n\n"
    
    if stats.get('achievements'):
        message += "*Recent Achievements:*\n"
        for achievement in stats.get('achievements', []):
            message += f"- {achievement['name']} (+{achievement['points']} pts)\n"
    
    await whatsapp_service.send_group_message(message)

async def send_help_to_group() -> None:
    help_message = """*ScorchTrack Bot Commands* 🤖
        When mentioning the bot, you can use:
        • 'stats' - View weekly progress
        • 'help' - Show this help message

        To complete a task:
        • Simply send the task number
        • Example: 42

        Stay accountable! 💪🔥"""

    await whatsapp_service.send_group_message(help_message)
