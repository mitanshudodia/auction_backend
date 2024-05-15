
import datetime
import uvicorn
from fastapi import Depends, FastAPI
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dependencies import get_db
from sqlalchemy.orm import Session
from crud import auction_crud, bid_crud

from apis.router import final_router

app = FastAPI()
scheduler = AsyncIOScheduler()

app.include_router(final_router)
from db.session import SessionLocal
db = SessionLocal()


async def check_auctions():
    all_open_auctions = await auction_crud.crud.get_open_auction(db=db)
    current_time = datetime.datetime.now(pytz.UTC)
    for auction in all_open_auctions:
        if auction.end_time <= current_time:
            all_bids_for_auction = await bid_crud.crud.get_by_auction_id(db=db, auction_id=auction.id)
            if len(all_bids_for_auction) > 0:
                all_bids_for_auction.sort(key=lambda x: x.bid_amount, reverse=True)
                highest_bid = all_bids_for_auction[0]
                auction.winner_id = highest_bid.buyer_id
                auction.closed = True
                auction.sold_price = highest_bid.bid_amount
                db.add(auction)
                db.commit()
                db.refresh(auction)


scheduler.add_job(check_auctions, "interval", seconds=5)

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.get("/timezones")
def get_timezones():
    all_timezones = set(pytz.all_timezones)
    return all_timezones


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
