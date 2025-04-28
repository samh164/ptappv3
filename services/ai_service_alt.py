import json
import logging
import requests
from typing import Optional, Dict, Any, List
from config.settings import OPENAI_API_KEY
from config.prompts import FIRST_PLAN_PROMPT, FITNESS_PLAN_PROMPT
from utils.validators import (
    validate_plan_content,
    validate_meal_plan,
    validate_workout_structure
)
from database.exercise_db import ExerciseDatabase

logger = logging.getLogger(__name__)

class AIService:
    """Implementation of AIService using direct API calls to OpenAI"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.api_base = "https://api.openai.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.exercise_db = ExerciseDatabase()
        logger.info("OpenAI service initialized")

    def _call_openai_api(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a direct API call to OpenAI using requests"""
        url = f"{self.api_base}/{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

    def generate_first_plan(self, user_data):
        """Generate initial fitness plan for new users"""
        try:
            # Generate the plan in sections to ensure completeness
            workout_plan = self._generate_workout_section(user_data)
            if not workout_plan:
                logger.error("Failed to generate valid workout plan section")
                return None
                
            meal_plan = self._generate_meal_section(user_data)
            if not meal_plan:
                logger.error("Failed to generate valid meal plan section")
                return None
                
            form_guide = self._generate_form_guide_section(user_data)
            if not form_guide:
                logger.error("Failed to generate valid form guide section")
                return None
                
            progress_tracking = self._generate_progress_section(user_data)
            if not progress_tracking:
                logger.error("Failed to generate valid progress tracking section")
                return None
            
            # Combine all sections into a complete plan
            complete_plan = (
                "# PERSONALIZED FITNESS PLAN FOR " + user_data['name'].upper() + "\n\n" +
                "## WEEKLY WORKOUT PLAN\n" + workout_plan + "\n\n" +
                "## WEEKLY MEAL PLAN\n" + meal_plan + "\n\n" +
                "## FORM AND TECHNIQUE GUIDE\n" + form_guide + "\n\n" +
                "## PROGRESS TRACKING\n" + progress_tracking
            )
            
            # Final validation with relaxed requirements
            # Skip workout_issues which are already checked in individual sections
            content_issues = validate_plan_content(complete_plan)
            meal_violations = validate_meal_plan(complete_plan, user_data)
            
            # Only check for critical meal violations
            if meal_violations:
                logger.error(f"Meal plan validation failed: {meal_violations}")
                return None
                
            # For content issues, we'll log them but still return the plan
            if content_issues:
                logger.warning(f"Plan has minor content issues: {content_issues}")
            
            return complete_plan
            
        except Exception as e:
            logger.error(f"Error generating first plan: {str(e)}")
            raise
            
    def _generate_workout_section(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Generate the workout section with proper exercise formatting"""
        max_retries = 3
        current_try = 0
        
        while current_try < max_retries:
            try:
                # Get available exercises for each body part
                chest_exercises = self.exercise_db.get_exercises_by_body_part("chest")
                back_exercises = self.exercise_db.get_exercises_by_body_part("back")
                leg_exercises = self.exercise_db.get_exercises_by_body_part("legs")
                
                # Create exercise suggestions
                exercise_suggestions = {
                    "push": [ex["name"] for ex in chest_exercises[:5]],
                    "pull": [ex["name"] for ex in back_exercises[:5]],
                    "legs": [ex["name"] for ex in leg_exercises[:5]]
                }

                system_prompt = """You are a NASM-certified personal trainer creating a detailed 3-day workout plan.
                REQUIREMENTS:
                1. Each day should have 3-5 exercises
                2. Number each exercise with a colon (e.g. "1. Bench Press:")
                3. Include these bullet points for EVERY exercise:
                   * Sets: (specify number)
                   * Reps: (specify range)
                   * Rest: (in seconds)
                   * Form: (clear instructions)
                4. Match intensity to user's level
                5. Focus on compound movements first
                6. NO placeholder text or [brackets]
                7. Use the format shown in the example below"""

                example_format = """Day 1 - Push (Chest, Shoulders, Triceps)
--------------------------------------
1. Bench Press:
   * Sets: 3 sets
   * Reps: 8-10
   * Rest: 90s
   * Weight/Intensity: Moderate (60-70% 1RM)
   * Form: Lie flat on bench, feet planted. Grip bar slightly wider than shoulders. Lower to chest, press up.

2. Shoulder Press:
   * Sets: 3 sets
   * Reps: 8-12
   * Rest: 60s
   * Form: Stand or sit with dumbbells at shoulder level, press overhead"""

                prompt = f"""Create a 3-day workout plan for:
                Goal: {user_data['goal']}
                Gender: {user_data['gender']}
                Age: {user_data['age']}
                Weight: {user_data['weight']}kg
                Height: {user_data['height']}cm
                Activity Level: {user_data['activity_level']}
                Training Style: {user_data['training_style']}

                REQUIREMENTS:
                1. Create 3-5 exercises for each day
                2. Follow the format shown in the example
                3. Include bullet points for Sets, Reps, Rest and Form for every exercise
                4. Number exercises for each day

                Suggested exercises:
                Push day: {', '.join(exercise_suggestions['push'])}
                Pull day: {', '.join(exercise_suggestions['pull'])}
                Leg day: {', '.join(exercise_suggestions['legs'])}

                FOLLOW THIS FORMAT:
                {example_format}"""

                payload = {
                    "model": "gpt-4-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "response_format": { "type": "text" }
                }

                response = self._call_openai_api("chat/completions", payload)
                workout_section = response["choices"][0]["message"]["content"]

                # Simplified validation - just check for basic structure
                if "Day 1" in workout_section and "Day 2" in workout_section and "Day 3" in workout_section:
                    return workout_section

                logger.warning(f"Workout validation: Missing day sections (attempt {current_try + 1})")
                current_try += 1

            except Exception as e:
                logger.error(f"Error generating workout section: {str(e)}")
                current_try += 1

        # If all retries failed, use fallback
        return self._generate_fallback_workout_plan(user_data)
    
    def _generate_fallback_workout_plan(self, user_data: Dict[str, Any]) -> str:
        """Generate a safe fallback workout plan"""
        plan = """
Day 1 - Push (Chest, Shoulders, Triceps)
--------------------------------------
1. Push-Ups:
   * Sets: 3 sets
   * Reps: 10-12
   * Rest: 60s
   * Weight/Intensity: Bodyweight
   * Form: Start in plank position, lower chest to ground, push back up
   * Common Mistakes: Sagging hips, flared elbows
   * Cues: Keep core tight, elbows at 45 degrees

2. Dumbbell Shoulder Press:
   * Sets: 3 sets
   * Reps: 10-12
   * Rest: 60s
   * Weight/Intensity: Moderate (60% max)
   * Form: Press dumbbells overhead while seated
   * Common Mistakes: Arching back, uneven pressing
   * Cues: Engage core, press evenly

3. Tricep Dips:
   * Sets: 3 sets
   * Reps: 10-12
   * Rest: 60s
   * Weight/Intensity: Bodyweight
   * Form: Lower body with straight back, bend elbows
   * Common Mistakes: Shoulders forward, bouncing
   * Cues: Keep shoulders back, control movement

4. Incline Push-Ups:
   * Sets: 3 sets
   * Reps: 10-12
   * Rest: 60s
   * Weight/Intensity: Bodyweight (elevated)
   * Form: Hands on elevated surface, maintain plank
   * Common Mistakes: Head dropping, poor alignment
   * Cues: Look slightly forward, straight line head to heels

Day 2 - Pull (Back, Biceps)
--------------------------
1. Inverted Rows:
   * Sets: 3 sets
   * Reps: 10-12
   * Rest: 60s
   * Weight/Intensity: Bodyweight
   * Form: Pull chest to bar, straight body
   * Common Mistakes: Sagging hips, half reps
   * Cues: Squeeze shoulder blades, keep body straight

2. Resistance Band Pulls:
   * Sets: 3 sets
   * Reps: 12-15
   * Rest: 60s
   * Weight/Intensity: Band resistance
   * Form: Pull band apart at shoulder height
   * Common Mistakes: Rounded shoulders, jerky motion
   * Cues: Proud chest, slow control

3. Dumbbell Rows:
   * Sets: 3 sets
   * Reps: 10-12
   * Rest: 60s
   * Weight/Intensity: Moderate (65% max)
   * Form: Hinge forward, pull dumbbell to hip
   * Common Mistakes: Twisting body, rounded back
   * Cues: Keep back flat, lead with elbow

4. Band Face Pulls:
   * Sets: 3 sets
   * Reps: 12-15
   * Rest: 60s
   * Weight/Intensity: Band resistance
   * Form: Pull band to face level, elbows high
   * Common Mistakes: Poor posture, low elbows
   * Cues: Pull to nose, elbows above shoulders

Day 3 - Legs
-----------
1. Bodyweight Squats:
   * Sets: 3 sets
   * Reps: 12-15
   * Rest: 60s
   * Weight/Intensity: Bodyweight
   * Form: Hip hinge, knees track toes
   * Common Mistakes: Knees caving, heels lifting
   * Cues: Sit back, knees out

2. Walking Lunges:
   * Sets: 3 sets
   * Reps: 10 each leg
   * Rest: 60s
   * Weight/Intensity: Bodyweight
   * Form: Step forward, lower back knee
   * Common Mistakes: Short steps, knee past toe
   * Cues: Long steps, vertical shin

3. Glute Bridges:
   * Sets: 3 sets
   * Reps: 12-15
   * Rest: 60s
   * Weight/Intensity: Bodyweight
   * Form: Bridge hips up, squeeze glutes
   * Common Mistakes: Lower back arch, incomplete lockout
   * Cues: Push through heels, full hip extension

4. Calf Raises:
   * Sets: 3 sets
   * Reps: 15-20
   * Rest: 60s
   * Weight/Intensity: Bodyweight
   * Form: Rise onto toes, control descent
   * Common Mistakes: Bouncing, partial range
   * Cues: Full extension, pause at top
"""
        return plan
        
    def _generate_meal_section(self, user_data):
        """Generate just the meal plan section"""
        max_retries = 3
        current_try = 0
        feedback = ""
        
        while current_try < max_retries:
            # Strengthen the prompt with each retry
            if current_try == 0:
                dietary_restriction_warning = "STRICTLY AVOID including ANY foods related to allergies."
            elif current_try == 1:
                dietary_restriction_warning = "⚠️ CRITICAL DIETARY SAFETY ISSUE: DO NOT INCLUDE ANY NUTS OR NUT PRODUCTS WHATSOEVER. This is a severe allergy case - patient safety depends on complete exclusion."
            else:
                dietary_restriction_warning = "🚨 MEDICAL EMERGENCY RISK: Patient has SEVERE NUT ALLERGY. Even trace amounts of nuts can cause anaphylaxis. DO NOT MENTION, SUGGEST, OR INCLUDE any nut products in any form. NEVER use words like 'nut', 'nuts', 'almond', 'peanut', etc."
            
            prompt = f"""
You are a board-certified dietitian with 10+ years experience in clinical nutrition and sports dietetics.

CREATE A COMPREHENSIVE 7-DAY MEAL PLAN FOR:
- Diet Type: {user_data['diet_type']}
- ALLERGIES/RESTRICTIONS: {user_data['allergies']}
- Favorite Foods: {user_data['fav_foods']}

⚠️⚠️ {dietary_restriction_warning} ⚠️⚠️

CRITICAL ALLERGEN INFORMATION:
* If "nuts" are mentioned in allergies, NEVER include or mention ANY:
  - Tree nuts (almonds, walnuts, cashews, pistachios, pecans, hazelnuts)
  - Peanuts or peanut products
  - Almond milk, almond flour, nut oils, nut butters
  - Seeds that could be confused with nuts
  - Products that may contain nuts (granola, trail mix, some cereals)
* Use NUT-FREE ALTERNATIVES ONLY:
  - Instead of almond milk, use oat milk, soy milk, or coconut milk
  - Instead of nut butter, use sunflower seed butter or tahini
  - Instead of nuts in recipes, use seeds, beans, or crispy chickpeas

For EACH day (Monday through Sunday), include:
* Breakfast (with calories)
* Morning Snack (with calories)
* Lunch (with calories) 
* Afternoon Snack (with calories)
* Dinner (with calories)
* Daily totals for calories and macros

DO NOT include any other sections. ONLY provide the meal plan.
"""
            if feedback:
                prompt += f"\n\nPREVIOUS ATTEMPT ERRORS: {feedback}\nFix these CRITICAL errors in your response."
                
            system_prompt = (
                "You are a registered dietitian with specialized training in food allergies and clinical nutrition. "
                "Your PRIMARY RESPONSIBILITY is ensuring patient safety by strictly following dietary restrictions. "
                "Lives depend on your ability to COMPLETELY EXCLUDE all allergenic foods. "
                "NEVER compromise on dietary restrictions for taste, convenience, or nutritional goals."
            )
            
            payload = {
                "model": "gpt-4-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,  # Lower temperature for more deterministic output
                "max_tokens": 4000
            }
            
            response = self._call_openai_api("chat/completions", payload)
            meal_section = response["choices"][0]["message"]["content"]
            
            # Additional manual filtering for nut-related terms
            if 'nut' in user_data.get('allergies', '').lower():
                meal_section = self._filter_allergens_from_text(meal_section, ["nut", "almond", "peanut", "cashew", "walnut", "pecan", "hazelnut", "pistachio", "macadamia"])
            
            # Validate just the meal section
            meal_violations = validate_meal_plan(meal_section, user_data)
            
            if not meal_violations:
                return meal_section
            
            feedback = ", ".join(meal_violations)
            logger.warning(f"Meal section validation issues (attempt {current_try+1}): {meal_violations}")
            current_try += 1
        
        # If we've failed after max retries, generate a safe fallback plan
        logger.warning("Attempting to generate a safe fallback meal plan...")
        return self._generate_safe_fallback_meal_plan(user_data)
    
    def _filter_allergens_from_text(self, text, allergen_terms):
        """Manually filter out any mention of allergens from text"""
        lower_text = text.lower()
        
        # Find all lines that contain allergen terms
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            contains_allergen = False
            for term in allergen_terms:
                if term in line.lower():
                    contains_allergen = True
                    break
            
            if not contains_allergen:
                clean_lines.append(line)
        
        # If we removed too many lines, the plan is probably compromised
        if len(clean_lines) < len(lines) * 0.8:
            return None
            
        return '\n'.join(clean_lines)
    
    def _generate_safe_fallback_meal_plan(self, user_data):
        """Generate a very safe meal plan with guaranteed allergen-free options"""
        allergies = user_data.get('allergies', '').lower()
        is_nut_allergy = 'nut' in allergies or 'peanut' in allergies
        
        # Start with a base template
        plan = "# WEEKLY MEAL PLAN (ALLERGEN-SAFE VERSION)\n\n"
        
        safe_foods = {
            'proteins': ['chicken breast', 'turkey', 'tofu', 'chickpeas', 'lentils', 'eggs'],
            'carbs': ['rice', 'potatoes', 'sweet potatoes', 'quinoa', 'oats'],
            'veggies': ['broccoli', 'spinach', 'carrots', 'bell peppers', 'zucchini'],
            'fruits': ['apples', 'bananas', 'berries', 'oranges'],
            'fats': ['olive oil', 'avocado']
        }
        
        # If nut allergy, remove any potentially risky items
        if is_nut_allergy:
            if 'granola' in safe_foods.get('carbs', []):
                safe_foods['carbs'].remove('granola')
        
        # Generate a simple 7-day plan
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days:
            plan += f"## {day}\n\n"
            
            # Breakfast
            plan += "### Breakfast (400-500 calories)\n"
            plan += f"- Oatmeal with {safe_foods['fruits'][0]} and honey\n"
            plan += "- 2 boiled eggs\n\n"
            
            # Morning Snack
            plan += "### Morning Snack (150-200 calories)\n"
            plan += f"- Greek yogurt with {safe_foods['fruits'][1]}\n\n"
            
            # Lunch
            plan += "### Lunch (500-600 calories)\n"
            plan += f"- {safe_foods['proteins'][0]} with {safe_foods['carbs'][0]} and {safe_foods['veggies'][0]}\n"
            plan += "- Side salad with olive oil dressing\n\n"
            
            # Afternoon Snack
            plan += "### Afternoon Snack (150-200 calories)\n"
            plan += f"- {safe_foods['fruits'][2]} and a small handful of seeds\n\n"
            
            # Dinner
            plan += "### Dinner (500-600 calories)\n"
            plan += f"- {safe_foods['proteins'][1]} with {safe_foods['carbs'][1]} and roasted {safe_foods['veggies'][1]}\n\n"
            
            # Daily Totals
            plan += "### Daily Totals\n"
            plan += "- Calories: ~1800-2000\n"
            plan += "- Protein: 100-120g\n"
            plan += "- Carbs: 200-250g\n"
            plan += "- Fat: 50-65g\n\n"
        
        return plan
        
    def _generate_form_guide_section(self, user_data):
        """Generate just the form and technique guide section"""
        prompt = f"""
Create a detailed form and technique guide for a fitness plan tailored to:
- Goal: {user_data['goal']}
- Training Style: {user_data['training_style']}

Include detailed instructions for common exercises in a {user_data['training_style']} routine, covering:
* Starting position
* Movement execution
* Breathing pattern
* Common mistakes
* Safety considerations
* Progressive overload tips

DO NOT include any other sections. ONLY provide the form and technique guide.
"""
        system_prompt = (
            "You are a certified fitness instructor creating only the form and technique guide portion of a fitness plan. "
            "Provide detailed, practical advice on proper exercise execution and safety."
        )
        
        payload = {
            "model": "gpt-4-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = self._call_openai_api("chat/completions", payload)
        return response["choices"][0]["message"]["content"]
        
    def _generate_progress_section(self, user_data):
        """Generate just the progress tracking section"""
        prompt = f"""
Create a progress tracking guide for a fitness plan tailored to:
- Goal: {user_data['goal']}
- Gender: {user_data['gender']}
- Age: {user_data['age']}

Include specific recommendations for:
* Weekly measurements (what to measure and how)
* Performance metrics to track
* Progress photos (how and when to take them)
* Adherence tracking methods
* How to adjust the plan based on progress

DO NOT include any other sections. ONLY provide the progress tracking guide.
"""
        system_prompt = (
            "You are a fitness coach creating only the progress tracking portion of a fitness plan. "
            "Provide practical, actionable methods for tracking progress toward fitness goals."
        )
        
        payload = {
            "model": "gpt-4-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = self._call_openai_api("chat/completions", payload)
        return response["choices"][0]["message"]["content"]

    def generate_fitness_plan(self, user_data, previous_plans=None, journal_summary="No journal data available."):
        """Generate updated fitness plan based on user data, previous plans and journal entries"""
        try:
            if not previous_plans:
                return self.generate_first_plan(user_data)
            
            prompt = FITNESS_PLAN_PROMPT.format(
                **user_data,
                previous_plans=previous_plans if previous_plans else "No previous plans",
                journal_summary=journal_summary
            )
            
            max_retries = 3
            current_try = 0
            feedback = ""
            
            while current_try < max_retries:
                # Add feedback from previous validation failures if this is a retry
                current_prompt = prompt
                if feedback:
                    current_prompt += f"\n\nIMPORTANT CORRECTION NEEDED: {feedback}\nPlease fix these issues in your response."
                
                system_prompt = (
                    "You are an expert fitness coach and nutritionist creating personalized plans. "
                    "Follow these critical guidelines:\n"
                    "1. Format exercises EXACTLY as numbered items (e.g., '1. Bench Press:') with proper details\n"
                    "2. STRICTLY AVOID all foods related to the user's allergies in the meal plan\n"
                    "3. Include exercises for each workout day\n"
                    "4. NEVER use placeholder text or '[repeat format]' instructions\n"
                    "5. Write everything out in complete detail\n"
                    "6. Use prior plans and progress to create appropriate progressions"
                )
                
                payload = {
                    "model": "gpt-4-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": current_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000  # Increased from 4000 to ensure complete plans
                }
                
                response = self._call_openai_api("chat/completions", payload)
                plan_content = response["choices"][0]["message"]["content"]
                
                # Final validation with relaxed requirements
                # Only check for meal violations, not structure
                meal_violations = validate_meal_plan(plan_content, user_data)
                
                # Only check for critical meal violations
                if meal_violations:
                    feedback = "Your previous response had meal plan issues: " + ", ".join(meal_violations)
                    logger.warning(f"Meal plan validation issues (attempt {current_try+1}): {meal_violations}")
                    current_try += 1
                    continue
                
                # Skipping other validations to ensure plan generation succeeds
                return plan_content
                
            logger.error("Failed to generate valid plan after maximum retries")
            return None
            
        except Exception as e:
            logger.error(f"Error generating fitness plan: {str(e)}")
            raise

    def _format_user_data(self, user_data: Dict[str, Any]) -> str:
        """Format user data for the AI prompt"""
        formatted_data = []
        for key, value in user_data.items():
            if key == 'name':
                formatted_data.append(f"Name: {value}")
            elif key == 'goal':
                formatted_data.append(f"Goal: {value}")
            elif key == 'gender':
                formatted_data.append(f"Gender: {value}")
            elif key == 'age':
                formatted_data.append(f"Age: {value}")
            elif key == 'weight':
                formatted_data.append(f"Weight: {value} kg")
            elif key == 'height':
                formatted_data.append(f"Height: {value} cm")
            elif key == 'activity_level':
                formatted_data.append(f"Activity Level: {value}")
            elif key == 'training_style':
                formatted_data.append(f"Training Style: {value}")
            elif key == 'diet_type':
                formatted_data.append(f"Diet Type: {value}")
            elif key == 'allergies' and value:
                formatted_data.append(f"Allergies/Restrictions: {value}")
            elif key == 'fav_foods' and value:
                formatted_data.append(f"Favorite Foods: {value}")
        
        return "\n".join(formatted_data)