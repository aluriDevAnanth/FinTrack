from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, field_validator, EmailStr, Field, ConfigDict
from enum import Enum


# Base models for responses
class BaseSuccessResponse(BaseModel):
    success: bool
    message: str


class BaseErrorResponse(BaseModel):
    success: bool
    error: str
    errorType: str


# Base models with common fields
class BaseUserModel(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=50)


class BaseTransactionModel(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    description: Optional[str] = Field(default=None, max_length=255)
    transaction_date: date


# User models
class User(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime
    updated_at: datetime


class CreateUser(BaseUserModel):
    password: str = Field()


class UpdateUser(BaseUserModel):
    user_id: int
    username: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)


# Income models
class BaseIncomeModel(BaseModel):
    income_id: Optional[int]
    user_id: Optional[int]
    amount: Optional[Decimal]
    description: Optional[str]
    income_date: Optional[date]
    created_at: Optional[datetime]


class Income(BaseIncomeModel):
    income_id: int
    user_id: int
    amount: Decimal
    description: Optional[str]
    income_date: date
    created_at: datetime


class CreateIncome(BaseModel):
    user_id: int
    amount: Decimal
    description: Optional[str]
    income_date: date


class UpdateIncome(BaseModel):
    income_id: int
    user_id: Optional[int] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    income_date: Optional[date] = None


# Expense models
class BaseExpenseModel(BaseModel):
    expense_id: Optional[int]
    user_id: Optional[int]
    amount: Optional[Decimal]
    description: Optional[str]
    expense_date: Optional[date]
    created_at: Optional[datetime]


class Expense(BaseExpenseModel):
    expense_id: int
    user_id: int
    amount: Decimal
    description: Optional[str]
    expense_date: date
    created_at: datetime


class CreateExpense(BaseModel):
    user_id: int
    amount: Decimal
    description: Optional[str]
    expense_date: date


class UpdateExpense(BaseModel):
    expense_id: int
    user_id: Optional[int] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    expense_date: Optional[date] = None


# Transaction models
class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class BaseTransactionModel(BaseModel):
    transaction_id: Optional[int]
    user_id: Optional[int]
    amount: Optional[Decimal]
    description: Optional[str]
    transaction_date: Optional[date]
    type: Optional[TransactionType]
    created_at: Optional[datetime]


class Transaction(BaseTransactionModel):
    transaction_id: int
    user_id: int
    amount: Decimal
    transaction_date: date
    type: TransactionType
    created_at: datetime


class CreateTransaction(BaseModel):
    user_id: int
    amount: Decimal
    description: Optional[str]
    transaction_date: date
    type: TransactionType


class UpdateTransaction(BaseModel):
    transaction_id: int
    user_id: Optional[int] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_date: Optional[date] = None
    type: Optional[TransactionType] = None


# Budget models
class BudgetCreate(BaseModel):
    user_id: int
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


class SavingsGoalResponse(SavingsGoalCreate):
    goal_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
