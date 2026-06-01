import requests
import json

def test_api_endpoint(agent_name, prompt):
    url = "http://127.0.0.1:8000/api/query/"
    payload = {
        "agent": agent_name,
        "prompt": prompt
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n--- Testing API Endpoint with {agent_name.upper()} ---")
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error Response text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n[Connection Error]: Could not connect to the Django server.")
        print("Please make sure your Django development server is running on http://127.0.0.1:8000/")
        print("You can run it in another terminal window using:")
        print("  cd Backend")
        print("  python manage.py runserver")

if __name__ == "__main__":
    # Test each of our configured agents via our new REST API endpoint
    print("Testing the Django REST API endpoint...")
    test_api_endpoint("gemini", "Summarize in 5 words why REST APIs are useful.")
    test_api_endpoint("nvidia", "Summarize in 5 words what machine learning does.")
    test_api_endpoint("openrouter", "Summarize in 5 words what the internet is.")
