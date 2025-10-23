from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import random
from decimal import Decimal
from ..database import get_db
from .. import models

router = APIRouter(prefix="/debug", tags=["debug"])

@router.post("/seed-demo")
def seed_demo(db: Session = Depends(get_db)):
    """Seed a few demo categories and random transactions. No auth required."""
    default_cats = [
        ("Jedzenie", "#f59e0b"),
        ("Transport", "#3b82f6"),
        ("Rachunki", "#ef4444"),
        ("Wypłata", "#10b981"),
    ]
    existing = {c.name for c in db.scalars(select(models.Category)).all()}
    created = 0
    for name, color in default_cats:
        if name not in existing:
            db.add(models.Category(name=name, color=color))
            created += 1
    db.commit()

    cats = db.scalars(select(models.Category)).all()
    tx_created = 0
    now = datetime.now(timezone.utc)
    for _ in range(12):
        cat = random.choice(cats) if cats else None
        is_income = random.random() > 0.6
        amount = Decimal(str(round(random.uniform(10, 500), 2)))
        if not is_income:
            amount = Decimal(str(round(random.uniform(10, 200), 2)))
        tx = models.Transaction(
            category_id=cat.id if cat else None,
            type=models.TxType.income if is_income else models.TxType.expense,
            amount=amount,
            description=("Przychód" if is_income else "Wydatek") + " demo",
            date=now - timedelta(days=random.randint(0, 45)),
            is_planned=False,
        )
        db.add(tx)
        tx_created += 1
    db.commit()

    return {"categories_created": created, "transactions_created": tx_created}


@router.post("/clear")
def clear_all(db: Session = Depends(get_db)):
    """Danger: remove all transactions and categories. No auth for MVP."""
    tx_deleted = db.query(models.Transaction).delete()
    cat_deleted = db.query(models.Category).delete()
    db.commit()
    return {"transactions_deleted": tx_deleted, "categories_deleted": cat_deleted}