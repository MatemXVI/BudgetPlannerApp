from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from .. import models
from ..schemas import CategoryCreate, CategoryUpdate, CategoryOut
from ..deps import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    categories = db.scalars(
        select(models.Category)
        .where(models.Category.user_id == current_user.id)
        .order_by(models.Category.name)
    ).all()
    return categories


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cat = models.Category(name=payload.name, color=payload.color, user_id=current_user.id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cat = db.get(models.Category, category_id)
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cat = db.get(models.Category, category_id)
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.name is not None:
        cat.name = payload.name
    if payload.color is not None:
        cat.color = payload.color
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cat = db.get(models.Category, category_id)
    if not cat or cat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    # Detach transactions from this category for current user before deletion
    db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.category_id == category_id
    ).update({models.Transaction.category_id: None})
    db.delete(cat)
    db.commit()
    return None