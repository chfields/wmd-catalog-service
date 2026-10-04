"""Print this service's OpenAPI contract: python -m app.contract > openapi.json"""

import json

from app.db import Database
from app.main import create_app


def contract() -> dict:
    return create_app(Database("postgresql://contract-only", "catalog"), migrate=False).openapi()


if __name__ == "__main__":
    print(json.dumps(contract(), indent=2, sort_keys=True))
