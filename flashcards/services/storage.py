import json
from pathlib import Path

from flashcards.models import (Card, Example, MeaningMCQCard, Target,
                               TypingCard, WordMCQCard)

class JsonDataStorage:

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def _load_data(self) -> dict:
        if not self._file_path.exists():
            return {"targets": [], "examples": [], "cards": []}
        with open(self._file_path, "r") as f:
            return json.load(f)

    def _save_data(self, data: dict) -> None:
        with open(self._file_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_targets(self) -> list[Target]:
        data = self._load_data()
        return [Target(**t) for t in data.get("targets", [])]

    def save_targets(self, targets: list[Target]) -> None:
        data = self._load_data()
        data["targets"] = [t.model_dump(mode='json') for t in targets]
        self._save_data(data)

    def load_examples(self) -> list[Example]:
        data = self._load_data()
        return [Example(**e) for e in data.get("examples", [])]

    def save_examples(self, examples: list[Example]) -> None:
        data = self._load_data()
        data["examples"] = [e.model_dump(mode='json') for e in examples]
        self._save_data(data)

    def load_cards(self) -> list[Card]:
        data = self._load_data()
        cards = []
        for card_data in data.get("cards", []):
            card_type = card_data.get("card_type")
            if card_type == "MeaningMCQ":
                cards.append(MeaningMCQCard(**card_data))
            elif card_type == "WordMCQ":
                cards.append(WordMCQCard(**card_data))
            elif card_type == "Typing":
                cards.append(TypingCard(**card_data))
        return cards

    def save_cards(self, cards: list[Card]) -> None:
        data = self._load_data()
        data["cards"] = [c.model_dump(mode='json') for c in cards]
        self._save_data(data)