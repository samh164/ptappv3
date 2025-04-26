import streamlit as st
from services.user_service import UserService
from utils.display import display_success_message, display_error_message
from typing import Dict, Any, Optional

def display_profile_page(username: str, user_service: UserService):
    """Display and manage user profile information"""
    st.subheader("👤 User Profile")
    
    # Load existing profile if available
    profile = user_service.get_user_profile(username)
    
    # Initialize form data
    form_data = {}
    if profile:
        # Profile is now a dictionary, so we can use it directly
        form_data = {
            'name': profile['name'],
            'goal': profile['goal'],
            'gender': profile['gender'],
            'age': profile['age'],
            'initial_weight': profile['initial_weight'],
            'height': profile['height'],
            'activity_level': profile['activity_level'],
            'training_style': profile['training_style'],
            'diet_type': profile['diet_type'],
            'allergies': profile['allergies'],
            'fav_foods': profile['fav_foods']
        }
    else:
        form_data = {
            'name': username,
            'goal': '',
            'gender': '',
            'age': 30,
            'initial_weight': 70.0,
            'height': 175.0,
            'activity_level': '',
            'training_style': '',
            'diet_type': '',
            'allergies': '',
            'fav_foods': ''
        }
    
    # Create form
    with st.form("profile_form"):
        # Personal information
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            form_data['gender'] = st.selectbox("Gender", 
                ["Male", "Female", "Other"], 
                index=0 if not form_data['gender'] else ["Male", "Female", "Other"].index(form_data['gender']))
            
            form_data['age'] = st.number_input("Age", 
                min_value=16, max_value=90, value=form_data['age'])
            
            form_data['initial_weight'] = st.number_input("Weight (kg)", 
                min_value=40.0, max_value=200.0, step=0.1, value=form_data['initial_weight'])
            
            form_data['height'] = st.number_input("Height (cm)", 
                min_value=140.0, max_value=220.0, step=0.1, value=form_data['height'])
        
        with col2:
            form_data['goal'] = st.selectbox("Primary Goal", 
                ["Weight Loss", "Muscle Gain", "Strength Improvement", "General Fitness", "Athletic Performance"],
                index=0 if not form_data['goal'] else ["Weight Loss", "Muscle Gain", "Strength Improvement", "General Fitness", "Athletic Performance"].index(form_data['goal']))
            
            form_data['activity_level'] = st.selectbox("Activity Level", 
                ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                index=0 if not form_data['activity_level'] else ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"].index(form_data['activity_level']))
            
            form_data['training_style'] = st.selectbox("Training Style", 
                ["Bodybuilding", "Powerlifting", "HIIT", "Functional Training", "Calisthenics", "Crossfit"],
                index=0 if not form_data['training_style'] else ["Bodybuilding", "Powerlifting", "HIIT", "Functional Training", "Calisthenics", "Crossfit"].index(form_data['training_style']))
            
            form_data['diet_type'] = st.selectbox("Diet Type", 
                ["Standard", "Vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean"],
                index=0 if not form_data['diet_type'] else ["Standard", "Vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean"].index(form_data['diet_type']))
        
        # Nutrition preferences
        st.markdown("### Nutrition Preferences")
        form_data['allergies'] = st.text_area("Food Allergies/Restrictions", value=form_data['allergies'], 
            help="List any food allergies, intolerances, or restrictions.")
        
        form_data['fav_foods'] = st.text_area("Favorite Foods", value=form_data['fav_foods'], 
            help="List foods you enjoy eating to include in your meal plan.")
        
        # Calculate daily calorie needs
        st.markdown("### Calorie Needs")
        calorie_text = st.text_input("Daily Calorie Target (calories)", 
            help="Leave empty to automatically calculate based on your profile, or enter a specific value.")
        
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
                st.session_state.generate_plan = True
                st.rerun()
                
            except Exception as e:
                display_error_message(f"Error saving profile: {str(e)}")
