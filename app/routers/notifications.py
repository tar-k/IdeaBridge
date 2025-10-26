from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.services.notifications_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def get_my_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = NotificationService(db)
    return service.get_user_notifications(current_user.user_id)

@router.post("/{notification_id}/read")
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = NotificationService(db)
    result = service.mark_as_read(notification_id, current_user.user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    return {"message": "Уведомление отмечено как прочитанное"}
