import streamlit as st
from services.user_service import UserService
from utils.display import display_success_message, display_error_message
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def display_profile_page(username: str, user_service: UserService):
    """Display and manage user profile information"""
    st.subheader("👤 User Profile")
    
    try:
        # Load existing profile if available
        profile = user_service.get_user_profile(username)
        
        # Initialize form data with defaults
        form_data = {
            'name': username,
            'goal': '',
            'gender': 'Male',
            'age': 30,
            'initial_weight': 70.0,
            'height': 175.0,
            'activity_level': 'Moderately Active',
            'training_style': 'Functional Training',
            'diet_type': 'Standard',
            'allergies': '',
            'fav_foods': ''
        }
        
        # Update with profile data if it exists
        if profile:
            form_data.update({
                'goal': profile.get('goal', form_data['goal']),
                'gender': profile.get('gender', form_data['gender']),
                'age': profile.get('age', form_data['age']),
                'initial_weight': profile.get('initial_weight', form_data['initial_weight']),
                'height': profile.get('height', form_data['height']),
                'activity_level': profile.get('activity_level', form_data['activity_level']),
                'training_style': profile.get('training_style', form_data['training_style']),
                'diet_type': profile.get('diet_type', form_data['diet_type']),
                'allergies': profile.get('allergies', form_data['allergies']),
                'fav_foods': profile.get('fav_foods', form_data['fav_foods'])
            })
        
        # Define options for selectboxes
        goal_options = ["Weight Loss", "Muscle Gain", "Strength Improvement", "General Fitness", "Athletic Performance"]
        gender_options = ["Male", "Female", "Other"]
        activity_options = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"]
        training_options = ["Bodybuilding", "Powerlifting", "HIIT", "Functional Training", "Calisthenics", "Crossfit"]
        diet_options = ["Standard", "Vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean"]
        
        # Create form
        with st.form("profile_form"):
            # Personal information
            st.markdown("### Personal Information")
            col1, col2 = st.columns(2)
            
            with col1:
                # Get index with safety check
                gender_index = gender_options.index(form_data['gender']) if form_data['gender'] in gender_options else 0
                form_data['gender'] = st.selectbox("Gender", 
                    gender_options, 
                    index=gender_index)
                
                form_data['age'] = st.number_input("Age", 
                    min_value=16, max_value=90, value=form_data['age'])
                
                form_data['initial_weight'] = st.number_input("Weight (kg)", 
                    min_value=40.0, max_value=200.0, step=0.1, value=form_data['initial_weight'])
                
                form_data['height'] = st.number_input("Height (cm)", 
                    min_value=140.0, max_value=220.0, step=0.1, value=form_data['height'])
            
            with col2:
                # Get index with safety check
                goal_index = goal_options.index(form_data['goal']) if form_data['goal'] in goal_options else 0
                form_data['goal'] = st.selectbox("Primary Goal", goal_options, index=goal_index)
                
                # Get index with safety check
                activity_index = activity_options.index(form_data['activity_level']) if form_data['activity_level'] in activity_options else 2
                form_data['activity_level'] = st.selectbox("Activity Level", activity_options, index=activity_index)
                
                # Get index with safety check
                training_index = training_options.index(form_data['training_style']) if form_data['training_style'] in training_options else 3
                form_data['training_style'] = st.selectbox("Training Style", training_options, index=training_index)
                
                # Get index with safety check
                diet_index = diet_options.index(form_data['diet_type']) if form_data['diet_type'] in diet_options else 0
                form_data['diet_type'] = st.selectbox("Diet Type", diet_options, index=diet_index)
            
            # Nutrition preferences
            st.markdown("### Nutrition Preferences")
            form_data['allergies'] = st.text_area("Food Allergies/Restrictions", value=form_data['allergies'], 
                help="List any food allergies, intolerances, or restrictions.")
            
            form_data['fav_foods'] = st.text_area("Favorite Foods", value=form_data['fav_foods'], 
                help="List foods you enjoy eating to include in your meal plan.")
            
            # Submit button
            submitted = st.form_submit_button("Save Profile")
            
            if submitted:
                try:
                    # Create profile data dictionary to save
                    profile_data = {
                        'name': username,
                        'goal': form_data['goal'],
                        'gender': form_data['gender'],
                        'age': form_data['age'],
                        'initial_weight': form_data['initial_weight'],
                        'height': form_data['height'],
                        'activity_level': form_data['activity_level'],
                        'training_style': form_data['training_style'],
                        'diet_type': form_data['diet_type'],
                        'allergies': form_data['allergies'],
                        'fav_foods': form_data['fav_foods']
                    }
                    
                    # Save profile
                    user_service.save_profile(profile_data)
                    display_success_message("Profile saved successfully!")
                    
                    # Go to home page to generate plan
                    st.session_state.nav = "home"
                    st.rerun()
                    
                except Exception as e:
                    logger.error(f"Error saving profile: {str(e)}")
                    display_error_message(f"Error saving profile: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error displaying profile page: {str(e)}")
        st.error(f"Error displaying profile: {str(e)}")
        st.warning("Please try again or restart the application.")
        
        # Display a simple recovery form
        if st.button("Create Basic Profile"):
            try:
                basic_profile = {
                    'name': username,
                    'goal': 'General Fitness',
                    'gender': 'Male',
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
                display_success_message("Basic profile created! Please refresh the page.")
                st.rerun()
            except Exception as e2:
                logger.error(f"Failed to create basic profile: {str(e2)}")
                st.error("Failed to create basic profile. Database may be corrupted.")
