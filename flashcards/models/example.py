from typing import Literal, Optional

from pydantic import BaseModel

from .common import BaseEntity, ExampleId, TargetId


class Example(BaseEntity):
    id: ExampleId
    target_id: TargetId
    text: str
    example_target: str
    target_start: int
    target_end: int
    example_type: Literal["contextual"]
    source: Literal["readlang", "ai", "human"]
    parent_example_id: Optional[str] = None
    context_hint: Optional[str] = None
    contextual_synonyms: list[str]
    translations: dict[str, list[str]]
    notes: Optional[str] = None
    raw_translation: Optional[str] = None
