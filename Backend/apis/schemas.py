from pydantic import BaseModel, Field, field_validator

class PeerReviewResult(BaseModel):
    """
    Defines the structured output format for peer reviews.
    Guarantees that score is a float in range [0.0, 10.0] and critique is a string.
    """
    score: float = Field(..., description="A rating out of 10.0 based on correctness, clarity, completeness, and formatting.")
    critique: str = Field(..., description="Constructive feedback explaining how to improve the draft, or 'None' if perfect.")

    @field_validator('score')
    @classmethod
    def validate_score(cls, val: float) -> float:
        if not (0.0 <= val <= 10.0):
            raise ValueError("Score must be between 0.0 and 10.0 inclusive.")
        return val
