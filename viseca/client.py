import time
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, TypedDict, cast

import requests
import requests.cookies

from viseca.credentials import get_credentials
from viseca.transactions import Transactions

BASE_URL = "https://one.viseca.ch/api"
API_URL = "https://api.one.viseca.ch/v1"
LOGIN_URL = "https://one.viseca.ch/oneidentity/login"  # legacy: "https://one.viseca.ch/login/login"
AUTHENTICATE_URL = "https://auth.one.viseca.ch/v1/web/user/authenticateuser"
CONFIRMATION_URL = "https://api.one.viseca.ch/v1/web/user/authentication/2fa/pollUserReply"  # legacy: "https://one.viseca.ch/login/app-confirmation"


class ConfirmationData(TypedDict):
    userReply: Literal["noReply", "accept"]
    pollDelay: int


def get_session():
    session = requests.Session()
    session.cookies = requests.cookies.RequestsCookieJar()

    # Set browser-like headers
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
    )

    return session


def await_app_confirmation(
    session: requests.Session, timeout: int = 300, interval: int = 2
):
    """Wait for app confirmation with a timeout."""
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            raise Exception("Timeout waiting for app confirmation")

        try:
            response = session.get(CONFIRMATION_URL, allow_redirects=False)

            if response.status_code != 200:
                return Exception("2FA Confirmation step failed.")

            data = cast(ConfirmationData, response.json())

            if data["userReply"] == "accept":
                return

        except requests.RequestException as e:
            raise Exception(f"App confirmation request failed: {str(e)}")

        time.sleep(interval)


class VisecaClient:
    def __init__(self, username: Optional[str], password: Optional[str]):
        self.session = get_session()
        username, password = get_credentials(username, password)
        self.login(username, password)

    def login(self, username: str, password: str):
        """Main login function that handles the Viseca authentication flow."""
        response = self.session.get(LOGIN_URL, allow_redirects=False)

        form_data = {
            "username": username,
            "password": password,
            "reason": "portalLogin",
        }

        try:
            response = self.session.post(
                AUTHENTICATE_URL,
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                allow_redirects=False,
            )

            if response.status_code != 200:
                raise Exception("Login failed when attempting to authenticate")

            # Wait for 2FA app confirmation
            await_app_confirmation(self.session)

        except requests.RequestException as e:
            raise Exception(f"Login request failed: {str(e)}")

    def list_cards(self) -> List[Dict[str, Any]]:
        """List all cards associated with the account."""
        res = self.session.get(f"{API_URL}/cards", allow_redirects=False)
        res.raise_for_status()
        return res.json()

    def list_transactions(
        self,
        card_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        page_size: int = 100,
    ) -> List[Transactions]:
        """List all transactions for a given card."""
        params = {
            "offset": offset,
            "pagesize": page_size,
            "statetype": "unknown",
        }
        if date_from is not None:
            params["dateFrom"] = date_from.strftime("%Y-%m-%d")
        if date_to is not None:
            params["dateTo"] = date_to.strftime("%Y-%m-%d")

        res = self.session.get(
            f"{API_URL}/card/{card_id}/transactions",
            params=params,
            allow_redirects=False,
            headers={"Accept": "application/json"},
        )
        data = res.json()
        txs = [Transactions(**tx) for tx in data["list"]]
        return txs

    def get_user(self) -> Dict[str, Any]:
        """Get user information."""
        res = self.session.get(f"{API_URL}/user", allow_redirects=False)
        res.raise_for_status()
        return res.json()
