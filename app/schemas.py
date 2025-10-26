
from pydantic import BaseModel, Field
from typing import Any, Optional, List

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str= Field(..., min_length=6, max_length=72)

class IdeaCreate(BaseModel):
    title: str
    description: str
    category_id: Optional[int] = None
    team_member_ids: Optional[List[int]] = []

class IdeaOut(BaseModel):
    idea_id: int
    title: str
    description: str
    author_id: int
    status: str

    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    idea_id: int
    user_id: int
    text: str

class PointsRuleUpdate(BaseModel):
    points: int
    coins: int

class VoteCreate(BaseModel):
    idea_id: int

class IdeaStatusCreate(BaseModel):
    idea_id: int
    status: str
    department: str | None = None
    need_type: str | None = None
    idea_type: str | None = None
    specialization: str | None = None
    time_frame: str | None = None
    budget_range: str | None = None
    level: str | None = None
    profit_estimation: str | None = None
    ai_scores: Optional[Any] = None   #в дальнейшем ai_scores: Optional[AIScores] = None
    comment: str | None = None

#----------------TODO-----------------
class AIScores(BaseModel):
    clarity: Optional[float]
    creativity: Optional[float]
    feasibility: Optional[float]
#----------------TODO-----------------