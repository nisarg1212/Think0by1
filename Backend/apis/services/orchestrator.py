import logging
from apis.models import Question, ModelResponse
from apis.agents.gemini_agent import GeminiAgent
from apis.agents.nvidia_agent import NvidiaAgent
from apis.agents.openrouter_agent import OpenRouterAgent
from apis.services.judge import ResponseJudge

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.gemini = GeminiAgent()
        self.nvidia = NvidiaAgent()
        self.openrouter = OpenRouterAgent()
        self.judge = ResponseJudge()

    def run(self, question_id: int):
        """
        Coordinates the round-robin peer-review collaborative flow:
        - Gemini reviews Nvidia
        - Nvidia reviews OpenRouter
        - OpenRouter reviews Gemini
        
        If a model's review score is below 7.0, it is triggered to self-correct.
        Finally, all three responses are synthesized into the final answer.
        """
        try:
            # 1. Fetch Question from DB
            question = Question.objects.get(id=question_id)
            prompt = question.prompt

            # 2. Get initial drafts from the 3 models
            logger.info("Generating initial model drafts...")
            drafts = self._get_initial_drafts(prompt)

            # Create Database records for each model's initial attempt
            db_responses = {}
            for name, draft_text in drafts.items():
                db_responses[name] = ModelResponse.objects.create(
                    question=question,
                    model_name=name,
                    response_text=draft_text
                )

            # 3. Round-Robin Peer Review
            # Assignment: Gemini reviews Nvidia
            logger.info("Gemini reviewing Nvidia...")
            score_nv, critique_nv = self._run_peer_evaluation("nvidia", prompt, drafts["nvidia"])
            db_responses["nvidia"].score = score_nv
            db_responses["nvidia"].critique = critique_nv
            db_responses["nvidia"].save()

            # Assignment: Nvidia reviews OpenRouter
            logger.info("Nvidia reviewing OpenRouter...")
            score_or, critique_or = self._run_peer_evaluation("openrouter", prompt, drafts["openrouter"])
            db_responses["openrouter"].score = score_or
            db_responses["openrouter"].critique = critique_or
            db_responses["openrouter"].save()

            # Assignment: OpenRouter reviews Gemini
            logger.info("OpenRouter reviewing Gemini...")
            score_gem, critique_gem = self._run_peer_evaluation("gemini", prompt, drafts["gemini"])
            db_responses["gemini"].score = score_gem
            db_responses["gemini"].critique = critique_gem
            db_responses["gemini"].save()

            # 4. Correction Loop
            # For each model, check its score. If low (< 7.0), ask it to self-correct using the critique.
            final_outputs = []
            for name, db_response in db_responses.items():
                original_draft = drafts[name]
                score = db_response.score
                critique = db_response.critique

                # If the score is low and the draft wasn't a skipped placeholder, run correction
                if score < 7.0 and "skipped:" not in original_draft.lower() and "failed:" not in original_draft.lower():
                    logger.info(f"{name} failed critique with score {score}. Triggering correction...")
                    corrected_text = self._self_correct(name, prompt, original_draft, critique)
                    db_response.final_answer = corrected_text
                    
                    # Re-evaluate the corrected response
                    new_score, new_critique = self._run_peer_evaluation(name, prompt, corrected_text)
                    db_response.score = new_score
                    db_response.critique = f"POST-CORRECTION CRITIQUE: {new_critique}"
                    db_response.save()
                else:
                    logger.info(f"{name} passed critique (or was skipped) with score {score}.")
                    db_response.final_answer = original_draft
                    db_response.save()

                final_outputs.append(db_response.final_answer)

            # 5. Synthesize the final consolidated answer using Gemini
            logger.info("Synthesizing final combined response...")
            final_answer = self._synthesize_final_answer(prompt, final_outputs)
            
            question.final_answer = final_answer
            question.critique = "Collaborative Round-Robin Peer Review and self-correction cycle completed."
            question.save()
            logger.info("Orchestration completed successfully.")

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            raise e

    def _get_initial_drafts(self, prompt: str) -> dict[str, str]:
        """Queries all 3 agents for their first drafts, catching errors individually."""
        drafts = {}
        
        # 1. Gemini (Always active)
        try:
            drafts['gemini'] = self.gemini.query(prompt)
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            drafts['gemini'] = f"Gemini failed to generate response: {e}"

        # 2. Nvidia Llama (Skip if key is placeholder)
        try:
            if self.nvidia.api_key == "your_key_here" or not self.nvidia.api_key:
                drafts['nvidia'] = "Nvidia Llama query skipped: API key not configured."
            else:
                drafts['nvidia'] = self.nvidia.query(prompt)
        except Exception as e:
            logger.error(f"Nvidia query failed: {e}")
            drafts['nvidia'] = f"Nvidia Llama failed to generate response: {e}"

        # 3. OpenRouter (Skip if key is placeholder)
        try:
            if self.openrouter.api_key == "your_key_here" or not self.openrouter.api_key:
                drafts['openrouter'] = "OpenRouter query skipped: API key not configured."
            else:
                drafts['openrouter'] = self.openrouter.query(prompt)
        except Exception as e:
            logger.error(f"OpenRouter query failed: {e}")
            drafts['openrouter'] = f"OpenRouter failed to generate response: {e}"

        return drafts

    def _run_peer_evaluation(self, subject_model: str, prompt: str, draft_text: str) -> tuple[float, str]:
        """Runs the peer evaluation, falling back to gemini if the designated reviewer is unconfigured."""
        reviewer_agent, reviewer_name = self._get_active_reviewer_for(subject_model)
        
        try:
            return self.judge.peer_evaluate(
                reviewer_agent=reviewer_agent,
                reviewer_name=reviewer_name,
                prompt=prompt,
                draft_text=draft_text
            )
        except Exception as e:
            logger.error(f"Peer evaluation of {subject_model} by {reviewer_name} failed: {e}")
            return 0.0, f"Peer review failed: {e}"

    def _get_active_reviewer_for(self, subject_model: str):
        """
        Determines the reviewer agent based on the subject model (Round-Robin).
        Falls back to Gemini if the designated reviewer is unconfigured.
        """
        if subject_model == 'nvidia':
            # Gemini reviews Nvidia (Gemini is always configured)
            return self.gemini, 'gemini'
            
        elif subject_model == 'openrouter':
            # Nvidia reviews OpenRouter
            if self.nvidia.api_key == "your_key_here" or not self.nvidia.api_key:
                logger.info("Nvidia unconfigured, falling back to Gemini for OpenRouter review.")
                return self.gemini, 'gemini (fallback)'
            return self.nvidia, 'nvidia'
            
        else:
            # OpenRouter reviews Gemini
            if self.openrouter.api_key == "your_key_here" or not self.openrouter.api_key:
                logger.info("OpenRouter unconfigured, falling back to Gemini for Gemini review.")
                return self.gemini, 'gemini (fallback)'
            return self.openrouter, 'openrouter'

    def _self_correct(self, model_name: str, prompt: str, original_answer: str, critique: str) -> str:
        """Asks a specific model to correct its answer based on the peer critique."""
        correction_prompt = f"""
        You previously wrote a draft response but your peer reviewer evaluated it and left a constructive critique.
        
        ORIGINAL PROMPT:
        {prompt}

        YOUR PREVIOUS DRAFT:
        {original_answer}

        PEER CRITIQUE TO ADDRESS:
        {critique}

        Please rewrite your response, fully correcting the issues pointed out in the critique.
        """
        try:
            if model_name == 'gemini':
                return self.gemini.query(correction_prompt)
            elif model_name == 'nvidia':
                # If key is placeholder, do not run query
                if self.nvidia.api_key == "your_key_here" or not self.nvidia.api_key:
                    return original_answer
                return self.nvidia.query(correction_prompt)
            elif model_name == 'openrouter':
                # If key is placeholder, do not run query
                if self.openrouter.api_key == "your_key_here" or not self.openrouter.api_key:
                    return original_answer
                return self.openrouter.query(correction_prompt)
        except Exception as e:
            logger.error(f"Self-correction for {model_name} failed: {e}")
            return f"{original_answer} (Self-correction failed: {e})"
            
        return original_answer

    def _synthesize_final_answer(self, prompt: str, answers: list[str]) -> str:
        """Asks Gemini to blend all three models' final corrected outputs."""
        blend_prompt = f"""
        You are a master editor. Combine the strengths of three different model answers into a single, cohesive, high-quality final response.

        ORIGINAL USER PROMPT:
        {prompt}

        MODEL ANSWER 1:
        {answers[0]}

        MODEL ANSWER 2:
        {answers[1]}

        MODEL ANSWER 3:
        {answers[2]}

        Produce a unified, complete response. Avoid redundancies and keep formatting clear.
        """
        try:
            return self.gemini.query(blend_prompt)
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            # Return the first non-error answer as fallback
            for ans in answers:
                if "failed" not in ans.lower() and "skipped" not in ans.lower():
                    return ans
            return answers[0]
