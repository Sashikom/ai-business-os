import enum
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Enum, Text, Boolean, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubscriptionStatus(str, enum.Enum):
    DEMO = "DEMO"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    telegram_username = Column(String, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    subscription_status = Column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.DEMO,
        nullable=False,
    )
    demo_started_at = Column(DateTime, nullable=True)
    access_token = Column(String, nullable=True)
    access_expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    generations = relationship("Generation", back_populates="user")

    @property
    def has_access(self) -> bool:
        if self.subscription_status == SubscriptionStatus.ACTIVE:
            if self.access_expires_at and self.access_expires_at > datetime.utcnow():
                return True
            elif self.access_expires_at is None:
                return True
            else:
                return False
        if self.subscription_status == SubscriptionStatus.DEMO:
            if self.demo_started_at is None:
                return True
            days_passed = (datetime.utcnow() - self.demo_started_at).days
            return days_passed < 3
        return False

    @property
    def days_left(self) -> int:
        if self.subscription_status == SubscriptionStatus.ACTIVE:
            if self.access_expires_at:
                delta = self.access_expires_at - datetime.utcnow()
                return max(0, delta.days)
            return 999
        if self.subscription_status == SubscriptionStatus.DEMO:
            if self.demo_started_at is None:
                return 3
            days_passed = (datetime.utcnow() - self.demo_started_at).days
            return max(0, 3 - days_passed)
        return 0


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subscription_status = Column(String, default="free")
    credits_balance = Column(Integer, default=0)
    credits_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    role = Column(String, default="member")
    created_at = Column(DateTime, default=datetime.utcnow)


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    module = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="generations")


class AccessToken(Base):
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    duration_days = Column(Integer, default=30, nullable=False)
    used_by_telegram_id = Column(BigInteger, nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_used = Column(Integer, default=0)

    @staticmethod
    def generate_token() -> str:
        part1 = uuid.uuid4().hex[:8].upper()
        part2 = uuid.uuid4().hex[:8].upper()
        return f"AIBOS-{part1}-{part2}"
