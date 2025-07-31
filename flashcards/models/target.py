from datetime import date
from typing import Optional

from pydantic import Field

from .common import BaseEntity, TargetId


class Target(BaseEntity):
    id: TargetId = Field(
        ...,
        description="The unique identifier for the target.",
    )
    target: str = Field(
        ...,
        description="The target word or phrase.",
        examples=["taken up"],
    )
    lang: str = Field(
        ...,
        description="The language of the target.",
        examples=["en"],
    )
    learned: bool = Field(
        default=False,
        description="Whether the target has been learned.",
        examples=[True],
    )
    date_learned: Optional[date] = Field(
        default=None,
        description="The date the target was learned.",
        examples=["2023-07-28"],
    )
