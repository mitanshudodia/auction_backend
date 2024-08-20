
import datetime
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dependencies import get_db
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, select
from crud import auction_crud, bid_crud

from apis.router import final_router

app = FastAPI()
origins = ["http://localhost:3000"]  # Replace with your frontend origin(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Set to True if cookies are needed
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers (Content-Type, etc.)
)


scheduler = AsyncIOScheduler()

app.include_router(final_router)
from db.session import SessionLocal
db = SessionLocal()


async def check_auctions():
    all_open_auctions = await auction_crud.crud.get_auctions_to_close(db=db)
    current_time = datetime.datetime.now(pytz.UTC)
    #for all the auctions
    for auction in all_open_auctions:
        #if the auctions are closed
        if auction.end_time <= current_time:
            #get the bids
            all_bids_for_auction = await bid_crud.crud.get_by_auction_id(db=db, auction_id=auction.id)
            if len(all_bids_for_auction) > 0:
                #if there are bids in that auction
                all_bids_for_auction.sort(key=lambda x: x.bid_amount, reverse=True)
                #get the highest bid
                highest_bid = all_bids_for_auction[0]
                #update the auction table with the bids
                auction.winner_id = highest_bid.buyer_id
                auction.closed = True
                auction.sold_price = highest_bid.bid_amount
                db.add(auction)
                db.commit()
                db.refresh(auction)
                print("Completed")




scheduler.add_job(check_auctions, "interval", seconds=10)

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
    uvicorn.run(app, host="127.0.0.1", port=8000)
