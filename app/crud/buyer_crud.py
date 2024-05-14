from typing import Any, Dict, List, Optional, Union

from db import models
from schemas import buyers

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

class CrudBuyer():
    async def get_by_id(self, db: Session, id: Union[int, str]) -> Optional[models.Buyer]:
        result = db.query(models.Buyer).get(id)
        return result

    async def get_by_email(self, db: Session, email: str) -> Optional[List[models.Buyer]]:
        result = db.query(models.Buyer).filter_by(email=email).all()
        return result

    async def create(self, db: Session, buyer: Union[buyers.BuyerCreate, Dict[str, Any]]):
        if isinstance(buyer, dict):
            buyer_data = buyer.copy()
        else:
            buyer_data = buyer.model_dump(exclude_unset=True)
        db_buyer = models.Buyer(**buyer_data)
        db.add(db_buyer)
        db.commit()
        db.refresh(db_buyer)
        return db_buyer
    
    async def update(self, db: Session, buyer: Union[buyers.BuyerUpdate, Dict[str, Any]]):
        if isinstance(buyer, dict):
            buyer_data = buyer.copy()
        else:
            buyer_data = buyer.model_dump(exclude_unset=True)
        db_buyer = await db.query(models.Buyer).get(id)
        for field, value in buyer_data.items():
            if hasattr(db_buyer, field):
                setattr(db_buyer, field, value)
        db.commit()
        db.refresh(db_buyer)
        return db_buyer
    
    async def delete_by_id(self, db: Session, buyer: Union[buyers.BuyerDelete, Dict[str, Any]]):
        if buyer.id:
            db_buyer = await self.get_by_id(buyer.id)
        elif buyer.email:
            db_buyer = await self.get_by_email(buyer.email)
        else:
            raise Exception("Either id or email of buyer is required")
        db.delete(db_buyer)
        db.commit()
        return db_buyer

crud = CrudBuyer()