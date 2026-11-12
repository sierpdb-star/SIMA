
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey
)
from datetime import datetime, timezone

from app.database import Base


class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, index=True)

    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id"),
        nullable=False
    )

    contact_id = Column(
        Integer,
        ForeignKey("contacts.id"),
        nullable=False
    )

    channel = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="pending"
    )

    provider_message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
