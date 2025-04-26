# Personal Trainer AI Assistant (Updated for openai>=1.0.0)
# Streamlit App using ChatGPT API to Generate Custom Meal & Workout Plans

import streamlit as st
from datetime import datetime
import logging
from database.connection import db_manager
# Import the AIService directly from renamed module
from services.ai_service_alt import AIService
from services.user_service import UserService
from services.plan_service import PlanService
from utils.display import show_workflow_guidance, display_user_summary
from pages.home import display_home_page
from pages.profile import display_profile_page
from pages.journal import display_journal_page
from pages.progress import display_progress_page

# Configure page and logging
st.set_page_config(page_title="AI Fitness Plan Generator", page_icon="💪", layout="wide")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
ai_service = AIService()
user_service = UserService()
plan_service = PlanService()

def main():
    try:
        # Initialize database on first run
        if 'db_initialized' not in st.session_state:
            db_manager.init_db()
            st.session_state.db_initialized = True

        st.title("🏋️ AI Personal Trainer")
        
        # Initialize session state variables
        if 'nav' not in st.session_state:
            st.session_state.nav = 'home'
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'shown_popups' not in st.session_state:
            st.session_state.shown_popups = set()

        # Show workflow guidance
        show_workflow_guidance()
        
        # Sidebar user management
        with st.sidebar:
            st.header("👤 User Management")
            users = user_service.get_all_users()
            user_options = ["Create New User"] + users if users else ["Create New User"]
            selected_user = st.selectbox("Select or create user:", user_options)
            
            if selected_user == "Create New User":
                new_name = st.text_input("Enter new username:")
                if new_name and new_name not in users:
                    st.session_state.current_user = new_name
                    st.session_state.nav = 'profile'
            else:
                st.session_state.current_user = selected_user
            
            if st.session_state.current_user:
                display_user_summary(st.session_state.current_user)

        # Navigation buttons in sidebar
        if st.session_state.current_user:
            with st.sidebar:
                st.markdown("---")
                st.header("📍 Navigation")
                cols = st.columns(2)
                
                # Use buttons for navigation
                if cols[0].button("🏠 Home"):
                    st.session_state.nav = 'home'
                if cols[1].button("👤 Profile"):
                    st.session_state.nav = 'profile'
                if cols[0].button("📓 Journal"):
                    st.session_state.nav = 'journal'
                if cols[1].button("📊 Progress"):
                    st.session_state.nav = 'progress'

        # Main content area
        if not st.session_state.current_user:
            st.info("👋 Welcome! Please select a user or create a new profile to get started.")
        else:
            # Display the appropriate page based on navigation state
            if st.session_state.nav == 'home':
                display_home_page(st.session_state.current_user, plan_service, ai_service)
            elif st.session_state.nav == 'profile':
                display_profile_page(st.session_state.current_user, user_service)
            elif st.session_state.nav == 'journal':
                display_journal_page(st.session_state.current_user, plan_service)
            elif st.session_state.nav == 'progress':
                display_progress_page(st.session_state.current_user)

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    main()
