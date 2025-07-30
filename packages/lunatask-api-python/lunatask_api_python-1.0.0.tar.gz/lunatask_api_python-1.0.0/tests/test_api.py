"""Test API creation."""

# ruff: noqa: D103, S101

import pytest

from config import TokenLengthError
from lunatask.api import LunataskAPI
from tests.test_config import TEST_LUNATASK_API_TOKEN


def test_api_create() -> None:
    with pytest.raises(TokenLengthError):
        _ = LunataskAPI("hi")

    test_api = LunataskAPI(TEST_LUNATASK_API_TOKEN)
    assert test_api
