import random
import google.generativeai as genai
from typing import Dict, Any, List
from app.config import settings
from app.db.models import User, RoastIntensity

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_roast(
        self, 
        user: User, 
        context: Dict[str, Any]
    ) -> str:
        try:
            prompt = self._create_roast_prompt(context)
            
            response = await self.model.generate_content_async(prompt)
            roast_content = response.text
            print("🚀 ~ roast_content:", roast_content)
            return roast_content
        except Exception as e:
            print(f"Error generating roast: {str(e)}")
            return f"Hey {user.username}, we noticed you missed your tasks. Don't make us come find you! Get back on track."
    
    async def generate_daily_roast(self) -> str:
        """
        Generate a brutally aggressive daily roast with Pidgin English flair
        """
        roast_templates = [
            "Create an extremely harsh, no-holds-barred roast that destroys excuses and calls out laziness with raw, unfiltered truth. Use Pidgin English to add intensity and local flavor.",
            "Write a roast that absolutely demolishes weak mindsets, procrastination, and self-sabotage. Make it so direct and brutal that it forces people to confront their mediocrity.",
            "Craft a roasting message that exposes the deepest, most painful truths about why people fail - use language that cuts deep, with a Pidgin twist that adds extra sting.",
            "Generate a ruthless takedown of comfort zone mentality, using language that's so aggressive it makes people uncomfortable enough to actually change.",
            "Create a roast that rips apart every single excuse, weakness, and moment of hesitation - make it so raw that it's almost painful to read."
        ]
        
        pidgin_intensifiers = [
            "Chai!",
            "Weh you dey play?",
            "You no serious!",
            "Gbege don burst!",
            "Wahala dey!",
            "You don fall my hand!",
            "Shey you dey joke?"
        ]
        
        try:
            prompt = random.choice(roast_templates)
            
            full_prompt = f"{prompt} Ensure the roast is:\n" + \
                            "- Brutally honest and aggressive\n" + \
                            "- Uses strong Pidgin English phrases\n" + \
                            "- Cuts deep into excuses and laziness\n" + \
                            "- Uncomfortably direct and painful\n" + \
                            "- Forces personal accountability\n" + \
                            "- Includes at least 3-4 Pidgin slang words\n" + \
                            "- Ends with a challenge that demands immediate action"
            
            response = await self.model.generate_content_async(full_prompt)
            roast_content = response.text
            
            pidgin_intensifier = random.choice(pidgin_intensifiers)
            roast_content = f"{pidgin_intensifier} {roast_content}"
            
            return roast_content
        except Exception as e:
            print(f"Error generating daily roast: {str(e)}")
            
            return (
                "Weh you dey play?! 🔥 \n"
                "You don turn professional failure be dat! Everyday dey form busy, "
                "but nothing dey happen. Your life be like football match wey nobody "
                "score goal. You dey waste time, waste energy, waste everything! "
                "Mediocrity don become your special talent. Either you wake up now "
                "or continue dey form mumu! Time no dey wait for nobody! 💥 "
                "#WakeUpOrGetLostForLife"
            )
    async def generate_daily_motivation(self) -> str:
        """
        Generate an inspiring daily motivation message
        """
        motivation_prompts = [
            "Create an inspiring motivational message about personal growth, accountability, and taking consistent action towards goals. Focus on the power of small, daily habits and how they compound over time.",
            "Write a motivational message that encourages people to push beyond their comfort zone, embrace challenges, and see failures as learning opportunities.",
            "Craft an uplifting message about resilience, persistence, and the importance of showing up for yourself every single day, even when motivation is low.",
            "Generate a motivational message that highlights the connection between daily discipline and long-term success, using powerful and energetic language.",
            "Create an inspirational message about the transformative power of consistent effort and how small, seemingly insignificant actions can lead to massive personal achievements."
        ]
        
        try:
            import random
            prompt = random.choice(motivation_prompts)
            
            full_prompt = f"{prompt} Ensure the message is:\n" + \
                            "- Between 75-150 words\n" + \
                            "- Highly motivational and energetic\n" + \
                            "- Uses emojis to add impact\n" + \
                            "- Ends with a strong call to action\n" + \
                            "- Speaks directly to the reader"
            
            response = await self.model.generate_content_async(full_prompt)
            motivation_content = response.text
            
            return motivation_content
        except Exception as e:
            print(f"Error generating daily motivation: {str(e)}")
            
            return (
                "🚀 Rise and Shine! Today is your day to crush your goals. "
                "Remember, every small step counts. Don't wait for motivation – "
                "create it. Your future self will thank you for the effort you put in today. "
                "Let's make it happen! 💪 #NoExcuses"
            )
    def _create_roast_prompt(
        self,
        context: Dict[str, Any],
        intensity: RoastIntensity = None
    ) -> str:
        username = context.get('username', 'user')
        routine_name = context.get('routine_name', '')
        missed_tasks = context.get('missed_tasks', [])
        
        if intensity is None:
            intensity_str = context.get('roast_intensity', 'medium')
            if isinstance(intensity_str, str):
                intensity = getattr(RoastIntensity, intensity_str.upper(), RoastIntensity.MEDIUM)
            else:
                intensity = intensity_str
        
        task_details = []
        longest_streak = 0
        
        for task in missed_tasks:
            title = task.get('title', 'task')
            days_missed = task.get('days_missed', 1)
            longest_streak = max(longest_streak, days_missed)
            
            if days_missed > 1:
                task_details.append(f"{title} (missed for {days_missed} days)")
            else:
                task_details.append(title)
        
        tasks_str = ", ".join(task_details) if task_details else "your tasks"
        
        prompt = f"Generate a personalized accountability 'roast' message for {username} who has missed {tasks_str} "
        
        if routine_name:
            prompt += f"from their {routine_name} routine. "
        else:
            prompt += "from their routine. "
        
        if longest_streak > 1:
            prompt += f"They have tasks that have been missed for up to {longest_streak} consecutive days. "
        
        if intensity == RoastIntensity.MILD:
            prompt += "Keep it light, friendly, and mildly teasing - just enough to motivate them but not too harsh. "
            prompt += "Use humor but be encouraging. "
        elif intensity == RoastIntensity.MEDIUM:
            prompt += "Use moderate teasing with a bit more edge, but still keep it motivational. "
            prompt += "Include some humor but make the accountability more direct. "
        elif intensity == RoastIntensity.SPICY:
            prompt += "Make it spicy and direct with sharp humor and strong accountability. "
            prompt += "Don't hold back much, but avoid being truly mean. Funny but brutally honest. "
        elif intensity == RoastIntensity.EXTREME:
            prompt += "Go all out with an extreme roast - brutal honesty, sharp wit, and no-holds-barred accountability. "
            prompt += "Make it uncomfortably direct but still ultimately motivational. "
            
            multiple_day_tasks = [task for task in missed_tasks if task.get('days_missed', 1) > 1]
            if multiple_day_tasks:
                task_names = [f"{task['title']} ({task['days_missed']} days)" for task in multiple_day_tasks]
                prompt += f"Emphasize that they've repeatedly ignored {', '.join(task_names)}. "
        
        # Add formatting guidance
        prompt += "Keep it under 100 words, use emojis where appropriate, and end with a motivational call to action. "
        prompt += "Incorporate specific task names in the roast. Don't use placeholder text."
        
        return prompt


ai_service = AIService()