"""Test the data classes.

source.py models:

Source:
    source: str
    source_id: str | None = None
"""

# ruff: noqa: D103, S101

import pytest
from dataclass_wizard.errors import MissingFields

from lunatask.models import source
from tests.data.sample_source import (
    dict_source_full,
    dict_source_no_optional,
)


def test_source_from_dict() -> None:
    test_source = source.Source.from_dict(dict_source_full)
    assert test_source.source == "A source"
    assert test_source.source_id == "1"


def test_source_from_dict_partial() -> None:
    test_source = source.Source.from_dict(dict_source_no_optional)
    assert test_source.source == "A source"
    assert test_source.source_id is None


def test_source_empty() -> None:
    with pytest.raises(MissingFields):
        _ = source.Source.from_dict({})


def test_source_empty_json() -> None:
    with pytest.raises(MissingFields):
        _ = source.Source.from_json("{}")
