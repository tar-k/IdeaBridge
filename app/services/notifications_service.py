from app import models
from sqlalchemy.orm import Session
from datetime import datetime
from app.routers.websocket import active_connections
import json, asyncio

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, user_id: int, title: str, message: str):
        notification = models.Notification(
            user_id=user_id,
            title=title,
            message=message,
            created_at=datetime.utcnow()
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        if user_id in active_connections:
            websocket = active_connections[user_id]
            
            data = {"title": title, "message": message, "id": notification.notification_id}
            try:
                asyncio.create_task(websocket.send_text(json.dumps(data)))
            except Exception as e:
                print(f"Ошибка при отправке WebSocket уведомления: {e}")
        
        return notification

    def get_user_notifications(self, user_id: int):
        return self.db.query(models.Notification).filter(
            models.Notification.user_id == user_id
        ).order_by(models.Notification.created_at.desc()).all()

    def mark_as_read(self, notification_id: int, user_id: int):
        notification = self.db.query(models.Notification).filter(
            models.Notification.notification_id == notification_id,
            models.Notification.user_id == user_id
        ).first()
        if notification:
            notification.is_read = True
            self.db.commit()
            return notification
        return None
