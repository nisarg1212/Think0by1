import os
import sys

# Add the current directory to python path so it can resolve imports like 'apis.agents.gemini_agent'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to load environment variables from .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env using python-dotenv.")
except ImportError:
    print("python-dotenv is not installed. Reading system environment variables directly.")

from apis.agents.gemini_agent import GeminiAgent

def test_agent():
    print("Initializing GeminiAgent...")
    try:
        agent = GeminiAgent()
        prompt = "Hello! Tell me in one sentence why learning programming step-by-step is a good idea."
        print(f"Querying agent with prompt: '{prompt}'")
        
        response = agent.query(prompt)
        print("\n--- Agent Response ---")
        print(response)
        print("----------------------")
        print("\nSuccess! The Gemini connection is working properly.")
    except ValueError as ve:
        print(f"\n[Configuration Error]: {ve}")
        print("Please make sure you have set the GEMINI_API_KEY environment variable.")
        print("You can create a '.env' file in the 'Backend/' directory with:")
        print("GEMINI_API_KEY=your_actual_api_key_here")
    except Exception as e:
        print(f"\n[Execution Error]: An error occurred while communicating with the API:")
        print(e)

if __name__ == "__main__":
    test_agent()
