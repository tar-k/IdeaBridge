
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.services.reward_achievements_service import RewardAchievementService

def create_idea(db: Session, idea_in: schemas.IdeaCreate, author_id: int):
    idea = models.Idea(title=idea_in.title, description=idea_in.description, author_id=author_id, category_id=idea_in.category_id)
    db.add(idea)
    db.commit()
    db.refresh(idea)
    # team members handling - simple: add idea_team_members if table exists
    try:
        for uid in (idea_in.team_member_ids or []):
            db.execute("INSERT INTO ideabridge.idea_team_members (idea_id, user_id, is_primary) VALUES (:idea_id, :user_id, false) ON CONFLICT DO NOTHING", {"idea_id": idea.idea_id, "user_id": uid})
            db.commit()
    except Exception:
        pass

    service = RewardAchievementService(db)
    service.add_points(author_id, "create_idea")

    return idea

def list_ideas(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Idea).order_by(models.Idea.created_at.desc()).offset(skip).limit(limit).all()

def create_comment(
        idea_id: int,
        comment_in: schemas.CommentCreate,
        db: Session,
        current_user: models.User
    ):
    idea = db.query(models.Idea).filter(models.Idea.idea_id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Идея не найдена")

    # создаём комментарий
    new_comment = models.Comment(
        idea_id=idea_id,
        user_id=current_user.user_id,
        text=comment_in.text
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    service = RewardAchievementService(db)
    
    # автор идеи получает бонус за комментарии других пользователей
    if idea.author_id != current_user.user_id:
        service.add_points(idea.author_id, "comment_received") 

    # начисляем баллы по правилу
    service.add_points(current_user.user_id, "comment_add") 
    return new_comment

def create_user(user: schemas.UserCreate, db: Session):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_user_by_idea_id(db: Session,idea_id):
    idea = db.query(models.Idea).filter(models.Idea.idea_id == idea_id).first()
    
    user = db.query(models.User).filter(models.User.user_id == idea.author_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


def login_user(form_data: OAuth2PasswordRequestForm, db: Session):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    access_token = create_access_token(data={"sub": str(user.user_id)})
    
    return access_token

def get_points_logs(
    db: Session,
    current_user: models.User
):
    logs = (
        db.query(models.PointsLog)
        .filter(models.PointsLog.user_id == current_user.user_id)
        .order_by(models.PointsLog.created_at.desc())
        .all()
    )

    return logs

def get_points_rules(db: Session):
    return db.query(models.PointsRule).all()

def update_points_rule(action: str, update: schemas.PointsRuleUpdate, db: Session):
    rule = db.query(models.PointsRule).filter(models.PointsRule.action_key == action).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Правило не найдено")
    rule.points_amount = update.points
    rule.coins_amount = update.coins
    db.commit()
    db.refresh(rule)
    return rule

def change_idea_status(db: Session, idea_id: int, new_status: str, expert_id: int):
    db.execute("CALL ideabridge.update_idea_status(:idea_id, :new_status, :expert_id)",
               {"idea_id": idea_id, "new_status": new_status, "expert_id": expert_id})
    db.commit()
    service = RewardAchievementService(db)
    idea = db.query(models.Idea).filter(models.Idea.idea_id== idea_id)
    if new_status == "submitted":
        service.add_points(idea.author_id, "idea_submit")
    elif new_status == "approved":
        service.add_points(idea.author_id, "idea_approved")
    # elif new_status == "implemented":
    #     service.add_points(idea.author_id, "idea_implemented")

