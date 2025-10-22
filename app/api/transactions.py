from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional
from ..database import get_db
from .. import models
from ..schemas import TransactionCreate, TransactionUpdate, TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("", response_model=List[TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    type: Optional[models.TxType] = Query(None, description="income or expense"),
    category_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    q: Optional[str] = Query(None, description="search in description"),
    skip: int = 0,
    limit: int = 100,
):
    stmt = select(models.Transaction)
    if type is not None:
        stmt = stmt.where(models.Transaction.type == type)
    if category_id is not None:
        stmt = stmt.where(models.Transaction.category_id == category_id)
    if date_from is not None:
        stmt = stmt.where(models.Transaction.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(models.Transaction.date <= date_to)
    if q:
        like = f"%{q.replace('%','').replace('_',' ')}%"
        stmt = stmt.where(models.Transaction.description.ilike(like))

    stmt = stmt.order_by(models.Transaction.date.desc()).offset(skip).limit(limit)
    txs = db.scalars(stmt).all()
    return txs


@router.post("/", response_model=TransactionOut, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    # Validate category if provided
    if payload.category_id is not None:
        cat = db.get(models.Category, payload.category_id)
        if not cat:
            raise HTTPException(status_code=400, detail="Category does not exist")

    tx = models.Transaction(
        category_id=payload.category_id,
        type=models.TxType(payload.type),
        amount=payload.amount,
        description=payload.description,
        date=payload.date,
        is_planned=payload.is_planned,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.put("/{tx_id}", response_model=TransactionOut)
def update_transaction(tx_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if payload.category_id is not None:
        if payload.category_id is not None:
            if payload.category_id:
                cat = db.get(models.Category, payload.category_id)
                if not cat:
                    raise HTTPException(status_code=400, detail="Category does not exist")
        tx.category_id = payload.category_id

    if payload.type is not None:
        tx.type = models.TxType(payload.type)
    if payload.amount is not None:
        tx.amount = payload.amount
    if payload.description is not None:
        tx.description = payload.description
    if payload.date is not None:
        tx.date = payload.date
    if payload.is_planned is not None:
        tx.is_planned = payload.is_planned

    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=204)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return None