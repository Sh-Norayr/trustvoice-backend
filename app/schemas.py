"""
Pydantic schemas — define the shape of data going in and out of the API.
Keeping these separate from the DB models (models.py) means we never
accidentally leak internal fields like password_hash to the client.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ---------- Auth ----------

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Voice Profile ----------

class VoiceProfileIn(BaseModel):
    preset: str = "Natural"
    preferred_loudness: int = Field(55, ge=0, le=100)
    preferred_pace: int = Field(135, ge=80, le=220)
    preferred_clarity: int = Field(72, ge=0, le=100)
    processing_intensity: int = Field(60, ge=0, le=100)


class VoiceProfileOut(VoiceProfileIn):
    id: str
    user_id: str
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Sessions ----------

class SessionCreate(BaseModel):
    title: Optional[str] = "Session"


class SessionMetricsOut(BaseModel):
    confidence_score: Optional[float]
    clarity_score: Optional[float]
    stability_score: Optional[float]
    energy_score: Optional[float]
    speaking_wpm: Optional[float]
    filler_words_per_min: Optional[float]
    pause_count: Optional[int]

    class Config:
        from_attributes = True


class AIAnalysisOut(BaseModel):
    strengths: Optional[str]
    improvements: Optional[str]
    coach_note: Optional[str]

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: str
    title: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    status: str

    class Config:
        from_attributes = True


class SessionDetailOut(SessionOut):
    metrics: Optional[SessionMetricsOut]
    analysis: Optional[AIAnalysisOut]
    notice: Optional[str] = None
