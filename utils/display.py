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


def parse_plan(plan_text: str) -> Dict[str, Any]:
    """Parse the raw plan text into workout and meal day sections."""
    import re

    workouts, meals = {}, {}

    # Extract workout section
    if "## WEEKLY WORKOUT PLAN" in plan_text:
        workout_section = plan_text.split("## WEEKLY WORKOUT PLAN", 1)[1]
        if "## WEEKLY MEAL PLAN" in workout_section:
            workout_section = workout_section.split("## WEEKLY MEAL PLAN", 1)[0]
        day_blocks = re.findall(r"(Day\s+\d+[^\n]*\n(?:.*?))(?:\n(?=Day\s+\d+)|$)", workout_section, re.DOTALL)
        for block in day_blocks:
            lines = [ln for ln in block.strip().splitlines() if ln.strip()]
            if not lines:
                continue
            header = lines[0].strip()
            content = "\n".join(lines[1:]).strip()
            workouts[header] = content

    # Extract meal section
    if "## WEEKLY MEAL PLAN" in plan_text:
        meal_section = plan_text.split("## WEEKLY MEAL PLAN", 1)[1]
        if "## FORM AND TECHNIQUE GUIDE" in meal_section:
            meal_section = meal_section.split("## FORM AND TECHNIQUE GUIDE", 1)[0]
        meal_blocks = re.findall(
            r"((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday):\n(?:.*?))(?:\n(?=(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday):)|$)",
            meal_section,
            re.DOTALL,
        )
        for block in meal_blocks:
            lines = [ln for ln in block.strip().splitlines() if ln.strip()]
            if not lines:
                continue
            header = lines[0].rstrip(":")
            content = "\n".join(lines[1:]).strip()
            meals[header] = content

    # Remaining sections
    form_guide = ""
    progress = ""
    if "## FORM AND TECHNIQUE GUIDE" in plan_text:
        form_section = plan_text.split("## FORM AND TECHNIQUE GUIDE", 1)[1]
        if "## PROGRESS TRACKING" in form_section:
            form_guide = form_section.split("## PROGRESS TRACKING", 1)[0].strip()
        else:
            form_guide = form_section.strip()
    if "## PROGRESS TRACKING" in plan_text:
        progress = plan_text.split("## PROGRESS TRACKING", 1)[1].strip()

    return {
        "workouts": workouts,
        "meals": meals,
        "form_guide": form_guide,
        "progress_tracking": progress,
    }


def display_plan(plan_text: str) -> None:
    """Render a plan in a tabbed layout for easier reading."""
    sections = parse_plan(plan_text)

    if sections["workouts"]:
        st.markdown("### Weekly Workout Plan")
        workout_tabs = st.tabs(list(sections["workouts"].keys()))
        for tab, title in zip(workout_tabs, sections["workouts"].keys()):
            with tab:
                st.markdown(f"#### {title}")
                st.markdown(sections["workouts"][title])

    if sections["meals"]:
        st.markdown("### Weekly Meal Plan")
        meal_tabs = st.tabs(list(sections["meals"].keys()))
        for tab, title in zip(meal_tabs, sections["meals"].keys()):
            with tab:
                st.markdown(f"#### {title}")
                st.markdown(sections["meals"][title])

    if sections["form_guide"]:
        st.markdown("### Form and Technique Guide")
        st.markdown(sections["form_guide"])

    if sections["progress_tracking"]:
        st.markdown("### Progress Tracking")
        st.markdown(sections["progress_tracking"])

