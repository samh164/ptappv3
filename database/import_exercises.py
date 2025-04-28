"""
Script to import exercise data from multiple sources and create a unified database.
"""

import logging
import os
from exercise_importer import ExerciseImporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URLs for exercise data sources
SOURCES = {
    "free_exercise_db": "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json",
    "exercemus": "https://raw.githubusercontent.com/exercemus/exercises/main/exercises.json"
}

def main():
    """Main function to import and merge exercise data."""
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(output_dir, "exercise_db.json")
        
        # Initialize importer
        importer = ExerciseImporter(output_file=output_file)
        
        # Fetch exercises from all sources
        exercise_lists = []
        for source_name, url in SOURCES.items():
            logger.info(f"Fetching exercises from {source_name}")
            exercises = importer.fetch_dataset(url)
            if exercises:
                logger.info(f"Successfully fetched {len(exercises)} exercises from {source_name}")
                exercise_lists.append(exercises)
            else:
                logger.warning(f"No exercises fetched from {source_name}")
        
        if not exercise_lists:
            logger.error("No exercises fetched from any source")
            return
        
        # Merge exercises
        logger.info("Merging exercises from all sources")
        merged_exercises = importer.merge_exercises(exercise_lists)
        logger.info(f"Successfully merged {len(merged_exercises)} unique exercises")
        
        # Save to file
        importer.save_to_file(merged_exercises)
        logger.info("Exercise import completed successfully")
        
    except Exception as e:
        logger.error(f"Error during exercise import: {str(e)}")
        raise

if __name__ == "__main__":
    main() 