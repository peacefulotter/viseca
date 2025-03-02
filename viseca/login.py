from typing import Optional

import click

from viseca.client import VisecaClient


def login_cli(
    client: VisecaClient, username: Optional[str], password: Optional[str]
) -> Optional[VisecaClient]:
    """CLI wrapper for the login function."""
    try:
        client = VisecaClient(username, password)
        return client
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return None


@click.command()
@click.option("--username", required=True, help="Viseca account username")
@click.option("--password", required=True, help="Viseca account password")
def main(username: str, password: str):
    """Command line interface for Viseca login."""
    client = login_cli(username, password)
    if client:
        print("Login successful!")


if __name__ == "__main__":
    main()
