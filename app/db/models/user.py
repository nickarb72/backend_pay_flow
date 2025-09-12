from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class UserRole(enum.Enum):
    """Enumeration for user roles."""
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    """
    Represents a user of the system.

    Users can have multiple accounts and can be either regular users or administrators.
    """
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole, name="userrole"), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
