from typing import Literal, Optional

from pydantic import Field

from .common import BaseEntity, ExampleId, TargetId


class Example(BaseEntity):
    id: ExampleId = Field(
        ...,
        description="The unique identifier for the example.",
    )
    target_id: TargetId = Field(
        ...,
        description="The identifier of the target this example belongs to.",
    )
    text: str = Field(
        ...,
        description="The text of the example sentence.",
        examples=["Peter has [[taken up]] his English with great reluctance."],
    )
    example_target: str = Field(
        ...,
        description="The target word or phrase in the example.",
        examples=["taken up"],
    )
    target_start: int = Field(
        ...,
        description="The starting index of the target in the text.",
        examples=[10],
    )
    target_end: int = Field(
        ...,
        description="The ending index of the target in the text.",
        examples=[18],
    )
    example_type: Literal["contextual"] = Field(
        ...,
        description="The type of the example.",
        examples=["contextual"],
    )
    source: Literal["readlang", "ai", "human"] = Field(
        ...,
        description="The source of the example.",
        examples=["readlang"],
    )
    parent_example_id: Optional[str] = Field(
        default=None,
        description="The identifier of the parent example.",
    )
    context_hint: Optional[str] = Field(
        default=None,
        description="A hint for the context of the example.",
        examples=["To start a new hobby"],
    )
    contextual_synonyms: list[str] = Field(
        ...,
        description="A list of contextual synonyms for the target.",
        examples=[["start", "begin"]],
    )
    translations: dict[str, list[str]] = Field(
        ...,
        description="A dictionary of translations for the target.",
        examples=[{"pt-BR": ["assumido"]}],
    )
    notes: Optional[str] = Field(
        default=None,
        description="Notes about the example.",
        examples=["This is a note."],
    )
    raw_translation: Optional[str] = Field(
        default=None,
        description="The raw translation of the example.",
        examples=["assumido"],
    )
