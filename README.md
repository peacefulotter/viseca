<div align="center">
    <h1>💸 viseca</h2>
    <div>
        <p align="center">
          <a aria-label="MIT License" href="https://opensource.org/licenses/MIT">
            <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge">
          </a>
          <a aria-label="pypi" href="https://img.shields.io/pypi/pyversions/viseca">
            <img src="https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/peacefulotter/viseca/main/pyproject.toml&style=for-the-badge">  
          </a>
          <a aria-label="GitHub last commit" href="https://www.github.com/peacefulotter/viseca">
            <img src="https://img.shields.io/github/last-commit/peacefulotter/viseca/main?style=for-the-badge">
          </a>
        </p>
    </div>
    <h3><b>Fetch transactions from Viseca One</b></h3>
</div>

![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fpeacefulotter%2Fviseca%2Fmain%2Fpyproject.toml)


```sh
>>> uv add viseca
```


## Usage

This method processes the auth flow in the CLI and will trigger a 2FA request like the login in a browser would.

1. Log in to [one.viseca.ch](https://one.viseca.ch) and navigate to "Transactions"
1. Obtain the card ID from the path (between `/v1/card/` and `/transactions`) and store it in your `.env` file. Additionaly, to avoid entering your credentials everytime, feel free to add them to the `.env` file as well. 
    ```sh
    cp .env.example .env
    >>> VISECA_USERNAME=YOUR_MAIL
    >>> VISECA_PASSWORD=YOUR_PASSWORD
    >>> VISECA_CARD_ID=YOUR_CARD_ID
    ```
1.  Fetch transactions (and save them to a file)
    - Using commands
    ```sh
    uv run viseca/transactions.py --file transactions.csv
    ```
    - Or the python package
    ```python
    from viseca import VisecaClient, format_transactions

    client = VisecaClient()
    txs = client.list_transactions()
    df = format_transactions(txs)
    df.to_csv("transactions.csv")
    ```
