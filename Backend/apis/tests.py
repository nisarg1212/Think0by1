import os
from django.test import TestCase
from unittest.mock import patch
from asgiref.sync import async_to_sync
from apis.models import Question, ModelResponse
from apis.engine.graph import OrchestrationGraph

class StateGraphEngineTest(TestCase):
    def setUp(self):
        # Set mock environment keys so agent constructors don't raise ValueError
        # and execution nodes don't skip querying them
        os.environ["GEMINI_API_KEY"] = "mock_gemini_key"
        os.environ["NVIDIA_API_KEY"] = "mock_nvidia_key"
        os.environ["OPENROUTER_API_KEY"] = "mock_openrouter_key"

    @patch('apis.agents.gemini_agent.GeminiAgent.query')
    @patch('apis.agents.nvidia_agent.NvidiaAgent.query')
    @patch('apis.agents.openrouter_agent.OpenRouterAgent.query')
    def test_full_graph_execution(self, mock_or, mock_nv, mock_gem):
        """
        Tests the entire StateGraph Orchestration Engine flow end-to-end.
        Mocks LLM API queries and verifies State transitions, Pydantic schemas,
        Prompt management, and SQLite DB persistence via callbacks.
        """
        # Define mock behavior for prompt queries
        def mock_query(prompt, **kwargs):
            if "JSON schema" in prompt or "peer reviewer" in prompt:
                # Returns valid JSON that matches the Pydantic schema
                return '{"score": 8.5, "critique": "Draft looks good, could optimize database queries."}'
            elif "master editor" in prompt or "Combine the strengths" in prompt:
                return "This is the final blended consensus answer."
            else:
                return "This is a mock draft response."

        mock_gem.side_effect = mock_query
        mock_nv.side_effect = mock_query
        mock_or.side_effect = mock_query

        # 1. Create a Question in the Database
        question = Question.objects.create(prompt="How to optimize SQLite database in Django?")

        # 2. Run the Orchestration Graph (Uses async_to_sync because django test is sync)
        graph = OrchestrationGraph()
        async_to_sync(graph.run)(question.id)

        # 3. Assertions
        question.refresh_from_db()
        
        # Verify synthesis node ran and saved blended answer
        self.assertEqual(question.final_answer, "This is the final blended consensus answer.")
        self.assertIn("StateGraph Orchestration", question.critique)

        # Verify ModelResponse records exist and are complete
        responses = question.responses.all()
        self.assertEqual(responses.count(), 3)
        
        for resp in responses:
            # Verify draft node saved initial answers
            self.assertIn("mock draft response", resp.response_text)
            
            # Verify peer review score and critique were parsed and saved correctly
            # (The test score is >= 7.0, so the correction loop shouldn't trigger, preserving the draft as final_answer)
            self.assertEqual(resp.score, 8.5)
            self.assertEqual(resp.critique, "Draft looks good, could optimize database queries.")
            self.assertEqual(resp.final_answer, resp.response_text)