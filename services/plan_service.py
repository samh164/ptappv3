from datetime import datetime, timedelta
import logging
from database.connection import db_manager
from database.models import Plan, UserProfile, Journal, UserStatus
from services.user_service import UserService
import copy

logger = logging.getLogger(__name__)

class PlanService:
    def get_latest_plan(self, username):
        """Get the user's most recent fitness plan"""
        with db_manager.session_scope() as session:
            plan = session.query(Plan)\
                .filter(Plan.name == username)\
                .order_by(Plan.created_date.desc())\
                .first()
                
            # If plan exists, create a detached copy with all attributes loaded
            if plan:
                # Create a dictionary of the plan's attributes
                plan_dict = {
                    'id': plan.id,
                    'name': plan.name,
                    'age': plan.age,
                    'gender': plan.gender,
                    'goal': plan.goal,
                    'weight': plan.weight,
                    'height': plan.height,
                    'activity_level': plan.activity_level,
                    'training_style': plan.training_style,
                    'diet_type': plan.diet_type,
                    'plan': plan.plan,
                    'created_date': plan.created_date
                }
                
                # Create a detached Plan object with the copied attributes
                detached_plan = Plan()
                for key, value in plan_dict.items():
                    setattr(detached_plan, key, value)
                
                return detached_plan
            
            return None

    def save_plan(self, username, plan_content):
        """Save a new fitness plan"""
        try:
            # Get user profile using UserService
            user_service = UserService()
            profile = user_service.get_user_profile(username)
            
            if not profile:
                raise ValueError("User profile not found")
                
            # Get latest weight from journal if available
            latest_weight = profile['initial_weight']
            with db_manager.session_scope() as session:
                latest_journal = session.query(Journal)\
                    .filter(Journal.name == username)\
                    .order_by(Journal.entry_date.desc())\
                    .first()
                    
                if latest_journal:
                    latest_weight = latest_journal.weight

            with db_manager.session_scope() as session:
                # Create new plan
                new_plan = Plan(
                    name=username,
                    age=profile['age'],
                    gender=profile['gender'],
                    goal=profile['goal'],
                    weight=latest_weight,  # Use latest weight from journal
                    height=profile['height'],
                    activity_level=profile['activity_level'],
                    training_style=profile['training_style'],
                    diet_type=profile['diet_type'],
                    plan=plan_content,
                    created_date=datetime.now().date()
                )
                
                session.add(new_plan)
                return True
                
        except Exception as e:
            logger.error(f"Error saving plan: {str(e)}")
            raise

    def get_previous_plans(self, username, limit=3):
        """Get user's previous plans for context when generating new plans"""
        with db_manager.session_scope() as session:
            plans = session.query(Plan)\
                .filter(Plan.name == username)\
                .order_by(Plan.created_date.desc())\
                .limit(limit)\
                .all()
                
            if not plans:
                return None
                
            # Format plans for use in the AI prompt
            plan_texts = []
            for i, plan in enumerate(plans):
                plan_date = plan.created_date.strftime("%Y-%m-%d")
                plan_texts.append(f"PLAN {i+1} ({plan_date}):\n{plan.plan}\n\n")
                
            return "\n".join(plan_texts)

    def get_journal_summary(self, username, weeks=4):
        """Get a summary of recent journal entries for context in AI prompts"""
        with db_manager.session_scope() as session:
            # Get entries from the last few weeks
            cutoff_date = datetime.now().date() - timedelta(weeks=weeks)
            entries = session.query(Journal)\
                .filter(Journal.name == username)\
                .filter(Journal.entry_date >= cutoff_date)\
                .order_by(Journal.entry_date)\
                .all()
                
            if not entries:
                return "No journal data available."
                
            # Create a summary of journal data
            summary = "JOURNAL SUMMARY:\n"
            for entry in entries:
                summary += f"Date: {entry.entry_date.strftime('%Y-%m-%d')}\n"
                summary += f"Weight: {entry.weight}kg\n"
                summary += f"Mood: {entry.mood}\n"
                summary += f"Energy: {entry.energy}\n"
                summary += f"Workout Adherence: {entry.workout_adherence}%\n"
                summary += f"Diet Adherence: {entry.diet_adherence}%\n"
                if entry.notes:
                    summary += f"Notes: {entry.notes}\n"
                summary += "\n"
                
            return summary

    def has_journal_for_week(self, username, week):
        """Check if user has submitted journal entry for current week"""
        try:
            with db_manager.session_scope() as session:
                # Get user status to find when they started
                status = session.query(UserStatus).filter_by(name=username).first()
                if not status or not status.last_journal_date:
                    return False
                    
                # Check for entries in the last 7 days
                one_week_ago = datetime.now().date() - timedelta(days=7)
                recent_entry = session.query(Journal)\
                    .filter(Journal.name == username)\
                    .filter(Journal.entry_date >= one_week_ago)\
                    .first()
                    
                return recent_entry is not None
        except Exception as e:
            logger.error(f"Error checking journal entry: {str(e)}")
            return False

    def get_user_progress(self, username):
        """Get user's progress data for visualization"""
        with db_manager.session_scope() as session:
            journals = session.query(Journal)\
                .filter(Journal.name == username)\
                .order_by(Journal.entry_date)\
                .all()
                
            # Create detached copies of the journal entries
            detached_journals = []
            for journal in journals:
                # Create a dictionary of the journal's attributes
                journal_dict = {
                    'id': journal.id,
                    'name': journal.name,
                    'entry_date': journal.entry_date,
                    'weight': journal.weight,
                    'mood': journal.mood,
                    'energy': journal.energy,
                    'workout_adherence': journal.workout_adherence,
                    'diet_adherence': journal.diet_adherence,
                    'notes': journal.notes
                }
                
                # Create a detached Journal object with the copied attributes
                detached_journal = Journal()
                for key, value in journal_dict.items():
                    setattr(detached_journal, key, value)
                
                detached_journals.append(detached_journal)
                
            return detached_journals
