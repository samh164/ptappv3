import re
from typing import List, Dict, Any

def validate_plan_content(plan_content: str) -> List[str]:
    """Check for placeholder text and incomplete sections"""
    issues = []
    
    if not plan_content or len(plan_content.strip()) < 100:
        return ["Content is too short or empty"]
    
    # Check for required sections
    required_sections = [
        "FORM AND TECHNIQUE GUIDE",
        "PROGRESS TRACKING"
    ]
    
    for section in required_sections:
        if section not in plan_content:
            issues.append(f"Missing required section: {section}")
    
    # Check for required day headers
    required_days = ["Day 1", "Day 2", "Day 3"]
    for day in required_days:
        if day not in plan_content:
            issues.append(f"Missing {day} section")
    
    # Split into days and validate each
    days = [d for d in plan_content.split("Day ") if d.strip()]
    if len(days) < 3:
        issues.append(f"Found {len(days)} days, expected at least 3")
        return issues
    
    required_fields = [
        "* Sets:", "* Reps:", "* Rest:", "* Weight/Intensity:",
        "* Form:", "* Common Mistakes:", "* Cues:"
    ]
    
    for i, day in enumerate(days, 1):
        # Count exercises (lines ending with colon and starting with a number)
        exercise_lines = [line.strip() for line in day.split('\n') 
                        if line.strip().endswith(':') and 
                        any(line.strip().startswith(str(j) + ".") for j in range(1, 10))]
        
        num_exercises = len(exercise_lines)
        if num_exercises < 1:
            issues.append(f"Day {i}: Not enough exercises (found {num_exercises}, minimum is 1)")
            continue
        
        # Verify exercise numbering and colons
        for j, line in enumerate(exercise_lines, 1):
            if not line.endswith(':'):
                issues.append(f"Day {i}: Exercise {j} should end with ':'")
            if not line.strip():
                issues.append(f"Day {i}: Exercise name is empty")
        
        # Check for required fields in each exercise
        exercise_blocks = day.split('\n\n')
        for j, block in enumerate(exercise_blocks, 1):
            if not block.strip():
                continue
            
            if not any(block.strip().startswith(str(k) + ".") for k in range(1, 10)):
                continue
                
            minimal_fields = [
                "* Sets:", "* Reps:", "* Form:"
            ]
            
            for field in minimal_fields:
                if field not in block:
                    issues.append(f"Day {i}, Exercise {j}: Missing field '{field}'")
                else:
                    # Check that the field has a value
                    field_line = [line for line in block.split('\n') if field in line][0]
                    field_value = field_line.split(':')[1].strip()
                    if not field_value:
                        issues.append(f"Day {i}, Exercise {j}: Empty value for field '{field}'")
    
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
    
    if "WEEKLY WORKOUT PLAN" not in workout_content:
        issues.append("Missing required section: WEEKLY WORKOUT PLAN")
    
    return issues
