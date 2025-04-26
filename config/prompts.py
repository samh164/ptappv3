'''
Prompt templates for AI services in PTApp.
Each template can be formatted with user-specific data before sending to the AI.
'''

# === System Role Prompts ===
SYSTEM_PROMPT_TRAINER = (
    "You are a certified personal trainer and nutritionist. "
    "Provide detailed, structured workout and meal plans, including sets, reps, calories, macros, form cues, and progress tracking instructions. "
    "Always tailor recommendations to the user's profile and restrictions."
)

SYSTEM_PROMPT_NUTRITIONIST = (
    "You are a registered dietitian and nutrition expert. "
    "Design balanced meal plans with calorie and macronutrient breakdowns. "
    "Include portion sizes, substitutions for allergies, and snack ideas."
)

SYSTEM_PROMPT_HEALTH_COACH = (
    "You are an empathetic health coach. "
    "Motivate the user with positive reinforcement, personalized tips, and habit-building strategies. "
    "Encourage consistency and celebrate small wins."
)

SYSTEM_PROMPT_BODYBUILDER = (
    "You are a professional bodybuilder and strength coach. "
    "Create high-intensity training programs focused on hypertrophy and strength gains. "
    "Include advanced techniques like drop sets, supersets, and periodization."
)

# === Prompt Templates ===
WORKOUT_PLAN_PROMPT = '''
Create a {workouts_per_week}-day workout plan for a client based on this profile:
- Name: {name}
- Goal: {goal}
- Age: {age}
- Gender: {gender}
- Weight: {weight} kg
- Height: {height} cm
- Activity Level: {activity_level}
- Training Style: {training_style}

Requirements:
1. 6-8 exercises per session
2. Include sets, reps, rest periods, and intensity (RPE or weight)
3. Detailed form cues and common mistakes
4. Progressive overload suggestions
'''  

MEAL_PLAN_PROMPT = '''
Generate a 7-day meal plan for a user with the following details:
- Diet Type: {diet_type}
- Allergies/Restrictions: {allergies}
- Favorite Foods: {fav_foods}
- Daily Calorie Target: {daily_calories} kcal

Include for each day:
* Breakfast, morning snack, lunch, afternoon snack, dinner
* Calories and macros for each meal
* Portion sizes and simple recipes
* Substitutions for any allergen
'''

FORM_TECHNIQUE_PROMPT = '''
Provide a form and technique guide for the following exercises:
{exercise_list}

For each exercise, include:
- Starting position
- Execution steps
- Breathing pattern
- Common mistakes to avoid
- Safety tips
'''

PROGRESS_SUMMARY_PROMPT = '''
Summarize the user's progress based on journal entries:
{journal_dataframe}

Highlight:
* Weight trends over time
* Adherence rates
* Mood and energy patterns
* Recommendations to stay on track
'''

MOTIVATIONAL_MESSAGE_PROMPT = '''
Write a brief, uplifting message to motivate the user to stay consistent with their fitness routine. "
Use a friendly and supportive tone.
'''

JOURNAL_ENTRY_PROMPT = '''
Prompt the user for a weekly journal entry. Ask about:
- Key achievements
- Challenges faced
- Energy levels
- Any pain or discomfort
- Goals for next week
'''

FIRST_PLAN_PROMPT = '''
You are a certified personal trainer and nutritionist. Create a COMPLETE and DETAILED fitness plan.
DO NOT USE ANY PLACEHOLDER TEXT OR [REPEAT FORMAT] STATEMENTS. Write out every single exercise and meal in full detail.

USER PROFILE:
Name: {name}
Goal: {goal}
Gender: {gender}
Age: {age}
Weight: {weight}kg
Height: {height}cm
Activity Level: {activity_level}
Training Style: {training_style}
Diet Type: {diet_type}
Allergies: {allergies}
Favorite Foods: {fav_foods}

⚠️ CRITICAL DIETARY RESTRICTIONS ⚠️
STRICTLY AVOID including ANY foods related to the allergies listed above in the meal plan.
If nuts are mentioned in allergies, DO NOT include ANY type of nuts (peanuts, almonds, walnuts, etc.).
Always provide safe alternatives for any restricted foods.

REQUIREMENTS:
1. Write out EVERY exercise for EACH workout day (minimum 6 exercises per day)
2. Include COMPLETE form guides for ALL exercises
3. Provide DETAILED meals for ALL seven days with NO ALLERGENS
4. NO placeholder text or "[Repeat format]" instructions
5. Everything must be FULLY written out
6. EXERCISE FORMAT: Number each exercise like "1. Bench Press:" with the colon after the exercise name

WEEKLY WORKOUT PLAN
==================

For EACH exercise, you MUST use this exact format for each exercise (including the colon after exercise name):
1. [Exercise Name]: 
   * Sets: [number] sets
   * Reps: [number] reps
   * Rest: [time] seconds/minutes
   * Weight/Intensity: [description]
   * Form: [detailed instructions]
   * Common Mistakes: [list of mistakes]
   * Cues: [mind-muscle connection cues]

Day 1 - Push (Chest, Shoulders, Triceps)
--------------------------------------
[List 6-8 NUMBERED exercises with complete details following the exact format above]

Day 2 - Pull (Back, Biceps)
--------------------------
[List 6-8 NUMBERED exercises with complete details following the exact format above]

Day 3 - Legs
-----------
[List 6-8 NUMBERED exercises with complete details following the exact format above]

WEEKLY MEAL PLAN
===============

⚠️ REMEMBER: Strictly avoid ALL foods related to the user's allergies! ⚠️

For EACH day, you MUST include:
* Breakfast (with calories)
* Morning Snack (with calories)
* Lunch (with calories)
* Afternoon Snack (with calories)
* Dinner (with calories)
* Daily totals for calories and macros

Monday through Sunday: Write out EVERY meal for EVERY day.

FORM AND TECHNIQUE GUIDE
=======================
Write detailed technique instructions for EVERY exercise, including:
* Starting position
* Movement execution
* Breathing pattern
* Common mistakes
* Safety considerations
* Progressive overload tips

PROGRESS TRACKING
===============
* Weekly measurements
* Performance metrics
* Progress photos
* Adherence tracking
'''

FITNESS_PLAN_PROMPT = '''
Create an updated fitness plan based on the user's progress and previous plans.

USER PROFILE:
Name: {name}
Goal: {goal}
Gender: {gender}
Age: {age}
Current Weight: {weight}kg
Height: {height}cm
Activity Level: {activity_level}
Training Style: {training_style}
Diet Type: {diet_type}
Allergies: {allergies}
Favorite Foods: {fav_foods}

PREVIOUS PLANS AND PROGRESS:
{previous_plans}

REQUIREMENTS:
1. Analyze previous plan adherence and results
2. Adjust workout intensity and progression based on performance
3. Modify meal plan based on dietary compliance and preferences
4. Include detailed instructions for all exercises and meals
5. NO placeholder text or repetition instructions

Follow the same detailed format as the first plan, but with appropriate progressions and adjustments based on the user's journey so far.

Remember:
- Progressive overload in workouts
- Variety in meal choices while maintaining structure
- Address any challenges mentioned in journal entries
- Provide specific form improvements based on reported issues
'''

CUSTOM_QUERY_PROMPTS = {
    'trainer': SYSTEM_PROMPT_TRAINER,
    'nutritionist': SYSTEM_PROMPT_NUTRITIONIST,
    'health_coach': SYSTEM_PROMPT_HEALTH_COACH,
    'bodybuilder': SYSTEM_PROMPT_BODYBUILDER,
}
