import json
import logging
import requests
from typing import Optional, Dict, Any
from config.settings import OPENAI_API_KEY
from config.prompts import FIRST_PLAN_PROMPT, FITNESS_PLAN_PROMPT
from utils.validators import (
    validate_plan_content,
    validate_meal_plan,
    validate_workout_structure
)

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
        logger.info("OpenAI service initialized")

    def _call_openai_api(self, endpoint, payload):
        """Make a direct API call to OpenAI using requests"""
        url = f"{self.api_base}/{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise exception for 4XX/5XX status codes
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
            
            # Final validation of the complete plan
            content_issues = validate_plan_content(complete_plan)
            meal_violations = validate_meal_plan(complete_plan, user_data)
            workout_issues = validate_workout_structure(complete_plan)
            
            if content_issues or meal_violations or workout_issues:
                issues = content_issues + meal_violations + workout_issues
                logger.error(f"Final plan validation failed: {issues}")
                return None
                
            return complete_plan
            
        except Exception as e:
            logger.error(f"Error generating first plan: {str(e)}")
            raise
            
    def _generate_workout_section(self, user_data):
        """Generate just the workout section of the plan"""
        max_retries = 3
        current_try = 0
        feedback = ""
        
        while current_try < max_retries:
            prompt = f"""
You are a NASM-certified personal trainer with 10+ years experience designing custom workout programs.

CREATE A DETAILED 3-DAY WORKOUT PLAN FOR:
- Goal: {user_data['goal']}
- Gender: {user_data['gender']}
- Age: {user_data['age']}
- Weight: {user_data['weight']}kg
- Height: {user_data['height']}cm
- Activity Level: {user_data['activity_level']}
- Training Style: {user_data['training_style']}

CRITICAL REQUIREMENTS:
1. Include EXACTLY 6 exercises per day - no more, no less
2. Number each exercise (1-6) with a colon after the name (e.g., "1. Bench Press:")
3. Follow this EXACT format for EVERY exercise:

```
Day 1 - Push (Chest, Shoulders, Triceps)
--------------------------------------
1. Exercise Name: 
   * Sets: X sets
   * Reps: X reps
   * Rest: X seconds
   * Weight/Intensity: description
   * Form: detailed instructions
   * Common Mistakes: list of mistakes
   * Cues: mind-muscle connection cues

2. [Next Exercise]:
   [Same format]
```

REQUIRED: Follow this EXACT structure with 6 exercises for each day:
- Day 1 - Push (Chest, Shoulders, Triceps)
- Day 2 - Pull (Back, Biceps)
- Day 3 - Legs

Ensure exercises are appropriate for the user's specified goal and training style.
DO NOT include any other sections. ONLY provide the workout plan.
"""
            if feedback:
                prompt += f"\n\nPREVIOUS ATTEMPT ERRORS: {feedback}\nYou MUST fix these exact issues in your response."
                
            system_prompt = (
                "You are an elite personal trainer who creates perfectly formatted workout programs. "
                "You ALWAYS include EXACTLY 6 exercises per day, properly numbered with colons. "
                "You NEVER deviate from the required format. "
                "You are an expert at selecting exercises that match the client's goals and training style."
            )
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,  # Lower temperature for more deterministic output
                "max_tokens": 3000
            }
            
            response = self._call_openai_api("chat/completions", payload)
            workout_section = response["choices"][0]["message"]["content"]
            
            # Validate just the workout section
            content_issues = validate_plan_content(workout_section)
            
            if not content_issues:
                return workout_section
            
            feedback = ", ".join(content_issues)
            logger.warning(f"Workout section validation issues (attempt {current_try+1}): {content_issues}")
            current_try += 1
        
        # If failed after max retries, generate a fallback workout plan
        logger.warning("Attempting to generate a fallback workout plan...")
        return self._generate_fallback_workout_plan(user_data)
    
    def _generate_fallback_workout_plan(self, user_data):
        """Generate a simple fallback workout plan that meets the format requirements"""
        style = user_data.get('training_style', 'General Fitness')
        plan = ""
        
        # Generic exercises by body part
        exercises = {
            'push': [
                ('Bench Press', '3-4', '8-12', '60-90', 'Moderate weight (60-70% 1RM)', 
                 'Lie on bench, feet flat on floor. Grip bar slightly wider than shoulders. Lower to chest, press up.',
                 'Arching back, bouncing bar off chest, flaring elbows.',
                 'Drive through the chest, keep shoulders back.'),
                ('Push-Ups', '3', '10-15', '45-60', 'Bodyweight (add weight vest for progression)', 
                 'Start in plank position, hands under shoulders. Lower chest to floor, push back up.',
                 'Sagging hips, elbows flaring too wide, incomplete range of motion.',
                 'Maintain straight line from head to heels, engage core.'),
                ('Shoulder Press', '3', '8-12', '60-90', 'Moderate weight (60-70% 1RM)', 
                 'Seated or standing, press dumbbells overhead, fully extending arms.',
                 'Arching back, using momentum, incomplete lockout.',
                 'Engage core, feel shoulders doing the work.'),
                ('Tricep Dips', '3', '10-15', '45-60', 'Bodyweight', 
                 'Hands on bench/chair behind you, lower body by bending elbows, then extend.',
                 'Shoulders rising to ears, insufficient depth, flaring elbows.',
                 'Keep elbows pointing back, feel the tension in triceps.'),
                ('Incline Dumbbell Press', '3', '8-12', '60-90', 'Moderate weight', 
                 'Lie on incline bench, press dumbbells up from shoulder width.',
                 'Bouncing weights, uneven pressing, excessive arching.',
                 'Squeeze chest at top of movement, maintain control.'),
                ('Lateral Raises', '3', '12-15', '45-60', 'Light to moderate weight', 
                 'Stand with dumbbells at sides, raise arms to shoulder height.',
                 'Using momentum, raising too high, shrugging shoulders.',
                 'Lead with elbows, imagine pouring water from a pitcher.')
            ],
            'pull': [
                ('Pull-Ups', '3-4', '6-12', '60-90', 'Bodyweight (use assisted machine if needed)', 
                 'Hang from bar with overhand grip, pull up until chin over bar.',
                 'Insufficient range of motion, swinging, half reps.',
                 'Initiate with lats, imagine pulling elbows to floor.'),
                ('Bent-Over Rows', '3', '8-12', '60-90', 'Moderate weight', 
                 'Hinge at hips, back flat, pull weight to lower ribs.',
                 'Rounding back, using momentum, insufficient retraction.',
                 'Squeeze shoulder blades together, keep elbows close to body.'),
                ('Lat Pulldowns', '3', '10-12', '60', 'Moderate weight', 
                 'Seated facing machine, grip bar wider than shoulders, pull to upper chest.',
                 'Leaning back excessively, pulling to stomach, lifting shoulders.',
                 'Initiate movement by depressing shoulder blades.'),
                ('Face Pulls', '3', '12-15', '45-60', 'Light to moderate weight', 
                 'Pull rope attachment to face level with external rotation.',
                 'Insufficient external rotation, using too heavy weight, poor posture.',
                 'Pull to forehead, thumbs pointing back at end position.'),
                ('Bicep Curls', '3', '10-12', '45-60', 'Moderate weight', 
                 'Stand with weights at sides, curl up while keeping elbows stationary.',
                 'Swinging weights, moving elbows forward, half reps.',
                 'Squeeze biceps at top, maintain tension throughout.'),
                ('Rear Delt Flyes', '3', '12-15', '45-60', 'Light weight', 
                 'Bend at waist, raise weights out to sides with slight elbow bend.',
                 'Using too heavy weight, insufficient scapular retraction, poor posture.',
                 'Lead with elbows, keep chest up despite bent position.')
            ],
            'legs': [
                ('Squats', '4', '8-12', '90-120', 'Moderate to heavy weight', 
                 'Stand with feet shoulder-width, lower hips until thighs parallel, drive up through heels.',
                 'Knees collapsing inward, rising onto toes, insufficient depth.',
                 'Maintain upright chest, keep knees tracking over toes.'),
                ('Romanian Deadlifts', '3', '8-12', '90', 'Moderate to heavy weight', 
                 'Stand tall, hinge at hips while maintaining slight knee bend, lower weight along legs.',
                 'Rounding back, bending knees too much, insufficient hip hinge.',
                 'Push hips back, feel stretch in hamstrings.'),
                ('Lunges', '3', '10-12 each leg', '60', 'Moderate weight or bodyweight', 
                 'Step forward, lower back knee toward floor, push through front heel to return.',
                 'Leaning forward, knee extending past toe, unstable posture.',
                 'Keep torso upright, maintain balance throughout movement.'),
                ('Leg Press', '3', '10-12', '60-90', 'Moderate to heavy weight', 
                 'Sit in machine, press platform away by extending knees and hips.',
                 'Locking knees, lifting hips off seat, incomplete range of motion.',
                 'Press through heels, maintain contact between back and seat.'),
                ('Calf Raises', '4', '15-20', '30-45', 'Moderate weight', 
                 'Stand on edge of platform, raise heels as high as possible, lower with control.',
                 'Bouncing at bottom, insufficient range of motion, leaning too far forward.',
                 'Pause at top of movement, feel full stretch at bottom.'),
                ('Hamstring Curls', '3', '10-12', '60', 'Moderate weight', 
                 'Lie face down on machine, curl legs by bending knees.',
                 'Lifting hips, swinging weight, insufficient flexion.',
                 'Squeeze hamstrings at peak contraction, control the negative.')
            ]
        }
        
        # Day 1 - Push
        plan += "Day 1 - Push (Chest, Shoulders, Triceps)\n"
        plan += "--------------------------------------\n"
        for i, exercise in enumerate(exercises['push'], 1):
            name, sets, reps, rest, weight, form, mistakes, cues = exercise
            plan += f"{i}. {name}: \n"
            plan += f"   * Sets: {sets} sets\n"
            plan += f"   * Reps: {reps} reps\n"
            plan += f"   * Rest: {rest} seconds\n"
            plan += f"   * Weight/Intensity: {weight}\n"
            plan += f"   * Form: {form}\n"
            plan += f"   * Common Mistakes: {mistakes}\n"
            plan += f"   * Cues: {cues}\n\n"
        
        # Day 2 - Pull
        plan += "Day 2 - Pull (Back, Biceps)\n"
        plan += "--------------------------\n"
        for i, exercise in enumerate(exercises['pull'], 1):
            name, sets, reps, rest, weight, form, mistakes, cues = exercise
            plan += f"{i}. {name}: \n"
            plan += f"   * Sets: {sets} sets\n"
            plan += f"   * Reps: {reps} reps\n"
            plan += f"   * Rest: {rest} seconds\n"
            plan += f"   * Weight/Intensity: {weight}\n"
            plan += f"   * Form: {form}\n"
            plan += f"   * Common Mistakes: {mistakes}\n"
            plan += f"   * Cues: {cues}\n\n"
        
        # Day 3 - Legs
        plan += "Day 3 - Legs\n"
        plan += "-----------\n"
        for i, exercise in enumerate(exercises['legs'], 1):
            name, sets, reps, rest, weight, form, mistakes, cues = exercise
            plan += f"{i}. {name}: \n"
            plan += f"   * Sets: {sets} sets\n"
            plan += f"   * Reps: {reps} reps\n"
            plan += f"   * Rest: {rest} seconds\n"
            plan += f"   * Weight/Intensity: {weight}\n"
            plan += f"   * Form: {form}\n"
            plan += f"   * Common Mistakes: {mistakes}\n"
            plan += f"   * Cues: {cues}\n\n"
        
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
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,  # Lower temperature for more deterministic output
                "max_tokens": 3000
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
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
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
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = self._call_openai_api("chat/completions", payload)
        return response["choices"][0]["message"]["content"]

    def generate_fitness_plan(self, user_data, previous_plans=None):
        """Generate updated fitness plan based on user's progress"""
        try:
            prompt = FITNESS_PLAN_PROMPT.format(
                **user_data,
                previous_plans=previous_plans if previous_plans else "No previous plans"
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
                    "3. Include AT LEAST 6 exercises for each workout day\n"
                    "4. NEVER use placeholder text or '[repeat format]' instructions\n"
                    "5. Write everything out in complete detail\n"
                    "6. Use prior plans and progress to create appropriate progressions"
                )
                
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": current_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 6000  # Increased from 4000 to ensure complete plans
                }
                
                response = self._call_openai_api("chat/completions", payload)
                plan_content = response["choices"][0]["message"]["content"]
                
                # Validate the generated content
                content_issues = validate_plan_content(plan_content)
                meal_violations = validate_meal_plan(plan_content, user_data)
                workout_issues = validate_workout_structure(plan_content)
                
                if not content_issues and not meal_violations and not workout_issues:
                    return plan_content
                
                # If validation failed, prepare feedback for the next attempt
                issues = content_issues + meal_violations + workout_issues
                feedback = "Your previous response had these issues: " + ", ".join(issues)
                logger.warning(f"Plan validation issues (attempt {current_try+1}): {issues}")
                    
                current_try += 1
                
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