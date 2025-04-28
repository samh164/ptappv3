import streamlit as st
from datetime import datetime
import logging
import sys
import traceback
from database.connection import db_manager
from services.ai_service_alt import AIService
from services.user_service import UserService
from services.plan_service import PlanService
from utils.display import show_workflow_guidance, display_user_summary
from pages.home import display_home_page
from pages.profile import display_profile_page
from pages.journal import display_journal_page
from pages.progress import display_progress_page
from pages.history import display_history_page

# Configure page and logging
st.set_page_config(
    page_title="AI Fitness Plan Generator", 
    page_icon="💪", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Hide the default Streamlit menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stButton button {
    background-color: #2e2e38;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 15px;
    font-weight: bold;
    transition: background-color 0.3s;
}
.stButton button:hover {
    background-color: #4a4a63;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize services
try:
    ai_service = AIService()
    user_service = UserService()
    plan_service = PlanService()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    st.error(f"Error initializing services: {str(e)}")

# Initialize session state
if 'nav' not in st.session_state:
    st.session_state.nav = 'home'
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'shown_popups' not in st.session_state:
    st.session_state.shown_popups = set()

# Initialize database
try:
    if 'db_initialized' not in st.session_state:
        db_manager.init_db()
        st.session_state.db_initialized = True
        logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization error: {str(e)}")
    st.error(f"Database initialization error: {str(e)}")

def handle_user_selection():
    """Handle user selection and creation with proper form fields"""
    try:
        # Get all existing users
        users = user_service.get_all_users()
        user_names = [user for user in users]
        
        col1, col2 = st.columns([3, 1])
        
        # User creation form
        with col1:
            with st.form(key="new_user_form", clear_on_submit=True):
                new_name = st.text_input(
                    "Enter your name:",
                    key="new_user_input",
                    help="Enter your name to create a new profile",
                    max_chars=50,
                    placeholder="Your name"
                )
                submit_button = st.form_submit_button(
                    "Create User",
                    help="Click to create a new user profile"
                )
                
                if submit_button and new_name:
                    if new_name not in user_names:
                        success = user_service.create_user(new_name)
                        if success:
                            st.session_state.current_user = new_name
                            st.session_state.nav = 'profile'  # Always go to profile for new users
                            st.success(f"Created new user: {new_name}")
                            st.rerun()
                        else:
                            st.error("Failed to create user. Please try again.")
                    else:
                        st.error("This username already exists")
        
        # User selection dropdown
        with col2:
            if user_names:
                # Get current index safely
                selected_index = 0
                if st.session_state.current_user in user_names:
                    selected_index = user_names.index(st.session_state.current_user)
                
                selected_user = st.selectbox(
                    "Select existing user:",
                    options=user_names,
                    index=selected_index,
                    key="user_select"
                )
                
                # If user changed, update session and rerun
                if selected_user != st.session_state.current_user:
                    st.session_state.current_user = selected_user
                    st.session_state.nav = 'profile'  # Start with profile page
                    st.rerun()
            else:
                st.info("No existing users")
    except Exception as e:
        logger.error(f"Error in user selection: {str(e)}")
        st.error(f"Error loading users: {str(e)}")

def main():
    """Main application function"""
    try:
        # Sidebar user management and debugging
        with st.sidebar:
            st.title("🏋️ AI Personal Trainer")
            st.header("👤 User Management")
            
            # Debug info - helpful for troubleshooting
            with st.expander("Debug Info", expanded=False):
                st.write(f"Current user: {st.session_state.current_user}")
                st.write(f"Current page: {st.session_state.nav}")
                st.write(f"Python version: {sys.version}")
                
            # Handle user selection
            handle_user_selection()
            
            # Display user summary if available
            if st.session_state.current_user:
                try:
                    display_user_summary(st.session_state.current_user)
                except Exception as e:
                    logger.error(f"Error displaying user summary: {str(e)}")
                    st.error("Error loading user profile. Please update your profile.")
                
        # Main content area
        if not st.session_state.current_user:
            st.info("👋 Welcome! Please select a user or create a new profile to get started.")
            show_workflow_guidance()
        else:
            # Ensure we have a valid navigation key
            if st.session_state.nav not in ['home', 'profile', 'journal', 'progress', 'history']:
                st.session_state.nav = 'profile'
                
            # Navigation buttons
            st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
            cols = st.columns(5)
            
            nav_items = {
                'home': ('🏠 Home', display_home_page),
                'profile': ('👤 Profile', display_profile_page),
                'journal': ('📓 Journal', display_journal_page),
                'progress': ('📊 Progress', display_progress_page),
                'history': ('📚 History', display_history_page)
            }
            
            for i, (nav_key, (label, func)) in enumerate(nav_items.items()):
                if cols[i].button(label, key=f"nav_{nav_key}", use_container_width=True):
                    st.session_state.nav = nav_key
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display current page with error handling
            try:
                current_page = nav_items[st.session_state.nav][1]
                
                # Check for empty profile and redirect if needed
                if current_page != display_profile_page:
                    try:
                        profile = user_service.get_user_profile(st.session_state.current_user)
                        if not profile or not profile.get('goal') or not profile.get('gender'):
                            st.warning("Please complete your profile before accessing other pages.")
                            current_page = display_profile_page
                    except Exception as e:
                        logger.error(f"Error checking profile: {str(e)}")
                        st.error(f"Error checking profile: {str(e)}")
                        current_page = display_profile_page
                
                # Display the appropriate page
                if current_page == display_home_page:
                    current_page(st.session_state.current_user, plan_service, ai_service)
                elif current_page == display_profile_page:
                    current_page(st.session_state.current_user, user_service)
                elif current_page == display_journal_page:
                    current_page(st.session_state.current_user, plan_service)
                elif current_page == display_progress_page:
                    current_page(st.session_state.current_user)
                elif current_page == display_history_page:
                    current_page(st.session_state.current_user, plan_service)
                
            except Exception as e:
                logger.error(f"Error displaying page {st.session_state.nav}: {str(e)}")
                st.error(f"Error displaying page: {str(e)}")
                st.code(traceback.format_exc())
                
                # Show a simplified view if there's an error
                st.warning("Showing simplified profile view due to errors.")
                
                # Show a minimal profile
                st.header(f"👤 {st.session_state.current_user}'s Profile")
                
                with st.form("emergency_profile_form"):
                    st.markdown("### Update Basic Profile")
                    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "General Fitness"])
                    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                    
                    if st.form_submit_button("Save Basic Profile"):
                        try:
                            # Create basic profile
                            basic_profile = {
                                'name': st.session_state.current_user,
                                'goal': goal,
                                'gender': gender,
                                'age': 30,
                                'initial_weight': 70.0,
                                'height': 175.0,
                                'activity_level': 'Moderately Active',
                                'training_style': 'Functional Training',
                                'diet_type': 'Standard',
                                'allergies': '',
                                'fav_foods': ''
                            }
                            user_service.save_profile(basic_profile)
                            st.success("Basic profile saved!")
                            st.rerun()
                        except Exception as inner_e:
                            st.error(f"Could not save basic profile: {str(inner_e)}")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An unexpected error occurred: {str(e)}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main() 