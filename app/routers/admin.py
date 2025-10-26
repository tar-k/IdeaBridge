from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

def require_admin(user: models.User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён. Требуется роль администратора.")

# ---------- ПОЛЬЗОВАТЕЛИ ----------
@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin(current_user)
    return db.query(models.User).all()

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin(current_user)
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(user)
    db.commit()
    return {"message": "Пользователь удалён"}

# ---------- ИДЕИ ----------
@router.get("/ideas")
def list_ideas(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin(current_user)
    return db.query(models.Idea).all()

@router.put("/ideas/{idea_id}/status")
def admin_update_idea_status(
    idea_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    require_admin(current_user)
    idea = db.query(models.Idea).filter(models.Idea.idea_id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Идея не найдена")
    idea.status = status
    db.commit()
    return {"message": f"Статус идеи обновлён на {status}"}

# ---------- СТАТИСТИКА ----------
@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin(current_user)
    return {
        "users_total": db.query(models.User).count(),
        "ideas_total": db.query(models.Idea).count(),
        "comments_total": db.query(models.Comment).count(),
        "achievements_given": db.query(models.UserAchievement).count()
    }
