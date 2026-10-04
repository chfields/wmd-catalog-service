"""The published contract (openapi.json) must match the code. Regenerate it deliberately:
python -m app.contract > openapi.json
"""

import json
from pathlib import Path

from app.contract import contract


def test_openapi_matches_the_committed_contract():
    committed = json.loads((Path(__file__).parent.parent / "openapi.json").read_text())
    assert contract() == committed
