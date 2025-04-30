from datetime import datetime
import httpx
import json
import re
from typing import Dict, Any, Optional
from app.config import settings
from app.db.models import User, Task, Routine
import asyncio

class WhatsAppService:
    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_url = f"https://graph.facebook.com/v22.0/{self.phone_number_id}/messages"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        self.group_id = settings.WHATSAPP_GROUP_ID  # New setting for group ID
    
    def verify_webhook(self, mode: str, token: str) -> bool:
        return mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN

    def process_webhook(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            if 'object' in data and data['object'] == 'whatsapp_business_account':
                if 'entry' in data and len(data['entry']) > 0:
                    entry = data['entry'][0]
                    if 'changes' in entry and len(entry['changes']) > 0:
                        change = entry['changes'][0]
                        if 'value' in change and 'messages' in change['value']:
                            messages = change['value']['messages']
                            for message in messages:
                                # Check if message is from the group
                                if (message.get('from', '') == self.group_id and 
                                    message['type'] == 'text'):
                                    # Extract mentions and text
                                    text = message['text']['body']
                                    mentions = message.get('mentions', [])
                                    
                                    return {
                                        'group_id': self.group_id,
                                        'message_body': text,
                                        'mentions': mentions,
                                        'message_id': message['id'],
                                        'timestamp': message['timestamp']
                                    }
            return None
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            return None
    
    async def send_group_message(self, message: str) -> Dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            # "to": self.group_id,
            "to": "2348026184019",
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            print("🚀 ~ response:", response.json())
            
            if response.status_code != 200:
                # Log error details
                print(f"Error sending WhatsApp group message: {response.status_code} - {response.text}")
                
            return response.json()
        
    def extract_task_number(self, message: str) -> Optional[int]:
        """
        Extract task number from message, supporting various formats
        """
        # Try to find a number at the start or after some text
        match = re.search(r'(?:^|\s)(\d+)(?=\s|$)', message.strip())
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

whatsapp_service = WhatsAppService()