import json
from typing import Optional

import click

from viseca.client import VisecaClient


@click.command()
@click.argument("card_id")
@click.option("--username", help="Viseca account username")
@click.option("--password", help="Viseca account password")
def fetch_user(username: Optional[str] = None, password: Optional[str] = None):
    """Get user information."""
    try:
        client = VisecaClient(username, password)
        if not client:
            return 1

        user_info = client.get_user()
        print(json.dumps(user_info, indent=2, default=str))

    except Exception as e:
        print(f"Error getting user info: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    fetch_user()
