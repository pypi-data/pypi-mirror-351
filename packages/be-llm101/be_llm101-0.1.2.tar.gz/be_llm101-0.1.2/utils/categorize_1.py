from pydantic import BaseModel, Field
from typing import Literal


class Categorize_bound(BaseModel):
    """Categorization of IT-questionaire feedback."""

    categories: Literal["Cyber security", "IT training", "IT support", "Quality"] = (
        Field(description="Categorize the feedback into the most fitting category.")
    )


class Categorize_think(BaseModel):
    """Categorization of IT-questionaire feedback."""

    cot: str = Field(
        description="Think about and explain why this category is the most fitting one and why you chose it."
    )
    categories: Literal[
        "Cyber secyrity", "IT training", "IT support", "Technology quality"
    ] = Field(description="Categorize the feedback into the most fitting category.")


"""
class Categorize(BaseModel):
    "Categorization of news article."
    #Thoughts: Forklar tankegangen din.
    cat_1: str = Field(description="The best fitting genral category")
    cat_2: str = Field(description="The second to best fitting general category")
    rating: Optional[int] = Field(
        description="Your certainty of the corectness of the best category on a scale from 1-10"
    )


class Categorize_bound(BaseModel):
    "Categorization of news article into a predetermined set of categories."

    category: int = Field(
        description="The number corresponding to the best fitting category."
    )
    certainty: float = Field(
        description="Certainty of correctness in categorizing (0-1 scale)."
    )

"""


class Categorize(BaseModel):
    "Enrichment of dataset to make it more human"

    # Thoughts: Forklar tankegangen din.
    cat_1: str = Field(
        description="Return the enriched dataset in a comma separated format like the format of the input dataset"
    )
