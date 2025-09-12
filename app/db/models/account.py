from _decimal import Decimal
from sqlalchemy import Column, BigInteger, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Account(Base):
    """
    Represents a financial account belonging to a user.

    Each account has a balance and is associated with a single user.
    Users can have multiple accounts.
    """
    __tablename__ = "accounts"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    balance = Column(Numeric(scale=2), default=Decimal('0.00'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="accounts")
    payments = relationship("Payment", back_populates="account")

    def __repr__(self):
        return f"<Account(id={self.id}, user_id={self.user_id}, balance={self.balance})>"
