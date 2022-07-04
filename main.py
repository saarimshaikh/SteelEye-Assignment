from typing import Optional
from enum import Enum
from fastapi import FastAPI, Query, Depends, HTTPException, Body
from schemas import Trade
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, crud
from typing import List
from datetime import datetime, timezone

start = datetime.now(timezone.utc)


class AssertClassEnum(str, Enum):
    Bond = "Bond"
    Equity = "Equity"
    FX = "FX"
    Etc = "Etc"


class TradeTypeEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/trade/{trade_id}/", response_model=schemas.Trade)
async def get_trade(trade_id: str, db: Session = Depends(get_db)):
    trade_obj = crud.get_trade(db, trade_id=trade_id)
    if trade_obj is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade_obj


@app.post("/trade")
async def create_trade(trade: Trade, db: Session = Depends(get_db)):
    trade_obj = crud.create_trade_obj(db, trade=trade)
    return trade_obj


@app.delete("/trade/{trade_id}")
def delete_trade(trade_id: str, db: Session = Depends(get_db)):
    trade_resp = crud.delete_trade(db, trade_id=trade_id)
    return trade_resp


# @app.put("/trade/{trade_id}")

@app.get("/trades/search/", response_model=List[schemas.Trade])
async def filter(search: Optional[str] = None, offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    limit = offset + limit
    if search:
        trade_obj = crud.search_trade(db, search=search, offset=offset, limit=limit)
        return trade_obj
    trade_obj = crud.search_trade(db, offset=offset, limit=limit)
    return trade_obj


@app.get("/trades/filter/", response_model=List[schemas.Trade])
async def filter(asset_class: Optional[AssertClassEnum] = None, start: Optional[datetime] = None,
                 end: Optional[datetime] = None, maxPrice: Optional[float] = None,
                 minPrice: Optional[int] = None,
                 tradeType: Optional[TradeTypeEnum] = None, offset: int = 0, limit: int = 10,
                 db: Session = Depends(get_db)):
    limit = offset + limit
    trade_obj = crud.filter_trade(db, asset_class=asset_class, end=end, maxPrice=maxPrice, minPrice=minPrice,
                                  start=start,
                                  tradeType=tradeType, offset=offset, limit=limit)
    return trade_obj
