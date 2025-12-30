"""
SQLAlchemy models for the GlucoGuide application.

Tables:
- users: User accounts
- profiles: Health profiles for personalization
- chats: Chat sessions
- messages: Individual messages in chats
- attachments: Uploaded images/files
- foods: Cached food data from USDA
- gi_values: Glycemic index values from various sources
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    profile: Mapped[Optional["Profile"]] = relationship("Profile", back_populates="user", uselist=False)
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Profile(Base):
    """User health profile for personalized recommendations"""
    __tablename__ = "profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Basic info
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sex: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # male, female, other
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Lifestyle
    activity_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # sedentary, light, moderate, active, very_active
    goals: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # weight_loss, maintenance, muscle_gain, health
    
    # Diabetes/IR status
    has_insulin_resistance: Mapped[bool] = mapped_column(Boolean, default=False)
    diabetes_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # none, type1, type2, prediabetes, gestational
    diabetes_duration_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Medical metrics (optional)
    a1c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # HbA1c percentage
    fasting_glucose: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # mg/dL
    
    # Medications and conditions (stored as JSON)
    medications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    conditions_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object for other conditions
    
    # Dietary preferences
    dietary_preferences: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # vegetarian, vegan, keto, etc.
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Profile completion
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<Profile(user_id={self.user_id}, diabetes_type='{self.diabetes_type}')>"
    
    @property
    def bmi(self) -> Optional[float]:
        """Calculate BMI if height and weight are available"""
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 1)
        return None


class Chat(Base):
    """Chat session model"""
    __tablename__ = "chats"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), default="New Chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chats")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Chat(id={self.id}, title='{self.title}')>"


class Message(Base):
    """Individual message in a chat"""
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Optional: store eGL result as JSON for assistant messages
    egl_result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    food_analysis_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}')>"


class Attachment(Base):
    """Uploaded files (images) attached to messages"""
    __tablename__ = "attachments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), index=True)
    
    type: Mapped[str] = mapped_column(String(20), default="image")  # image, file
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)  # Relative path from uploads folder
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # bytes
    sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # For deduplication
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="attachments")
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, type='{self.type}')>"


class Food(Base):
    """Cached food data from USDA FoodData Central and other sources"""
    __tablename__ = "foods"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    
    # USDA data
    usda_fdc_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    usda_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Macros per 100g
    carbs_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    protein_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fat_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fiber_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calories_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Serving info
    serving_size_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    serving_description: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Category
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Data source tracking
    data_source: Mapped[str] = mapped_column(String(50), default="manual")  # manual, usda, imported
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gi_values: Mapped[List["GIValue"]] = relationship("GIValue", back_populates="food", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Food(id={self.id}, name='{self.canonical_name}')>"


class GIValue(Base):
    """Glycemic Index values from various sources"""
    __tablename__ = "gi_values"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    food_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("foods.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Alternative: store by name if food not in foods table yet
    food_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    
    # GI data
    gi: Mapped[float] = mapped_column(Float, nullable=False)
    gi_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # low, medium, high
    
    # Source tracking
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "University of Sydney", "Harvard"
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    confidence: Mapped[str] = mapped_column(String(20), default="medium")  # high, medium, low
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    food: Mapped[Optional["Food"]] = relationship("Food", back_populates="gi_values")
    
    # Index for faster lookups
    __table_args__ = (
        Index('ix_gi_values_food_name_source', 'food_name', 'source'),
    )
    
    def __repr__(self):
        return f"<GIValue(food='{self.food_name}', gi={self.gi}, source='{self.source}')>"


class Session(Base):
    """Server-side session storage"""
    __tablename__ = "sessions"
    
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # Session ID
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON session data
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Session(id='{self.id}', user_id={self.user_id})>"

