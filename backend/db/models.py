from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


def now_utc():
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=now_utc, nullable=False)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc, nullable=False)

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    recurring = relationship("RecurringTransaction", back_populates="user", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String, nullable=False)
    merchant = Column(String, nullable=True)
    account_type = Column(String, nullable=True)
    recurring_id = Column(Integer, ForeignKey("recurring_transactions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=now_utc, nullable=False)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc, nullable=False)

    user = relationship("User", back_populates="transactions")
    recurring = relationship("RecurringTransaction", back_populates="transactions")

    __table_args__ = (
        Index("idx_transactions_user_date", "user_id", "date"),
        Index("idx_transactions_user_category", "user_id", "category"),
    )


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String, nullable=False)
    target = Column(Float, nullable=False)
    current = Column(Float, nullable=False, default=0)
    deadline = Column(Date, nullable=True)
    category = Column(String, nullable=True)
    monthly_contribution = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now_utc, nullable=False)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc, nullable=False)

    user = relationship("User", back_populates="goals")

    __table_args__ = (
        Index("idx_goals_user_deadline", "user_id", "deadline"),
    )


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    category = Column(String, nullable=False)
    budgeted = Column(Float, nullable=False)
    month = Column(String, nullable=False)  # YYYY-MM
    created_at = Column(DateTime, default=now_utc, nullable=False)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc, nullable=False)

    user = relationship("User", back_populates="budgets")

    __table_args__ = (
        UniqueConstraint("user_id", "month", "category", name="uq_budgets_user_month_category"),
        Index("idx_budgets_user_month", "user_id", "month"),
    )


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    frequency = Column(String, nullable=False)
    interval = Column(Integer, nullable=False, default=1)
    next_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=now_utc, nullable=False)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc, nullable=False)

    user = relationship("User", back_populates="recurring")
    transactions = relationship("Transaction", back_populates="recurring")

    __table_args__ = (
        Index("idx_recurring_user_next_date", "user_id", "next_date"),
    )
