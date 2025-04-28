from database.connection import db_manager
from database.models import UserProfile, Journal
from sqlalchemy import desc
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class UserService:
    def get_all_users(self):
        with db_manager.session_scope() as session:
            users = session.query(UserProfile.name).all()
            return [user[0] for user in users]

    def save_profile(self, profile_data):
        with db_manager.session_scope() as session:
            profile = UserProfile(**profile_data)
            session.merge(profile)
            
    def get_user_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a user's profile by name"""
        with db_manager.session_scope() as session:
            profile = session.query(UserProfile).filter_by(name=name).first()
            if profile:
                # Return a dictionary instead of the SQLAlchemy object to avoid session issues
                return {
                    'name': profile.name,
                    'goal': profile.goal,
                    'gender': profile.gender,
                    'age': profile.age,
                    'initial_weight': profile.initial_weight,
                    'height': profile.height,
                    'activity_level': profile.activity_level,
                    'training_style': profile.training_style,
                    'diet_type': profile.diet_type,
                    'allergies': profile.allergies,
                    'fav_foods': profile.fav_foods,
                    'created_date': profile.created_date
                }
            return None
            
    def get_latest_journal_entry(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a user's most recent journal entry"""
        with db_manager.session_scope() as session:
            entry = session.query(Journal).filter_by(name=name).order_by(desc(Journal.entry_date)).first()
            if entry:
                # Return a dictionary instead of the SQLAlchemy object
                return {
                    'id': entry.id,
                    'name': entry.name,
                    'entry_date': entry.entry_date,
                    'weight': entry.weight,
                    'mood': entry.mood,
                    'energy': entry.energy,
                    'workout_adherence': entry.workout_adherence,
                    'diet_adherence': entry.diet_adherence,
                    'notes': entry.notes
                }
            return None
            
    def get_user_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a user's progress status"""
        try:
            # Check if the UserStatus model exists in database/models.py
            from database.models import UserStatus
            with db_manager.session_scope() as session:
                status = session.query(UserStatus).filter_by(name=name).first()
                if status:
                    return {
                        'name': status.name,
                        'first_plan_generated': status.first_plan_generated,
                        'current_week': status.current_week,
                        'last_journal_date': status.last_journal_date
                    }
                return None
        except ImportError:
            # If UserStatus doesn't exist, create a temporary status object
            with db_manager.session_scope() as session:
                # Check if user has any plans generated
                from database.models import Plan
                plan = session.query(Plan).filter_by(name=name).first()
                return {
                    'name': name,
                    'first_plan_generated': plan is not None,
                    'current_week': 1 if plan else 0,
                    'last_journal_date': None
                }
                
    def update_user_status(self, name: str, **kwargs):
        """Update user's status fields"""
        try:
            # Check if UserStatus exists in models
            from database.models import UserStatus
            with db_manager.session_scope() as session:
                status = session.query(UserStatus).filter_by(name=name).first()
                if not status:
                    status = UserStatus(name=name)
                    session.add(status)
                
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(status, key):
                        setattr(status, key, value)
        except ImportError:
            # If UserStatus doesn't exist, we need to add it to the models
            logger.warning("UserStatus model not found. Status updates won't persist.")
            
    def create_user_data_dict(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create a dictionary of user data for AI service"""
        if not profile:
            return {}
            
        return {
            'name': profile['name'],
            'goal': profile['goal'],
            'gender': profile['gender'],
            'age': profile['age'],
            'weight': profile['initial_weight'],
            'height': profile['height'],
            'activity_level': profile['activity_level'],
            'training_style': profile['training_style'],
            'diet_type': profile['diet_type'],
            'allergies': profile['allergies'],
            'fav_foods': profile['fav_foods']
        }

    def create_user(self, name: str) -> bool:
        """Create a new user profile with just the name"""
        try:
            with db_manager.session_scope() as session:
                # Check if user already exists
                existing = session.query(UserProfile).filter_by(name=name).first()
                if existing:
                    return False
                    
                # Create new user with minimal profile
                new_user = UserProfile(
                    name=name,
                    goal="",
                    gender="",
                    age=30,
                    initial_weight=70.0,
                    height=175.0,
                    activity_level="",
                    training_style="",
                    diet_type="",
                    allergies="",
                    fav_foods=""
                )
                session.add(new_user)
                
                # Also create UserStatus entry 
                try:
                    from database.models import UserStatus
                    new_status = UserStatus(
                        name=name,
                        first_plan_generated=False,
                        current_week=0
                    )
                    session.add(new_status)
                except ImportError:
                    # UserStatus model not available
                    pass
                    
                return True
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False
