import json

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
            
            # Parse and return score and critique
            return self._parse_json_response(response_string)
            
        except Exception as e:
            return 0.0, f"Peer review by {reviewer_name} failed: {str(e)}"

    def _parse_json_response(self, text: str) -> tuple[float, str]:
        """
        Helper method to clean and parse JSON from LLM outputs,
        handling cases where LLMs include markdown formatting (like ```json).
        """
        cleaned_text = text.strip()
        
        # Strip markdown json block delimiters if present
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_text:
            cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
            
        try:
            data = json.loads(cleaned_text)
            score = float(data.get("score", 0.0))
            critique = data.get("critique", "No critique provided.")
            return score, critique
        except Exception as e:
            return 0.0, f"Could not parse peer review JSON: {text}"
