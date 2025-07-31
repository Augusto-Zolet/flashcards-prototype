import json
from pathlib import Path
import uuid
from datetime import datetime

import pytest

from flashcards.models import MeaningMCQCard, Example, Target
from flashcards.models.common import CardId, ExampleId, TargetId
from flashcards.services.storage import JsonDataStorage


@pytest.fixture
def temp_json_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "test_data.json"
    return file_path


def test_json_data_storage_roundtrip(temp_json_file: Path):
    storage = JsonDataStorage(temp_json_file)

    # Create some test data
    target_id = TargetId(uuid.uuid4())
    example_id = ExampleId(uuid.uuid4())
    card_id = CardId(uuid.uuid4())

    targets = [
        Target(
            id=target_id,
            target="hello",
            lang="en",
            learned=False,
            date_learned=None,
        )
    ]
    examples = [
        Example(
            id=example_id,
            target_id=target_id,
            text="Hello, world!",
            example_target="Hello",
            target_start=0,
            target_end=5,
            example_type="contextual",
            source="human",
            contextual_synonyms=["greeting"],
            translations={"es": ["Hola, mundo!"]},
        )
    ]
    cards = [
        MeaningMCQCard(
            id=card_id,
            example_id=example_id,
            hints=["hint1", "hint2"],
            review_stats={
                "last_seen": None,
                "next_due": None,
                "interval": 0.0,
                "easiness": 2.5,
                "successes_in_row": 0,
                "mastered": False,
            },
        )
    ]

    # Save the data
    storage.save_targets(targets)
    storage.save_examples(examples)
    storage.save_cards(cards)

    # Load the data back
    loaded_targets = storage.load_targets()
    loaded_examples = storage.load_examples()
    loaded_cards = storage.load_cards()

    # Assert the data is the same
    assert len(loaded_targets) == 1
    assert loaded_targets[0].id == target_id

    assert len(loaded_examples) == 1
    assert loaded_examples[0].id == example_id

    assert len(loaded_cards) == 1
    assert loaded_cards[0].id == card_id