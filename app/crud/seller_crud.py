from typing import Any, Dict, Optional, Union

from db import models
from schemas import sellers

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

class CrudSeller():
    async def get_by_id(self, db: Session, id: Union[int, str]) -> models.Seller:
        result = db.query(models.Seller).filter_by(id=id).first()
        return result

    async def get_by_email(self, db: Session, email: str) -> models.Seller:
        result = db.query(models.Seller).filter_by(email=email).all()
        return result[0]

    async def create(self, db: Session, seller: Union[sellers.SellerCreate, Dict[str, Any]]):
        if isinstance(seller, dict):
            seller_data = seller.copy()
        else:
            seller_data = seller.model_dump(exclude_unset=True)
        db_seller = models.Seller(**seller_data)
        db.add(db_seller)
        db.commit()
        db.refresh(db_seller)
        return db_seller
    
    async def update(self, db: Session, seller: Union[sellers.SellerUpdate, Dict[str, Any]]):
        if isinstance(seller, dict):
            seller_data = seller.copy()
        else:
            seller_data = seller.model_dump(exclude_unset=True)
        db_seller = db.query(models.Seller).get(id)
        for field, value in seller_data.items():
            if hasattr(db_seller, field):
                setattr(db_seller, field, value)
        db.commit()
        db.refresh(db_seller)
        return db_seller
    
    async def delete_by_id(self, db: Session, seller: Union[sellers.SellerDelete, Dict[str, Any]]):
        if seller.id:
            db_seller = await self.get_by_id(seller.id)
        elif seller.email:
            db_seller = await self.get_by_email(seller.email)
        else:
            raise Exception("Either id or email of seller is required")
        db.delete(db_seller)
        db.commit()
        return db_seller

crud = CrudSeller()