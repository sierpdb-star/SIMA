from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone

from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="draft"
    )

    scheduled_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
