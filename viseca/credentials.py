import os
from typing import Optional

from dotenv import load_dotenv


def get_credentials(
    username: Optional[str] = None, password: Optional[str] = None
) -> tuple[str, str]:
    """
    Get credentials from either provided arguments or environment variables.
    Returns a tuple of (username, password).
    Raises ValueError if credentials cannot be found.
    """
    if username and password:
        return username, password

    load_dotenv()

    final_username = username or os.getenv("VISECA_USERNAME")
    final_password = password or os.getenv("VISECA_PASSWORD")

    if not final_username or not final_password:
        raise ValueError(
            "Credentials not found. Either provide --username and --password arguments "
            "or set VISECA_USERNAME and VISECA_PASSWORD in .env file"
        )

    return final_username, final_password
