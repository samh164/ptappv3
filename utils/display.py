import streamlit as st
from typing import Dict, Any
from services.user_service import UserService

def show_workflow_guidance():
    """Show guidance popups for different stages of the app"""
    guidance = {
        'welcome': {
            'title': "👋 Welcome to AI Personal Trainer!",
            'message': """
            Here's how to get started:
            1. Select 'Create New User' or choose an existing user
            2. Complete your profile with your fitness details
            3. Generate your personalized fitness plan
            4. Track your progress with weekly journal entries
            5. Get updated plans based on your progress
            """
        },
        'new_profile': {
            'title': "📝 Creating Your Profile",
            'message': """
            Tips for profile creation:
            • Be specific about food preferences and allergies
            • List ANY foods you absolutely won't eat
            • Mention all dietary restrictions
            • Specify any injuries or limitations
            • The more detail you provide, the better your plan will be!
            """
        },
        'first_plan': {
            'title': "🎯 Your First Fitness Plan",
            'message': """
            What happens next:
            1. Review your personalized workout and meal plan
            2. Follow the plan for a week
            3. Complete your weekly journal
            4. Get an updated plan based on your progress
            
            Remember: You can always adjust the plan if needed!
            """
        },
        'journal': {
            'title': "📓 Weekly Journal",
            'message': """
            Track your progress by:
            • Recording your weekly achievements
            • Noting any challenges
            • Updating your measurements
            • Rating your plan adherence
            
            This helps create better plans for you!
            """
        }
    }
    
    # Show relevant popups based on user state
    for popup_id, content in guidance.items():
        if popup_id not in st.session_state.shown_popups:
            with st.sidebar.expander(content['title'], expanded=True):
                st.write(content['message'])
                if st.button(f"Got it! (Don't show again)", key=f"dismiss_{popup_id}"):
                    st.session_state.shown_popups.add(popup_id)
                    st.rerun()

def display_user_summary(name: str):
    """Display user profile summary in the sidebar"""
    st.subheader(f"📊 Summary for {name}")
    
    user_service = UserService()
    profile = user_service.get_user_profile(name)
    
    if not profile:
        st.warning("Profile not found. Please create your profile.")
        return
    
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Profile Information")
        st.write(f"Goal: {profile.get('goal', 'Not set')}")
        st.write(f"Gender: {profile.get('gender', 'Not set')}")
        st.write(f"Age: {profile.get('age', 'Not set')}")
        st.write(f"Initial Weight: {profile.get('initial_weight', 'Not set')} {' kg' if profile.get('initial_weight') else ''}")
        st.write(f"Height: {profile.get('height', 'Not set')} {' cm' if profile.get('height') else ''}")
        st.write(f"Activity Level: {profile.get('activity_level', 'Not set')}")
        st.write(f"Training Style: {profile.get('training_style', 'Not set')}")
        st.write(f"Diet Type: {profile.get('diet_type', 'Not set')}")
        
        # Add allergies and favorite foods if they exist
        allergies = profile.get('allergies', '')
        fav_foods = profile.get('fav_foods', '')
        if allergies:
            st.write(f"Allergies/Restrictions: {allergies}")
        if fav_foods:
            st.write(f"Favorite Foods: {fav_foods}")
    
    with col2:
        # Get latest stats from journal
        latest_journal = user_service.get_latest_journal_entry(name)
        
        st.markdown("### Latest Statistics")
        if latest_journal:
            st.write(f"Current Weight: {latest_journal.get('weight', 'Not recorded')} kg")
            st.write(f"Workout Adherence: {latest_journal.get('workout_adherence', 'Not recorded')}%")
            st.write(f"Diet Adherence: {latest_journal.get('diet_adherence', 'Not recorded')}%")
            st.write(f"Energy Level: {latest_journal.get('energy', 'Not recorded')}")
            st.write(f"Mood: {latest_journal.get('mood', 'Not recorded')}")
        else:
            st.write("No journal entries yet")

def display_error_message(error: str):
    """Display error message in Streamlit"""
    st.error(f"An error occurred: {error}")

def display_success_message(message: str):
    """Display success message in Streamlit"""
    st.success(message)

def display_info_message(message: str):
    """Display info message in Streamlit"""
    st.info(message)


def _parse_plan_sections(plan_content: str) -> Dict[str, str]:
    """Split the full plan into sections by level-two headings."""
    sections = {}
    current_section = None
    current_lines = []

    for line in plan_content.splitlines():
        if line.startswith("##"):
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line.strip("# ")
            current_lines = []
        else:
            current_lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def _split_days(section_text: str, day_labels: list) -> Dict[str, str]:
    """Split a section text into day-specific content."""
    days = {}
    current_day = None
    current_lines = []

    for line in section_text.splitlines():
        stripped = line.strip()
        if any(stripped.startswith(label) for label in day_labels):
            if current_day:
                days[current_day] = "\n".join(current_lines).strip()
            current_day = stripped
            current_lines = []
        else:
            current_lines.append(line)

    if current_day:
        days[current_day] = "\n".join(current_lines).strip()

    return days


def display_plan_tabs(plan_content: str) -> None:
    """Display workout and meal plan sections using tabs for each day."""
    sections = _parse_plan_sections(plan_content)

    workout_days = _split_days(
        sections.get("WEEKLY WORKOUT PLAN", ""),
        [f"Day {i}" for i in range(1, 8)]
    )

    meal_days = _split_days(
        sections.get("WEEKLY MEAL PLAN", ""),
        [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
    )

    if workout_days:
        st.markdown("## Weekly Workout Plan")
        tabs = st.tabs(list(workout_days.keys()))
        for tab, day in zip(tabs, workout_days.keys()):
            with tab:
                st.markdown(workout_days[day])

    if meal_days:
        st.markdown("## Weekly Meal Plan")
        tabs = st.tabs(list(meal_days.keys()))
        for tab, day in zip(tabs, meal_days.keys()):
            with tab:
                st.markdown(meal_days[day])

    if "FORM AND TECHNIQUE GUIDE" in sections:
        st.markdown("## Form and Technique Guide")
        st.markdown(sections["FORM AND TECHNIQUE GUIDE"])

    if "PROGRESS TRACKING" in sections:
        st.markdown("## Progress Tracking")
        st.markdown(sections["PROGRESS TRACKING"])
