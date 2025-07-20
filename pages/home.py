import streamlit as st
from typing import Optional
from services.plan_service import PlanService
from services.ai_service_alt import AIService
from services.user_service import UserService
from utils.display import (
    display_success_message,
    display_info_message,
    display_error_message,
    display_plan,
)
import logging

logger = logging.getLogger(__name__)

def display_home_page(name: str, plan_service: PlanService, ai_service: AIService):
    """Display the home page with user's current plan and options"""
    st.subheader("🏠 Home")
    
    # Get user status and profile
    user_service = UserService()
    status = user_service.get_user_status(name)
    profile = user_service.get_user_profile(name)
    
    # Check if profile is complete
    if not profile or not profile.get('goal') or not profile.get('gender'):
        st.warning("Please complete your profile before generating a fitness plan.")
        if st.button("Go to Profile"):
            st.session_state.nav = "profile"
            st.rerun()
        return
    
    if not status or not status['first_plan_generated']:
        st.info("🎯 Let's create your first fitness plan!")
        if st.button("Generate My First Plan") or st.session_state.get('generate_plan', False):
            with st.spinner("Creating your personalized plan..."):
                try:
                    user_data = user_service.create_user_data_dict(profile)
                    output = ai_service.generate_first_plan(user_data)
                    if output:
                        plan_service.save_plan(name, output)
                        user_service.update_user_status(name, first_plan_generated=True, current_week=1)
                        display_success_message("✅ Your first plan is ready!")
                        display_plan(output)
                        
                        # Clear the generate_plan flag to prevent auto-regeneration
                        if 'generate_plan' in st.session_state:
                            st.session_state.generate_plan = False
                    else:
                        st.error("Failed to generate a valid fitness plan. This could be due to issues with dietary restrictions or exercise requirements.")
                        st.warning("Please try again or modify your dietary restrictions in your profile.")
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error generating plan: {error_msg}")
                    st.error(f"Error generating plan: {error_msg}")
                    if "quota" in error_msg.lower():
                        st.warning("API quota exceeded. Please try again later.")
                    elif "api" in error_msg.lower():
                        st.warning("API connection issue. Please check your internet connection.")
                    else:
                        st.warning("Please try again. If the problem persists, contact support.")
    else:
        # Show current plan and option to generate next week
        current_week = status['current_week']
        last_plan = plan_service.get_latest_plan(name)
        
        if last_plan:
            try:
                st.subheader(f"Week {current_week} Plan")
                
                # Safely access plan content
                plan_content = getattr(last_plan, 'plan', None)
                if plan_content:
                    display_plan(plan_content)
                else:
                    st.error("The plan content appears to be empty.")
                
                # Check if journal entry exists for current week
                if plan_service.has_journal_for_week(name, current_week):
                    if st.button("Generate Next Week's Plan"):
                        with st.spinner("Updating your plan based on your progress..."):
                            try:
                                user_data = user_service.create_user_data_dict(profile)
                                previous_plans = plan_service.get_previous_plans(name)
                                # Get journal summary to include in the plan generation
                                journal_summary = plan_service.get_journal_summary(name, weeks=1)
                                output = ai_service.generate_fitness_plan(
                                    user_data, 
                                    previous_plans,
                                    journal_summary=journal_summary
                                )
                                if output:
                                    plan_service.save_plan(name, output)
                                    user_service.update_user_status(name, current_week=current_week + 1)
                                    display_success_message("✅ Your new plan is ready!")
                                    display_plan(output)
                                else:
                                    st.error("Failed to generate a valid fitness plan. This could be due to issues with dietary restrictions or exercise requirements.")
                                    st.warning("Please try again or modify your dietary restrictions in your profile.")
                            except Exception as e:
                                error_msg = str(e)
                                logger.error(f"Error generating updated plan: {error_msg}")
                                display_error_message(f"Error generating plan: {error_msg}")
                                if "quota" in error_msg.lower():
                                    st.warning("API quota exceeded. Please try again later.")
                else:
                    display_info_message("📝 Please complete your journal entry for this week before generating a new plan")
                    if st.button("Go to Journal"):
                        st.session_state.nav = "journal"
                        st.rerun()
            except Exception as e:
                logger.error(f"Error displaying plan: {str(e)}")
                st.error(f"Error displaying your fitness plan. Please try refreshing the page.")
        else:
            st.error("No plan found. Please generate a new plan.")
            if st.button("Generate New Plan"):
                with st.spinner("Creating your personalized plan..."):
                    try:
                        user_data = user_service.create_user_data_dict(profile)
                        output = ai_service.generate_first_plan(user_data)
                        if output:
                            plan_service.save_plan(name, output)
                            user_service.update_user_status(name, first_plan_generated=True, current_week=1)
                            display_success_message("✅ Your new plan is ready!")
                            display_plan(output)
                        else:
                            st.error("Failed to generate a valid fitness plan. This could be due to issues with dietary restrictions or exercise requirements.")
                            st.warning("Please try again or modify your dietary restrictions in your profile.")
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Error generating new plan: {error_msg}")
                        display_error_message(f"Error generating plan: {error_msg}")
                        if "quota" in error_msg.lower():
                            st.warning("API quota exceeded. Please try again later.")
