
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()
SCHEMA = "ideabridge"

class User(Base):
    __tablename__ = "users"
    __table_args__ = ({'schema': SCHEMA},)

    user_id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False, default='user')
    points = Column(Integer, nullable=False, default=0)
    coins = Column(Integer, nullable=False, default=0)
    department = Column(String(150))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    #связи
    idea = relationship("Idea", back_populates="author", cascade="all, delete-orphan")
    points_log = relationship("PointsLog", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = ({'schema': SCHEMA},)
    category_id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)

class Idea(Base):
    __tablename__ = "ideas"
    __table_args__ = ({'schema': SCHEMA},)
    idea_id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey(f"{SCHEMA}.users.user_id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey(f"{SCHEMA}.categories.category_id"))
    status = Column(String(50), nullable=False, default='new')
    ai_generated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    #связи
    author = relationship("User", back_populates="idea")
    comments = relationship("Comment", back_populates="idea", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="idea", cascade="all, delete-orphan")
    statuses = relationship("IdeaStatus", back_populates="idea", cascade="all, delete-orphan")


class IdeaStatus(Base):
    __tablename__ = "idea_statuses"
    __table_args__ = ({'schema': SCHEMA},)
    status_id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey(f"{SCHEMA}.ideas.idea_id", ondelete="CASCADE"), nullable=False)
    expert_id = Column(Integer, ForeignKey(f"{SCHEMA}.users.user_id"))
    status = Column(String(80), nullable=False)
    department = Column(String(150))
    need_type = Column(String(120))
    idea_type = Column(String(150))
    specialization = Column(String(200))
    time_frame = Column(String(80))
    budget_range = Column(String(120))
    level = Column(String(80))
    profit_estimation = Column(String(120))
    ai_scores = Column(JSON)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    idea = relationship("Idea", back_populates="statuses")
    expert = relationship("User")

class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = ({'schema': SCHEMA},)
    comment_id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey(f"{SCHEMA}.ideas.idea_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(f"{SCHEMA}.users.user_id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # связи
    idea = relationship("Idea", back_populates="comments")
    user = relationship("User", back_populates="comments")

class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint('idea_id','user_id', name='uq_votes_idea_user'), {'schema': SCHEMA})
    vote_id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey(f"{SCHEMA}.ideas.idea_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(f"{SCHEMA}.users.user_id", ondelete="CASCADE"), nullable=False)
    vote_type = Column(Boolean, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # связи
    idea = relationship("Idea", back_populates="votes")
    user = relationship("User", back_populates="votes")

class Reward(Base):
    __tablename__ = "rewards"
    __table_args__ = ({'schema': SCHEMA},)
    reward_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    image_url = Column(Text)
    cost = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RewardPurchase(Base):
    __tablename__ = "reward_purchases"
    __table_args__ = ({'schema': SCHEMA},)
    purchase_id = Column(Integer, primary_key=True)
    reward_id = Column(Integer, ForeignKey(f"{SCHEMA}.rewards.reward_id"), nullable=False)
    user_id = Column(Integer, ForeignKey(f"{SCHEMA}.users.user_id"), nullable=False)
    status = Column(String(30), nullable=False, default='requested')
    cost = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint('user_id','type','related_type','related_id', name='uq_transactions_event'), {'schema': SCHEMA})
    transaction_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f"{SCHEMA}.users.user_id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(Text)
    related_type = Column(String(50))
    related_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PointsRule(Base):
    __tablename__ = "points_rules"
    __table_args__ = {"schema": "ideabridge"}

    rule_id = Column(Integer, primary_key=True, index=True)
    action_key = Column(String, unique=True, nullable=False)  # например: "create_idea", "vote", "comment"
    points_amount = Column(Integer, default=0)
    coins_amount = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class PointsLog(Base):
    __tablename__ = "points_log"
    __table_args__ = {"schema": "ideabridge"}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("ideabridge.users.user_id", ondelete="CASCADE"))
    action = Column(String, nullable=False)  # например: create_idea, vote, comment
    points = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # связь с пользователем
    user = relationship("User", back_populates="points_log")

class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = {"schema": "ideabridge"}

    achievement_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    condition_key = Column(String(100), unique=True, nullable=False)
    reward_points = Column(Integer, default=0)
    reward_coins = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = {"schema": "ideabridge"}

    # user_achievement_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("ideabridge.users.user_id", ondelete="CASCADE"), primary_key=True)
    achievement_id = Column(Integer, ForeignKey("ideabridge.achievements.achievement_id", ondelete="CASCADE"), primary_key=True)
    received_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="notifications") 

