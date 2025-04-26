from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    name = Column(String, primary_key=True)
    goal = Column(String)
    gender = Column(String)
    age = Column(Integer)
    initial_weight = Column(Float)
    height = Column(Float)
    activity_level = Column(String)
    training_style = Column(String)
    diet_type = Column(String)
    allergies = Column(Text)
    fav_foods = Column(Text)
    created_date = Column(Date, default=datetime.now().date())

    journals = relationship("Journal", back_populates="user")
    plans = relationship("Plan", back_populates="user")

class UserStatus(Base):
    __tablename__ = 'user_status'
    
    name = Column(String, ForeignKey('user_profiles.name'), primary_key=True)
    first_plan_generated = Column(Boolean, default=False)
    current_week = Column(Integer, default=0)
    last_journal_date = Column(Date, nullable=True)
    
    user = relationship("UserProfile")

class Plan(Base):
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, ForeignKey('user_profiles.name'))
    age = Column(Integer)
    gender = Column(String)
    goal = Column(String)
    weight = Column(Float)
    height = Column(Float)
    activity_level = Column(String)
    training_style = Column(String)
    diet_type = Column(String)
    plan = Column(Text)
    created_date = Column(Date, default=datetime.now().date())
    
    user = relationship("UserProfile")

class Journal(Base):
    __tablename__ = 'journals'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, ForeignKey('user_profiles.name'))
    entry_date = Column(Date)
    weight = Column(Float)
    mood = Column(String)
    energy = Column(String)
    workout_adherence = Column(Integer)
    diet_adherence = Column(Integer)
    notes = Column(Text)
    
    user = relationship("UserProfile")
