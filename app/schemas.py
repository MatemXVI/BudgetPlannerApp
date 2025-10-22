from pydantic import BaseModel, Field, condecimal
from typing import Optional, Literal
from datetime import datetime, date


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=32)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=32)


class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# Transaction Schemas
TxTypeLiteral = Literal["income", "expense"]


class TransactionBase(BaseModel):
    category_id: Optional[int] = None
    type: TxTypeLiteral
    amount: condecimal(max_digits=10, decimal_places=2)  # type: ignore
    description: Optional[str] = Field(None, max_length=255)
    date: datetime
    is_planned: bool = False


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    type: Optional[TxTypeLiteral] = None
    amount: Optional[condecimal(max_digits=10, decimal_places=2)] = None  # type: ignore
    description: Optional[str] = Field(None, max_length=255)
    date: Optional[datetime] = None
    is_planned: Optional[bool] = None


class TransactionOut(TransactionBase):
    id: int

    class Config:
        from_attributes = True


# Filters
class TransactionFilters(BaseModel):
    type: Optional[TxTypeLiteral] = None
    category_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    q: Optional[str] = None
    skip: int = 0
    limit: int = 100


# Reports
class BalanceOut(BaseModel):
    income: condecimal(max_digits=12, decimal_places=2)  # type: ignore
    expense: condecimal(max_digits=12, decimal_places=2)  # type: ignore
    net: condecimal(max_digits=12, decimal_places=2)  # type: ignore
