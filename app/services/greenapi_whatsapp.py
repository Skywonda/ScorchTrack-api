from whatsapp_api_client_python import API
import re
from typing import Dict, Any, Optional
from app.config import settings
from app.db.models import User, Task

class GreenApiWhatsAppService:
    def __init__(self):
        self.client = API.GreenAPI(
            settings.GREEN_API_INSTANCE_ID, 
            settings.GREEN_API_ACCESS_TOKEN
        )
        
        self.group_id = settings.WHATSAPP_GROUP_ID
    
    def verify_webhook(self, mode: str, token: str) -> bool:
        return token == settings.GREEN_API_WEBHOOK_TOKEN
    
    def process_webhook(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            if 'message' in data and 'body' in data.get('message', {}):
                message = data['message']
                
                return {
                    'group_id': message.get('chatId', ''),
                    'message_body': message.get('body', '').strip(),
                    'sender_phone': message.get('senderData', {}).get('sender', ''),
                    'timestamp': message.get('timestamp')
                }
            return None
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            return None
    
    def extract_task_number(self, message: str) -> Optional[int]:
        match = re.search(r'(?:^|\s)(\d+)(?=\s|$)', message.strip())
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None
    
    async def send_group_message(self, message: str) -> Dict[str, Any]:
        try:
            response = self.client.sending.sendMessage(
                self.group_id, 
                "*I am Scorch Track Bot!* \n" + message
            )
            
            print(f"Message sent. Response: {response.data}")
            
            return {
                "status": "success",
                "message_id": response.data.get('id') if response.data else None
            }
        except Exception as e:
            print(f"Error sending WhatsApp group message: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def send_file_to_group(
        self, 
        file_path: str = None, 
        file_url: str = None, 
        caption: str = None
    ) -> Dict[str, Any]:
        try:
            if file_path:
                response = self.client.sending.sendFileByUpload(
                    self.group_id,
                    file_path,
                    caption or "File attachment"
                )
            elif file_url:
                response = self.client.sending.sendFileByUrl(
                    self.group_id,
                    file_url,
                    caption or "File attachment"
                )
            else:
                raise ValueError("Either file_path or file_url must be provided")
            
            print(f"File sent. Response: {response.data}")
            
            return {
                "status": "success",
                "message_id": response.data.get('id') if response.data else None
            }
        except Exception as e:
            print(f"Error sending file to WhatsApp group: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

whatsapp_service = GreenApiWhatsAppService()