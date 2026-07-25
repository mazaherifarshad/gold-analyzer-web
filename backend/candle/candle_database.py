from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Index

from database.database import Base


class MarketCandle(Base):

    __tablename__ = "market_candles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    symbol = Column(
        String,
        nullable=False
    )

    timeframe = Column(
        String,
        nullable=False
    )

    candle_time = Column(
        DateTime,
        nullable=False
    )

    open = Column(
        Float,
        nullable=False
    )

    high = Column(
        Float,
        nullable=False
    )

    low = Column(
        Float,
        nullable=False
    )

    close = Column(
        Float,
        nullable=False
    )

    volume = Column(
        Float,
        default=0,
        nullable=False
    )


Index(
    "idx_symbol_timeframe_time",
    MarketCandle.symbol,
    MarketCandle.timeframe,
    MarketCandle.candle_time
)