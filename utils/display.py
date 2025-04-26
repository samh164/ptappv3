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
        return
    
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Profile Information")
        st.write(f"Goal: {profile['goal']}")
        st.write(f"Gender: {profile['gender']}")
        st.write(f"Age: {profile['age']}")
        st.write(f"Initial Weight: {profile['initial_weight']} kg")
        st.write(f"Height: {profile['height']} cm")
        st.write(f"Activity Level: {profile['activity_level']}")
        st.write(f"Training Style: {profile['training_style']}")
        st.write(f"Diet Type: {profile['diet_type']}")
        
        # Add allergies and favorite foods if they exist
        if profile['allergies']:
            st.write(f"Allergies/Restrictions: {profile['allergies']}")
        if profile['fav_foods']:
            st.write(f"Favorite Foods: {profile['fav_foods']}")
    
    with col2:
        # Get latest stats from journal
        latest_journal = user_service.get_latest_journal_entry(name)
        
        st.markdown("### Latest Statistics")
        if latest_journal:
            st.write(f"Current Weight: {latest_journal['weight']} kg")
            st.write(f"Workout Adherence: {latest_journal['workout_adherence']}%")
            st.write(f"Diet Adherence: {latest_journal['diet_adherence']}%")
            st.write(f"Energy Level: {latest_journal['energy']}")
            st.write(f"Mood: {latest_journal['mood']}")
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
