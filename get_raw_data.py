import datetime
from typing import List, Dict

import requests
import json
import os
import sqlalchemy
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
import os
from model import FinancialData

ALPHA_VANTAGE_API_KEY = "ALPHA_VANTAGE_API_KEY"
POSTGRES_URL = "POSTGRES_URL"
DEFAULT_TICKERS = ['IBM', 'AAPL']


def fetch_financial_data(req_api_key: str, ticker: str) -> List[Dict]:
    """
    Queries the alpha vantage api and return a list of dictionary with keys

    - symbol: str
    - date: date
    - open_price: float
    - close_price: float
    - volume: float
    :param req_api_key: alpha vantage api key
    :param ticker: the ticker to query for
    :return: a list of dictionaries or if invalid input is provided, a key error may be raised.
    """
    resp = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&"
                        f"symbol={ticker}&apikey={req_api_key}")
    resp.raise_for_status()
    out_json = json.loads(resp.content.decode('utf8'))
    records = []
    time_series = out_json['Time Series (Daily)']
    for record_date in time_series.keys():
        record = time_series[record_date]
        records.append({
            "symbol": ticker,
            "date": datetime.date.fromisoformat(record_date),
            "open_price": float(record['1. open']),
            "close_price": float(record['4. close']),
            "volume": float(record['6. volume'])
        })
    return records


def write_to_db(records: List[Dict]):
    """
    Writes the list of records to db
    """
    engine = sqlalchemy.create_engine(os.environ[POSTGRES_URL], echo=True)
    with Session(engine) as session:
        for rec in records:
            stmt = insert(FinancialData).values(**rec)
            stmt = stmt.on_conflict_do_update(
                constraint='unique_symbol_date',
                index_where=FinancialData.symbol == rec['symbol'] and FinancialData.date == rec['date'],
                set_=rec
            )
            session.execute(stmt)
        session.commit()


if __name__ == '__main__':
    if ALPHA_VANTAGE_API_KEY not in os.environ:
        raise ValueError(f"Error, env var {ALPHA_VANTAGE_API_KEY} is not set.")
    if POSTGRES_URL not in os.environ:
        raise ValueError(f"Error, missing {POSTGRES_URL} in env var")

    api_key = os.environ[ALPHA_VANTAGE_API_KEY]
    try:
        for ticker in DEFAULT_TICKERS:
            entries = fetch_financial_data(api_key, ticker)
            write_to_db(entries)
    except KeyError:
        raise ValueError("Error, please check your alpha vantage api key and ticker.")
