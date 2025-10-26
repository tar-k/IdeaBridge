from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, database, schemas
from app.auth import get_current_user
from typing import List

router = APIRouter(prefix="/achievements", tags=["Achievements"])

@router.get("/my", response_model=List[dict])
def get_my_achievements(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    achievements = (
        db.query(models.Achievement, models.UserAchievement.received_at)
        .join(models.UserAchievement)
        .filter(models.UserAchievement.user_id == current_user.user_id)
        .all()
    )
    result = []
    for ach, received_at in achievements:
        result.append({
            "achievement_id": ach.achievement_id,
            "name": ach.name,
            "description": ach.description,
            "reward_points": ach.reward_points,
            "reward_coins": ach.reward_coins,
            "received_at": received_at.isoformat() if received_at else None
        })
    return result
