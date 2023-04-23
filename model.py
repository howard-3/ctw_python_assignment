import datetime
import os

import sqlalchemy

from sqlalchemy import MetaData, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

metadata_obj = MetaData(schema="public")


class Base(DeclarativeBase):
    metadata = metadata_obj


class FinancialData(Base):
    __tablename__ = "financial_data"

    id: Mapped[int] = mapped_column(type_=sqlalchemy.types.BIGINT, primary_key=True)
    symbol: Mapped[str]
    date: Mapped[datetime.date] = mapped_column(sqlalchemy.types.Date)
    open_price: Mapped[float]
    close_price: Mapped[float]
    volume: Mapped[float]
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name="unique_symbol_date"),
    )

    def __repr__(self):
        return str({x: self.__dict__[x] for x in self.__dict__.keys() if x != '_sa_instance_state'})


if __name__ == '__main__':
    if 'POSTGRES_URL' not in os.environ:
        raise ValueError("Error, missing POSTGRES_URL in env var")

    engine = sqlalchemy.create_engine(os.environ['POSTGRES_URL'], echo=True)
    conn = engine.connect()
    metadata = sqlalchemy.MetaData()
    Base.metadata.create_all(engine)
