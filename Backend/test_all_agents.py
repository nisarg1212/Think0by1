import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env\n")
except ImportError:
    print("python-dotenv not installed. Reading environment directly.\n")

def test_gemini():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_key_here":
        print("[GEMINI] Status: Skipped (Key not set in .env)")
        return
    
    print("[GEMINI] Initializing GeminiAgent...")
    try:
        from apis.agents.gemini_agent import GeminiAgent
        agent = GeminiAgent()
        prompt = "Explain in one sentence what an 'API Router' does."
        print(f"[GEMINI] Prompt: '{prompt}'")
        res = agent.query(prompt)
        print(f"[GEMINI] Response: {res.strip()}\n")
    except Exception as e:
        print(f"[GEMINI] Error: {e}\n")

def test_nvidia():
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    if not nvidia_key or nvidia_key == "your_key_here":
        print("[NVIDIA] Status: Skipped (Key not set or still set to 'your_key_here')")
        print("  -> Get an API key from: https://build.nvidia.com/")
        print("  -> Set it in .env under NVIDIA_API_KEY\n")
        return
    
    print("[NVIDIA] Initializing NvidiaAgent...")
    try:
        # Check if openai package is installed
        import openai
    except ImportError:
        print("[NVIDIA] Error: The 'openai' package is required. Run 'pip install openai'\n")
        return

    try:
        from apis.agents.nvidia_agent import NvidiaAgent
        agent = NvidiaAgent()
        # Using a default model. Llama 3 70b is standard.
        prompt = "Explain in one sentence what a 'Model Orchestrator' is."
        print(f"[NVIDIA] Prompt: '{prompt}'")
        res = agent.query(prompt)
        print(f"[NVIDIA] Response: {res.strip()}\n")
    except Exception as e:
        print(f"[NVIDIA] Error: {e}\n")

def test_openrouter():
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key or openrouter_key == "your_key_here":
        print("[OPENROUTER] Status: Skipped (Key not set or still set to 'your_key_here')")
        print("  -> Get an API key from: https://openrouter.ai/")
        print("  -> Set it in .env under OPENROUTER_API_KEY\n")
        return
    
    print("[OPENROUTER] Initializing OpenRouterAgent...")
    try:
        import openai
    except ImportError:
        print("[OPENROUTER] Error: The 'openai' package is required. Run 'pip install openai'\n")
        return

    try:
        from apis.agents.openrouter_agent import OpenRouterAgent
        agent = OpenRouterAgent()
        prompt = "Explain in one sentence what a 'Response Judge' does."
        print(f"[OPENROUTER] Prompt: '{prompt}'")
        res = agent.query(prompt)
        print(f"[OPENROUTER] Response: {res.strip()}\n")
    except Exception as e:
        print(f"[OPENROUTER] Error: {e}\n")


if __name__ == "__main__":
    print("=== Testing All Configured Agents ===")
    test_gemini()
    test_nvidia()
    test_openrouter()
    print("=====================================")
