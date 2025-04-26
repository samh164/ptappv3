from services.ai_service_alt import AIService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_service():
    print("Testing AI service implementation...")
    
    # Create test user data
    test_user = {
        'name': 'Test User',
        'goal': 'Weight Loss',
        'gender': 'Male',
        'age': 30,
        'weight': 80.0,
        'height': 175.0,
        'activity_level': 'Moderately Active',
        'training_style': 'HIIT',
        'diet_type': 'Standard',
        'allergies': 'None',
        'fav_foods': 'Chicken, Rice, Vegetables'
    }
    
    # Initialize the service
    print("Initializing AIService...")
    service = AIService()
    
    # Test simple completion to check if API is working
    print("Testing API connection with a simple request...")
    try:
        result = service._call_openai_api("chat/completions", {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello! Please respond with just 'API is working' to test the connection."}],
            "max_tokens": 20
        })
        print(f"API Response: {result['choices'][0]['message']['content']}")
        print("API connection test successful!")
        
        # Test the main method with test user
        print("\nTesting generate_first_plan with test user data...")
        print("NOTE: This will make an API call to generate a full fitness plan.")
        print("Press Ctrl+C to skip this test, or wait for it to complete...")
        
        import time
        time.sleep(3)  # Give user time to cancel if needed
        
        plan = service.generate_first_plan(test_user)
        if plan:
            print("Successfully generated fitness plan!")
            print(f"Plan snippet (first 100 chars): {plan[:100]}...")
        else:
            print("Failed to generate a valid plan - validation issues detected.")
            
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    except Exception as e:
        print(f"Error during testing: {type(e).__name__}: {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_ai_service() 