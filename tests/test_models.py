import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from flashcards.models import MeaningMCQCard, WordMCQCard, TypingCard, Example, Target
from flashcards.models.common import CardId, ExampleId, TargetId


def test_target_model():
    target_id = TargetId(uuid.uuid4())
    target = Target(
        id=target_id,
        target="hello",
        lang="en",
        learned=False,
        date_learned=None,
    )
    assert target.id == target_id
    assert target.target == "hello"


def test_example_model():
    example_id = ExampleId(uuid.uuid4())
    target_id = TargetId(uuid.uuid4())
    example = Example(
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
    assert example.id == example_id
    assert example.target_id == target_id


def test_meaning_mcq_card_model():
    card_id = CardId(uuid.uuid4())
    example_id = ExampleId(uuid.uuid4())
    card = MeaningMCQCard(
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
    assert card.id == card_id
    assert card.example_id == example_id
    assert card.card_type == "MeaningMCQ"


def test_word_mcq_card_model():
    card_id = CardId(uuid.uuid4())
    example_id = ExampleId(uuid.uuid4())
    card = WordMCQCard(
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
    assert card.id == card_id
    assert card.example_id == example_id
    assert card.card_type == "WordMCQ"


def test_typing_card_model():
    card_id = CardId(uuid.uuid4())
    example_id = ExampleId(uuid.uuid4())
    card = TypingCard(
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
    assert card.id == card_id
    assert card.example_id == example_id
    assert card.card_type == "Typing"