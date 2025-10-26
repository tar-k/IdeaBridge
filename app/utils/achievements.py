from sqlalchemy.orm import Session
from app import models
from datetime import datetime

# ----------Перенес в сервис----------------------
# def check_and_award_achievements(user_id: int, db: Session):
#     """Проверяет условия и выдает достижения пользователю"""
#     user = db.query(models.User).filter(models.User.user_id == user_id).first()
#     if not user:
#         return

#     # Получаем количество идей, комментариев и лайков пользователя
#     ideas_count = db.query(models.Idea).filter(models.Idea.user_id == user_id).count()
#     comments_count = db.query(models.Comment).filter(models.Comment.user_id == user_id).count()
#     likes_received = db.query(models.Vote).join(models.Idea).filter(
#         models.Idea.user_id == user_id, models.Vote.vote_type == True
#     ).count()

#     # Список возможных достижений
#     rules = {
#         "first_idea": ideas_count >= 1,
#         "ten_ideas": ideas_count >= 10,
#         "five_comments": comments_count >= 5,
#         "hundred_likes": likes_received >= 100
#     }

#     for key, condition in rules.items():
#         if condition:
#             achievement = db.query(models.Achievement).filter(models.Achievement.condition_key == key).first()
#             if achievement:
#                 already_awarded = db.query(models.UserAchievement).filter_by(
#                     user_id=user_id, achievement_id=achievement.achievement_id
#                 ).first()
#                 if not already_awarded:
#                     db.add(models.UserAchievement(user_id=user_id, achievement_id=achievement.achievement_id))
#                     user.points += achievement.points_reward
#                     user.coins += achievement.coins_reward
#                     db.commit()
#                     db.refresh(user)
#                     print(f"Достижение {achievement.name} выдано пользователю {user.email}")
