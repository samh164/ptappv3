FOOD_CATEGORIES = {
    'proteins': {
        'items': [
            'chicken', 'turkey', 'beef', 'lamb', 'pork', 'egg', 'tofu', 'tempeh',
            'salmon', 'tuna', 'cod', 'shrimp', 'crab', 'mussel', 'fish', 'shellfish'
        ],
        'categories': ['meat', 'poultry', 'seafood', 'eggs', 'soy_protein']
    },
    'carbohydrates': {
        'items': [
            'rice', 'pasta', 'bread', 'potato', 'quinoa', 'oat', 'couscous',
            'tortilla', 'lentil', 'bean', 'sweet potato', 'brown rice', 'white rice'
        ],
        'categories': ['grains', 'starches', 'legumes']
    },
    'fats': {
        'items': [
            'olive oil', 'avocado', 'butter', 'ghee', 'cheese', 'nut', 'seed',
            'coconut oil', 'peanut', 'almond', 'cashew', 'walnut'
        ],
        'categories': ['oils', 'dairy_fats', 'nuts_and_seeds']
    },
    'vegetables': {
        'items': [
            'broccoli', 'spinach', 'kale', 'carrot', 'pea', 'pepper', 'lettuce',
            'cabbage', 'mushroom', 'zucchini', 'cauliflower', 'onion', 'bell pepper'
        ],
        'categories': ['leafy_greens', 'cruciferous', 'root_vegetables']
    },
    'fruits': {
        'items': [
            'banana', 'apple', 'berry', 'orange', 'grape', 'mango', 'pineapple',
            'watermelon', 'pear', 'strawberry', 'blueberry'
        ],
        'categories': ['fresh_fruits', 'berries', 'citrus']
    }
}

# data/allergy_groups.py
ALLERGY_GROUPS = {
    'nut_allergy': {
        'items': [
            'peanut', 'almond', 'cashew', 'hazelnut', 'pecan', 'walnut', 'pistachio',
            'nut butter', 'trail mix', 'granola'
        ],
        'related_ingredients': [
            'almond milk', 'almond flour', 'peanut oil', 'nut extract'
        ]
    },
    # ... [rest of allergies]
}
