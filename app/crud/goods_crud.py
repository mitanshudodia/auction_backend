from typing import Any, Dict, Optional, Union

from db import models
from schemas import goods

from sqlalchemy.orm import Session

class CrudGoods():
    async def get_by_id(self, db: Session, id: Union[int, str]) -> Optional[models.Good]:
        result = db.query(models.Good).get(id)
        return result
    
    async def get_by_user_id(self, db: Session, user_id: Union[int, str]) -> Optional[models.Good]:
        result = db.query(models.Good).filter(models.Good.seller_id == user_id).all()
        return result

    async def create(self, db: Session, goods: Union[goods.GoodsCreate, Dict[str, Any]], seller_id: int):
        if isinstance(goods, dict):
            goods_data = goods.copy()
        else:
            goods_data = goods.model_dump(exclude_unset=True)
        goods_data["seller_id"] = seller_id
        db_goods = models.Good(**goods_data)
        db.add(db_goods)
        db.commit()
        db.refresh(db_goods)
        return db_goods

    async def update(self, db: Session, goods: Union[goods.GoodsUpdate, Dict[str, Any]]):
        if isinstance(goods, dict):
            data = goods.copy()
        else:
            data = goods.model_dump(exclude_unset=True)
        print(data)
        db_data = db.query(models.Good).get(goods.id)
        for field, value in data.items():
            if hasattr(db_data, field) and value:
                setattr(db_data, field, value)
        db.commit()
        db.refresh(db_data)
        return db_data
    
    async def delete(self, db: Session, goods: Union[goods.GoodsGetorDelete, Dict[str, Any]]):
        if goods.id:
            db_data = await self.get_by_id(goods.id)
        else:
            raise Exception("Id is required")
        db.delete(db_data)
        db.commit()
        return db_data

crud = CrudGoods()