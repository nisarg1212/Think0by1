class ModelRouter:
    
    def get_available_model(self):

        if open_router_has_quoata():
            return OpenRouterAgent()

        if nvidia_agent_has_quoata():
            return NVIDIAAgent()
        
        return GeminiAgent()