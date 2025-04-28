"""
Module for importing and merging exercise data from various sources.
"""

import json
import logging
import os
from typing import List, Dict, Any
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class ExerciseImporter:
    """Class to handle importing and merging exercise data from various sources."""
    
    def __init__(self, output_file: str = "exercise_db.json"):
        """
        Initialize the ExerciseImporter.
        
        Args:
            output_file (str): Path to save the merged exercise database.
        """
        self.output_file = output_file
        
    def fetch_dataset(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch exercise data from a given URL.
        
        Args:
            url (str): URL to fetch the exercise data from.
            
        Returns:
            List[Dict[str, Any]]: List of exercise dictionaries.
            
        Raises:
            RequestException: If there's an error fetching the data.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Error fetching data from {url}: {str(e)}")
            return []
            
    def standardize_exercise(self, exercise: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize exercise data to a common format.
        
        Args:
            exercise (Dict[str, Any]): Exercise data to standardize.
            
        Returns:
            Dict[str, Any]: Standardized exercise data.
        """
        # Create a standardized exercise object with required fields
        standardized = {
            "name": exercise.get("name", "").strip(),
            "description": exercise.get("description", "").strip(),
            "type": exercise.get("type", "weight_reps"),  # Default to weight_reps
            "body_part": exercise.get("bodyPart", "").strip().lower(),
            "equipment": exercise.get("equipment", "").strip().lower(),
            "target_muscle": exercise.get("target", "").strip().lower(),
            "secondary_muscles": [m.strip().lower() for m in exercise.get("secondaryMuscles", [])],
            "instructions": exercise.get("instructions", []),
            "difficulty": exercise.get("difficulty", "intermediate"),
            "source": exercise.get("source", "unknown")
        }
        
        # Only include exercises with required fields
        if not all([standardized["name"], standardized["body_part"], standardized["target_muscle"]]):
            return None
            
        return standardized
        
    def merge_exercises(self, exercise_lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Merge multiple lists of exercises, removing duplicates and standardizing format.
        
        Args:
            exercise_lists (List[List[Dict[str, Any]]]): Lists of exercises to merge.
            
        Returns:
            List[Dict[str, Any]]: Merged and deduplicated list of exercises.
        """
        merged = {}
        
        for exercises in exercise_lists:
            for exercise in exercises:
                standardized = self.standardize_exercise(exercise)
                if standardized:
                    # Use exercise name as key for deduplication
                    key = standardized["name"].lower()
                    if key not in merged:
                        merged[key] = standardized
                    else:
                        # If exercise exists, update with more complete data
                        existing = merged[key]
                        if len(str(standardized["description"])) > len(str(existing["description"])):
                            merged[key] = standardized
                            
        return list(merged.values())
        
    def save_to_file(self, exercises: List[Dict[str, Any]]) -> None:
        """
        Save the merged exercise database to a JSON file.
        
        Args:
            exercises (List[Dict[str, Any]]): List of exercises to save.
        """
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(exercises, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved {len(exercises)} exercises to {self.output_file}")
        except IOError as e:
            logger.error(f"Error saving exercises to file: {str(e)}")
            raise

def main():
    logging.basicConfig(level=logging.INFO)
    importer = ExerciseImporter()
    exercises = importer.merge_exercises()
    importer.save_to_file(exercises)

if __name__ == "__main__":
    main() 