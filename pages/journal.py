import streamlit as st
from datetime import datetime, timedelta
from database.connection import db_manager
from database.models import Journal
from services.plan_service import PlanService
from services.user_service import UserService
from utils.display import display_success_message, display_error_message
import logging

logger = logging.getLogger(__name__)

def display_journal_page(username: str, plan_service: PlanService):
    """Display the journal page for tracking progress"""
    st.subheader("📓 Weekly Journal")
    
    # Check if user has a plan first
    latest_plan = plan_service.get_latest_plan(username)
    if not latest_plan:
        st.warning("You need to generate a fitness plan before you can start journaling.")
        if st.button("Go to Home"):
            st.session_state.nav = "home"
            st.rerun()
        return
    
    # Get user status to determine current week
    user_service = UserService()
    status = user_service.get_user_status(username)
    current_week = status['current_week'] if status else 1
    
    st.markdown(f"### Week {current_week} Check-In")
    
    # Check for recent entries to avoid duplicates
    with db_manager.session_scope() as session:
        one_week_ago = datetime.now().date() - timedelta(days=7)
        recent_entries = session.query(Journal).filter(
            Journal.name == username,
            Journal.entry_date >= one_week_ago
        ).order_by(Journal.entry_date.desc()).all()
        
        if recent_entries:
            st.info(f"You've made {len(recent_entries)} journal entries in the past week. Latest entry was on {recent_entries[0].entry_date.strftime('%Y-%m-%d')}.")
    
    # Journal entry form
    with st.form("journal_form"):
        # Date picker
        entry_date = st.date_input("Date", value=datetime.now().date())
        
        # Weight tracking
        col1, col2 = st.columns(2)
        with col1:
            # Safely access the weight attribute
            default_weight = 70.0
            if latest_plan and hasattr(latest_plan, 'weight'):
                default_weight = latest_plan.weight
            
            weight = st.number_input("Current Weight (kg)", 
                min_value=30.0, max_value=250.0, step=0.1, 
                value=default_weight)
        
        # Adherence sliders
        with col2:
            workout_adherence = st.slider("Workout Plan Adherence (%)", 
                min_value=0, max_value=100, value=80, step=5)
            diet_adherence = st.slider("Diet Plan Adherence (%)", 
                min_value=0, max_value=100, value=80, step=5)
        
        # Mood and energy
        col1, col2 = st.columns(2)
        with col1:
            mood = st.selectbox("Overall Mood", 
                ["Excellent", "Good", "Average", "Poor", "Terrible"])
        with col2:
            energy = st.selectbox("Energy Level", 
                ["Very High", "High", "Average", "Low", "Very Low"])
        
        # Notes
        notes = st.text_area("Notes", 
            placeholder="How did your week go? Any challenges or victories? Issues with the plan?")
        
        # Submit button
        submitted = st.form_submit_button("Save Journal Entry")
        
        if submitted:
            try:
                with db_manager.session_scope() as session:
                    # Check if entry for this date already exists
                    existing_entry = session.query(Journal).filter_by(
                        name=username, entry_date=entry_date).first()
                    
                    if existing_entry:
                        # Update existing entry
                        existing_entry.weight = weight
                        existing_entry.mood = mood
                        existing_entry.energy = energy
                        existing_entry.workout_adherence = workout_adherence
                        existing_entry.diet_adherence = diet_adherence
                        existing_entry.notes = notes
                        message = "Journal entry updated successfully!"
                    else:
                        # Create new entry
                        new_entry = Journal(
                            name=username,
                            entry_date=entry_date,
                            weight=weight,
                            mood=mood,
                            energy=energy,
                            workout_adherence=workout_adherence,
                            diet_adherence=diet_adherence,
                            notes=notes
                        )
                        session.add(new_entry)
                        message = "New journal entry saved successfully!"
                    
                    # Update last_journal_date in user status
                    user_service.update_user_status(username, last_journal_date=entry_date)
                
                display_success_message(message)
                
                # Offer to generate new plan if this is for the current week
                current_date = datetime.now().date()
                is_current_week = abs((entry_date - current_date).days) <= 7
                
                if is_current_week:
                    st.success("You've completed your journal entry for this week! You can now generate a new plan.")
                    if st.button("Generate New Plan"):
                        st.session_state.nav = "home"
                        st.session_state.generate_plan = True
                        st.rerun()
                
            except Exception as e:
                logger.error(f"Error saving journal entry: {str(e)}")
                display_error_message(f"Error saving journal entry: {str(e)}")
    
    # Display journal history if available
    st.markdown("### Journal History")
    
    with db_manager.session_scope() as session:
        entries = session.query(Journal).filter_by(name=username).order_by(Journal.entry_date.desc()).all()
        
        if entries:
            # Create a container to show progress insights
            with st.expander("Progress Insights", expanded=True):
                if len(entries) >= 2:
                    first_weight = entries[-1].weight
                    latest_weight = entries[0].weight
                    weight_change = latest_weight - first_weight
                    
                    st.write(f"Starting weight: {first_weight} kg")
                    st.write(f"Current weight: {latest_weight} kg")
                    st.write(f"Total change: {weight_change:.1f} kg")
                    
                    # Calculate average adherence
                    avg_workout = sum([e.workout_adherence for e in entries]) / len(entries)
                    avg_diet = sum([e.diet_adherence for e in entries]) / len(entries)
                    st.write(f"Average workout adherence: {avg_workout:.1f}%")
                    st.write(f"Average diet adherence: {avg_diet:.1f}%")
                else:
                    st.info("Add more journal entries to see progress insights.")
            
            # Show individual entries
            for entry in entries:
                with st.expander(f"Entry: {entry.entry_date.strftime('%Y-%m-%d')}"):
                    st.write(f"Weight: {entry.weight} kg")
                    st.write(f"Mood: {entry.mood}")
                    st.write(f"Energy: {entry.energy}")
                    st.write(f"Workout Adherence: {entry.workout_adherence}%")
                    st.write(f"Diet Adherence: {entry.diet_adherence}%")
                    st.write(f"Notes: {entry.notes}")
        else:
            st.info("No journal entries found. Start tracking your progress by adding your first entry.")

def calculate_week_number(start_date, current_date):
    """Calculate the week number based on the start date and current date"""
    days_diff = (current_date - start_date).days
    return max(1, (days_diff // 7) + 1)
