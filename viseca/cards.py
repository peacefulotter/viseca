import json
from typing import Optional

import click

from viseca.client import VisecaClient


@click.command()
@click.option("--username", help="Viseca account username")
@click.option("--password", help="Viseca account password")
def fetch_cards(username: Optional[str] = None, password: Optional[str] = None):
    """List all cards associated with the account."""
    try:
        client = VisecaClient(username, password)
        if not client:
            return

        cards = client.list_cards()
        print(json.dumps(cards, indent=2, default=str))

    except Exception as e:
        print(f"Error listing cards: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    fetch_cards()
