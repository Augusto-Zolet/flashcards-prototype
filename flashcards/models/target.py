from pydantic import BaseModel
from .common import BaseEntity, TargetId


class Target(BaseEntity):
    id: TargetId
    target: str
    lang: str
    learned: bool
    date_learned: str | None = None