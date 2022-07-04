from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from database import Base
import datetime


class Trade(Base):
    __tablename__ = "trade"
    id = Column(Integer, primary_key=True)
    assetClass = Column(String, default=None)
    counterparty = Column(String, default=None)
    instrumentId = Column(String)
    instrumentName = Column(String)
    tradeDateTime = Column(DateTime, default=datetime.datetime.utcnow)
    # tradeDetails = Column(ForeignKey('trade_details.id'))
    tradeDetails = relationship('TradeDetails', backref='tradeDetails', uselist=False)
    tradeId = Column(Integer, default=None, unique=True, index=True)
    trader = Column(String)


class TradeDetails(Base):
    __tablename__ = "trade_details"
    id = Column(Integer, primary_key=True)
    buySellIndicator = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer)
    trade = Column(Integer, ForeignKey('trade.id'))
