import asyncio
import logging
from typing import Dict
from apis.engine.state import OrchestrationState, AgentState
from apis.engine.context import ExecutionContext
from apis.prompts import PromptManager

logger = logging.getLogger(__name__)

async def draft_node(state: OrchestrationState, context: ExecutionContext) -> OrchestrationState:
    """Generates initial drafts concurrently from all configured agents using personas."""
    logger.info("Executing DraftNode...")
    
    # Map agent names to dynamic roles defined in Prompts registry
    agent_personas = context.config.get("agent_personas", {
        'gemini': 'innovator',
        'nvidia': 'auditor',
        'openrouter': 'optimizer'
    })

    async def fetch_draft(name: str, agent):
        try:
            # Skip if API key is not configured
            if hasattr(agent, 'api_key') and (agent.api_key == "your_key_here" or not agent.api_key):
                return name, f"{name.capitalize()} query skipped: API key not configured."
            
            persona = agent_personas.get(name, 'general')
            prompt = PromptManager.get_persona_prompt(persona, state.prompt)
            draft = await agent.async_query(prompt)
            return name, draft
        except Exception as e:
            logger.error(f"{name} failed to generate draft: {e}")
            return name, f"{name.capitalize()} failed to generate response: {e}"

    tasks = [fetch_draft(name, agent) for name, agent in context.agents.items()]
    results = await asyncio.gather(*tasks)
    
    new_agent_states = {}
    for name, draft in results:
        new_agent_states[name] = AgentState(draft=draft)
        
    return state.update(agent_states=new_agent_states)


async def peer_review_node(state: OrchestrationState, context: ExecutionContext) -> OrchestrationState:
    """Executes round-robin peer reviews concurrently."""
    logger.info("Executing PeerReviewNode...")
    
    # Define Round-Robin Assignments: subject -> reviewer
    assignments = {
        'nvidia': 'gemini',
        'openrouter': 'nvidia',
        'gemini': 'openrouter'
    }

    async def fetch_review(subject_name: str, subject_draft: str):
        reviewer_name = assignments.get(subject_name, 'gemini')
        reviewer_agent = context.agents.get(reviewer_name)
        
        # Fallback to Gemini if the assigned reviewer is unconfigured
        if not reviewer_agent or (hasattr(reviewer_agent, 'api_key') and (reviewer_agent.api_key == "your_key_here" or not reviewer_agent.api_key)):
            logger.info(f"{reviewer_name} unconfigured, falling back to Gemini for {subject_name} review.")
            reviewer_name = 'gemini'
            reviewer_agent = context.agents['gemini']

        try:
            # Use asyncio.to_thread since ResponseJudge is currently synchronous
            score, critique = await asyncio.to_thread(
                context.judge.peer_evaluate, reviewer_agent, reviewer_name, state.prompt, subject_draft
            )
            return subject_name, score, critique
        except Exception as e:
            logger.error(f"Peer evaluation of {subject_name} failed: {e}")
            return subject_name, 0.0, f"Peer review failed: {e}"

    tasks = []
    for subject_name, agent_state in state.agent_states.items():
        # Only review if the draft wasn't skipped or failed
        draft = agent_state.draft or ""
        if "skipped:" not in draft.lower() and "failed:" not in draft.lower():
            tasks.append(fetch_review(subject_name, draft))

    results = await asyncio.gather(*tasks)
    
    updated_state = state
    for subject_name, score, critique in results:
        updated_state = updated_state.update_agent_state(subject_name, score=score, critique=critique)
        
    return updated_state


async def correction_node(state: OrchestrationState, context: ExecutionContext) -> OrchestrationState:
    """Runs self-correction for models that scored below the threshold."""
    logger.info("Executing CorrectionNode...")
    
    score_threshold = context.config.get("score_threshold", 7.0)

    async def fetch_correction(name: str, agent, original_draft: str, critique: str):
        prompt = PromptManager.get_correction_prompt(state.prompt, original_draft, critique)
        try:
            corrected = await agent.async_query(prompt)
            # Re-evaluate post-correction
            new_score, new_critique = await asyncio.to_thread(
                context.judge.peer_evaluate, agent, name, state.prompt, corrected
            )
            return name, corrected, new_score, f"POST-CORRECTION CRITIQUE: {new_critique}"
        except Exception as e:
            logger.error(f"Correction for {name} failed: {e}")
            return name, f"{original_draft} (Self-correction failed: {e})", 0.0, "Correction failed."

    tasks = []
    for name, agent_state in state.agent_states.items():
        draft = agent_state.draft or ""
        score = agent_state.score or 0.0
        critique = agent_state.critique or ""
        
        if score < score_threshold and "skipped:" not in draft.lower() and "failed:" not in draft.lower():
            agent = context.agents.get(name)
            if agent and not (hasattr(agent, 'api_key') and (agent.api_key == "your_key_here" or not agent.api_key)):
                tasks.append(fetch_correction(name, agent, draft, critique))

    updated_state = state
    # Handle the defaults for non-correcting models first
    for name, agent_state in state.agent_states.items():
        if agent_state.score >= score_threshold or "skipped:" in (agent_state.draft or "").lower() or "failed:" in (agent_state.draft or "").lower():
            updated_state = updated_state.update_agent_state(name, final_answer=agent_state.draft)

    if tasks:
        results = await asyncio.gather(*tasks)
        for name, corrected_ans, new_score, new_critique in results:
            updated_state = updated_state.update_agent_state(
                name,
                corrected_answer=corrected_ans,
                final_answer=corrected_ans,
                score=new_score,
                critique=new_critique
            )
            
    return updated_state


async def synthesis_node(state: OrchestrationState, context: ExecutionContext) -> OrchestrationState:
    """Synthesizes the final answers into a single cohesive response."""
    logger.info("Executing SynthesisNode...")
    
    master_agent_name = context.config.get("master_agent", "gemini")
    master_agent = context.agents.get(master_agent_name)

    answers = []
    for name in ['gemini', 'nvidia', 'openrouter']:
        agent_state = state.agent_states.get(name)
        if agent_state:
            ans = agent_state.final_answer or agent_state.draft or "No answer available."
            answers.append(ans)
        else:
            answers.append("No answer available.")

    prompt = PromptManager.get_synthesis_prompt(state.prompt, answers)
    
    try:
        blended = await master_agent.async_query(prompt)
        return state.update(blended_result=blended)
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        # Fallback to the first non-error answer
        fallback = next((ans for ans in answers if "failed" not in ans.lower() and "skipped" not in ans.lower()), answers[0])
        return state.update(blended_result=fallback)
