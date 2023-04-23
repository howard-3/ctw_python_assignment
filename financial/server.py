import os

import pandas
import datetime
import json
from typing import Optional, Dict

import sqlalchemy.exc
from flask import request, make_response
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(engine_options={"echo": True})
app = Flask(__name__)
if 'POSTGRES_URL' not in os.environ:
    raise ValueError("Error, missing POSTGRES_URL in env var")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['POSTGRES_URL']
db.init_app(app)


class FinancialData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String)
    date = db.Column(db.Date)
    open_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    volume = db.Column(db.Float)


def to_date(args: Dict, date_param: str) -> Optional[datetime.date]:
    """
    Extracts an optional date from the args with keys date_param and
    returns a parsed date. The date is expected to be in iso format.
    """
    extracted = args[date_param] if date_param in args else None
    return datetime.date.fromisoformat(extracted) if extracted else None


@app.route("/api/financial_data")
def financial_data():
    args = request.args
    start_date, end_date = to_date(request.args, 'start_date'), to_date(request.args, 'end_date')
    symbol = request.args['symbol'].upper() if 'symbol' in args else None
    limit = int(request.args['limit']) if 'limit' in args else 5
    page = int(request.args['page']) if 'page' in args else 1

    # create the query with the right filters.
    query = FinancialData.query
    if symbol:
        query = query.filter(FinancialData.symbol == symbol)
    if end_date:
        query = query.filter(FinancialData.date < end_date)
    if start_date:
        query = query.filter(FinancialData.date > start_date)

    # create the pagination info data
    data = query.paginate(page=page, per_page=limit)
    count = query.count()
    pages = int(count / limit)
    if count % limit != 0:
        pages += 1

    pagination_info = {
        "count": count,
        "page": page,
        "limit": limit,
        "pages": pages
    }

    info = {
        "error": ""
    }

    # parse and create the data from db.
    records = []
    for x in data:
        records.append({
            "symbol": x.symbol,
            "date": x.date.isoformat(),
            "open_price": str(x.open_price),
            "close_price": str(x.close_price),
            "volume": str(x.volume)
        })
    return json.dumps({
        "data": records,
        "pagination": pagination_info,
        "info": info
    })


@app.route("/api/statistics")
def statistics():
    args = request.args
    start_date, end_date = to_date(request.args, 'start_date'), to_date(request.args, 'end_date')
    symbol = request.args['symbol'].upper() if 'symbol' in args else None

    if not start_date or not end_date or not symbol:
        resp = make_response("Please ensure start_date, end_date, symbols are provided and valid.", 400)
        return resp

    query = FinancialData.query
    if symbol:
        query = query.filter(FinancialData.symbol == symbol)
    if end_date:
        query = query.filter(FinancialData.date < end_date)
    if start_date:
        query = query.filter(FinancialData.date > start_date)

    def to_dict(input):
        return {
            "symbol": input.symbol,
            "date": input.date.isoformat(),
            "open_price": input.open_price,
            "close_price": input.close_price,
            "volume": input.volume
        }

    # use pandas to do the calculation.
    records = [to_dict(x) for x in query.all()]
    df = pandas.DataFrame(records, columns=['symbol', 'date', 'open_price', 'close_price', 'volume'])

    return json.dumps({
        "data": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "symbol": symbol,
            "average_daily_open_price": df['open_price'].mean(),
            "average_daily_close_price": df['close_price'].mean(),
            "average_daily_volume": df['volume'].mean(),
        },
        "info": {"error": "No data" if len(df) == 0 else ""}
    })


@app.errorhandler(500)
def handle_error(e):
    if isinstance(e.original_exception, ValueError) and 'Invalid isoformat string' in e.original_exception.args[0]:
        return e.original_exception.args[0], 400
    elif isinstance(e.original_exception, sqlalchemy.exc.OperationalError):
        print(e)
        return "Application was not configured properly.", 500
    elif isinstance(e.original_exception, sqlalchemy.exc.ProgrammingError):
        print(e)
        return "Application was not properly setup, please see the readme file.", 500
    else:
        print(e)
        return "Server error"


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)