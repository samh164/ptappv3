"""
Exercise database with detailed information for workout plan generation.
Fetches exercises from ExerciseDB API with fallback to local database.
"""

import json
import os
import requests
import logging
from typing import List, Dict, Any
from config.settings import EXERCISEDB_API_KEY  # Add this to your settings file

logger = logging.getLogger(__name__)

class ExerciseDatabase:
    def __init__(self):
        self.api_key = EXERCISEDB_API_KEY
        # Update to use RapidAPI endpoint
        self.api_base_url = "https://exercisedb.p.rapidapi.com"
        self.exercises: Dict[str, Dict[str, Any]] = self._load_exercises()
        
    def _load_exercises(self) -> Dict[str, Dict[str, Any]]:
        """Load exercises from JSON file or use default exercises if file doesn't exist."""
        # First, try to load from local cache file
        json_path = os.path.join(os.path.dirname(__file__), 'exercise_db.json')
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    exercises = json.load(f)
                logger.info(f"Loaded {len(exercises)} exercises from local cache")
                return exercises
        except Exception as e:
            logger.error(f"Error loading exercises from {json_path}: {str(e)}")
        
        # If local file doesn't exist, try to fetch from API without authentication first
        if self.api_key:
            try:
                exercises = self._fetch_from_api_authenticated()
                if exercises and len(exercises) > 0:
                    # Cache the exercises locally
                    self._cache_exercises(exercises, json_path)
                    return exercises
            except Exception as e:
                logger.error(f"Error fetching exercises from authenticated API: {str(e)}")
        
        # Fallback to default exercises if API fails
        logger.info("Using default exercise database")
        return self._get_default_exercises()
    
    def _fetch_from_api_authenticated(self) -> Dict[str, Dict[str, Any]]:
        """Fetch exercises from ExerciseDB API with RapidAPI authentication."""
        logger.info("Fetching exercises from ExerciseDB API (RapidAPI)")
        
        # RapidAPI specific headers
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        }
        
        try:
            # First, try getting all exercises (limited by the API)
            logger.info("Fetching all exercises from API")
            response = requests.get(
                f"{self.api_base_url}/exercises",
                headers=headers
            )
            response.raise_for_status()
            
            # Get the response content as text first for debugging
            content = response.text
            logger.debug(f"API Response content: {content[:200]}...")  # Log first 200 chars
            
            # Parse JSON response
            try:
                exercises_data = response.json()
                
                # Check if we got a list (normal RapidAPI response)
                if not isinstance(exercises_data, list):
                    logger.error(f"Expected list response, got {type(exercises_data)}")
                    return {}
                
                logger.info(f"Successfully retrieved {len(exercises_data)} exercises from RapidAPI")
                
                # Transform API format to our internal format
                all_exercises = {}
                for exercise in exercises_data:
                    # Ensure exercise is a dictionary
                    if not isinstance(exercise, dict):
                        logger.warning(f"Skipping non-dictionary exercise: {exercise}")
                        continue
                    
                    # Get ID from the exercise
                    exercise_id = str(exercise.get("id", "")).lower().replace(" ", "_")
                    if not exercise_id:
                        # Try name as fallback if no ID
                        name = exercise.get("name", "")
                        if name:
                            exercise_id = name.lower().replace(" ", "_")
                    
                    # Skip empty IDs or duplicates
                    if not exercise_id or exercise_id in all_exercises:
                        continue
                    
                    # Map fields from RapidAPI format
                    body_part = exercise.get("bodyPart", "")
                    equipment = exercise.get("equipment", "")
                    target = exercise.get("target", "")
                    
                    all_exercises[exercise_id] = {
                        "id": exercise_id,
                        "name": exercise.get("name", ""),
                        "equipment": [equipment] if equipment else [],
                        "body_parts": [body_part] if body_part else [],
                        "target_muscles": [target] if target else [],
                        "secondary_muscles": exercise.get("secondaryMuscles", []),
                        "exercise_type": self._determine_exercise_type_rapidapi(exercise),
                        "difficulty": self._determine_difficulty_rapidapi(exercise),
                        "instructions": exercise.get("instructions", []),
                        "form_tips": [],  # API doesn't provide this
                        "common_mistakes": [],  # API doesn't provide this
                        "variations": []  # API doesn't provide this
                    }
                
                logger.info(f"Successfully processed {len(all_exercises)} exercises from RapidAPI")
                return all_exercises
                
            except json.JSONDecodeError as je:
                logger.error(f"Failed to decode JSON response: {str(je)}")
                logger.debug(f"Response content: {content[:500]}...")  # Log more content for debugging
                return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"RapidAPI request failed: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error in _fetch_from_api_authenticated: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    def _determine_exercise_type_rapidapi(self, exercise: Dict[str, Any]) -> str:
        """Determine the exercise type based on equipment for RapidAPI format."""
        try:
            equipment = str(exercise.get("equipment", "")).lower()
            
            if not equipment or equipment == "body weight" or equipment == "none":
                return "bodyweight"
            elif "barbell" in equipment or "dumbbell" in equipment or "kettlebell" in equipment:
                return "weight_reps"
            elif "cable" in equipment or "machine" in equipment:
                return "machine_reps"
            else:
                return "bodyweight"
        except Exception as e:
            logger.error(f"Error in _determine_exercise_type_rapidapi: {str(e)}")
            return "bodyweight"  # Default to bodyweight if error
    
    def _determine_difficulty_rapidapi(self, exercise: Dict[str, Any]) -> str:
        """Determine difficulty level based on exercise attributes for RapidAPI format."""
        try:
            equipment = str(exercise.get("equipment", "")).lower()
            name = str(exercise.get("name", "")).lower()
            
            if "barbell" in equipment or "cable" in equipment:
                return "intermediate"
            elif "dumbbell" in equipment:
                return "beginner"
            elif not equipment or "body weight" in equipment or "none" in equipment:
                if "plank" in name or "pushup" in name or "push-up" in name:
                    return "beginner"
                else:
                    return "intermediate"
            else:
                return "intermediate"
        except Exception as e:
            logger.error(f"Error in _determine_difficulty_rapidapi: {str(e)}")
            return "intermediate"  # Default to intermediate if error
    
    def _cache_exercises(self, exercises: Dict[str, Dict[str, Any]], file_path: str) -> None:
        """Cache exercises to a local JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(exercises, f)
            logger.info(f"Cached {len(exercises)} exercises to {file_path}")
        except Exception as e:
            logger.error(f"Error caching exercises to {file_path}: {str(e)}")
    
    def _get_default_exercises(self) -> Dict[str, Dict[str, Any]]:
        """Return a default set of exercises when all else fails."""
        return {
            "bench_press": {
                "id": "bench_press",
                "name": "Bench Press",
                "equipment": ["Barbell", "Bench"],
                "body_parts": ["Chest"],
                "target_muscles": ["Pectoralis Major"],
                "secondary_muscles": ["Anterior Deltoids", "Triceps"],
                "exercise_type": "weight_reps",
                "difficulty": "intermediate",
                "instructions": [
                    "Lie flat on bench with feet planted firmly on ground",
                    "Grip barbell slightly wider than shoulder width",
                    "Unrack the bar and position it above chest",
                    "Lower bar with control to mid-chest",
                    "Press bar back up to starting position"
                ],
                "form_tips": [
                    "Keep wrists straight and elbows at 45-degree angle",
                    "Maintain natural arch in lower back",
                    "Drive through chest and keep shoulders retracted"
                ],
                "common_mistakes": [
                    "Bouncing bar off chest",
                    "Excessive back arch",
                    "Uneven pressing"
                ],
                "variations": [
                    "Dumbbell Bench Press",
                    "Incline Bench Press",
                    "Close-Grip Bench Press"
                ]
            },
            "squat": {
                "id": "squat",
                "name": "Barbell Squat",
                "equipment": ["Barbell", "Squat Rack"],
                "body_parts": ["Legs"],
                "target_muscles": ["Quadriceps"],
                "secondary_muscles": ["Glutes", "Hamstrings", "Calves"],
                "exercise_type": "weight_reps",
                "difficulty": "intermediate",
                "instructions": [
                    "Position bar on upper back, slightly below neck",
                    "Grip bar with hands wider than shoulders",
                    "Unrack bar and step back, feet shoulder-width apart",
                    "Bend knees and hips to lower body, keeping chest up",
                    "Lower until thighs are parallel to ground",
                    "Push through heels to return to starting position"
                ],
                "form_tips": [
                    "Keep weight on heels and mid-foot",
                    "Maintain neutral spine throughout movement",
                    "Keep knees in line with toes"
                ],
                "common_mistakes": [
                    "Knees caving inward",
                    "Rising onto toes",
                    "Rounding lower back"
                ],
                "variations": [
                    "Front Squat",
                    "Goblet Squat",
                    "Bulgarian Split Squat"
                ]
            },
            "pushup": {
                "id": "pushup",
                "name": "Push-Up",
                "equipment": ["None"],
                "body_parts": ["Chest"],
                "target_muscles": ["Pectoralis Major"],
                "secondary_muscles": ["Anterior Deltoids", "Triceps", "Core"],
                "exercise_type": "bodyweight",
                "difficulty": "beginner",
                "instructions": [
                    "Start in plank position with hands slightly wider than shoulders",
                    "Keep body in straight line from head to heels",
                    "Lower body by bending elbows until chest nearly touches floor",
                    "Push back up to starting position",
                    "Repeat for desired number of repetitions"
                ],
                "form_tips": [
                    "Keep core tight throughout movement",
                    "Elbows should be at 45-degree angle to body",
                    "Breathe out when pushing up"
                ],
                "common_mistakes": [
                    "Sagging hips",
                    "Flaring elbows too wide",
                    "Incomplete range of motion"
                ],
                "variations": [
                    "Incline Push-Up",
                    "Decline Push-Up",
                    "Diamond Push-Up"
                ]
            }
        }
    
    def get_exercise(self, exercise_id: str) -> Dict[str, Any]:
        """Get exercise details by ID."""
        return self.exercises.get(exercise_id, {})
    
    def get_exercises_by_body_part(self, body_part: str) -> List[Dict[str, Any]]:
        """Get all exercises for a specific body part."""
        return [
            exercise for exercise in self.exercises.values()
            if body_part.lower() in [bp.lower() for bp in exercise["body_parts"]]
        ]
    
    def get_exercises_by_equipment(self, equipment: str) -> List[Dict[str, Any]]:
        """Get all exercises that use specific equipment."""
        return [
            exercise for exercise in self.exercises.values()
            if equipment.lower() in [e.lower() for e in exercise["equipment"]]
        ]
    
    def get_exercises_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Get all exercises of a specific difficulty level."""
        return [
            exercise for exercise in self.exercises.values()
            if exercise["difficulty"].lower() == difficulty.lower()
        ]
    
    def get_exercise_variations(self, exercise_id: str) -> List[str]:
        """Get variations of a specific exercise."""
        exercise = self.get_exercise(exercise_id)
        return exercise.get("variations", [])
    
    def get_exercises_by_type(self, exercise_type: str) -> List[Dict[str, Any]]:
        """Get all exercises of a specific type (e.g., 'weight_reps', 'bodyweight')."""
        return [
            exercise for exercise in self.exercises.values()
            if exercise["exercise_type"].lower() == exercise_type.lower()
        ]
    
    def get_exercises_by_target_muscle(self, muscle: str) -> List[Dict[str, Any]]:
        """Get all exercises that target a specific muscle."""
        return [
            exercise for exercise in self.exercises.values()
            if muscle.lower() in [m.lower() for m in exercise["target_muscles"]]
        ]
    
    def get_exercises_by_secondary_muscle(self, muscle: str) -> List[Dict[str, Any]]:
        """Get all exercises that work a muscle as a secondary muscle."""
        return [
            exercise for exercise in self.exercises.values()
            if muscle.lower() in [m.lower() for m in exercise["secondary_muscles"]]
        ]
    
    def get_all_body_parts(self) -> List[str]:
        """Get a list of all unique body parts."""
        body_parts = set()
        for exercise in self.exercises.values():
            body_parts.update(exercise["body_parts"])
        return sorted(list(body_parts))
    
    def get_all_equipment(self) -> List[str]:
        """Get a list of all unique equipment."""
        equipment = set()
        for exercise in self.exercises.values():
            equipment.update(exercise["equipment"])
        return sorted(list(equipment))
    
    def get_all_muscles(self) -> List[str]:
        """Get a list of all unique muscles (both target and secondary)."""
        muscles = set()
        for exercise in self.exercises.values():
            muscles.update(exercise["target_muscles"])
            muscles.update(exercise["secondary_muscles"])
        return sorted(list(muscles)) 