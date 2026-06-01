import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from apis.agents.gemini_agent import GeminiAgent
from apis.agents.nvidia_agent import NvidiaAgent
from apis.agents.openrouter_agent import OpenRouterAgent

@method_decorator(csrf_exempt, name='dispatch')
class AgentQueryView(View):
    """
    A Django View that accepts a POST request containing:
    {
        "agent": "gemini" | "nvidia" | "openrouter",
        "prompt": "your prompt string"
    }
    Queries the respective agent and returns the text response as JSON.
    """
    def post(self, request):
        try:
            # Parse the incoming JSON body
            data = json.loads(request.body)
            agent_name = data.get('agent', 'gemini').lower()
            prompt = data.get('prompt')

            if not prompt:
                return JsonResponse({'error': 'Missing prompt parameter'}, status=400)

            # Initialize the selected agent
            if agent_name == 'gemini':
                agent = GeminiAgent()
            elif agent_name == 'nvidia':
                agent = NvidiaAgent()
            elif agent_name == 'openrouter':
                agent = OpenRouterAgent()
            else:
                return JsonResponse({'error': f"Unknown agent: '{agent_name}'. Supported agents are: gemini, nvidia, openrouter."}, status=400)

            # Query the agent
            response_text = agent.query(prompt)

            # Return the response as JSON
            return JsonResponse({
                'status': 'success',
                'agent': agent_name,
                'response': response_text
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
