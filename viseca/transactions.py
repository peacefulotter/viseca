import os
import traceback
from datetime import datetime
from typing import List, Optional

import click
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict


class PfmCategory(BaseModel):
    model_config = ConfigDict()

    id: str
    name: str
    lightColor: str
    mediumColor: str
    color: str
    imageUrl: str
    transparentImageUrl: str


class Links(BaseModel):
    model_config = ConfigDict()

    transactiondetails: str


class Transactions(BaseModel):
    model_config = ConfigDict()

    transactionId: str
    cardId: Optional[str] = None
    maskedCardNumber: Optional[str] = None
    cardName: Optional[str] = None
    date: str
    showTimestamp: bool
    amount: float
    currency: str
    originalAmount: Optional[float] = None
    originalCurrency: Optional[str] = None
    merchantName: Optional[str] = None
    prettyName: Optional[str] = None
    merchantPlace: Optional[str] = None
    isOnline: bool = False
    pfmCategory: PfmCategory
    stateType: str
    details: str
    type: str
    isBilled: bool
    links: Links


def get_card_id(card_id: Optional[str]):
    if card_id is not None:
        return card_id

    load_dotenv()

    final_card_id = os.getenv("VISECA_CARD_ID")

    if not final_card_id:
        raise ValueError(
            "Card ID not found. Either provide a card_id as argument "
            "or set VISECA_CARD_ID in .env file"
        )

    return final_card_id


def format_transactions(txs: List[Transactions]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            (
                tx.transactionId,
                tx.date,
                tx.merchantName,
                tx.prettyName,
                tx.amount,
                tx.currency,
                tx.pfmCategory.id,
                tx.pfmCategory.name,
                tx.isOnline,
            )
            for tx in txs
        ],
        columns=[
            "TransactionID",
            "Date",
            "Merchant",
            "Name",
            "Amount",
            "Currency",
            "PFMCategoryID",
            "PFMCategoryName",
            "Online",
        ],
    )


@click.command()
@click.argument("card_id", required=False)
@click.option("--username", help="Viseca account username")
@click.option("--password", help="Viseca account password")
@click.option(
    "--date-from",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="From which date on transactions should be fetched (format: YYYY-MM-DD)",
)
@click.option(
    "--date-to",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="To which date transactions should be fetched (format: YYYY-MM-DD)",
)
@click.option("--file", help="Path at which transactions will be saved to")
def fetch_transactions(
    card_id: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    file: Optional[str] = None,
) -> List[Transactions]:
    """List all transactions for given card ID."""
    try:
        from viseca.client import VisecaClient

        client = VisecaClient(username, password)
        card_id = get_card_id(card_id)
        transactions = client.list_transactions(
            card_id=card_id, date_from=date_from, date_to=date_to
        )

        if file is not None:
            format_transactions(transactions).to_csv(file, index=False)

        return transactions

    except Exception:
        traceback.print_exc()
        return None


if __name__ == "__main__":
    fetch_transactions()
