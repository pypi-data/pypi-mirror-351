"""Sample Source for unit tests.

Source:
    source: str
    source_id: str | None = None
"""

from typing import Final

dict_source_full: Final[dict[str, str]] = {"source": "A source", "source_id": "1"}

dict_source_no_optional: Final[dict[str, str]] = {
    k: dict_source_full[k] for k in dict_source_full if k not in ["source_id"]
}
