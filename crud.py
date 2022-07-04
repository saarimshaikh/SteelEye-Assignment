from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import exc
from fastapi import status
from fastapi.responses import JSONResponse


def create_trade_obj(db: Session, trade: schemas.Trade):
    trade_item = models.Trade(
        assetClass=trade.instrument_name,
        counterparty=trade.counterparty,
        instrumentId=trade.instrument_id,
        instrumentName=trade.instrument_name,
        tradeDateTime=trade.trade_date_time,
        tradeId=trade.trade_id,
        trader=trade.trader,
    )
    db.add(trade_item)
    try:
        db.commit()
    except exc.IntegrityError as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": 'IntegrityError'}
        )

    db.refresh(trade_item)
    trade_details = create_trade_details(db, trade_item.id, trade.trade_details)
    trade_item.tradeDetails = trade_details
    db.add(trade_item)
    db.commit()
    db.refresh(trade_item)
    return get_trade(db, trade_id=trade_item.tradeId)


def create_trade_details(db: Session, trade_item, trade_details: schemas.TradeDetails):
    trade_details_item = models.TradeDetails(
        buySellIndicator=trade_details.buySellIndicator,
        price=trade_details.price,
        quantity=trade_details.quantity,
        trade=trade_item
    )
    db.add(trade_details_item)
    db.commit()
    db.refresh(trade_details_item)
    return trade_details_item


def get_trade(db: Session, trade_id):
    trade_item = db.query(models.Trade).filter(models.Trade.tradeId == trade_id).first()
    if not trade_item:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": 'Trade Object Not Found'}
        )
    trade_item_dict = trade_item.__dict__
    trade_item_dict['tradeDetails'] = trade_item.tradeDetails.__dict__
    return trade_item_dict


def delete_trade(db: Session, trade_id):
    trade_item = db.query(models.Trade).filter(models.Trade.tradeId == trade_id).delete()
    db.commit()
    if trade_item ==0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": 'Trade Object Not Found'}
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": 'Trade deleted'}
    )



def search_trade(db: Session, search=None, offset=None, limit=None):
    if search:
        search_items = db.query(models.Trade).filter(
            (models.Trade.counterparty == search) | (models.Trade.instrumentId == search) | (
                    models.Trade.instrumentName == search) |
            (models.Trade.trader == search)).offset(offset).limit(limit).all()
        return get_dict_trades(search_items)
    search_items = db.query(models.Trade).offset(offset).limit(limit).all()
    return get_dict_trades(search_items)


def filter_trade(db: Session, asset_class=None, end=None, maxPrice=None, minPrice=None, start=None,
                 tradeType=None, offset=None, limit=None):
    search_items = db.query(models.Trade)
    if asset_class:
        search_items = search_items.filter(models.Trade.assetClass == asset_class)
    if start and end:
        # handle if both params are provided
        search_items = search_items.filter((models.Trade.tradeDateTime >= start) & (models.Trade.tradeDateTime <= end))
    elif end:
        search_items = search_items.filter(models.Trade.tradeDateTime <= end)
    elif start:
        search_items = search_items.filter(models.Trade.tradeDateTime >= start)
    if maxPrice and minPrice:
        # handle if both params are provided
        search_items = search_items.join(models.TradeDetails).filter(
            (models.TradeDetails.price >= minPrice) & (models.TradeDetails.price <= maxPrice))
    elif maxPrice:
        search_items = search_items.join(models.TradeDetails).filter(models.TradeDetails.price <= maxPrice)
    elif minPrice:
        search_items = search_items.join(models.TradeDetails).filter(models.TradeDetails.price >= minPrice)
    if tradeType:
        search_items = search_items.join(models.TradeDetails).filter(models.TradeDetails.buySellIndicator == tradeType)
    search_items = search_items.offset(offset).limit(limit).all()
    return get_dict_trades(search_items)


def get_dict_trades(search_items):
    items = []
    for trade in search_items:
        trade_item_dict = trade.__dict__
        trade_details_dict = trade.tradeDetails.__dict__
        trade_item_dict['tradeDetails'] = trade_details_dict
        items.append(trade_item_dict)
    return items
