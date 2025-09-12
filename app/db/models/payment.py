from sqlalchemy import Column, BigInteger, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.session import Base


class Payment(Base):
    """
    Represents a payment transaction that credits a user's account.

    Each payment is associated with a user and an account.
    Financial records must be preserved even if the user or account is deleted.
    Therefore, foreign keys use SET NULL to maintain the record while allowing deletion.
    """
    __tablename__ = "payments"

    # transaction_id = Column(Text, primary_key=True, index=True)
    transaction_id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    account_id = Column(BigInteger, ForeignKey("accounts.id", ondelete="SET NULL"))
    amount = Column(Numeric(scale=2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payments")
    account = relationship("Account", back_populates="payments")

    def __repr__(self):
        return f"<Payment(transaction_id='{self.transaction_id}', amount={self.amount}, account_id={self.account_id})>"
