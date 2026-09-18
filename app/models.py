"""
Database models — one class per table, matching the product spec's data model.
"""
import uuid
import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base


def gen_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    voice_profile = relationship("VoiceProfile", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")


class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)

    preset = Column(String, default="Natural")          # Natural / Professional / Calm / Clear
    preferred_loudness = Column(Integer, default=55)      # 0-100
    preferred_pace = Column(Integer, default=135)         # target words per minute
    preferred_clarity = Column(Integer, default=72)        # 0-100
    processing_intensity = Column(Integer, default=60)     # 0-100

    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="voice_profile")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    title = Column(String, default="Session")
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(String, default="active")  # active | completed | interrupted

    user = relationship("User", back_populates="sessions")
    metrics = relationship("SessionMetrics", back_populates="session", uselist=False)
    analysis = relationship("AIAnalysis", back_populates="session", uselist=False)


class SessionMetrics(Base):
    __tablename__ = "session_metrics"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, ForeignKey("sessions.id"), unique=True, nullable=False)

    confidence_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    stability_score = Column(Float, nullable=True)
    energy_score = Column(Float, nullable=True)
    speaking_wpm = Column(Float, nullable=True)
    filler_words_per_min = Column(Float, nullable=True)
    pause_count = Column(Integer, nullable=True)

    session = relationship("Session", back_populates="metrics")


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, ForeignKey("sessions.id"), unique=True, nullable=False)

    strengths = Column(Text, nullable=True)
    improvements = Column(Text, nullable=True)
    coach_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("Session", back_populates="analysis")
