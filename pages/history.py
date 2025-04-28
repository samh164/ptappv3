import streamlit as st
from services.plan_service import PlanService
import logging

logger = logging.getLogger(__name__)

def display_history_page(username: str, plan_service: PlanService):
    """Display all previous fitness plans for the user"""
    st.subheader("📚 Plan History")
    
    # Get all plans for this user
    all_plans = plan_service.get_all_user_plans(username)
    
    if not all_plans:
        st.info("You haven't generated any fitness plans yet. Go to the Home page to create your first plan!")
        return
    
    # Get current week number
    current_week = max([plan.week_number for plan in all_plans])
    
    # Initialize session state for history_week if not present
    if 'history_week' not in st.session_state:
        st.session_state.history_week = current_week
    
    # Add a dropdown in the main area for week selection
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("#### Select Week:")
    
    with col2:
        selected_week = st.selectbox(
            "",
            options=list(range(1, current_week + 1)),
            index=st.session_state.history_week - 1,
            key="week_selector",
            label_visibility="collapsed"
        )
        
        # Update session state if dropdown changed
        if selected_week != st.session_state.history_week:
            st.session_state.history_week = selected_week
            st.rerun()
    
    # Find the selected plan
    selected_plan = next((plan for plan in all_plans if plan.week_number == st.session_state.history_week), None)
    
    if selected_plan:
        # Display plan header with week number and creation date
        st.markdown(f"""
        <div style='background-color: transparent; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
            <h2 style='margin: 0; color: white;'>Week {selected_plan.week_number} Plan</h2>
            <p style='margin: 0; color: #B0B0B0;'>Created on {selected_plan.created_date.strftime('%Y-%m-%d')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display user stats at the time of plan creation
        with st.expander("User Stats at Time of Plan Creation", expanded=False):
            cols = st.columns(4)
            cols[0].metric("Weight", f"{selected_plan.weight} kg")
            cols[1].metric("Goal", selected_plan.goal)
            cols[2].metric("Activity Level", selected_plan.activity_level)
            cols[3].metric("Training Style", selected_plan.training_style)
            
            st.markdown("---")
            
            cols = st.columns(2)
            cols[0].metric("Diet Type", selected_plan.diet_type)
            if hasattr(selected_plan, 'allergies') and selected_plan.allergies:
                cols[1].metric("Allergies/Restrictions", selected_plan.allergies)
        
        # Display the plan content
        st.markdown(selected_plan.plan)
        
        # Add navigation buttons for easier week switching
        st.markdown("---")
        cols = st.columns(3)
        
        # Previous week button
        if st.session_state.history_week > 1:
            if cols[0].button("← Previous Week", use_container_width=True):
                st.session_state.history_week -= 1
                st.rerun()
                
        # Current week button (latest)
        if st.session_state.history_week != current_week:
            if cols[1].button("Latest Plan", use_container_width=True):
                st.session_state.history_week = current_week
                st.rerun()
                
        # Next week button
        if st.session_state.history_week < current_week:
            if cols[2].button("Next Week →", use_container_width=True):
                st.session_state.history_week += 1
                st.rerun()
    else:
        st.error("Could not find the selected plan. Please try again.") 