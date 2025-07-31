from typing import Literal, Optional

from pydantic import BaseModel, Field

from .common import BaseEntity, CardId, ExampleId, IsoTimestamp


class ReviewStats(BaseModel):
    last_seen: Optional[IsoTimestamp] = Field(
        default=None,
        description="The last time the card was reviewed.",
        examples=["2023-07-28T10:30:00Z"],
    )
    next_due: Optional[IsoTimestamp] = Field(
        default=None,
        description="The next time the card is due for review.",
        examples=["2023-07-29T10:30:00Z"],
    )
    interval: float = Field(
        default=0.0,
        description="The interval in days between reviews.",
        examples=[1.5],
    )
    easiness: float = Field(
        default=2.5,
        description="The easiness factor of the card.",
        examples=[2.5],
    )
    successes_in_row: int = Field(
        default=0,
        description="The number of times the card has been answered correctly in a row.",
        examples=[3],
    )
    mastered: bool = Field(
        default=False,
        description="Whether the card has been mastered.",
        examples=[True],
    )


class Card(BaseEntity):
    id: CardId = Field(..., description="The unique identifier for the card.")
    example_id: ExampleId = Field(
        ...,
        description="The identifier of the example this card belongs to.",
    )
    hints: list[str] = Field(
        ...,
        description="A list of hints for the card.",
        examples=[["hint 1", "hint 2"]],
    )
    review_stats: ReviewStats = Field(
        ...,
        description="The review statistics for the card.",
    )


class MeaningMCQCard(Card):
    card_type: Literal["MeaningMCQ"] = "MeaningMCQ"


class WordMCQCard(Card):
    card_type: Literal["WordMCQ"] = "WordMCQ"


class TypingCard(Card):
    card_type: Literal["Typing"] = "Typing"



