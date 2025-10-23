from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import random
from decimal import Decimal
from ..database import get_db
from .. import models
from ..deps import get_current_user

router = APIRouter(prefix="/debug", tags=["debug"])

@router.post("/seed-demo")
def seed_demo(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Seed a few demo categories and random transactions for the current user. Auth required."""
    default_cats = [
        ("Jedzenie", "#f59e0b"),
        ("Transport", "#3b82f6"),
        ("Rachunki", "#ef4444"),
        ("Wypłata", "#10b981"),
    ]
    existing = {c.name for c in db.scalars(select(models.Category).where(models.Category.user_id == current_user.id)).all()}
    created = 0
    for name, color in default_cats:
        if name not in existing:
            db.add(models.Category(name=name, color=color, user_id=current_user.id))
            created += 1
    db.commit()

    cats = db.scalars(select(models.Category).where(models.Category.user_id == current_user.id)).all()
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
            user_id=current_user.id,
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
def clear_all(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Danger: remove all current user's transactions and categories. Auth required."""
    tx_deleted = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).delete()
    cat_deleted = db.query(models.Category).filter(models.Category.user_id == current_user.id).delete()
    db.commit()
    return {"transactions_deleted": tx_deleted, "categories_deleted": cat_deleted}