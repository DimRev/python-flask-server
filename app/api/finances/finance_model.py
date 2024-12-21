from datetime import datetime, timezone

from sqlalchemy import Column, Boolean, Integer, Float, String, ForeignKey, TIMESTAMP

from db.db import Database

Base = Database().Base


class Finance(Base):
    __tablename__ = "finances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, unique=True)

    is_tracking = Column(Boolean, nullable=False, default=False)

    last_closing_price = Column(Integer, nullable=True)
    daily_change_value = Column(Float, nullable=True)
    daily_change_percentage = Column(Float, nullable=True)

    created_at = Column(
        TIMESTAMP, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Finance(id={self.id}, symbol={self.symbol})>"

    def __str__(self):
        return f"<Finance(id={self.id}, symbol={self.symbol})>"


class FinanceHistory(Base):
    __tablename__ = "finance_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    finance_id = Column(Integer, ForeignKey("finances.id"), nullable=False)
    current_price = Column(Integer, nullable=False)

    created_at = Column(
        TIMESTAMP, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<FinanceHistory(id={self.id}, finance_id={self.finance_id}, current_price={self.current_price})>"

    def __str__(self):
        return f"<FinanceHistory(id={self.id}, finance_id={self.finance_id}, current_price={self.current_price})>"
