from os import name
from typing import Any, Dict, Optional, Union

from db import models
from schemas import category

from sqlalchemy.orm import Session

class CrudCategory():
    async def get_by_id(self, db: Session, id: Union[int, str]) -> Optional[models.Category]:
        result = db.query(models.Category).get(id)
        return result

    async def get_all(self, db: Session) -> models.Category:
        result = db.query(models.Category).all()
        return result

    async def create(self, db: Session, category: Union[category.CategoryOperations, Dict[str, Any]]):
        if isinstance(category, dict):
            category_data = category.copy()
        else:
            category_data = category.model_dump(exclude_unset=True)
        category_db = models.Category(**category_data)
        db.add(category_db)
        db.commit()
        db.refresh(category_db)
        return category_db
    
    async def delete_by_name(self, db: Session, category: Union[category.CategoryOperations, Dict[str, Any]]):
        if category.name:
            db_seller = db.query(models.Category).filter_by(name=name).first()
        else:
            raise Exception("Either id or email of seller is required")
        db.delete(db_seller)
        db.commit()
        return db_seller

crud = CrudCategory()