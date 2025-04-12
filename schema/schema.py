from datetime import date, datetime, UTC
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
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
class BaseBudgetModel(BaseModel):
    budget_id: Optional[int]
    user_id: Optional[int]
    amount: Optional[Decimal]
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: Optional[datetime]


class Budget(BaseBudgetModel):
    budget_id: int
    user_id: int
    amount: Decimal
    start_date: date
    end_date: date
    created_at: datetime


class CreateBudget(BaseModel):
    user_id: int
    amount: Decimal
    start_date: date
    end_date: date


class UpdateBudget(BaseModel):
    budget_id: int
    user_id: Optional[int] = None
    amount: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# Savings Goal models
class BaseSavingsGoalModel(BaseModel):
    goal_id: Optional[int]
    user_id: Optional[int]
    name: Optional[str]
    target_amount: Optional[Decimal]
    current_amount: Optional[Decimal]
    target_date: Optional[date]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class SavingsGoal(BaseSavingsGoalModel):
    goal_id: int
    user_id: int
    name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: Optional[date]
    created_at: datetime
    updated_at: datetime


class CreateSavingsGoal(BaseModel):
    user_id: int
    name: str
    target_amount: Decimal
    current_amount: Optional[Decimal] = 0.00
    target_date: date


class UpdateSavingsGoal(BaseModel):
    goal_id: int
    user_id: Optional[int] = None
    name: Optional[str] = None
    target_amount: Optional[Decimal] = None
    current_amount: Optional[Decimal] = None
    target_date: Optional[date] = None
