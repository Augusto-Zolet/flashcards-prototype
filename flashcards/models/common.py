from datetime import datetime, timezone
from typing import NewType
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# Common types
IsoTimestamp = NewType("IsoTimestamp", str)
CardId = NewType("CardId", UUID)
ExampleId = NewType("ExampleId", UUID)
TargetId = NewType("TargetId", UUID)


class BaseEntity(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="The unique identifier for the entity.",
    )
    date_created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The date and time the entity was created.",
    )