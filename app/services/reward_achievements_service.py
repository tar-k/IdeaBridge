from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app import models


class RewardAchievementService:
    """
    Универсальная система рейтинга и наград.
    Начисляет очки и монеты, проверяет достижения.
    """

    def __init__(self, db: Session):
        self.db = db

    def add_points(self, user_id: int, action_key: str):
        """
        Начисление очков и монет пользователю по действию из таблицы points_rules.
        """
        # Найти правило начисления
        rule = self.db.query(models.PointsRule).filter_by(action_key=action_key).first()
        if not rule:
            return None  # если нет правила, просто ничего не делаем

        user = self.db.query(models.User).filter_by(user_id=user_id).first()
        if not user:
            return None

        # Начисление очков и монет
        user.points += rule.points_amount
        user.coins += rule.coins_amount

        # Запись в лог
        log = models.PointsLog(
            user_id=user_id,
            action=action_key,
            points=rule.points_amount,
            coins=rule.coins_amount,
            # created_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        
        # Проверяем достижения
        self.check_achievements(user_id)

        
        return {"points_added": rule.points_amount, "coins_added": rule.coins_amount}

    def check_achievements(self, user_id: int):
        """
        Проверяет, есть ли новые достижения для пользователя.
        """
        user = self.db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            return

        # Получаем количество идей, комментариев и лайков пользователя
        ideas_count = self.db.query(models.Idea).filter(models.Idea.author_id == user_id).count()
        comments_count = self.db.query(models.Comment).filter(models.Comment.user_id == user_id).count()
        likes_received = self.db.query(models.Vote).join(models.Idea).filter(
            models.Idea.author_id == user_id, models.Vote.vote_type == True
        ).count()

        # Список возможных достижений
        rules = {
            "first_idea": ideas_count >= 1,
            "ten_ideas": ideas_count >= 10,
            "five_comments": comments_count >= 5,
            "hundred_likes": likes_received >= 100
        }

        for key, condition in rules.items():
            if condition:
                achievement = self.db.query(models.Achievement).filter(models.Achievement.condition_key == key).first()
                if achievement:
                    already_awarded = self.db.query(models.UserAchievement).filter_by(
                        user_id=user_id, achievement_id=achievement.achievement_id
                    ).first()
                    if not already_awarded:
                        self._grant_achievement(user, achievement)
                        print(f"✅ Достижение {achievement.name} выдано пользователю {user.email}")

        self.db.commit()

    def _grant_achievement(self, user: models.User, achievement: models.Achievement):
        """
        Выдает достижение пользователю.
        """
        user_ach = models.UserAchievement(
            user_id=user.user_id,
            achievement_id=achievement.achievement_id,
            # awarded_at=datetime.utcnow()
        )
        self.db.add(user_ach)
        self.db.commit()
        # Можно также дать бонусные монеты/очки
        if achievement.reward_points or achievement.reward_coins:
            user.points += achievement.reward_points
            user.coins += achievement.reward_coins
            self.db.refresh(user)

        # 🔔 уведомление о достижении
        from app.services.notifications_service import NotificationService
        NotificationService(self.db).create_notification(
            user_id=user.user_id,
            title="Новое достижение!",
            message=f"Поздравляем! Вы получили достижение «{achievement.name}» 🎉"
        )
