import json
import logging
from apis.schemas import PeerReviewResult

logger = logging.getLogger(__name__)

class ResponseJudge:
    def peer_evaluate(self, reviewer_agent, reviewer_name: str, prompt: str, draft_text: str) -> tuple[float, str]:
        """
        Asks a specific reviewer agent to evaluate another model's draft.
        
        Args:
            reviewer_agent: The agent class instance executing the review (GeminiAgent, NvidiaAgent, etc.)
            reviewer_name (str): Name of the reviewer (e.g. 'gemini', 'nvidia', 'openrouter')
            prompt (str): Original user prompt.
            draft_text (str): The draft response to evaluate.
        """
        judge_prompt = f"""
        You are a meticulous peer reviewer. Your task is to evaluate another AI model's draft response to a user's prompt.

        USER PROMPT:
        {prompt}

        DRAFT RESPONSE TO EVALUATE:
        {draft_text}

        Rate the response out of 10.0 based on correctness, clarity, completeness, and formatting.
        If there are any issues, write a constructive critique explaining how to improve it.
        If it is perfect, score it 10.0 and write "None" for critique.

        You MUST respond strictly in the following JSON schema:
        {{
            "score": <float between 0.0 and 10.0>,
            "critique": "<constructive feedback to help the other model improve, or 'None'>"
        }}
        """

        try:
            # Query the reviewer agent using its generic .query() method
            response_string = reviewer_agent.query(judge_prompt)
            
            # Parse and validate with Pydantic
            return self._parse_json_response(response_string)
            
        except Exception as e:
            logger.error(f"Peer review by {reviewer_name} failed: {e}")
            return 0.0, f"Peer review by {reviewer_name} failed: {str(e)}"

    def _parse_json_response(self, text: str) -> tuple[float, str]:
        """
        Cleans the response text, parses it as JSON, and validates it using Pydantic.
        """
        cleaned_text = text.strip()
        
        # Clean markdown code block markers if present
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_text:
            cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
            
        try:
            # Pydantic validation guarantees correct types and constraints
            result = PeerReviewResult.model_validate_json(cleaned_text)
            return result.score, result.critique
        except Exception as e:
            logger.warning(f"Structured JSON validation failed. Attempting lenient fallback. Error: {e}")
            
            # Lenient fallback in case of schema validation warnings (e.g. float as string)
            try:
                data = json.loads(cleaned_text)
                # Coerce score to float, default to 0.0 if not found
                score = float(data.get("score", 0.0))
                # Bound check the fallback
                score = max(0.0, min(10.0, score))
                critique = str(data.get("critique", "No critique provided."))
                return score, critique
            except Exception as inner_e:
                logger.error(f"Lenient fallback also failed. Text was: {text}. Error: {inner_e}")
                return 0.0, f"Failed to parse peer review JSON: {text}"
