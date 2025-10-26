
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, crud, schemas
from app.database import engine, SessionLocal, init_db, get_db
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.services.reward_achievements_service import RewardAchievementService
from app.services.notifications_service import NotificationService
from app.routers import achievements, notifications, websocket, admin

app = FastAPI(title="IdeaBridge API (MVP)")
app.include_router(achievements.router)
app.include_router(notifications.router)
app.include_router(websocket.router)
app.include_router(admin.router)

models.Base.metadata.create_all(bind=engine)

# initialize DB (dev only)
init_db()

@app.get("/")
def root():
    return {"message": "IdeaBridge backend is running"}

@app.get("/ideas/", response_model=list[schemas.IdeaOut])
def get_ideas(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_ideas(db, skip, limit)

@app.post("/auth/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = crud.create_user(user, db)
    return {"id": new_user.user_id, "email": new_user.email}


@app.post("/auth/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    access_token = crud.login_user(form_data, db)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id, 
        "email": current_user.email, 
        "full_name": current_user.full_name,
        "points": current_user.points,
        "coins": current_user.coins
    }

# ---------- Работа с идеями ----------
@app.post("/ideas/create")
def create_idea(
    idea: schemas.IdeaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Создание новой идеи и автоматическое начисление очков"""
    new_idea = crud.create_idea(db, idea, current_user.user_id)
    
    service = NotificationService(db)
    service.create_notification(
        user_id=current_user.user_id,
        title="Идея создана",
        message=f"Ваша идея '{idea.title}' успешно добавлена!"
    )

    return {
        "message": f"Идея '{new_idea.title}' успешно добавлена!",
        "idea_id": new_idea.idea_id,
        "author": current_user.full_name
    }


# ---------- Просмотр баллов ----------
@app.get("/users/me/points")
def get_user_points(current_user: models.User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "full_name": current_user.full_name,
        "points": current_user.points,
        "coins": current_user.coins
    }

@app.get("/points/logs")
def get_points_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    logs = crud.get_points_logs(db, current_user)
    return [
        {
            "date": log.created_at,
            "action": log.action,
            "points": log.points,
            "coins": log.coins
        }
        for log in logs
    ]

@app.get("/admin/points_rules")
def get_points_rules(db: Session = Depends(get_db)):
    points_rules = crud.get_points_rules(db)
    return points_rules


@app.put("/admin/points_rules/{action}")
def update_points_rule(action: str, update: schemas.PointsRuleUpdate, db: Session = Depends(get_db)):
    rule = crud.update_points_rule(action, update, db)
    return rule

@app.post("/ideas/{idea_id}/comment")
def add_comment(
    idea_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_comment = crud.create_comment(idea_id, comment, db, current_user)

    idea = db.query(models.Idea).filter(models.Idea.idea_id == new_comment.idea_id).first()
    if idea and idea.author_id != current_user.user_id:
        notification_service = NotificationService(db)
        notification_service.create_notification(
            user_id=idea.author_id,
            title="Новый комментарий к вашей идее",
            message=f"Пользователь {current_user.email} оставил комментарий: «{new_comment.text[:80]}...»"
        )

    return {"message": "Комментарий добавлен", "comment_id": new_comment.comment_id}

@app.post("/ideas/{idea_id}/vote")
def vote_idea(
    idea_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    service = RewardAchievementService(db)
    
    idea = db.query(models.Idea).filter(models.Idea.idea_id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Идея не найдена")

    # проверка, чтобы не голосовать дважды
    existing_vote = db.query(models.Vote).filter(
        models.Vote.idea_id == idea_id,
        models.Vote.user_id == current_user.user_id
    ).first()
    if existing_vote:
        db.delete(existing_vote)
        db.commit()
        return {"message": "Голос удалён"}

    new_vote = models.Vote(idea_id=idea_id, user_id=current_user.user_id, vote_type=1)
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    
     # автор идеи получает бонус за голос
    if idea.author_id != current_user.user_id:
        service.add_points(idea.author_id, "idea_like")
    
    # начисляем награду
    service.add_points(current_user.user_id, "vote")

    #Уведомление автора о голосе к его идее
    if idea.author_id != current_user.user_id:
        notification_service = NotificationService(db)
        notification_service.create_notification(
            user_id=idea.author_id,
            title="Новый лайк вашей идеи",
            message=f"Пользователь {current_user.email} проголосовал за вашу идею «{idea.title}»"
        )

    return {"message": "Голос принят", "vote_id": new_vote.vote_id}

@app.post("/expert/ideas/{idea_id}/status")
def update_idea_status(
    idea_id: int,
    status_data: schemas.IdeaStatusCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    service = RewardAchievementService(db)
    notification_service = NotificationService(db)
    
    # проверяем, что идея существует
    idea = db.query(models.Idea).filter(models.Idea.idea_id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Идея не найдена")

    # проверяем роль
    if current_user.role not in ("expert", "admin"):
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения статуса")

    # добавляем запись об изменении статуса
    new_status = models.IdeaStatus(
        idea_id=idea_id,
        expert_id=current_user.user_id,
        status=status_data.status,
        department=status_data.department,
        need_type=status_data.need_type,
        idea_type=status_data.idea_type,
        specialization=status_data.specialization,
        time_frame=status_data.time_frame,
        budget_range=status_data.budget_range,
        level=status_data.level,
        profit_estimation=status_data.profit_estimation,
        comment=status_data.comment,
    )
    db.add(new_status)
    idea.status = status_data.status
    db.commit()
    # если статус "Реализована" — начисляем награду автору
    service = RewardAchievementService(db)

    notification_service.create_notification(
        user_id=idea.author_id,
        title="Статус вашей идеи изменён",
        message=f"Ваша идея «{idea.title}» теперь имеет статус: {status_data.status}"
    )


    if status_data.status.lower() in ["реализована", "утверждена"]:
        service.add_points(idea.author_id, "idea_approved")
    return {"message": f"Статус идеи обновлён на '{status_data.status}'"}

@app.get("/ideas/{idea_id}/history")
def get_idea_history(idea_id: int, db: Session = Depends(get_db)):
    history = db.query(models.IdeaStatus).filter(
        models.IdeaStatus.idea_id == idea_id
    ).order_by(models.IdeaStatus.created_at.desc()).all()
    return history    




# --- Пример защищённого маршрута ---
@app.get("/ideas/protected")
def protected_test(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Привет, {current_user.full_name}! Это защищённый маршрут"}