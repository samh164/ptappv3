import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Print debug information
print(f"Python version: {sys.version}")
print(f"OpenAI module path: {getattr(OpenAI, '__file__', 'Unknown')}")

# Attempt to create client without any extra configuration
try:
    print("Attempting to create OpenAI client...")
    client = OpenAI(api_key=api_key)
    print("Client created successfully!")
    
    # Test a simple API call
    print("Testing API with a simple completion...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}],
        max_tokens=10
    )
    print(f"Response received: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"ERROR: {e.__class__.__name__}: {str(e)}")
    print("Traceback:")
    import traceback
    traceback.print_exc()

print("\nEnvironment variables that might affect proxy settings:")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'PROXY', 'http_proxy', 'https_proxy', 'proxy']
for var in proxy_vars:
    if var in os.environ:
        print(f"{var}={os.environ[var]}")
    else:
        print(f"{var} not set")

print("\nDone.") 