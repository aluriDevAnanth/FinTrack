from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, field_validator, EmailStr, Field, ConfigDict
from enum import Enum
from typing import get_type_hints


# Enums for type fields
class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# Base models with common fields
class BaseUserModel(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=50)


class BaseCategoryModel(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    type: CategoryType


class BaseTransactionModel(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=255)
    transaction_date: date


# User models
class UserCreate(BaseUserModel):
    password: str = Field()


class UserUpdate(BaseUserModel):
    user_id: int
    username: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)


# Category models
class CategoryCreate(BaseCategoryModel):
    user_id: int


class CategoryResponse(BaseCategoryModel):
    category_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Income models
class IncomeCreate(BaseTransactionModel):
    user_id: int
    category_id: int


class IncomeResponse(BaseTransactionModel):
    income_id: int
    user_id: int
    category_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Expense models
class ExpenseCreate(BaseTransactionModel):
    user_id: int
    category_id: int


class ExpenseResponse(BaseTransactionModel):
    expense_id: int
    user_id: int
    category_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Transaction models
class TransactionCreate(BaseTransactionModel):
    user_id: int
    category_id: int
    type: TransactionType


class TransactionResponse(BaseTransactionModel):
    transaction_id: int
    user_id: int
    category_id: int
    type: TransactionType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Budget models
class BudgetCreate(BaseModel):
    user_id: int
    category_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        start_date = info.data.get("start_date")
        if start_date and v <= start_date:
            raise ValueError("End date must be after start date")
        return v


class BudgetResponse(BudgetCreate):
    budget_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Savings Goal models
class SavingsGoalCreate(BaseModel):
    user_id: int
    name: str = Field(..., min_length=1, max_length=100)
    target_amount: Decimal = Field(..., gt=0, decimal_places=2)
    current_amount: Decimal = Field(..., ge=0, decimal_places=2)
    target_date: Optional[date] = None

    @field_validator("current_amount")
    @classmethod
    def validate_current_amount(cls, v: Decimal, info) -> Decimal:
        target_amount = info.data.get("target_amount")
        if target_amount and v > target_amount:
            raise ValueError("Current amount cannot exceed target amount")
        return v


class BaseSuccessResponse(BaseModel):
    success: bool
    message: str


class BaseErrorResponse(BaseModel):
    success: bool
    error: str
    errorType: str


class SavingsGoalResponse(SavingsGoalCreate):
    goal_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# DB Schema
class User(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime
    updated_at: datetime
