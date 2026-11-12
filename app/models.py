
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from datetime import datetime, timezone

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    channel = Column(String, nullable=False)

    consent_status = Column(
        String,
        nullable=False,
        default="pending"
    )

    consent_source = Column(String, nullable=True)
    consent_at = Column(DateTime(timezone=True), nullable=True)
    opted_out_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "phone",
            "channel",
            name="uq_company_phone_channel"
        ),
    )
