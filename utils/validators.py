import re
from typing import List, Dict, Any

def validate_plan_content(plan_content: str) -> List[str]:
    """Check for placeholder text and incomplete sections"""
    issues = []
    
    placeholder_patterns = [
        r"\[Repeat format.*?\]",
        r"\[Include.*?\]",
        r"\[Continue.*?\]",
        r"\[Add.*?\]",
        r"\[List.*?\]",
        r"\.\.\.",
        r"etc\.",
        r"\[specify.*?\]",
    ]
    
    for pattern in placeholder_patterns:
        if re.search(pattern, plan_content, re.IGNORECASE):
            issues.append(f"Found placeholder text matching pattern: {pattern}")
    
    # Check for minimum required exercises per day
    required_exercises = {
        "Day 1": 6,
        "Day 2": 6,
        "Day 3": 6
    }
    
    # Add multiple regex patterns to detect exercises in different formats
    exercise_patterns = [
        r"\d+\.\s+[A-Za-z\s\-]+(:|$)",  # Numbered with colon: "1. Bench Press:"
        r"\d+\.\s+[A-Za-z\s\-]+\n\s+\*\s+Sets",  # Numbered without colon but with "Sets" bullet
        r"[A-Za-z\s\-]+\s+\(\d+\s+sets",  # Exercise with sets in parentheses
        r"Exercise\s+\d+:\s+[A-Za-z\s\-]+",  # "Exercise 1: Bench Press"
    ]
    
    for day, min_exercises in required_exercises.items():
        day_content_match = re.search(f"{day}.*?(?=Day|WEEKLY|FORM AND TECHNIQUE|$)", plan_content, re.DOTALL)
        if day_content_match:
            day_content = day_content_match.group(0)
            # Count exercises using multiple patterns
            exercise_count = 0
            for pattern in exercise_patterns:
                exercise_count += len(re.findall(pattern, day_content))
            
            # If still no exercises found, try a more general pattern as fallback
            if exercise_count == 0:
                exercise_count = len(re.findall(r"\d+\.\s+[A-Za-z\s\-]+", day_content))
            
            if exercise_count < min_exercises:
                issues.append(f"{day} should have at least {min_exercises} exercises, found {exercise_count}")
    
    return issues

def validate_meal_plan(plan_content: str, user_data: Dict[str, Any]) -> List[str]:
    """Validate meal plan against user's dietary restrictions"""
    violations = []
    plan_content_lower = plan_content.lower()
    
    allergies = user_data.get('allergies', '').lower()
    diet_type = user_data.get('diet_type', '').lower()
    
    # Define common allergens and their related foods
    allergen_groups = {
        'nuts': ['peanut', 'almond', 'cashew', 'walnut', 'pecan', 'hazelnut', 'macadamia', 'pistachio', 'pine nut', 
                'nut butter', 'almond milk', 'almond flour', 'nut oil', 'nutella', 'marzipan', 'nougat'],
        'peanut': ['peanut', 'peanut butter', 'peanut oil', 'groundnut', 'arachis oil', 'beer nuts', 'mixed nuts'],
        'tree nuts': ['almond', 'cashew', 'walnut', 'pecan', 'hazelnut', 'macadamia', 'pistachio', 'pine nut', 'brazil nut'],
        'dairy': ['milk', 'cheese', 'yogurt', 'cream', 'butter', 'whey', 'casein', 'lactose', 'ice cream', 
                 'dairy', 'buttermilk', 'ghee', 'custard', 'pudding', 'kefir'],
        'gluten': ['wheat', 'bread', 'pasta', 'flour', 'cereal', 'barley', 'rye', 'oats', 'couscous', 
                  'beer', 'bulgur', 'durum', 'semolina', 'farina', 'seitan'],
        'seafood': ['fish', 'shellfish', 'shrimp', 'crab', 'lobster', 'tuna', 'salmon', 'cod', 'prawn', 
                   'clam', 'mussel', 'oyster', 'scallop', 'squid', 'octopus', 'anchovy', 'sardine'],
        'eggs': ['egg', 'mayonnaise', 'custard', 'omelette', 'meringue', 'egg white', 'egg yolk', 
                'quiche', 'frittata', 'hollandaise', 'aioli'],
        'soy': ['soy', 'tofu', 'edamame', 'soy sauce', 'soy milk', 'tempeh', 'miso', 'natto', 
               'tamari', 'soybean', 'soy protein'],
    }
    
    # Special case for nuts - add generic terms as well
    if 'nut' in allergies:
        generic_nuts = ['nut', 'nuts', 'mixed nuts', 'nut mix', 'trail mix', 'granola']
        for term in generic_nuts:
            if term in plan_content_lower:
                violations.append(f"Found generic nuts reference '{term}' for nut allergy")
    
    # Process allergy text to extract relevant allergens
    allergen_keywords = []
    for allergen in allergen_groups.keys():
        if allergen in allergies:
            allergen_keywords.append(allergen)
    
    # If no specific allergens found but "allergy" words exist, check for common terms
    if not allergen_keywords and allergies:
        # Look for mentions of specific foods
        for food in ['peanut', 'nut', 'almond', 'egg', 'dairy', 'milk', 'fish', 'seafood', 'gluten', 'wheat', 'soy']:
            if food in allergies:
                if food == 'nut':  # Handle the case where "nut" is mentioned without specifics
                    allergen_keywords.append('nuts')
                    allergen_keywords.append('peanut')
                    allergen_keywords.append('tree nuts')
                else:
                    for allergen, foods in allergen_groups.items():
                        if food in allergen or food in foods:
                            allergen_keywords.append(allergen)
    
    # Check for allergens
    for allergen in allergen_keywords:
        foods = allergen_groups.get(allergen, [])
        for food in foods:
            # Use word boundary check to avoid partial matches (e.g., "nut" in "nutrition")
            pattern = r'\b' + re.escape(food) + r'\b'
            matches = re.findall(pattern, plan_content_lower)
            if matches:
                for match in matches:
                    violations.append(f"Found forbidden food '{match}' for {allergen} allergy")
    
    # Check dietary restrictions
    if 'vegetarian' in diet_type:
        meat_products = ['chicken', 'beef', 'pork', 'turkey', 'lamb', 'veal', 'ham', 'bacon', 'sausage', 
                         'fish', 'meat', 'steak', 'burger', 'meatball', 'pepperoni', 'salami']
        for meat in meat_products:
            pattern = r'\b' + re.escape(meat) + r'\b'
            if re.search(pattern, plan_content_lower):
                violations.append(f"Found non-vegetarian food '{meat}' in vegetarian diet")
    
    if 'vegan' in diet_type:
        animal_products = ['meat', 'fish', 'egg', 'milk', 'cheese', 'yogurt', 'butter', 'honey', 'whey', 
                          'cream', 'gelatin', 'lard', 'ghee', 'casein', 'lactose', 'poultry', 'beef']
        for product in animal_products:
            pattern = r'\b' + re.escape(product) + r'\b'
            if re.search(pattern, plan_content_lower):
                violations.append(f"Found non-vegan food '{product}' in vegan diet")
    
    return violations

def validate_workout_structure(workout_content: str) -> List[str]:
    """Validate workout plan structure"""
    issues = []
    
    required_sections = [
        "WEEKLY WORKOUT PLAN",
        "FORM AND TECHNIQUE GUIDE",
        "PROGRESS TRACKING"
    ]
    
    for section in required_sections:
        if section not in workout_content:
            issues.append(f"Missing required section: {section}")
    
    return issues
