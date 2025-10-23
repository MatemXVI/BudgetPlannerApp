from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case
from datetime import datetime, timezone
from typing import Optional
from ..database import get_db
from .. import models

router = APIRouter(prefix="/reports", tags=["reports"])

from ..deps import get_current_user

@router.get("/balance")
def get_balance(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    income_sum = db.scalar(
        select(func.coalesce(func.sum(models.Transaction.amount), 0))
        .where(models.Transaction.user_id == current_user.id)
        .where(models.Transaction.type == models.TxType.income)
    ) or 0
    expense_sum = db.scalar(
        select(func.coalesce(func.sum(models.Transaction.amount), 0))
        .where(models.Transaction.user_id == current_user.id)
        .where(models.Transaction.type == models.TxType.expense)
    ) or 0
    net = income_sum - expense_sum
    return {"income": str(income_sum), "expense": str(expense_sum), "net": str(net)}

@router.get("/monthly")
def get_monthly_report(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return income/expense/net for a given month (defaults to current month)."""
    now = datetime.now(timezone.utc)
    y = year or now.year
    m = month or now.month
    if m < 1 or m > 12:
        raise HTTPException(status_code=400, detail="Invalid month")
    start = datetime(y, m, 1)
    # compute start of next month
    if m == 12:
        end = datetime(y + 1, 1, 1)
    else:
        end = datetime(y, m + 1, 1)

    income_sum = db.scalar(
        select(func.coalesce(func.sum(models.Transaction.amount), 0))
        .where(models.Transaction.user_id == current_user.id)
        .where(models.Transaction.type == models.TxType.income)
        .where(models.Transaction.date >= start)
        .where(models.Transaction.date < end)
    ) or 0
    expense_sum = db.scalar(
        select(func.coalesce(func.sum(models.Transaction.amount), 0))
        .where(models.Transaction.user_id == current_user.id)
        .where(models.Transaction.type == models.TxType.expense)
        .where(models.Transaction.date >= start)
        .where(models.Transaction.date < end)
    ) or 0
    net = income_sum - expense_sum
    return {
        "year": y,
        "month": m,
        "income": str(income_sum),
        "expense": str(expense_sum),
        "net": str(net),
    }


@router.get("/by-category")
def report_by_category(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Aggregate income/expense by category for current user (including uncategorized)."""
    income_sum = func.coalesce(func.sum(case((models.Transaction.type == models.TxType.income, models.Transaction.amount), else_=0)), 0)
    expense_sum = func.coalesce(func.sum(case((models.Transaction.type == models.TxType.expense, models.Transaction.amount), else_=0)), 0)

    stmt = (
        select(
            models.Category.id.label("category_id"),
            models.Category.name.label("category_name"),
            income_sum.label("income"),
            expense_sum.label("expense"),
        )
        .join(
            models.Transaction,
            (models.Transaction.category_id == models.Category.id)
            & (models.Transaction.user_id == current_user.id),
            isouter=True,
        )
        .where(models.Category.user_id == current_user.id)
        .group_by(models.Category.id, models.Category.name)
        .order_by(models.Category.name.asc())
    )
    rows = db.execute(stmt).mappings().all()

    unc_stmt = select(
        income_sum.label("income"),
        expense_sum.label("expense"),
    ).where(models.Transaction.category_id.is_(None)).where(models.Transaction.user_id == current_user.id)
    unc = db.execute(unc_stmt).mappings().first()
    result = [
        {
            "category_id": r["category_id"],
            "category_name": r["category_name"],
            "income": str(r["income"] or 0),
            "expense": str(r["expense"] or 0),
            "total": str((r["income"] or 0) - (r["expense"] or 0)),
        }
        for r in rows
    ]
    if unc and ((unc["income"] or 0) != 0 or (unc["expense"] or 0) != 0):
        result.append({
            "category_id": None,
            "category_name": "(Brak kategorii)",
            "income": str(unc["income"] or 0),
            "expense": str(unc["expense"] or 0),
            "total": str((unc["income"] or 0) - (unc["expense"] or 0)),
        })
    return result