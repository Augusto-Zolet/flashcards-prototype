from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from .common import BaseEntity, CardId, ExampleId, IsoTimestamp


class ReviewStats(BaseModel):
    last_seen: Optional[IsoTimestamp] = None
    next_due: Optional[IsoTimestamp] = None
    interval: float = 0.0
    easiness: float = 2.5
    successes_in_row: int = 0
    mastered: bool = False


class Card(BaseEntity):
    id: CardId
    example_id: ExampleId
    hints: list[str]
    review_stats: ReviewStats


class MeaningMCQCard(Card):
    card_type: Literal["MeaningMCQ"] = "MeaningMCQ"


class WordMCQCard(Card):
    card_type: Literal["WordMCQ"] = "WordMCQ"


class TypingCard(Card):
    card_type: Literal["Typing"] = "Typing"



