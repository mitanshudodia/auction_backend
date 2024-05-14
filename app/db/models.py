# models.py
from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Buyer(Base):
    __tablename__  = "buyers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    timezone = Column(String, nullable=False)
    password = Column(String, nullable=False)

    auction_goods_won = relationship("AuctionGood", back_populates="winner")
    bids = relationship("Bid", back_populates="buyer")

class Seller(Base):
    __tablename__  = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    contact = Column(BigInteger, unique=True, nullable=False)
    rating = Column(Float)
    timezone = Column(String, nullable=False)
    password = Column(String, nullable=False)
    
    goods = relationship("Good", back_populates="seller")

class Category(Base):
    __tablename__  = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    goods = relationship("Good", back_populates="category")

class Good(Base):
    __tablename__  = "goods"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    images_link = Column(String, nullable=True)
    company_name = Column(String, nullable=False)
    # verification_code = Column(String, nullable=False)  ask @arjun wether its needed or not 
    category_id = Column(Integer, ForeignKey("categories.id"))
    seller_id = Column(Integer, ForeignKey("sellers.id"))

    category = relationship("Category", back_populates="goods")
    seller = relationship("Seller", back_populates="goods")
    auction_goods = relationship("AuctionGood", back_populates="good")

class AuctionGood(Base):
    __tablename__ = "auction_goods"

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    closed = Column(Boolean, default=False)
    initial_price = Column(Float, nullable=False)
    sold_price = Column(Float)
    good_id = Column(Integer, ForeignKey("goods.id"))
    winner_id = Column(Integer, ForeignKey("buyers.id"))

    good = relationship("Good", back_populates="auction_goods")
    winner = relationship("Buyer", back_populates="auction_goods_won")
    bids = relationship("Bid", back_populates="auction_good")

class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True)
    bid_amount = Column(Float, nullable=False)
    auction_good_id = Column(Integer, ForeignKey("auction_goods.id"))
    buyer_id = Column(Integer, ForeignKey("buyers.id"))

    auction_good = relationship("AuctionGood", back_populates="bids")
    buyer = relationship("Buyer", back_populates="bids")
