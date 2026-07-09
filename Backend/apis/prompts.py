from typing import Dict

# Persona definitions mapping role names to system instructions
PERSONAS: Dict[str, str] = {
    "innovator": (
        "You are an Optimistic Innovator. When responding, focus on creative solutions, "
        "future-proof design patterns, novel features, and out-of-the-box thinking."
    ),
    "auditor": (
        "You are a Strict Security & Robustness Auditor. When responding, focus on edge cases, "
        "security vulnerabilities, error handling, input validation, and code constraints."
    ),
    "optimizer": (
        "You are a Performance & Efficiency Optimizer. When responding, focus on code execution speed, "
        "memory allocation, database query costs, simplicity, scalability, and resource limits."
    ),
    "general": (
        "You are a helpful AI assistant. Provide a clear, correct, and comprehensive response."
    )
}

class PromptManager:
    """
    Manages prompting formats, injecting agent personas, and formatting debater prompts.
    Decouples raw prompt texts from agent execution nodes.
    """
    @staticmethod
    def get_persona_prompt(persona_name: str, original_prompt: str) -> str:
        """Prepends a persona system prompt to the user prompt."""
        system_instruction = PERSONAS.get(persona_name, PERSONAS["general"])
        return (
            f"SYSTEM INSTRUCTION: {system_instruction}\n\n"
            f"Please write a response to the following prompt adhering to your role:\n"
            f"USER PROMPT:\n{original_prompt}"
        )

    @staticmethod
    def get_correction_prompt(original_prompt: str, original_draft: str, critique: str) -> str:
        """Formats the prompt for the self-correction loop."""
        return (
            f"You previously wrote a draft response, but your peer reviewer evaluated it and left a constructive critique.\n\n"
            f"ORIGINAL PROMPT:\n{original_prompt}\n\n"
            f"YOUR PREVIOUS DRAFT:\n{original_draft}\n\n"
            f"PEER CRITIQUE TO ADDRESS:\n{critique}\n\n"
            f"Please rewrite your response, fully correcting the issues pointed out in the critique."
        )

    @staticmethod
    def get_synthesis_prompt(original_prompt: str, answers: list[str]) -> str:
        """Formats the prompt for blending multiple drafts."""
        return (
            f"You are a master editor. Combine the strengths of three different model answers into a single, cohesive, high-quality final response.\n\n"
            f"ORIGINAL USER PROMPT:\n{original_prompt}\n\n"
            f"MODEL ANSWER 1:\n{answers[0]}\n\n"
            f"MODEL ANSWER 2:\n{answers[1]}\n\n"
            f"MODEL ANSWER 3:\n{answers[2]}\n\n"
            f"Produce a unified, complete response. Avoid redundancies and keep formatting clear."
        )
