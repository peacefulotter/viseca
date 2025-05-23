<div align="center">
    <h1><b>💸 viseca</b><br/></h1>
    <h3>A python package to easily fetch transactions from the Viseca One app</h3>
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
</div>

With **pip**:
```
>>> pip install viseca
```

With **uv**:
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
    ```python
    from viseca import VisecaClient, format_transactions
    
    client = VisecaClient()
    txs = client.list_transactions()
    df = format_transactions(txs)
    df.to_csv("transactions.csv")
    ```


### Locally
We provide commands as an alternative to the python api, e.g. for fetching transactions and saving them to a file:
```sh
uv run viseca/transactions.py --file transactions.csv
```

